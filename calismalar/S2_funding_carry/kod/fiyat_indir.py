"""S2 ön kayıt §2: funding geçmişiyle aynı dönemin spot ve vadeli 1h mumları.

Dönem: coinin ilk funding gününden 2026-10-17 00:00 UTC'ye (S2 veri kesimi).
Çalıştırma: .venv/Scripts/python -m calismalar.S2_funding_carry.kod.fiyat_indir <piyasa> <COIN,COIN,...>
Çıktı: results/kalite_1h_<piyasa>_<ilk coin>.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from ortak import veri

SONUC = Path(__file__).resolve().parents[1] / "results"
KESIM = pd.Timestamp("2026-10-17", tz="UTC")


def vadeli_sembol(coin: str) -> str:
    return "1000PEPEUSDT" if coin == "PEPE" else f"{coin}USDT"


def baslangic(coin: str) -> pd.Timestamp:
    f = pd.read_parquet(veri.VERI_DIZINI / "funding" / f"{vadeli_sembol(coin)}.parquet")
    return f.index[0].normalize()


def fiyatlar(coin: str, piyasa: str) -> pd.DataFrame:
    s = vadeli_sembol(coin) if piyasa == "vadeli" else f"{coin}USDT"
    df = veri.mumlar(s, "1h", baslangic(coin), KESIM, piyasa)
    if coin == "PEPE" and piyasa == "vadeli":
        for c in ("open", "high", "low", "close"):
            df[c] = df[c] / 1000
    return df


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    piyasa, coinler = sys.argv[1], sys.argv[2].split(",")
    satirlar = []
    for c in coinler:
        k = veri.kalite_kontrol(fiyatlar(c, piyasa), "1h")
        k.update({"coin": c, "piyasa": piyasa})
        satirlar.append(k)
        print({x: k.get(x) for x in ("coin", "mum", "baslangic", "eksik_mum", "bosluk_sayisi",
                                       "en_uzun_bosluk")}, flush=True)
    SONUC.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(satirlar).to_csv(SONUC / f"kalite_1h_{piyasa}_{coinler[0]}.csv", index=False)


if __name__ == "__main__":
    main()
