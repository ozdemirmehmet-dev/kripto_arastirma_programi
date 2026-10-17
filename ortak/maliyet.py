"""Maliyet modeli (Bölüm 2.4): komisyon, kayma, funding.

Tüm oranlar kesir olarak tutulur (0.001 = %0,10). Ana senaryo taker'dır;
kapılar taker'a göre değerlendirilir, maker yalnız ek senaryodur.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import pandas as pd

# Binance standart (VIP0, BNB indirimsiz) oranlar. Çalışma başında güncel oranlar
# kontrol edilir ve ön kayda yazılır.
VARSAYILAN_KOMISYON = {
    "spot": {"taker": 0.0010, "maker": 0.0010},
    "vadeli": {"taker": 0.0005, "maker": 0.0002},
}
BUYUK_KAYMA = 0.0003       # Referans/Büyük/Orta grup, tek yön
KUCUK_KAYMA_TABAN = 0.0005  # Küçük grup alt sınırı, tek yön


@dataclass(frozen=True)
class MaliyetModeli:
    komisyon: dict = field(default_factory=lambda: {k: dict(v) for k, v in VARSAYILAN_KOMISYON.items()})
    # coin -> ölçülen yarım spread (kesir). Küçük grup için kayma = max(2·yarım spread, taban)
    olculen_yarim_spread: dict = field(default_factory=dict)
    carpan: float = 1.0  # sağlamlık senaryosu: 1,5x maliyet

    def kayma(self, coin: str, grup: str) -> float:
        if grup == "Küçük":
            yarim = self.olculen_yarim_spread.get(coin, 0.0)
            return max(2 * yarim, KUCUK_KAYMA_TABAN)
        return BUYUK_KAYMA

    def tek_yon(self, coin: str, grup: str, piyasa: str = "spot", senaryo: str = "taker") -> float:
        """Tek bir alış ya da satışın maliyeti (notional'ın kesri)."""
        return (self.komisyon[piyasa][senaryo] + self.kayma(coin, grup)) * self.carpan

    def gidis_donus(self, coin: str, grup: str, piyasa: str = "spot", senaryo: str = "taker") -> float:
        return 2 * self.tek_yon(coin, grup, piyasa, senaryo)

    def carry_4_bacak(self, coin: str, grup: str, senaryo: str = "taker") -> float:
        """Spot alış + vadeli satış + kapanışta tersleri (S2)."""
        return 2 * (self.tek_yon(coin, grup, "spot", senaryo) + self.tek_yon(coin, grup, "vadeli", senaryo))

    def olcekli(self, carpan: float) -> "MaliyetModeli":
        return replace(self, carpan=carpan)


def funding_nakit_akisi(adet: pd.Series, mark_fiyat: pd.Series, oran: pd.Series) -> pd.Series:
    """Her funding anındaki nakit akışı (pozitif = alınan).

    Pozitif oranda longlar öder, shortlar alır: akış = −adet · mark · oran.
    `adet` vadeli pozisyon adedi (short için negatif), funding anına hizalı olmalı.
    """
    return -(adet * mark_fiyat * oran)


def yillik_maliyet(gidis_donus_maliyeti: float, ortalama_tutma_gun: float) -> float:
    """Gidiş-dönüş maliyetini yıllık orana çevirir (S2 Aşama B, ölçüm 4)."""
    return gidis_donus_maliyeti * 365.0 / ortalama_tutma_gun
