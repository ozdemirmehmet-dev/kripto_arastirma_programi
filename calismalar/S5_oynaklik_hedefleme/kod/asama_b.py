"""S5 Aşama B ölçümleri ve Kapı 1 (ön kayıt commit 19b967a, §3–§5). Maliyetsiz, strateji yok.

Haftalık ızgara: pazartesi 00:00 UTC. Hafta getirisi R = open(sonraki pazartesi) / open(pazartesi) − 1.
Ağırlık w = min(1, 0,40 / tahmin); tahmin pazar kapanışına kadarki son 20/60 günlük getirilerin
std'si × √365. Yönetilen getiri g = w · R (pazartesi alınan adet hafta boyunca sabit).

Çalıştırma: .venv/Scripts/python -m calismalar.S5_oynaklik_hedefleme.kod.asama_b [--olc] [--kayit]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from calismalar.S4_trend_takibi.kod.asama_b import gunluk
from ortak import istatistik, rapor

SONUC = Path(__file__).resolve().parents[1] / "results"
COINLER = ("BTC", "ETH")
PENCERELER = (20, 60)
HEDEF, ESIK_W, MALIYET_TEK = 0.40, 0.10, 0.0013
BLOK, TEKRAR, Q = 12, 9999, 0.10


def haftalik(df: pd.DataFrame, pencere: int) -> pd.DataFrame:
    r = np.log(df["close"]).diff()
    tahmin = r.rolling(pencere, min_periods=pencere).std() * np.sqrt(365)
    pazartesiler = df.index[df.index.dayofweek == 0]
    satirlar = []
    for p in pazartesiler:
        sonraki = p + pd.Timedelta(days=7)
        pazar = p - pd.Timedelta(days=1)
        if sonraki not in df.index or pazar not in tahmin.index:
            continue
        est = tahmin.loc[pazar]
        o0, o1 = df["open"].loc[p], df["open"].loc[sonraki]
        hafta_r = r.loc[p:sonraki - pd.Timedelta(days=1)]  # pazartesi–pazar 7 günlük kapanış getirisi
        satirlar.append({"pazartesi": p, "tahmin": est, "R": o1 / o0 - 1,
                         "gerceklesen_vol": hafta_r.std() * np.sqrt(365)})
    h = pd.DataFrame(satirlar).set_index("pazartesi").dropna()
    h["w"] = np.minimum(1.0, HEDEF / h["tahmin"])
    h["g"] = h["w"] * h["R"]
    return h


def alfa(g: np.ndarray, R: np.ndarray) -> float:
    X = np.column_stack([np.ones(len(R)), R])
    return float(np.linalg.lstsq(X, g, rcond=None)[0][0])


def blok_bootstrap_alfa(g: np.ndarray, R: np.ndarray) -> np.ndarray:
    n = len(g)
    rng = istatistik.rng()
    k = int(np.ceil(n / BLOK))
    out = np.empty(TEKRAR)
    for i in range(TEKRAR):
        idx = (rng.integers(0, n - BLOK + 1, k)[:, None] + np.arange(BLOK)).ravel()[:n]
        gg, rr = g[idx], R[idx]
        rm = rr.mean()
        b = np.sum((rr - rm) * (gg - gg.mean())) / np.sum((rr - rm) ** 2)
        out[i] = gg.mean() - b * rm
    return out


def devir(w: pd.Series) -> float:
    """0,10 eşikli yıllık devir (Σ|Δw| / yıl)."""
    mevcut, toplam = w.iloc[0], 0.0
    for v in w.iloc[1:]:
        if abs(v - mevcut) >= ESIK_W:
            toplam += abs(v - mevcut)
            mevcut = v
    yil = (w.index[-1] - w.index[0]).days / 365.25
    return toplam / yil


def olc():
    ozet, kalicilik, dilimler = [], [], []
    for c in COINLER:
        df = gunluk(c)
        for pen in PENCERELER:
            h = haftalik(df, pen)
            g, R = h["g"].to_numpy(), h["R"].to_numpy()
            a = alfa(g, R)
            boot = blok_bootstrap_alfa(g, R)
            orta = h.index[0] + (h.index[-1] - h.index[0]) / 2
            ia, ib = h.index < orta, h.index >= orta
            a1, a2 = alfa(g[ia], R[ia]), alfa(g[ib], R[ib])
            dv = devir(h["w"])
            yil_maliyet = dv * MALIYET_TEK
            ozet.append({
                "coin": c, "pencere": pen, "hafta": len(h), "ilk": h.index[0].date(), "son": h.index[-1].date(),
                "ort_w": h["w"].mean(), "w_1_orani": float((h["w"] >= 1).mean()),
                "alfa_yillik": a * 52, "alfa_boot_p05_yillik": float(np.quantile(boot, 0.05)) * 52,
                "p": float((np.sum(boot <= 0) + 1) / (TEKRAR + 1)),
                "alfa_ilk_yari": a1 * 52, "alfa_ikinci_yari": a2 * 52,
                "yarilar_gecti": bool(a1 > 0 and a2 > 0 and min(a1, a2) / max(a1, a2) >= 0.5),
                "yillik_devir": dv, "yillik_maliyet": yil_maliyet, "esik": 2 * yil_maliyet,
                "sharpe_althut_haftalik": R.mean() / R.std() * np.sqrt(52),
                "sharpe_yonetilen_haftalik": g.mean() / g.std() * np.sqrt(52),
            })
            # B1 kalıcılık
            kalicilik.append({"coin": c, "pencere": pen, "corr": h["tahmin"].corr(h["gerceklesen_vol"]),
                              "egim": float(np.polyfit(h["tahmin"], h["gerceklesen_vol"], 1)[0]),
                              "r2": h["tahmin"].corr(h["gerceklesen_vol"]) ** 2})
            # B2 genişleyen beşte birler (en az 52 haftalık geçmişle)
            for i in range(52, len(h)):
                gecmis = h["tahmin"].iloc[:i]
                sinirlar = gecmis.quantile([0.2, 0.4, 0.6, 0.8]).to_numpy()
                h.loc[h.index[i], "dilim"] = int(np.searchsorted(sinirlar, h["tahmin"].iloc[i])) + 1
            for d, hd in h.dropna(subset=["dilim"]).groupby("dilim"):
                dilimler.append({"coin": c, "pencere": pen, "dilim": int(d), "hafta": len(hd),
                                 "ort_R": hd["R"].mean(), "std_R": hd["R"].std(),
                                 "oran": hd["R"].mean() / hd["R"].std(), "ort_tahmin": hd["tahmin"].mean()})
            print(c, pen, f"alfa yıllık %{a * 52 * 100:.2f}", f"eşik %{2 * yil_maliyet * 100:.2f}", flush=True)
    oz = pd.DataFrame(ozet)
    oz["bh_anlamli"], oz["bh_p"] = istatistik.benjamini_hochberg(oz["p"].to_numpy(), Q)
    oz["k_yarilar"] = oz["yarilar_gecti"]
    oz["k_bootstrap"] = oz["alfa_boot_p05_yillik"] > 0
    oz["k_bh"] = oz["bh_anlamli"]
    oz["k_maliyet"] = oz["alfa_yillik"] >= oz["esik"]
    oz["kapi1"] = oz[["k_yarilar", "k_bootstrap", "k_bh", "k_maliyet"]].all(axis=1)
    oz.to_csv(SONUC / "kapi1.csv", index=False)
    pd.DataFrame(kalicilik).to_csv(SONUC / "b1_kalicilik.csv", index=False)
    pd.DataFrame(dilimler).to_csv(SONUC / "b2_dilimler.csv", index=False)
    for pen in PENCERELER:
        g = oz[(oz.pencere == pen) & oz.kapi1]
        print(f"pencere {pen}: Kapı 1 geçen {list(g.coin)} → Aşama C koşulu "
              f"{'SAĞLANDI' if set(g.coin) == set(COINLER) else 'yok'}")


def kayit():
    oz = pd.read_csv(SONUC / "kapi1.csv")
    for r in oz.itertuples():
        rapor.kayit_ekle("S5", "B3", f"alfa>0 V{r.pencere} (ana test)", r.coin, "1w",
                         f"alfa yıllık %{r.alfa_yillik * 100:.2f}, eşik %{r.esik * 100:.2f}, boot p05 %{r.alfa_boot_p05_yillik * 100:.2f}, "
                         f"BH p={r.bh_p:.3g}, yarılar %{r.alfa_ilk_yari * 100:.2f}/%{r.alfa_ikinci_yari * 100:.2f}, "
                         f"Kapı 1 {'GEÇTİ' if r.kapi1 else 'kaldı'}")
    for r in pd.read_csv(SONUC / "b1_kalicilik.csv").itertuples():
        rapor.kayit_ekle("S5", "B1", f"tanımlayıcı oynaklık kalıcılığı V{r.pencere}", r.coin, "1w",
                         f"corr={r.corr:.2f}, eğim={r.egim:.2f}")
    for r in pd.read_csv(SONUC / "b2_dilimler.csv").itertuples():
        rapor.kayit_ekle("S5", "B2", f"tanımlayıcı oynaklık dilimi {r.dilim} V{r.pencere}", r.coin, "1w",
                         f"ort R %{r.ort_R * 100:.2f}, std %{r.std_R * 100:.2f}, oran {r.oran:.3f}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    SONUC.mkdir(parents=True, exist_ok=True)
    if "--olc" in sys.argv:
        olc()
    if "--kayit" in sys.argv:
        kayit()


if __name__ == "__main__":
    main()
