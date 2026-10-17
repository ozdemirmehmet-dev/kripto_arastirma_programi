"""Ortak backtest motoru: sinyal → gerçek fiyatla dolum.

Kurallar (Bölüm 2.3):
- Karar mum KAPANIŞINDA verilir; işlem BİR SONRAKİ mumun AÇILIŞINDA yapılır.
- Dolumlar gerçek OHLC fiyatlarıyla yapılır (Heikin Ashi vb. sentetik fiyat yok).
- Maliyet, işlem gören notional üzerinden kesir olarak düşülür.

İki motor var:
- `pozisyon_backtest`: sürekli hedef ağırlık serisi (trend, carry, oynaklık hedefleme).
- `islem_backtest`: tek tek olay işlemleri (sabit süre çıkışı + stop; S1, S3).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

YIL_SANIYE = 365 * 24 * 3600


def yillik_mum_sayisi(index: pd.DatetimeIndex) -> float:
    adim = pd.Series(index).diff().median().total_seconds()
    return YIL_SANIYE / adim


# ---------------------------------------------------------------- sürekli pozisyon

def pozisyon_backtest(df: pd.DataFrame, hedef_agirlik: pd.Series, maliyet_tek_yon: float,
                      baslangic: float = 1.0, funding: pd.Series | None = None) -> pd.DataFrame:
    """Hedef ağırlık serisini gerçek fiyatlarla simüle eder.

    df: open/close sütunlu mumlar. hedef_agirlik[t]: t mumunun KAPANIŞINDA karar
    verilen ağırlık (özsermayeye oranla; 1 = tam long, -1 = tam short, 0 = nakit).
    İşlem t+1 açılışında yapılır. Adet yalnız hedef değişince yeniden ayarlanır
    (arada fiyatla serbestçe kayar). Maliyet = |Δadet|·açılış·maliyet_tek_yon.

    funding (isteğe bağlı): funding anı mumuna hizalı oran serisi. O mum içinde
    tutulan adet için nakit akışı = −adet·kapanış·oran (pozitif oranda long öder).

    Dönüş: her mum için adet, nakit, özsermaye (kapanışta), işlem maliyeti.
    """
    h = hedef_agirlik.reindex(df.index).astype(float)
    # t kapanışındaki karar t+1 açılışında uygulanır
    uygulanan = h.shift(1).to_numpy()
    acilis = df["open"].to_numpy(float)
    kapanis = df["close"].to_numpy(float)
    f = np.zeros(len(df)) if funding is None else funding.reindex(df.index).fillna(0.0).to_numpy(float)

    n = len(df)
    adet_d = np.zeros(n)
    nakit_d = np.zeros(n)
    ozs_d = np.zeros(n)
    mal_d = np.zeros(n)
    nakit, adet, onceki_hedef = baslangic, 0.0, 0.0
    for i in range(n):
        hedef = uygulanan[i]
        if not np.isnan(hedef) and hedef != onceki_hedef:
            ozs_acilis = nakit + adet * acilis[i]
            yeni_adet = hedef * ozs_acilis / acilis[i]
            d = yeni_adet - adet
            m = abs(d) * acilis[i] * maliyet_tek_yon
            nakit -= d * acilis[i] + m
            adet = yeni_adet
            mal_d[i] = m
            onceki_hedef = hedef
        if f[i] != 0.0 and adet != 0.0:
            nakit += -adet * kapanis[i] * f[i]
        adet_d[i], nakit_d[i] = adet, nakit
        ozs_d[i] = nakit + adet * kapanis[i]
    return pd.DataFrame({"adet": adet_d, "nakit": nakit_d, "ozsermaye": ozs_d,
                         "maliyet": mal_d, "agirlik": np.nan_to_num(uygulanan)}, index=df.index)


# ---------------------------------------------------------------- olay işlemleri

@dataclass
class Islem:
    giris_zamani: pd.Timestamp
    cikis_zamani: pd.Timestamp
    yon: int
    giris: float
    cikis: float
    cikis_nedeni: str
    brut: float
    net: float
    sure: int


def islem_backtest(df: pd.DataFrame, sinyal_indeksleri, yonler, tutma: int,
                   maliyet_tek_yon: float, stoplar=None, cakisma_izni: bool = False) -> pd.DataFrame:
    """Olay bazlı işlemler.

    sinyal_indeksleri: sinyal mumlarının konumları (0 tabanlı, kapanışta karar).
    Giriş: i+1 açılışı. Çıkış: giriş mumundan itibaren `tutma` mum sonra, son mumun
    kapanışı yerine bir sonraki mumun AÇILIŞINDA (i+1+tutma). Stop: mum içinde
    stop'a değilirse stop fiyatından; açılış stop'un ötesindeyse açılıştan (kayma).
    Aynı mumda hem giriş hem stop: muhafazakâr olarak stop sayılır.
    """
    o, hi, lo = (df[c].to_numpy(float) for c in ("open", "high", "low"))
    zaman = df.index
    n = len(df)
    stoplar = [None] * len(sinyal_indeksleri) if stoplar is None else list(stoplar)
    kayitlar, mesgul_kadar = [], -1
    for i, yon, stop in zip(sinyal_indeksleri, yonler, stoplar):
        g, c = i + 1, i + 1 + tutma
        if c >= n:
            continue
        if not cakisma_izni and g <= mesgul_kadar:
            continue
        giris, cikis, neden, cikis_idx = o[g], o[c], "sure", c
        if stop is not None and not np.isnan(stop):
            for j in range(g, c):
                acilis_otesinde = o[j] <= stop if yon > 0 else o[j] >= stop
                if acilis_otesinde:  # açılış stop'un ötesinde: açılıştan çık
                    cikis, neden, cikis_idx = o[j], "stop_bosluk", j
                    break
                degdi = lo[j] <= stop if yon > 0 else hi[j] >= stop
                if degdi:
                    cikis, neden, cikis_idx = stop, "stop", j
                    break
        brut = yon * (cikis / giris - 1.0)
        net = brut - 2 * maliyet_tek_yon  # giriş notional'ı üzerinden gidiş-dönüş
        kayitlar.append(Islem(zaman[g], zaman[cikis_idx], int(yon), giris, cikis, neden,
                              brut, net, cikis_idx - g))
        mesgul_kadar = cikis_idx
    return pd.DataFrame([k.__dict__ for k in kayitlar])


# ---------------------------------------------------------------- metrikler

def dusus_istatistikleri(ozsermaye: pd.Series) -> dict:
    tepe = ozsermaye.cummax()
    dd = ozsermaye / tepe - 1
    sualti = dd < 0
    en_uzun, mevcut, bas = pd.Timedelta(0), None, None
    for t, s in sualti.items():
        if s and bas is None:
            bas = t
        elif not s and bas is not None:
            en_uzun = max(en_uzun, t - bas)
            bas = None
    if bas is not None:
        en_uzun = max(en_uzun, ozsermaye.index[-1] - bas)
    return {"max_dusus": float(dd.min()), "en_uzun_dusus_suresi": en_uzun}


def pozisyon_metrikleri(sonuc: pd.DataFrame) -> dict:
    e = sonuc["ozsermaye"]
    r = e.pct_change().dropna()
    k = yillik_mum_sayisi(e.index)
    yil = (e.index[-1] - e.index[0]).total_seconds() / YIL_SANIYE
    toplam = e.iloc[-1] / e.iloc[0] - 1
    m = {
        "toplam_getiri": float(toplam),
        "yillik_getiri": float((1 + toplam) ** (1 / yil) - 1) if yil > 0 and toplam > -1 else np.nan,
        "yillik_oynaklik": float(r.std() * np.sqrt(k)),
        "sharpe": float(r.mean() / r.std() * np.sqrt(k)) if r.std() > 0 else np.nan,
        "piyasada_kalma": float((sonuc["adet"] != 0).mean()),
        "toplam_maliyet": float(sonuc["maliyet"].sum()),
    }
    m.update(dusus_istatistikleri(e))
    return m


def islem_metrikleri(islemler: pd.DataFrame, sutun: str = "net") -> dict:
    if islemler.empty:
        return {"islem": 0}
    x = islemler[sutun]
    kazanc, kayip = x[x > 0].sum(), -x[x < 0].sum()
    return {
        "islem": int(len(x)),
        "ortalama": float(x.mean()),
        "medyan": float(x.median()),
        "kazanma_orani": float((x > 0).mean()),
        "profit_factor": float(kazanc / kayip) if kayip > 0 else np.inf,
        "toplam_bilesik": float(np.prod(1 + x) - 1),
    }
