"""S6 Aşama B ölçümleri ve Kapı 1 (ön kayıt commit 9f25bdd, §3–§4). Strateji yok.

Saatlik getiri r = ln(close / open), aynı mum. Günlük getiri = ln(close 23:00 mumu / open 00:00 mumu).
ABD açılışı: 09:30 America/New_York → UTC; o anı içeren 1h mum (pazartesi–cuma).
Test: H0 ortalama = 0 (iki yönlü), ISO haftası bloklu işaret çevirme, 9.999 tekrar. BH 96 test.

Çalıştırma: .venv/Scripts/python -m calismalar.S6_zaman_etkisi.kod.asama_b [--olc] [--kayit]
"""
from __future__ import annotations

import sys
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from calismalar.S1_btc_alt_gecikme.kod.veri_indir import yukle
from ortak import istatistik, rapor

SONUC = Path(__file__).resolve().parents[1] / "results"
COINLER = ("BTC", "ETH", "SOL")
YILLAR = [("Y1", "2023-10-17", "2024-10-17"), ("Y2", "2024-10-17", "2025-10-17"), ("Y3", "2025-10-17", "2026-10-17")]
ORTA = pd.Timestamp("2025-04-17", tz="UTC")
TEKRAR, Q = 9999, 0.10
MALIYET_ESIK = 2 * 2 * (0.0005 + 0.0003)  # 2 × vadeli taker gidiş-dönüş = %0,32
NY = ZoneInfo("America/New_York")


def hafta_isaret(y: pd.Series) -> dict:
    iso = y.index.isocalendar()
    kod = pd.factorize(iso["year"].astype(str) + "-" + iso["week"].astype(str))[0]
    s = np.bincount(kod, weights=y.to_numpy())
    w = istatistik.rng().choice([-1.0, 1.0], size=(TEKRAR, len(s)))
    sifir = np.abs((w @ s) / len(y))
    g = abs(float(y.mean()))
    return {"yuzdelik_iki_yonlu": istatistik.yuzdelik(g, sifir),
            "p": float((np.sum(sifir >= g) + 1) / (TEKRAR + 1))}


def yil_ve_yarilar(y: pd.Series) -> dict:
    out = {}
    for ad, b, s in YILLAR:
        out[f"ort_{ad}"] = y[(y.index >= b) & (y.index < s)].mean()
    isaretler = np.sign([out[f"ort_{a}"] for a, _, _ in YILLAR])
    out["her_yil_ayni_yon"] = bool(np.all(isaretler == isaretler[0]) and isaretler[0] != 0)
    a, b = y[y.index < ORTA].mean(), y[y.index >= ORTA].mean()
    out.update({"ilk_yari": a, "ikinci_yari": b,
                "yarilar_gecti": bool(np.sign(a) == np.sign(b) and a != 0
                                      and min(abs(a), abs(b)) / max(abs(a), abs(b)) >= 0.5)})
    return out


def abd_acilis_mumlari(gunler: pd.DatetimeIndex) -> pd.DatetimeIndex:
    out = []
    for g in gunler:
        if g.dayofweek >= 5:
            continue
        acilis = datetime.combine(g.date(), time(9, 30), tzinfo=NY)
        out.append(pd.Timestamp(acilis).tz_convert("UTC").floor("h"))
    return pd.DatetimeIndex(out)


def kalemler(df: pd.DataFrame) -> dict[str, pd.Series]:
    r = np.log(df["close"] / df["open"])
    k = {f"saat_{h:02d}": r[r.index.hour == h] for h in range(24)}
    gun = df.groupby(df.index.floor("D")).agg(acilis=("open", "first"), kapanis=("close", "last"), n=("open", "size"))
    gun = gun[gun["n"] == 24]
    rg = np.log(gun["kapanis"] / gun["acilis"])
    adlar = ["pzt", "sal", "car", "per", "cum", "cmt", "paz"]
    for i, ad in enumerate(adlar):
        k[f"gun_{i}_{ad}"] = rg[rg.index.dayofweek == i]
    mumlar = abd_acilis_mumlari(gun.index).intersection(r.index)
    k["abd_acilis"] = r.loc[mumlar]
    return k


def olc():
    satirlar, ek = [], []
    for c in COINLER:
        df = yukle(c, "1h", "spot")
        k = kalemler(df)
        for ad, y in k.items():
            s = {"coin": c, "kalem": ad, "n": len(y), "ortalama": y.mean(), "medyan": y.median(), "std": y.std()}
            s.update(hafta_isaret(y))
            s.update(yil_ve_yarilar(y))
            satirlar.append(s)
        # tanımlayıcı: ABD açılışından sonraki saat
        r = np.log(df["close"] / df["open"])
        sonraki = k["abd_acilis"].index + pd.Timedelta(hours=1)
        ys = r.reindex(sonraki).dropna()
        ek.append({"coin": c, "kalem": "abd_acilis_sonraki_saat", "n": len(ys), "ortalama": ys.mean(),
                   **hafta_isaret(ys)})
        print(c, "bitti", flush=True)
    t = pd.DataFrame(satirlar)
    t["bh_anlamli"], t["bh_p"] = istatistik.benjamini_hochberg(t["p"].to_numpy(), Q)
    t["k_her_yil"] = t["her_yil_ayni_yon"]
    t["k_yarilar"] = t["yarilar_gecti"]
    t["k_rastgele"] = t["yuzdelik_iki_yonlu"] > 95
    t["k_bh"] = t["bh_anlamli"]
    t["k_maliyet"] = t["ortalama"].abs() >= MALIYET_ESIK
    t["kapi1"] = t[["k_her_yil", "k_yarilar", "k_rastgele", "k_bh", "k_maliyet"]].all(axis=1)
    t["filtre_adayi"] = t[["k_her_yil", "k_yarilar", "k_rastgele", "k_bh"]].all(axis=1) & ~t["k_maliyet"]
    t.to_csv(SONUC / "kapi1.csv", index=False)
    pd.DataFrame(ek).to_csv(SONUC / "abd_acilis_sonraki_saat.csv", index=False)
    print("Kapı 1 geçen:", int(t.kapi1.sum()), "/", len(t), "; filtre adayı:", int(t.filtre_adayi.sum()))


def kayit():
    t = pd.read_csv(SONUC / "kapi1.csv")
    for r in t.itertuples():
        rapor.kayit_ekle("S6", "B", f"{r.kalem} ort≠0 (ana test)", r.coin, "1h/1d",
                         f"ort=%{r.ortalama * 100:.4f}, yıllar %{r.ort_Y1 * 100:.3f}/%{r.ort_Y2 * 100:.3f}/%{r.ort_Y3 * 100:.3f}, "
                         f"yüzdelik %{r.yuzdelik_iki_yonlu:.1f}, BH p={r.bh_p:.3g}, "
                         f"{'Kapı 1 GEÇTİ' if r.kapi1 else ('filtre adayı' if r.filtre_adayi else 'kaldı')}")
    for r in pd.read_csv(SONUC / "abd_acilis_sonraki_saat.csv").itertuples():
        rapor.kayit_ekle("S6", "B", "tanımlayıcı: ABD açılışı sonraki saat", r.coin, "1h",
                         f"ort=%{r.ortalama * 100:.4f}, yüzdelik %{r.yuzdelik_iki_yonlu:.1f}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    SONUC.mkdir(parents=True, exist_ok=True)
    if "--olc" in sys.argv:
        olc()
    if "--kayit" in sys.argv:
        kayit()


if __name__ == "__main__":
    main()
