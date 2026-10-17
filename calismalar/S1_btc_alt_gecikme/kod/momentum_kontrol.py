"""B3 tanımlayıcı kontrol (ön kayıt dışı, kapı kararına girmez).

Soru: Olay sonrası altcoinin BTC yönündeki hareketi gecikmeli yetişme mi, yoksa BTC'nin
kendisinin aynı yönde devam etmesi (momentum) mi?
- btc_h3: olay sonrası BTC'nin işaretli açılış→açılış getirisi (h=3)
- hedgeli_h3: altcoin işaretli getirisi − β_rolling · btc_h3 (gecikme varsa > 0)

Çalıştırma: .venv/Scripts/python -m calismalar.S1_btc_alt_gecikme.kod.momentum_kontrol
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from calismalar.S1_btc_alt_gecikme.kod import kapi1, olcum
from calismalar.S1_btc_alt_gecikme.kod.ara_rapor_1 import ALTLAR
from calismalar.S1_btc_alt_gecikme.kod.veri_indir import yukle
from ortak import rapor

SONUC = Path(__file__).resolve().parents[1] / "results"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    satirlar = []
    for aralik in ("1m", "5m", "15m", "1h"):
        tam = kapi1.tam_izgara(aralik)
        btc = olcum.izgara(yukle("BTC", aralik, "spot"), aralik, tam)
        r_btc = np.log(btc["close"]).diff()
        ev = olcum.olaylar(r_btc, 2)
        # BTC'nin kendi devamı: BTC'yi "altcoin" yerine koyarak aynı tablo
        tb = olcum.b3_olay_tablosu(btc, btc, aralik, ev)
        btc_h3 = tb["acilis_h3"]
        for c in ALTLAR:
            alt = olcum.izgara(yukle(c, aralik, "spot"), aralik, tam)
            t = olcum.b3_olay_tablosu(btc, alt, aralik, ev)
            d = pd.DataFrame({"alt": t["acilis_h3"], "btc": btc_h3, "beta": t["beta"]}).dropna()
            hedgeli = d["alt"] - d["beta"] * d["btc"]
            w = olcum.wild_ortalama(hedgeli.to_numpy(), d.index, olcum.BLOK[aralik])
            satirlar.append({"coin": c, "aralik": aralik, "olay": len(d),
                             "alt_h3_bps": d["alt"].mean() * 1e4, "btc_h3_bps": d["btc"].mean() * 1e4,
                             "beta_ort": d["beta"].mean(), "hedgeli_h3_bps": hedgeli.mean() * 1e4,
                             "hedgeli_wild_yuzdelik": w["wild_yuzdelik"]})
            print(satirlar[-1], flush=True)
    df = pd.DataFrame(satirlar)
    df.to_csv(SONUC / "b3_momentum_kontrol.csv", index=False)
    for _, r in df.iterrows():
        rapor.kayit_ekle("S1", "B3", "tanımlayıcı: β-hedgeli h=3 (ön kayıt dışı)", r.coin, r.aralik,
                         f"hedgeli={r.hedgeli_h3_bps:.2f} bps, BTC devamı={r.btc_h3_bps:.2f} bps, "
                         f"wild %{r.hedgeli_wild_yuzdelik:.1f}")


if __name__ == "__main__":
    main()
