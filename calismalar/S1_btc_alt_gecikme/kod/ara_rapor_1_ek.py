"""Ara rapor 1 eki (ön kayıt dışı, tanımlayıcı): B2 için wild blok bootstrap.

Blok karıştırma testinin her kombinasyonda %100 vermesinin nedenini göstermek için:
aynı b1 için karıştırma sıfır dağılımı yerine heteroskedastisiteye dayanıklı sıfır dağılımı.
Kapı kararı için kullanılmaz; kullanıcının onayıyla ön kayda Ek olarak alınırsa kullanılır.

Çalıştırma: .venv/Scripts/python -m calismalar.S1_btc_alt_gecikme.kod.ara_rapor_1_ek
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from calismalar.S1_btc_alt_gecikme.kod import olcum
from calismalar.S1_btc_alt_gecikme.kod.ara_rapor_1 import getiriler
from ortak import rapor, veri

SONUC = Path(__file__).resolve().parents[1] / "results"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    satirlar = []
    for aralik, piyasa in (("1s", "spot"), ("1m", "spot"), ("1m", "vadeli")):
        _, r_btc, altlar = getiriler(aralik, piyasa)
        for c, (_, r_alt) in altlar.items():
            s = {"coin": c, "grup": veri.coin_grubu(c), "aralik": aralik, "piyasa": piyasa}
            s.update(olcum.b2_wild_bootstrap(r_btc.reindex(r_alt.index), r_alt, aralik))
            satirlar.append(s)
            print(s, flush=True)
    df = pd.DataFrame(satirlar)
    df.to_csv(SONUC / "b2_wild_bootstrap_ek.csv", index=False)
    for _, r in df.iterrows():
        rapor.kayit_ekle("S1", "B2", "EK ön kayıt dışı: wild blok bootstrap (BH dışı)", r.coin,
                         f"{r.aralik} {r.piyasa}", f"b1={r.wild_b1:.4f}, yüzdelik %{r.wild_yuzdelik:.1f}, "
                                                    f"p={r.wild_p:.3g}")


if __name__ == "__main__":
    main()
