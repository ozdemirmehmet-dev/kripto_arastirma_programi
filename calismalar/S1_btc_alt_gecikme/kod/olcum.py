"""S1 Aşama B ölçümleri (ön kayıt §5). Strateji yok.

Getiriler tam zaman ızgarasına yeniden indekslenmiş kapanışlardan hesaplanır:
eksik mum doldurulmaz, eksik mumun iki yanındaki getiriler NaN olur. Kaydırmalar
(t+k) takvim zamanıyla yapılır; korelasyon ve regresyonlar yalnız tam gözlemleri kullanır.

Karıştırma testi (B2): BTC serisi sabit, altcoin satırları (r_alt_t, r_alt_{t+1})
birlikte bloklar halinde karıştırılır. Blok: 1m ve üstü için 1 gün, 1s için 1 saat
(her ikisinde de ~350 blok). Bu blok seçimi sonuçlar görülmeden yapıldı.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ortak import istatistik, veri

BLOK = {"1s": "1h", "1m": "1D", "5m": "1D", "15m": "1D", "1h": "1D"}


def izgara_getiri(df: pd.DataFrame, aralik: str) -> pd.Series:
    adim = pd.Timedelta(milliseconds=veri.ARALIK_MS[aralik])
    tam = pd.date_range(df.index[0], df.index[-1], freq=adim)
    c = df["close"].reindex(tam)
    return np.log(c).diff()


# ---------------------------------------------------------------- B1

def b1_eszamanli(r_btc: pd.Series, r_alt: pd.Series) -> dict:
    d = pd.concat([r_btc, r_alt], axis=1).dropna()
    x, y = d.iloc[:, 0].to_numpy(), d.iloc[:, 1].to_numpy()
    beta = np.cov(x, y)[0, 1] / np.var(x, ddof=1)
    return {"n": len(d), "corr_0": float(np.corrcoef(x, y)[0, 1]), "beta": float(beta)}


# ---------------------------------------------------------------- B2

def _b1_katsayi(y, x1, x2) -> float:
    m = ~(np.isnan(y) | np.isnan(x1) | np.isnan(x2))
    X = np.column_stack([np.ones(m.sum()), x1[m], x2[m]])
    return float(np.linalg.lstsq(X, y[m], rcond=None)[0][1])


def b2_gecikmeli(r_btc: pd.Series, r_alt: pd.Series, aralik: str, n_karistirma: int = 1000, _yavas: bool = False,
                 tohum: int | None = None) -> dict:
    out = {}
    for k in (1, 2, 3, 5, 10):
        out[f"corr_btc_alt_k{k}"] = istatistik.korelasyon_gecikmeli(r_btc, r_alt, k)
    out["corr_ters_k1"] = istatistik.korelasyon_gecikmeli(r_alt, r_btc, 1)

    X = pd.DataFrame({"r_btc": r_btc, "r_alt": r_alt})
    model = istatistik.newey_west_ols(r_alt.shift(-1).rename("y"), X)
    b1, se = model.params["r_btc"], model.bse["r_btc"]
    out.update({"n": int(model.nobs), "b1": float(b1), "b1_t": float(b1 / se),
                "b1_p_tek": float(model.pvalues["r_btc"] / 2 if b1 > 0 else 1 - model.pvalues["r_btc"] / 2),
                "b2": float(model.params["r_alt"]), "r2": float(model.rsquared)})
    ters = istatistik.newey_west_ols(r_btc.shift(-1).rename("y"), X)
    out.update({"ters_c1": float(ters.params["r_alt"]), "ters_c1_t": float(ters.tvalues["r_alt"])})

    # iki yarı
    yari = X.index[len(X) // 2]
    for ad, m in (("ilk", X.index < yari), ("ikinci", X.index >= yari)):
        y = r_alt.shift(-1)[m].to_numpy()
        out[f"b1_{ad}_yari"] = _b1_katsayi(y, X["r_btc"][m].to_numpy(), X["r_alt"][m].to_numpy())
    a, b = out["b1_ilk_yari"], out["b1_ikinci_yari"]
    out["yarilar_gecti"] = bool(np.sign(a) == np.sign(b) and np.sign(a) > 0
                                and min(abs(a), abs(b)) / max(abs(a), abs(b)) >= 0.5)

    if n_karistirma == 0:
        return out
    # blok karıştırma: altcoin satırları (r_alt_t, r_alt_{t+1}) birlikte.
    # b1, maskeli normal denklemlerden kapalı formda çözülür (lstsq ile aynı sonuç, çok daha hızlı).
    y_all = r_alt.shift(-1).to_numpy()
    x2_all = r_alt.to_numpy()
    x1 = r_btc.to_numpy()
    v1 = np.isfinite(x1)
    va = np.isfinite(y_all) & np.isfinite(x2_all)
    x1z = np.where(v1, x1, 0.0)
    yz, x2z = np.where(va, y_all, 0.0), np.where(va, x2_all, 0.0)
    x1k = x1z * x1z
    bloklar = pd.Series(np.arange(len(X)), index=X.index).groupby(X.index.floor(BLOK[aralik])).apply(
        lambda s: s.to_numpy()).tolist()
    g = istatistik.rng(tohum)
    sifir = np.empty(n_karistirma)
    uzunluklar = {len(b) for b in bloklar}
    if len(uzunluklar) == 1 and not _yavas:
        # Eşit bloklar: permütasyon π altında her toplam Σ_i M[i, π(i)] olur; M = blok×blok
        # çapraz çarpımlar. Satır karıştırmayla birebir aynı sonuç, döngü başına O(blok sayısı).
        B = len(bloklar)
        def mat(a):
            return a.reshape(B, -1)
        sol = {"1": mat(v1.astype(float)), "x1": mat(x1z), "x1k": mat(x1k)}
        sag = {"va": mat(va.astype(float)), "y": mat(yz), "x2": mat(x2z), "x2k": mat(x2z * x2z),
               "x2y": mat(x2z * yz)}
        M = {(a, b): sol[a] @ sag[b].T for a, b in
             [("1", "va"), ("x1", "va"), ("1", "x2"), ("x1k", "va"), ("x1", "x2"), ("1", "x2k"),
              ("1", "y"), ("x1", "y"), ("1", "x2y")]}
        satir = np.arange(B)
        for i in range(n_karistirma):
            p = g.permutation(B)
            s = {k: v[satir, p].sum() for k, v in M.items()}
            A = np.array([[s["1", "va"], s["x1", "va"], s["1", "x2"]],
                          [s["x1", "va"], s["x1k", "va"], s["x1", "x2"]],
                          [s["1", "x2"], s["x1", "x2"], s["1", "x2k"]]])
            bvec = np.array([s["1", "y"], s["x1", "y"], s["1", "x2y"]])
            sifir[i] = np.linalg.solve(A, bvec)[1]
        n_karistirma_yavas = 0
    else:
        n_karistirma_yavas = n_karistirma
    for i in range(n_karistirma_yavas):
        sira = np.concatenate([bloklar[j] for j in g.permutation(len(bloklar))])
        m = (v1 & va[sira]).astype(float)
        yp, x2p = yz[sira] * m, x2z[sira] * m
        A = np.array([[m.sum(), x1z @ m, x2p.sum()],
                      [x1z @ m, x1k @ m, x1z @ x2p],
                      [x2p.sum(), x1z @ x2p, x2p @ x2p]])
        bvec = np.array([yp.sum(), x1z @ yp, x2p @ yp])
        sifir[i] = np.linalg.solve(A, bvec)[1]
    out["karistirma_yuzdelik"] = istatistik.yuzdelik(float(b1), sifir)
    out["karistirma_p"] = float((np.sum(sifir >= b1) + 1) / (n_karistirma + 1))
    return out


# ---------------------------------------------------------------- B4 (1s)

def capraz_korelasyon(r_btc: pd.Series, r_alt: pd.Series, k_max: int = 120) -> pd.Series:
    return pd.Series({k: istatistik.korelasyon_gecikmeli(r_btc, r_alt, k) for k in range(k_max + 1)})


def olaylar(r_btc: pd.Series, K: float, pencere: int = 500, sogu: int = 10) -> pd.DatetimeIndex:
    """|r_btc_t| > K·σ_t, σ_t = son `pencere` mum (t dahil). Aynı yönde art arda olay
    mumlarından yalnız ilki; sonrasında en az `sogu` mum olaysız geçmeden yeni olay yok."""
    sig = r_btc.rolling(pencere, min_periods=pencere).std()
    adaylar = np.flatnonzero((r_btc.abs() > K * sig).to_numpy())
    if len(adaylar) == 0:
        return r_btc.index[[]]
    # bir aday ancak önceki adaydan sonra en az `sogu` olaysız mum geçmişse olaydır;
    # böylece art arda olay mumları (aynı ya da ters yön) kümenin ilkine indirgenir
    bosluk = np.diff(adaylar, prepend=-10**12) - 1
    return r_btc.index[adaylar[bosluk >= sogu]]


def b4_yetisme(alt_close: pd.Series, r_btc: pd.Series, r_alt: pd.Series, olay_zamanlari,
               beta_disaridan: pd.Series | None = None, k_max: int = 120, pencere: int = 500) -> dict:
    """Olay sonrası altcoinin beklenen hareketin %50/%90'ını tamamlama süresi (saniye).

    Beklenen hareket = β · r_btc_t; β olay mumu hariç son `pencere` mumdan (t−500…t−1),
    ya da `beta_disaridan` verilirse o seri (ör. 1m β, tanımlayıcı ek).
    Kümülatif hareket m(k) = ln(alt_{t+k} / alt_{t−1}), k = 0…k_max.
    """
    lc = np.log(alt_close)
    idx = lc.index
    pos = idx.get_indexer(olay_zamanlari)
    if beta_disaridan is None:
        cov = r_btc.rolling(pencere).cov(r_alt).shift(1)
        var = r_btc.rolling(pencere).var().shift(1)
        beta = (cov / var)
    else:
        beta = beta_disaridan.reindex(idx, method="ffill")
    lcv, bv, rb = lc.to_numpy(), beta.to_numpy(), r_btc.reindex(idx).to_numpy()
    isaretli, beklenenler, t50, t90 = [], [], [], []
    for p in pos:
        if p < 1 or p + k_max >= len(lcv):
            continue
        beklenen = bv[p] * rb[p]
        if not np.isfinite(beklenen) or beklenen == 0 or not np.isfinite(lcv[p - 1]):
            continue
        m = lcv[p:p + k_max + 1] - lcv[p - 1]
        oran = m / beklenen
        isaretli.append(np.sign(rb[p]) * m)  # BTC yönüyle işaretli kümülatif hareket
        beklenenler.append(abs(beklenen))
        for liste, esik in ((t50, 0.5), (t90, 0.9)):
            ulasti = np.flatnonzero(np.nan_to_num(oran, nan=-np.inf) >= esik)
            liste.append(ulasti[0] if len(ulasti) else np.inf)
    if not isaretli:
        return {"olay": 0}
    toplu_oran = np.nanmean(isaretli, axis=0) / np.mean(beklenenler)
    t50, t90 = np.array(t50), np.array(t90)

    def ilk(esik):
        u = np.flatnonzero(toplu_oran >= esik)
        return int(u[0]) if len(u) else None

    return {
        "olay": len(isaretli),
        "medyan_t50_sn": float(np.median(t50)),
        "medyan_t90_sn": float(np.median(t90)),
        "t50_ulasmayan_oran": float(np.isinf(t50).mean()),
        "t90_ulasmayan_oran": float(np.isinf(t90).mean()),
        "toplu_t50_sn": ilk(0.5),
        "toplu_t90_sn": ilk(0.9),
        "toplu_oran_k0": float(toplu_oran[0]),
        "toplu_oran_k120": float(toplu_oran[-1]),
        "_egri": toplu_oran,
    }


# ---------------------------------------------------------------- B2 ek: wild blok bootstrap
# Ön kayıt dışı, tanımlayıcı (2026-10-17, ara rapor 1'de karıştırma testinin her coinde %100
# vermesi üzerine eklendi). Sıfır altında kısıtlı model y = a + b2·x2 + e kurulur;
# y* = ŷ + w_blok · e (w: gün/saat bloğu başına Rademacher ±1). Oynaklık kümelenmesi ve
# BTC–altcoin ortak oynaklığı korunur. b1* = c·y*, c = ((X'X)^-1 X')'nin b1 satırı.

def b2_wild_bootstrap(r_btc: pd.Series, r_alt: pd.Series, aralik: str, n: int = 9999,
                      tohum: int | None = None) -> dict:
    d = pd.DataFrame({"y": r_alt.shift(-1), "x1": r_btc, "x2": r_alt}).dropna()
    X = np.column_stack([np.ones(len(d)), d["x1"], d["x2"]])
    c = np.linalg.solve(X.T @ X, X.T)[1]
    b1 = float(c @ d["y"].to_numpy())
    Xr = np.column_stack([np.ones(len(d)), d["x2"]])
    yhat = Xr @ np.linalg.lstsq(Xr, d["y"].to_numpy(), rcond=None)[0]
    e = d["y"].to_numpy() - yhat
    blok_kodu = pd.factorize(d.index.floor(BLOK[aralik]))[0]
    s = np.bincount(blok_kodu, weights=c * e)
    sabit = float(c @ yhat)  # ≈ 0
    w = istatistik.rng(tohum).choice([-1.0, 1.0], size=(n, len(s)))
    sifir = sabit + w @ s
    return {"wild_b1": b1, "wild_yuzdelik": istatistik.yuzdelik(b1, sifir),
            "wild_p": float((np.sum(sifir >= b1) + 1) / (n + 1)),
            "wild_sifir_sd": float(sifir.std())}
