"""S4 Aşama B ölçümleri ve Kapı 1 (ön kayıt commit 67c48cd, §4–§5). Strateji yok.

B1: s_t = sign(ln(close_t / close_{t−N})), y_t = ln(open_{t+1+M} / open_{t+1}),
    D = ort(y | s=+1) − ort(y | s=−1); N ∈ {20, 60, 120}, M ∈ {5, 20}.
Test: hareketli blok bootstrap, (s, y) çiftleri 60 günlük bloklarla, 9.999 tekrar.
    p = P(D* ≤ 0); "rastgele %95" = D*'nin %5. yüzdeliği > 0. BH: 78 test, q = %10.
Günlük ızgara tamdır; eksik gün doldurulmaz (NaN olan s ya da y atılır).

Çalıştırma: .venv/Scripts/python -m calismalar.S4_trend_takibi.kod.asama_b [--olc] [--kayit]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ortak import istatistik, maliyet, rapor, veri

SONUC = Path(__file__).resolve().parents[1] / "results"
S1_SPREAD = veri.KOK / "calismalar" / "S1_btc_alt_gecikme" / "results" / "spread_ozet.csv"
KESIM = pd.Timestamp("2026-10-17", tz="UTC")
COINLER = veri.tum_coinler()
NLER, MLER = (20, 60, 120), (5, 20)
BLOK, TEKRAR, Q = 60, 9999, 0.10


def gunluk(coin: str) -> pd.DataFrame:
    bas = veri.ilk_mum_zamani(f"{coin}USDT", "spot")
    df = veri.mumlar(f"{coin}USDT", "1d", bas, KESIM, "spot")
    tam = pd.date_range(df.index[0], df.index[-1], freq="1D")
    return df[["open", "close"]].reindex(tam)


def sinyal_ve_ileri(df: pd.DataFrame, N: int, M: int) -> pd.DataFrame:
    lc, lo = np.log(df["close"]), np.log(df["open"])
    s = np.sign(lc - lc.shift(N))
    y = lo.shift(-(1 + M)) - lo.shift(-1)
    d = pd.DataFrame({"s": s, "y": y}).dropna()
    return d[d["s"] != 0]


def fark(s: np.ndarray, y: np.ndarray) -> float:
    pos = s > 0
    if pos.all() or not pos.any():
        return np.nan
    return float(y[pos].mean() - y[~pos].mean())


def blok_bootstrap_fark(s: np.ndarray, y: np.ndarray, tohum: int | None = None) -> np.ndarray:
    n = len(s)
    g = istatistik.rng(tohum)
    k = int(np.ceil(n / BLOK))
    ofset = np.arange(BLOK)
    out = np.empty(TEKRAR)
    for bas in range(0, TEKRAR, 1000):
        r = min(1000, TEKRAR - bas)
        baslar = g.integers(0, n - BLOK + 1, size=(r, k))
        idx = (baslar[:, :, None] + ofset).reshape(r, -1)[:, :n]
        ss, yy = s[idx], y[idx]
        pos = ss > 0
        n_pos = pos.sum(1)
        n_neg = n - n_pos
        with np.errstate(invalid="ignore", divide="ignore"):
            out[bas:bas + r] = (np.where(pos, yy, 0).sum(1) / n_pos) - (np.where(~pos, yy, 0).sum(1) / n_neg)
    return out


def esik(coin: str, m: maliyet.MaliyetModeli) -> float:
    return 2 * m.gidis_donus(coin, veri.coin_grubu(coin), "spot", "taker")


def maliyet_modeli() -> maliyet.MaliyetModeli:
    sp = pd.read_csv(S1_SPREAD)
    return maliyet.MaliyetModeli(olculen_yarim_spread={
        (r.coin, r.piyasa): r.ortalama_yarim_spread for r in sp.itertuples()})


def olc():
    m = maliyet_modeli()
    satirlar, yillar = [], []
    for c in COINLER:
        df = gunluk(c)
        orta = df.index[0] + (df.index[-1] - df.index[0]) / 2
        for N in NLER:
            for M in MLER:
                d = sinyal_ve_ileri(df, N, M)
                s, y = d["s"].to_numpy(), d["y"].to_numpy()
                D = fark(s, y)
                boot = blok_bootstrap_fark(s, y)
                a = d[d.index < orta]
                b = d[d.index >= orta]
                Da, Db = fark(a["s"].to_numpy(), a["y"].to_numpy()), fark(b["s"].to_numpy(), b["y"].to_numpy())
                satirlar.append({
                    "coin": c, "grup": veri.coin_grubu(c), "N": N, "M": M, "n": len(d),
                    "ilk": d.index[0].date(), "son": d.index[-1].date(),
                    "pozitif_oran": float((s > 0).mean()),
                    "ort_pozitif_sonrasi": float(y[s > 0].mean()), "ort_negatif_sonrasi": float(y[s < 0].mean()),
                    "D": D, "D_boot_p05": float(np.nanquantile(boot, 0.05)),
                    "D_boot_p95": float(np.nanquantile(boot, 0.95)),
                    "p": float((np.sum(boot <= 0) + 1) / (np.sum(~np.isnan(boot)) + 1)),
                    "D_ilk_yari": Da, "D_ikinci_yari": Db,
                    "yarilar_gecti": bool(Da > 0 and Db > 0 and min(Da, Db) / max(Da, Db) >= 0.5),
                    "esik": esik(c, m),
                })
                for yil, dy in d.groupby(d.index.year):
                    yillar.append({"coin": c, "N": N, "M": M, "yil": yil, "n": len(dy),
                                   "ort_pozitif_sonrasi": float(dy.loc[dy.s > 0, "y"].mean()),
                                   "ort_negatif_sonrasi": float(dy.loc[dy.s < 0, "y"].mean()),
                                   "D": fark(dy["s"].to_numpy(), dy["y"].to_numpy())})
        print(c, "bitti", flush=True)
    t = pd.DataFrame(satirlar)
    t["bh_anlamli"], t["bh_p"] = istatistik.benjamini_hochberg(t["p"].to_numpy(), Q)
    t["k_yarilar"] = t["yarilar_gecti"]
    t["k_bootstrap"] = t["D_boot_p05"] > 0
    t["k_bh"] = t["bh_anlamli"]
    t["k_maliyet"] = t["D"] >= t["esik"]
    t["kapi1"] = t[["k_yarilar", "k_bootstrap", "k_bh", "k_maliyet"]].all(axis=1)
    t["maliyet_orani"] = t["D"] / t["esik"]
    t.to_csv(SONUC / "b1_kapi1.csv", index=False)
    pd.DataFrame(yillar).to_csv(SONUC / "b2_yillar.csv", index=False)
    # Aşama C koşulu (ön kayıt §5): bir N'de, M = 20, BTC ya da ETH dahil ≥ 3 coin
    for N in NLER:
        g = t[(t.N == N) & (t.M == 20) & t.kapi1]
        kosul = len(g) >= 3 and bool(g.coin.isin(["BTC", "ETH"]).any())
        print(f"N={N}, M=20: Kapı 1 geçen {len(g)} coin {list(g.coin)} → Aşama C koşulu {'SAĞLANDI' if kosul else 'yok'}")
    print("Toplam Kapı 1 geçen:", int(t.kapi1.sum()), "/ 78")


def kayit():
    t = pd.read_csv(SONUC / "b1_kapi1.csv")
    for r in t.itertuples():
        rapor.kayit_ekle("S4", "B1", f"D>0 N={r.N} M={r.M} (ana test)", r.coin, "1d",
                         f"D=%{r.D * 100:.2f}, eşik=%{r.esik * 100:.2f}, boot p05=%{r.D_boot_p05 * 100:.2f}, "
                         f"BH p={r.bh_p:.3g}, yarılar %{r.D_ilk_yari * 100:.2f}/%{r.D_ikinci_yari * 100:.2f}, "
                         f"Kapı 1 {'GEÇTİ' if r.kapi1 else 'kaldı'}")
    for r in pd.read_csv(SONUC / "b2_yillar.csv").itertuples():
        rapor.kayit_ekle("S4", "B2", f"tanımlayıcı yıl {r.yil} N={r.N} M={r.M}", r.coin, "1d",
                         f"D=%{r.D * 100:.2f} (n={r.n})")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    SONUC.mkdir(parents=True, exist_ok=True)
    if "--olc" in sys.argv:
        olc()
    if "--kayit" in sys.argv:
        kayit()


if __name__ == "__main__":
    main()
