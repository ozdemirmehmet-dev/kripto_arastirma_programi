"""İstatistik: HAC (Newey-West) regresyon, bootstrap, karıştırma testi,
Benjamini-Hochberg düzeltmesi, rastgele işlem/pozisyon kıyası, yarı ömür."""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
import statsmodels.api as sm

RNG_TOHUM = 20261017


def rng(tohum: int | None = None) -> np.random.Generator:
    return np.random.default_rng(RNG_TOHUM if tohum is None else tohum)


# ---------------------------------------------------------------- regresyon

def newey_west_ols(y: pd.Series, X: pd.DataFrame, gecikme: int | None = None):
    """OLS + Newey-West (HAC) standart hatalar. gecikme verilmezse floor(4(n/100)^(2/9))."""
    veri = pd.concat([y.rename("_y"), X], axis=1).dropna()
    n = len(veri)
    if gecikme is None:
        gecikme = int(np.floor(4 * (n / 100) ** (2 / 9)))
    model = sm.OLS(veri["_y"], sm.add_constant(veri.drop(columns="_y")))
    return model.fit(cov_type="HAC", cov_kwds={"maxlags": gecikme})


def korelasyon_gecikmeli(x: pd.Series, y: pd.Series, k: int) -> float:
    """corr(x_t, y_{t+k})."""
    return float(x.corr(y.shift(-k)))


# ---------------------------------------------------------------- bootstrap

def blok_bootstrap(x: np.ndarray, istatistik: Callable[[np.ndarray], float], n: int = 2000,
                   blok: int | None = None, tohum: int | None = None) -> np.ndarray:
    """Hareketli blok bootstrap (otokorelasyonu korur). Dağılımı döndürür."""
    x = np.asarray(x)
    x = x[~np.isnan(x)] if x.ndim == 1 else x
    m = len(x)
    blok = blok or max(1, int(round(m ** (1 / 3))))
    g = rng(tohum)
    blok_sayisi = int(np.ceil(m / blok))
    sonuc = np.empty(n)
    for b in range(n):
        baslar = g.integers(0, m - blok + 1, blok_sayisi)
        idx = (baslar[:, None] + np.arange(blok)[None, :]).ravel()[:m]
        sonuc[b] = istatistik(x[idx])
    return sonuc


def guven_araligi(dagilim: np.ndarray, duzey: float = 0.95) -> tuple[float, float]:
    a = (1 - duzey) / 2
    return float(np.nanquantile(dagilim, a)), float(np.nanquantile(dagilim, 1 - a))


# ---------------------------------------------------------------- karıştırma

def yuzdelik(deger: float, dagilim: np.ndarray) -> float:
    """Değerin rastgele dağılımın yüzde kaçından büyük olduğu (0–100)."""
    d = np.asarray(dagilim)
    d = d[~np.isnan(d)]
    return float(100.0 * (np.sum(d < deger) + 0.5 * np.sum(d == deger)) / len(d))


def karistirma_testi(istatistik: Callable[[np.ndarray], float], x: np.ndarray, n: int = 1000,
                     tohum: int | None = None, blok: int = 1) -> dict:
    """x'i (bloklar halinde) karıştırıp istatistiğin sıfır dağılımını üretir.

    p değeri tek yönlüdür: P(sıfır ≥ gözlenen).
    """
    x = np.asarray(x)
    g = rng(tohum)
    gozlenen = istatistik(x)
    sifir = np.empty(n)
    if blok <= 1:
        for b in range(n):
            sifir[b] = istatistik(g.permutation(x))
    else:
        parcalar = [x[i:i + blok] for i in range(0, len(x), blok)]
        for b in range(n):
            sira = g.permutation(len(parcalar))
            sifir[b] = istatistik(np.concatenate([parcalar[i] for i in sira]))
    p = (np.sum(sifir >= gozlenen) + 1) / (n + 1)
    return {"gozlenen": float(gozlenen), "yuzdelik": yuzdelik(gozlenen, sifir), "p": float(p),
            "sifir": sifir}


# ---------------------------------------------------------------- çoklu test

def benjamini_hochberg(p: np.ndarray, q: float = 0.10) -> tuple[np.ndarray, np.ndarray]:
    """BH düzeltmesi. Dönüş: (anlamlı mı, düzeltilmiş p)."""
    p = np.asarray(p, float)
    m = len(p)
    sira = np.argsort(p)
    sirali = p[sira]
    duz = sirali * m / np.arange(1, m + 1)
    duz = np.minimum.accumulate(duz[::-1])[::-1]
    duz = np.minimum(duz, 1.0)
    duzeltilmis = np.empty(m)
    duzeltilmis[sira] = duz
    return duzeltilmis <= q, duzeltilmis


# ---------------------------------------------------------------- rastgele kıyas (Bölüm 2.7)

