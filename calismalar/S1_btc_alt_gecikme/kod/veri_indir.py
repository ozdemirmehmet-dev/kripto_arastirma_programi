"""S1 veri indirme ve kalite kontrolü (ön kayıt §3).

Çalıştırma:
  .venv/Scripts/python -m calismalar.S1_btc_alt_gecikme.kod.veri_indir 1s spot
  .venv/Scripts/python -m calismalar.S1_btc_alt_gecikme.kod.veri_indir 1m spot
  .venv/Scripts/python -m calismalar.S1_btc_alt_gecikme.kod.veri_indir 1m vadeli
Çıktı: results/kalite_<aralik>_<piyasa>.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from ortak import veri

SONUC = Path(__file__).resolve().parents[1] / "results"

# Ön kayıt §3, yarı açık [bas, son)
DONEMLER = {
    "1s": ("2026-10-03", "2026-10-17"),
    "1m": ("2025-10-17", "2026-10-17"),
    "5m": ("2024-10-17", "2026-10-17"),
    "15m": ("2024-10-17", "2026-10-17"),
    "1h": ("2023-10-17", "2026-10-17"),
}


def sembol(coin: str, piyasa: str) -> str:
    return "1000PEPEUSDT" if (coin == "PEPE" and piyasa == "vadeli") else f"{coin}USDT"


def yukle(coin: str, aralik: str, piyasa: str = "spot") -> pd.DataFrame:
    bas, son = DONEMLER[aralik]
    df = veri.mumlar(sembol(coin, piyasa), aralik, bas, son, piyasa)
    if coin == "PEPE" and piyasa == "vadeli":  # 1000 katlı kontrat → spot ölçeğine
        for c in ("open", "high", "low", "close"):
            df[c] = df[c] / 1000
    return df


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    aralik, piyasa = sys.argv[1], sys.argv[2]
    satirlar = []
    for coin in veri.tum_coinler():
        df = yukle(coin, aralik, piyasa)
        k = veri.kalite_kontrol(df, aralik)
        k.update({"coin": coin, "aralik": aralik, "piyasa": piyasa})
        satirlar.append(k)
        print({x: k.get(x) for x in ("coin", "mum", "eksik_mum", "bosluk_sayisi", "en_uzun_bosluk",
                                       "ohlc_hatali")}, flush=True)
    SONUC.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(satirlar).to_csv(SONUC / f"kalite_{aralik}_{piyasa}.csv", index=False)


if __name__ == "__main__":
    main()
