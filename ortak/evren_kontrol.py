"""Coin evreni kontrolü (Bölüm 2.9, Bölüm 12 adım 3).

Her coin için: Binance spot ve USDT-M perpetual'da işlem görüyor mu, vadeli sembol
adı (ör. 1000PEPEUSDT), ilk günlük mum tarihi (geçmiş uzunluğu), funding aralığı.
Çıktı: EVREN_KONTROLU.md

Çalıştırma: .venv/Scripts/python -m ortak.evren_kontrol
"""
from __future__ import annotations

import pandas as pd

from ortak import rapor, veri


def vadeli_sembol_bul(coin: str, vadeli_semboller: dict) -> str | None:
    for aday in (f"{coin}USDT", f"1000{coin}USDT", f"1000000{coin}USDT"):
        s = vadeli_semboller.get(aday)
        if s and s.get("contractType") == "PERPETUAL" and s.get("quoteAsset") == "USDT":
            return aday
    return None


def funding_bilgisi() -> dict:
    """fundingInfo: varsayılan 8 saatten farklı aralığı olan semboller."""
    try:
        return {v["symbol"]: v for v in veri._get_json(f"{veri.VADELI_REST}/fapi/v1/fundingInfo")}
    except Exception:
        return {}


def kontrol() -> pd.DataFrame:
    spot = {s["symbol"]: s for s in veri.borsa_bilgisi("spot", yenile=True)["symbols"]}
    vadeli = {s["symbol"]: s for s in veri.borsa_bilgisi("vadeli", yenile=True)["symbols"]}
    finfo = funding_bilgisi()
    bugun = veri.son_tam_gun()
    satirlar = []
    for grup, coinler in veri.EVREN.items():
        for coin in coinler:
            ss = f"{coin}USDT"
            sp = spot.get(ss)
            vs = vadeli_sembol_bul(coin, vadeli)
            vd = vadeli.get(vs) if vs else None
            sp_ilk = veri.ilk_mum_zamani(ss, "spot") if sp else None
            vd_ilk = veri.ilk_mum_zamani(vs, "vadeli") if vd else None
            fi = finfo.get(vs, {}) if vs else {}
            satirlar.append({
                "grup": grup, "coin": coin,
                "spot_sembol": ss if sp else "YOK",
                "spot_durum": sp["status"] if sp else "YOK",
                "spot_ilk_gun": sp_ilk,
                "spot_gecmis_yil": round((bugun - sp_ilk).days / 365.25, 2) if sp_ilk is not None else None,
                "vadeli_sembol": vs or "YOK",
                "vadeli_durum": vd["status"] if vd else "YOK",
                "vadeli_ilk_gun": vd_ilk,
                "vadeli_gecmis_yil": round((bugun - vd_ilk).days / 365.25, 2) if vd_ilk is not None else None,
                "funding_aralik_saat": fi.get("fundingIntervalHours", 8) if vd else None,
            })
    return pd.DataFrame(satirlar)


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    df = kontrol()
    bugun = veri.son_tam_gun()
    sorunlar = []
    for _, r in df.iterrows():
        if r["spot_durum"] != "TRADING":
            sorunlar.append(f"- {r.coin}: spot durumu {r.spot_durum}")
        if r["vadeli_durum"] != "TRADING":
            sorunlar.append(f"- {r.coin}: vadeli durumu {r.vadeli_durum}")
        if r["vadeli_sembol"] not in ("YOK", f"{r.coin}USDT"):
            sorunlar.append(f"- {r.coin}: vadeli sembolü farklı → `{r.vadeli_sembol}` "
                            f"(fiyat ve adet 1000 katlı; spot ile karşılaştırırken ölçeklenmeli)")
        if r["funding_aralik_saat"] not in (None, 8):
            sorunlar.append(f"- {r.coin}: funding aralığı şu an {r.funding_aralik_saat} saat (8 değil)")
    metin = [
        "# Coin Evreni Kontrolü",
        "",
        f"Kontrol tarihi (UTC): {pd.Timestamp.now(tz='UTC'):%Y-%m-%d %H:%M}. "
        f"Geçmiş uzunluğu {bugun:%Y-%m-%d} itibarıyla. Kaynak: Binance exchangeInfo, "
        "ilk günlük mum, fapi fundingInfo.",
        "",
        rapor.md_tablo(df.set_index(["grup", "coin"]), ondalik=2),
        "",
        "## Notlar",
        "",
        *(sorunlar or ["- Sorun yok."]),
        "- `funding_aralik_saat` yalnız bugünkü ayardır. Geçmişte aralığın değiştiği dönemler "
        "S2'de funding verisinden ayrıca kontrol edilir.",
        *([] if any("durumu" in s for s in sorunlar) else
          ["- Listeden çıkmış coin yok; evrende değişiklik gerekmiyor."]),
    ]
    yol = veri.KOK / "EVREN_KONTROLU.md"
    yol.write_text("\n".join(metin) + "\n", encoding="utf-8")
    print("\n".join(metin))


if __name__ == "__main__":
    main()
