"""S1 Aşama B'nin tamamı ve Kapı 1 değerlendirmesi (ön kayıt §5–§6 + Ek 1).

- B2: 5m, 15m, 1h spot (+ 1h vadeli kontrol); 1s ve 1m ara rapor 1'den alınır.
- B3: 1m, 5m, 15m, 1h spot (+ 1m, 1h vadeli kontrol); K = 2 (ana) ve 3; h = 1, 3, 5, 10.
- B5: 1h spot (+ vadeli kontrol), ana ufuk 24 saat.
- BH aileleri: B2 60 (HAC tek yönlü p), B3 48 (wild p), B5 12 (wild p); q = %10.

Çalıştırma: .venv/Scripts/python -m calismalar.S1_btc_alt_gecikme.kod.kapi1 [--b3 [1m:spot,...]] [--b5] [--b2] [--degerlendir]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from calismalar.S1_btc_alt_gecikme.kod import olcum
from calismalar.S1_btc_alt_gecikme.kod.ara_rapor_1 import ALTLAR, b1_b2, getiriler
from calismalar.S1_btc_alt_gecikme.kod.veri_indir import DONEMLER, yukle
from ortak import istatistik, maliyet, rapor, veri

SONUC = Path(__file__).resolve().parents[1] / "results"
Q = 0.10


# ---------------------------------------------------------------- yardımcılar

def tam_izgara(aralik: str) -> pd.DatetimeIndex:
    bas, son = DONEMLER[aralik]
    return pd.date_range(pd.Timestamp(bas, tz="UTC"), pd.Timestamp(son, tz="UTC"),
                         freq=pd.Timedelta(milliseconds=veri.ARALIK_MS[aralik]), inclusive="left")


def orta_nokta(aralik: str) -> pd.Timestamp:
    bas, son = (pd.Timestamp(x, tz="UTC") for x in DONEMLER[aralik])
    return bas + (son - bas) / 2


def vadeli_yarim_spread() -> dict:
    yol = SONUC / "spread_ozet.csv"
    oz = pd.read_csv(yol)
    oz = oz[oz["piyasa"] == "vadeli"]
    return dict(zip(oz["coin"], oz["ortalama_yarim_spread"]))


def maliyet_modeli() -> maliyet.MaliyetModeli:
    return maliyet.MaliyetModeli(olculen_yarim_spread=vadeli_yarim_spread())


def b3_esik(coin: str, m: maliyet.MaliyetModeli) -> float:
    return 2 * m.gidis_donus(coin, veri.coin_grubu(coin), "vadeli", "taker")


def b5_esik(coin: str, m: maliyet.MaliyetModeli) -> float:
    cift = m.gidis_donus(coin, veri.coin_grubu(coin), "vadeli") + m.gidis_donus("BTC", "Referans", "vadeli")
    return 2 * cift


# ---------------------------------------------------------------- ölçümler

def olc_b2():
    parcalar = []
    for aralik in ("5m", "15m", "1h"):
        parcalar.append(b1_b2(aralik, "spot", 1000))
    b2 = pd.concat(parcalar, ignore_index=True)
    v = b1_b2("1h", "vadeli", 0)
    wild = []
    for aralik, piyasa in (("5m", "spot"), ("15m", "spot"), ("1h", "spot"), ("1h", "vadeli")):
        _, r_btc, altlar = getiriler(aralik, piyasa)
        for c, (_, r_alt) in altlar.items():
            w = olcum.b2_wild_bootstrap(r_btc.reindex(r_alt.index), r_alt, aralik)
            wild.append({"coin": c, "aralik": aralik, "piyasa": piyasa, **w})
    wild = pd.DataFrame(wild)
    b2 = b2.merge(wild, on=["coin", "aralik", "piyasa"])
    v = v.merge(wild, on=["coin", "aralik", "piyasa"])
    b2.to_csv(SONUC / "b1_b2_spot_5m_15m_1h.csv", index=False)
    v.to_csv(SONUC / "b1_b2_vadeli_1h_kontrol.csv", index=False)
    print("B2 bitti", flush=True)


B3_KOMBINASYONLAR = [("1m", "spot"), ("5m", "spot"), ("15m", "spot"), ("1h", "spot"),
                     ("1m", "vadeli"), ("1h", "vadeli")]


def olc_b3(kombinasyonlar=B3_KOMBINASYONLAR):
    for aralik, piyasa in kombinasyonlar:
        ozetler, ayrintilar = [], []
        tam = tam_izgara(aralik)
        orta = orta_nokta(aralik)
        btc = olcum.izgara(yukle("BTC", aralik, piyasa), aralik, tam)
        r_btc = np.log(btc["close"]).diff()
        altlar = {c: olcum.izgara(yukle(c, aralik, piyasa), aralik, tam) for c in ALTLAR}
        for K in (2, 3):
            ev = olcum.olaylar(r_btc, K)
            for c, alt in altlar.items():
                t = olcum.b3_olay_tablosu(btc, alt, aralik, ev)
                oz = olcum.b3_ozet(t, aralik, orta, ana_h=3)
                oz.update({"coin": c, "grup": veri.coin_grubu(c), "aralik": aralik, "piyasa": piyasa,
                           "K": K, "btc_olay": len(ev)})
                ozetler.append(oz)
                for h in olcum.UFUKLAR:
                    d = t.dropna(subset=[f"acilis_h{h}"])
                    w = olcum.wild_ortalama(d[f"acilis_h{h}"].to_numpy(), d.index, olcum.BLOK[aralik])
                    ayrintilar.append({"coin": c, "aralik": aralik, "piyasa": piyasa, "K": K, "h": h,
                                       "olay": len(d), "ortalama": float(d[f"acilis_h{h}"].mean()), **w})
                print("B3", aralik, piyasa, K, c, oz["olay"], f"{oz['ortalama']:.5f}", flush=True)
        pd.DataFrame(ozetler).to_csv(SONUC / "b3" / f"ozet_{aralik}_{piyasa}.csv", index=False)
        pd.DataFrame(ayrintilar).to_csv(SONUC / "b3" / f"ufuklar_{aralik}_{piyasa}.csv", index=False)


def b3_oku(tur: str) -> pd.DataFrame:
    return pd.concat([pd.read_csv(SONUC / "b3" / f"{tur}_{a}_{p}.csv") for a, p in B3_KOMBINASYONLAR],
                     ignore_index=True)


def olc_b5():
    satirlar = []
    for piyasa in ("spot", "vadeli"):
        tam = tam_izgara("1h")
        orta = orta_nokta("1h")
        btc = olcum.izgara(yukle("BTC", "1h", piyasa), "1h", tam)
        for c in ALTLAR:
            alt = olcum.izgara(yukle(c, "1h", piyasa), "1h", tam)
            t, z = olcum.b5_olaylar(btc, alt)
            d = t.dropna(subset=["y_h24"])
            y = d["y_h24"].to_numpy()
            s = {"coin": c, "grup": veri.coin_grubu(c), "piyasa": piyasa, "olay": len(d),
                 "ortalama_y24": float(y.mean()) if len(y) else np.nan,
                 "medyan_y24": float(np.median(y)) if len(y) else np.nan,
                 "yari_omur_saat": istatistik.yari_omur(z)}
            s.update(olcum.wild_ortalama(y, d.index, "1D"))
            s.update(olcum.iki_yari(y, d.index, orta))
            for h in (1, 6):
                dh = t.dropna(subset=[f"y_h{h}"])
                s[f"ortalama_y{h}"] = float(dh[f"y_h{h}"].mean())
                s.update({f"y{h}_{k}": v for k, v in
                          olcum.wild_ortalama(dh[f"y_h{h}"].to_numpy(), dh.index, "1D").items()})
            for h in (1, 6, 24):
                s[f"dz_h{h}_ort"] = float(t[f"dz_h{h}"].mean())
            satirlar.append(s)
            print("B5", piyasa, c, s["olay"], f"{s['ortalama_y24']:.5f}", flush=True)
    pd.DataFrame(satirlar).to_csv(SONUC / "b5_ozet.csv", index=False)


# ---------------------------------------------------------------- Kapı 1

def degerlendir():
    m = maliyet_modeli()

    # B2: 60'lık aile
    b2a = pd.read_csv(SONUC / "b1_b2_spot_1s_1m.csv")
    wa = pd.read_csv(SONUC / "b2_wild_bootstrap_ek.csv")
    b2a = b2a.merge(wa[["coin", "aralik", "piyasa", "wild_yuzdelik", "wild_p"]], on=["coin", "aralik", "piyasa"])
    b2b = pd.read_csv(SONUC / "b1_b2_spot_5m_15m_1h.csv")
    b2 = pd.concat([b2a, b2b], ignore_index=True)
    b2["bh_anlamli"], b2["bh_p"] = istatistik.benjamini_hochberg(b2["b1_p_tek"].to_numpy(), Q)
    b2["wild_gecti"] = b2["wild_yuzdelik"] > 95
    b2["istatistiksel_gecti"] = b2["bh_anlamli"] & b2["wild_gecti"] & b2["yarilar_gecti"]
    b2.to_csv(SONUC / "kapi1_b2.csv", index=False)

    # B3: 48'lik aile (spot, K=2, h=3)
    b3 = b3_oku("ozet")
    ana = b3[(b3.piyasa == "spot") & (b3.K == 2)].copy()
    ana["bh_anlamli"], ana["bh_p"] = istatistik.benjamini_hochberg(ana["wild_p"].to_numpy(), Q)
    ana["esik"] = [b3_esik(c, m) for c in ana["coin"]]
    ana["k_yarilar"] = ana["yarilar_gecti"]
    ana["k_wild"] = ana["wild_yuzdelik"] > 95
    ana["k_bh"] = ana["bh_anlamli"]
    ana["k_maliyet"] = ana["ortalama"] >= ana["esik"]
    ana["k_olay"] = ana["olay"] >= 200
    ana["kapi1"] = ana[["k_yarilar", "k_wild", "k_bh", "k_maliyet", "k_olay"]].all(axis=1)
    ana["maliyet_orani"] = ana["ortalama"] / ana["esik"]
    ana.to_csv(SONUC / "kapi1_b3.csv", index=False)

    # B5: 12'lik aile (spot)
    b5 = pd.read_csv(SONUC / "b5_ozet.csv")
    b5s = b5[b5.piyasa == "spot"].copy()
    b5s["bh_anlamli"], b5s["bh_p"] = istatistik.benjamini_hochberg(b5s["wild_p"].to_numpy(), Q)
    b5s["esik"] = [b5_esik(c, m) for c in b5s["coin"]]
    b5s["k_yarilar"] = b5s["yarilar_gecti"]
    b5s["k_wild"] = b5s["wild_yuzdelik"] > 95
    b5s["k_bh"] = b5s["bh_anlamli"]
    b5s["k_maliyet"] = b5s["ortalama_y24"] >= b5s["esik"]
    b5s["k_olay"] = b5s["olay"] >= 50
    b5s["kapi1"] = b5s[["k_yarilar", "k_wild", "k_bh", "k_maliyet", "k_olay"]].all(axis=1)
    b5s["maliyet_orani"] = b5s["ortalama_y24"] / b5s["esik"]
    b5s.to_csv(SONUC / "kapi1_b5.csv", index=False)

    kayitla(b2b, b3, ana, b5, b5s)
    print("B2 istatistiksel geçen:", int(b2["istatistiksel_gecti"].sum()), "/ 60")
    print("B3 Kapı 1 geçen:", int(ana["kapi1"].sum()), "/ 48;  maliyeti geçen:", int(ana["k_maliyet"].sum()))
    print("B5 Kapı 1 geçen:", int(b5s["kapi1"].sum()), "/ 12;  maliyeti geçen:", int(b5s["k_maliyet"].sum()))


def kayitla(b2b, b3, ana, b5, b5s):
    for _, r in b2b.iterrows():
        rapor.kayit_ekle("S1", "B2", "b1>0 HAC tek yönlü (ana test)", r.coin, r.aralik,
                         f"b1={r.b1:.4f}, t={r.b1_t:.2f}, p={r.b1_p_tek:.3g}, wild %{r.wild_yuzdelik:.1f}, "
                         f"yarılar {'geçti' if r.yarilar_gecti else 'kaldı'}")
    v = pd.read_csv(SONUC / "b1_b2_vadeli_1h_kontrol.csv")
    for _, r in v.iterrows():
        rapor.kayit_ekle("S1", "B2", "vadeli kontrol (BH dışı)", r.coin, "1h",
                         f"b1={r.b1:.4f}, t={r.b1_t:.2f}, wild %{r.wild_yuzdelik:.1f}")
    for _, r in ana.iterrows():
        rapor.kayit_ekle("S1", "B3", "K=2 h=3 açılış→açılış (ana test)", r.coin, r.aralik,
                         f"olay={r.olay}, ort=%{r.ortalama * 100:.4f}, eşik=%{r.esik * 100:.2f}, "
                         f"wild %{r.wild_yuzdelik:.1f}, BH p={r.bh_p:.3g}, yarılar "
                         f"{'geçti' if r.yarilar_gecti else 'kaldı'}, Q1(geride)=%{r.q1_geride_ort * 100:.4f}, "
                         f"Kapı 1 {'GEÇTİ' if r.kapi1 else 'kaldı'}")
    tum = b3_oku("ufuklar")
    for _, r in tum.iterrows():
        if r.piyasa == "spot" and r.K == 2 and r.h == 3:
            continue
        rapor.kayit_ekle("S1", "B3", f"tanımlayıcı K={r.K} h={r.h} ({r.piyasa})", r.coin, r.aralik,
                         f"olay={r.olay}, ort=%{r.ortalama * 100:.4f}, wild %{r.wild_yuzdelik:.1f}")
    for _, r in b5s.iterrows():
        rapor.kayit_ekle("S1", "B5", "ALT/BTC dengeye dönüş h=24 (ana test)", r.coin, "1h",
                         f"olay={r.olay}, ort=%{r.ortalama_y24 * 100:.3f}, eşik=%{r.esik * 100:.2f}, "
                         f"wild %{r.wild_yuzdelik:.1f}, BH p={r.bh_p:.3g}, Kapı 1 {'GEÇTİ' if r.kapi1 else 'kaldı'}")
    for _, r in b5.iterrows():
        for h in (1, 6):
            rapor.kayit_ekle("S1", "B5", f"tanımlayıcı h={h} ({r.piyasa})", r.coin, "1h",
                             f"ort=%{r[f'ortalama_y{h}'] * 100:.3f}, wild %{r[f'y{h}_wild_yuzdelik']:.1f}")
        if r.piyasa == "vadeli":
            rapor.kayit_ekle("S1", "B5", "vadeli kontrol h=24 (BH dışı)", r.coin, "1h",
                             f"olay={r.olay}, ort=%{r.ortalama_y24 * 100:.3f}, wild %{r.wild_yuzdelik:.1f}")


def main():
    """Bayraklar: --b3 [aralik:piyasa,...]  --b5  --b2  --degerlendir  (bayraksız: hepsi)"""
    sys.stdout.reconfigure(encoding="utf-8")
    (SONUC / "b3").mkdir(parents=True, exist_ok=True)
    a = sys.argv[1:]
    hepsi = not a
    if hepsi or "--b3" in a:
        secim = B3_KOMBINASYONLAR
        i = a.index("--b3") + 1 if "--b3" in a else None
        if i is not None and i < len(a) and not a[i].startswith("--"):
            secim = [tuple(x.split(":")) for x in a[i].split(",")]
        olc_b3(secim)
    if hepsi or "--b5" in a:
        olc_b5()
    if hepsi or "--b2" in a:
        olc_b2()
    if hepsi or "--degerlendir" in a:
        degerlendir()


if __name__ == "__main__":
    main()