def rastgele_islem_kiyasi(islem_fonksiyonu: Callable[[np.ndarray, np.ndarray, np.ndarray], pd.DataFrame],
                          islemler: pd.DataFrame, aday_indeksler: np.ndarray, n: int = 1000,
                          metrik: Callable[[pd.DataFrame], float] | None = None,
                          tohum: int | None = None) -> dict:
    """Aynı sayıda, aynı süre ve yön dağılımına sahip rastgele işlemlerle kıyas.

    islem_fonksiyonu(giris_indeksleri, yonler, sureler) -> işlem tablosu ('net' sütunlu).
    aday_indeksler: rastgele girişin seçilebileceği mum konumları.
    """
    metrik = metrik or (lambda t: float(t["net"].mean()) if len(t) else np.nan)
    g = rng(tohum)
    gozlenen = metrik(islemler)
    sureler = islemler["sure"].to_numpy()
    yonler = islemler["yon"].to_numpy()
    k = len(islemler)
    dagilim = np.empty(n)
    for b in range(n):
        idx = np.sort(g.choice(aday_indeksler, size=k, replace=False))
        dagilim[b] = metrik(islem_fonksiyonu(idx, g.permutation(yonler), g.permutation(sureler)))
    return {"gozlenen": gozlenen, "yuzdelik": yuzdelik(gozlenen, dagilim), "dagilim": dagilim}


def rastgele_pozisyon_serisi(pozisyon: pd.Series, g: np.random.Generator) -> pd.Series:
    """Aynı piyasada kalma oranını ve aynı segment uzunluklarını koruyan rastgele seri.

    Pozisyon serisi ardışık sabit segmentlere bölünür; segmentlerin sırası karıştırılır.
    """
    deger = pozisyon.to_numpy()
    sinirlar = np.flatnonzero(np.diff(deger) != 0) + 1
    segmentler = np.split(deger, sinirlar)
    sira = g.permutation(len(segmentler))
    return pd.Series(np.concatenate([segmentler[i] for i in sira]), index=pozisyon.index)


def rastgele_pozisyon_kiyasi(degerlendir: Callable[[pd.Series], float], pozisyon: pd.Series,
                             n: int = 1000, tohum: int | None = None) -> dict:
    g = rng(tohum)
    gozlenen = degerlendir(pozisyon)
    dagilim = np.array([degerlendir(rastgele_pozisyon_serisi(pozisyon, g)) for _ in range(n)])
    return {"gozlenen": gozlenen, "yuzdelik": yuzdelik(gozlenen, dagilim), "dagilim": dagilim}


# ---------------------------------------------------------------- dengeye dönüş

def yari_omur(z: pd.Series) -> float:
    """AR(1) ile yarı ömür (mum cinsinden): Δz_t = a + b·z_{t-1}; yarı ömür = −ln2/ln(1+b)."""
    z = z.dropna()
    dz = z.diff().dropna()
    gecikmeli = z.shift(1).loc[dz.index]
    b = sm.OLS(dz, sm.add_constant(gecikmeli)).fit().params.iloc[1]
    return float(-np.log(2) / np.log(1 + b)) if -1 < b < 0 else np.inf


def rolling_z(x: pd.Series, pencere: int, min_gozlem: int | None = None) -> pd.Series:
    """Yalnız geçmiş pencereyle z-skoru (t anı dahil, t+1 hariç)."""
    m = x.rolling(pencere, min_periods=min_gozlem or pencere)
    return (x - m.mean()) / m.std()


def yarilar_tutarli(x: pd.Series, istatistik: Callable[[pd.Series], float] = np.mean,
                    benzer_oran: float = 0.5) -> dict:
    """Kapı 1: iki yarıda aynı yön ve benzer büyüklük (küçük/büyük ≥ benzer_oran)."""
    x = x.dropna()
    yari = len(x) // 2
    a, b = float(istatistik(x.iloc[:yari])), float(istatistik(x.iloc[yari:]))
    ayni_yon = np.sign(a) == np.sign(b) and a != 0
    oran = min(abs(a), abs(b)) / max(abs(a), abs(b)) if max(abs(a), abs(b)) > 0 else 0.0
    return {"ilk_yari": a, "ikinci_yari": b, "ayni_yon": bool(ayni_yon), "buyukluk_orani": oran,
            "gecti": bool(ayni_yon and oran >= benzer_oran)}


def blok_isaret_cevirme(x: np.ndarray, blok_uzunluk: int, n: int = 1000,
                        tohum: int | None = None) -> dict:
    """H0: E[x] = 0 (simetrik). Ardışık `blok_uzunluk` gözlemlik bloklar aynı rastgele
    işareti alır (block sign-flip). Gözlenen ortalamanın sıfır dağılımındaki yüzdeliği."""
    x = np.asarray(x, float)
    kod = np.arange(len(x)) // blok_uzunluk
    s = np.bincount(kod, weights=x)
    w = rng(tohum).choice([-1.0, 1.0], size=(n, len(s)))
    sifir = (w @ s) / len(x)
    gozlenen = float(x.mean())
    return {"gozlenen": gozlenen, "yuzdelik": yuzdelik(gozlenen, sifir),
            "p": float((np.sum(sifir >= gozlenen) + 1) / (n + 1))}
