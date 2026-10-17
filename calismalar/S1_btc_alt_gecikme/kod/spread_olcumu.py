"""S1 ön kayıt §3: 3 saat boyunca 10 saniyede bir spot ve vadeli bookTicker örneklemesi.

Ham örnekler: data/spread/<baslangic>.csv (her örnekte satır satır eklenir)
Özet: calismalar/S1_btc_alt_gecikme/results/spread_ozet.csv

Çalıştırma: .venv/Scripts/python -m calismalar.S1_btc_alt_gecikme.kod.spread_olcumu [saniye_toplam] [aralik]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd

from ortak import veri

SONUC = Path(__file__).resolve().parents[1] / "results"


def semboller() -> dict[str, tuple[str, str]]:
    """coin -> (spot sembol, vadeli sembol)"""
    s = {}
    for c in veri.tum_coinler():
        s[c] = (f"{c}USDT", "1000PEPEUSDT" if c == "PEPE" else f"{c}USDT")
    return s


def ornek_al(eslesme) -> list[dict]:
    t = pd.Timestamp.now(tz="UTC")
    spot_list = [v[0] for v in eslesme.values()]
    spot = veri._get_json(f"{veri.SPOT_REST}/api/v3/ticker/bookTicker",
                          {"symbols": json.dumps(spot_list, separators=(",", ":"))})
    vadeli = veri._get_json(f"{veri.VADELI_REST}/fapi/v1/ticker/bookTicker")
    spot = {d["symbol"]: d for d in spot}
    vadeli = {d["symbol"]: d for d in vadeli}
    satirlar = []
    for coin, (ss, vs) in eslesme.items():
        for piyasa, d in (("spot", spot.get(ss)), ("vadeli", vadeli.get(vs))):
            if not d:
                continue
            bid, ask = float(d["bidPrice"]), float(d["askPrice"])
            if bid <= 0 or ask <= 0:
                continue
            orta = (bid + ask) / 2
            satirlar.append({"zaman": t, "coin": coin, "piyasa": piyasa, "bid": bid, "ask": ask,
                             "yarim_spread": (ask - bid) / 2 / orta})
    return satirlar


def ozetle(ham: pd.DataFrame) -> pd.DataFrame:
    g = ham.groupby(["coin", "piyasa"])["yarim_spread"]
    oz = pd.DataFrame({"ornek": g.size(), "ortalama_yarim_spread": g.mean(),
                       "medyan_yarim_spread": g.median(), "p90_yarim_spread": g.quantile(0.9)})
    oz["grup"] = [veri.coin_grubu(c) for c, _ in oz.index]
    oz["kucuk_grup_kayma"] = [max(2 * m, 0.0005) if gr == "Küçük" else None
                              for m, gr in zip(oz["ortalama_yarim_spread"], oz["grup"])]
    return oz


def main():
    toplam = int(sys.argv[1]) if len(sys.argv) > 1 else 3 * 3600
    aralik = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    eslesme = semboller()
    bas = pd.Timestamp.now(tz="UTC")
    ham_yol = veri.VERI_DIZINI / "spread" / f"{bas:%Y%m%dT%H%M}.csv"
    ham_yol.parent.mkdir(parents=True, exist_ok=True)
    bitis = time.time() + toplam
    ilk = True
    while time.time() < bitis:
        t0 = time.time()
        try:
            df = pd.DataFrame(ornek_al(eslesme))
            df.to_csv(ham_yol, mode="a", header=ilk, index=False)
            ilk = False
        except Exception as e:  # tek örnek kaybı ölçümü bozmaz; kaydedilir
            print(f"{pd.Timestamp.now(tz='UTC')} hata: {e}", flush=True)
        time.sleep(max(0.0, aralik - (time.time() - t0)))
    ham = pd.read_csv(ham_yol)
    oz = ozetle(ham)
    SONUC.mkdir(parents=True, exist_ok=True)
    oz.to_csv(SONUC / "spread_ozet.csv")
    print(f"örnekleme: {bas} – {pd.Timestamp.now(tz='UTC')}, ham: {ham_yol}")
    print(oz.to_string())


if __name__ == "__main__":
    main()
