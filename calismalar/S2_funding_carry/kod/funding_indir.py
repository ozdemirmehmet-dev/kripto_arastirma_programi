"""S2 veri adımı: funding geçmişini indirir ve yalnız VERİ KALİTESİNİ özetler.

Etki ölçümü (ortalama funding vb.) burada yapılmaz; o Aşama B'dir.
Ön kayıt §2: ana evren 13 coin + hayatta kalma ek senaryosu için delist semboller.

Çıktı: calismalar/S2_funding_carry/results/funding_veri_kalitesi.csv
Çalıştırma: .venv/Scripts/python -m calismalar.S2_funding_carry.kod.funding_indir
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from ortak import veri

SONUC = Path(__file__).resolve().parents[1] / "results"
DELIST_ADAYLARI = ["LUNAUSDT", "FTTUSDT"]


def vadeli_sembol(coin: str) -> str:
    return "1000PEPEUSDT" if coin == "PEPE" else f"{coin}USDT"


def kalite(sembol: str, df: pd.DataFrame) -> dict:
    if df.empty:
        return {"sembol": sembol, "kayit": 0}
    aralik = veri.funding_araligi_saat(df).dropna().round(2)
    dagilim = aralik.value_counts()
    # 8 saatten farklı aralıkların dönemleri (ilk/son görülme)
    farkli = aralik[aralik != 8]
    return {
        "sembol": sembol,
        "kayit": len(df),
        "ilk": df.index[0],
        "son": df.index[-1],
        "aralik_dagilimi_saat": "; ".join(f"{k:g}h×{v}" for k, v in dagilim.items()),
        "8h_disi_ilk": farkli.index[0] if len(farkli) else None,
        "8h_disi_son": farkli.index[-1] if len(farkli) else None,
        "tekrar": int(df.index.duplicated().sum()),
        "asiri_kayit_abs_gt_1pct": int((df["fundingRate"].abs() > 0.01).sum()),
        "eksik_oran": int(df["fundingRate"].isna().sum()),
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    satirlar = []
    semboller = [(c, vadeli_sembol(c), "ana") for c in veri.tum_coinler()] + \
                [(s.replace("USDT", ""), s, "delist_ek") for s in DELIST_ADAYLARI]
    for coin, s, rol in semboller:
        try:
            df = veri.funding_gecmisi(s, yenile=True)
            k = kalite(s, df)
        except Exception as e:
            k = {"sembol": s, "kayit": 0, "hata": str(e)}
        k.update({"coin": coin, "rol": rol})
        satirlar.append(k)
        print(k, flush=True)
    SONUC.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(satirlar).to_csv(SONUC / "funding_veri_kalitesi.csv", index=False)


if __name__ == "__main__":
    main()
