"""Ortak modüllerin elle hesaplanan değerlerle doğrulanması (Bölüm 12, adım 2)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ortak import backtest, istatistik, maliyet  # noqa: E402

C = 0.0013  # spot taker %0,10 + büyük coin kayma %0,03


@pytest.fixture
def mumlar():
    idx = pd.date_range("2024-01-01", periods=4, freq="1D", tz="UTC")
    return pd.DataFrame({"open": [100.0, 110.0, 121.0, 120.0],
                         "high": [106.0, 116.0, 131.0, 126.0],
                         "low": [99.0, 107.0, 119.0, 118.0],
                         "close": [105.0, 115.0, 130.0, 125.0]}, index=idx)


# ---------------------------------------------------------------- maliyet

def test_maliyet_buyuk_coin():
    m = maliyet.MaliyetModeli()
    assert m.tek_yon("BTC", "Referans", "spot") == pytest.approx(0.0013)
    assert m.tek_yon("ETH", "Büyük", "vadeli") == pytest.approx(0.0008)
    assert m.tek_yon("ETH", "Büyük", "vadeli", "maker") == pytest.approx(0.0005)
    assert m.gidis_donus("BTC", "Referans", "spot") == pytest.approx(0.0026)


def test_maliyet_kucuk_coin_olculen_spread_ve_taban():
    m = maliyet.MaliyetModeli(olculen_yarim_spread={"PEPE": 0.0004, "ARB": 0.0001})
    assert m.tek_yon("PEPE", "Küçük", "spot") == pytest.approx(0.0010 + 0.0008)
    assert m.tek_yon("ARB", "Küçük", "spot") == pytest.approx(0.0010 + 0.0005)  # taban
    assert m.olcekli(1.5).tek_yon("BTC", "Referans", "spot") == pytest.approx(0.0013 * 1.5)


def test_carry_4_bacak():
    m = maliyet.MaliyetModeli()
    assert m.carry_4_bacak("BTC", "Referans") == pytest.approx(2 * (0.0013 + 0.0008))


# ---------------------------------------------------------------- backtest

def test_al_tut_elle_hesapla(mumlar):
    """Karar 0. mum kapanışında, giriş 1. mum açılışında (110), son değer 125 kapanış."""
    s = backtest.pozisyon_backtest(mumlar, pd.Series(1.0, index=mumlar.index), C)
    beklenen = 125 / 110 - C
    assert s["ozsermaye"].iloc[0] == pytest.approx(1.0)
    assert s["ozsermaye"].iloc[1] == pytest.approx(115 / 110 - C)
    assert s["ozsermaye"].iloc[-1] == pytest.approx(beklenen, rel=1e-12)


def test_cikis_sonraki_acilista(mumlar):
    """[1,1,0,0]: 110'dan gir, 2. mum kapanışında çıkış kararı, 3. mum açılışında (120) çık."""
    s = backtest.pozisyon_backtest(mumlar, pd.Series([1.0, 1.0, 0.0, 0.0], index=mumlar.index), C)
    beklenen = 120 / 110 * (1 - C) - C
    assert s["ozsermaye"].iloc[-1] == pytest.approx(beklenen, rel=1e-12)
    assert s["adet"].iloc[-1] == 0


def test_short(mumlar):
    s = backtest.pozisyon_backtest(mumlar, pd.Series(-1.0, index=mumlar.index), C)
    assert s["ozsermaye"].iloc[-1] == pytest.approx(2 - C - 125 / 110, rel=1e-12)


def test_funding_long_oder(mumlar):
    f = pd.Series([0.0, 0.0, 0.001, 0.0], index=mumlar.index)
    s = backtest.pozisyon_backtest(mumlar, pd.Series(1.0, index=mumlar.index), 0.0, funding=f)
    assert s["ozsermaye"].iloc[-1] == pytest.approx(125 / 110 - (1 / 110) * 130 * 0.001)


def test_gelecegi_gormuyor(mumlar):
    """Son mumdaki sinyal hiçbir işlem üretmemeli (sonraki açılış yok)."""
    s = backtest.pozisyon_backtest(mumlar, pd.Series([0, 0, 0, 1.0], index=mumlar.index), C)
    assert (s["ozsermaye"] == 1.0).all()


def test_islem_sure_cikisi(mumlar):
    t = backtest.islem_backtest(mumlar, [0], [1], tutma=2, maliyet_tek_yon=C)
    assert len(t) == 1
    assert t.loc[0, "giris"] == 110 and t.loc[0, "cikis"] == 120
    assert t.loc[0, "net"] == pytest.approx(120 / 110 - 1 - 2 * C)


def test_islem_stop(mumlar):
    t = backtest.islem_backtest(mumlar, [0], [1], tutma=2, maliyet_tek_yon=C, stoplar=[108.0])
    assert t.loc[0, "cikis_nedeni"] == "stop" and t.loc[0, "cikis"] == 108.0


def test_islem_stop_bosluk(mumlar):
    """Short. Stop 115: 1. mum high 116 değer → 115'ten. Stop 117: 1. mumda değmez,
    2. mum 121'den açılır → stop yerine açılıştan (121) çıkılır."""
    t = backtest.islem_backtest(mumlar, [0], [-1], tutma=2, maliyet_tek_yon=0.0, stoplar=[115.0])
    assert t.loc[0, "cikis_nedeni"] == "stop" and t.loc[0, "cikis"] == 115.0
    t2 = backtest.islem_backtest(mumlar, [0], [-1], tutma=2, maliyet_tek_yon=0.0, stoplar=[117.0])
    assert t2.loc[0, "cikis_nedeni"] == "stop_bosluk" and t2.loc[0, "cikis"] == 121.0
    assert t2.loc[0, "brut"] == pytest.approx(-(121 / 110 - 1))


# ---------------------------------------------------------------- istatistik

def test_benjamini_hochberg():
    anlamli, duz = istatistik.benjamini_hochberg(np.array([0.01, 0.04, 0.03, 0.005]), q=0.05)
    assert anlamli.all()
    assert duz == pytest.approx([0.02, 0.04, 0.04, 0.02])


def test_yuzdelik():
    assert istatistik.yuzdelik(5.5, np.arange(10)) == 60.0


def test_yari_omur_ar1():
    g = np.random.default_rng(1)
    phi, z = 0.9, [0.0]
    for _ in range(20000):
        z.append(phi * z[-1] + g.normal())
    assert istatistik.yari_omur(pd.Series(z)) == pytest.approx(np.log(2) / -np.log(phi), rel=0.1)
