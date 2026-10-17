"""S1 sonuç grafiği: B3 (K=2, h=3, açılış→açılış) ortalama vs Kapı 1 maliyet eşiği."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from ortak import rapor  # noqa: E402

SONUC = Path(__file__).resolve().parents[1] / "results"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    d = pd.read_csv(SONUC / "kapi1_b3.csv")
    sira = ["1m", "5m", "15m", "1h"]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    renk = {"Büyük": "#1f77b4", "Orta": "#2ca02c", "Küçük": "#d62728"}
    for i, a in enumerate(sira):
        x = d[d.aralik == a]
        for j, (_, r) in enumerate(x.iterrows()):
            ax.scatter(i + (j - 5.5) * 0.04, r.ortalama * 1e4, color=renk[r.grup], s=22,
                       marker="o" if r.wild_yuzdelik > 95 else "x")
    ax.axhline(32, color="black", ls="--", lw=1, label="Kapı 1 eşiği Büyük/Orta (32 bps)")
    ax.axhline(40, color="gray", ls=":", lw=1, label="Kapı 1 eşiği Küçük (40 bps)")
    ax.axhline(0, color="gray", lw=0.6)
    ax.set_xticks(range(len(sira)), sira)
    ax.set(ylabel="ortalama işaretli altcoin getirisi (bps)",
           title="S1 B3: BTC 2σ olayından sonra 3 mum (spot, açılış→açılış). o = wild %95 üstü, x = değil")
    for g, c in renk.items():
        ax.scatter([], [], color=c, label=g)
    ax.legend(fontsize=8, loc="upper left")
    rapor.grafik_kaydet(fig, SONUC / "b3_maliyet_esigi.png")


if __name__ == "__main__":
    main()
