"""S1 ilk ara rapor (ön kayıt §7): B4 (1s gecikme ölçeği) + B1/B2 (1s ve 1m, spot),
1m vadeli kontrolü. Çıktılar results/ altına.

Çalıştırma: .venv/Scripts/python -m calismalar.S1_btc_alt_gecikme.kod.ara_rapor_1
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from calismalar.S1_btc_alt_gecikme.kod import olcum  # noqa: E402
from calismalar.S1_btc_alt_gecikme.kod.veri_indir import yukle  # noqa: E402
from ortak import istatistik, rapor, veri  # noqa: E402

SONUC = Path(__file__).resolve().parents[1] / "results"
ALTLAR = [c for c in veri.tum_coinler() if c != "BTC"]
B2_AILE = 60  # 12 coin × 5 zaman dilimi (ön kayıt §5)


def getiriler(aralik, piyasa):
    btc = yukle("BTC", aralik, piyasa)
    r_btc = olcum.izgara_getiri(btc, aralik)
    out = {}
    for c in ALTLAR:
        df = yukle(c, aralik, piyasa)
        r = olcum.izgara_getiri(df, aralik)
        ortak_idx = r_btc.index.union(r.index)
        out[c] = (df, r.reindex(ortak_idx))
    return btc, r_btc, out


def b1_b2(aralik, piyasa, n_karistirma):
    _, r_btc, altlar = getiriler(aralik, piyasa)
    satirlar = []
    for c, (_, r_alt) in altlar.items():
        rb = r_btc.reindex(r_alt.index)
        s = {"coin": c, "grup": veri.coin_grubu(c), "aralik": aralik, "piyasa": piyasa}
        s.update(olcum.b1_eszamanli(rb, r_alt))
        s.update(olcum.b2_gecikmeli(rb, r_alt, aralik, n_karistirma=n_karistirma))
        # ekonomik büyüklük (tanımlayıcı): 2σ'lık BTC mumundan sonra beklenen ek alt hareketi
        s["b1_x_2sigma_pct"] = float(s["b1"] * 2 * rb.std() * 100)
        satirlar.append(s)
        print(aralik, piyasa, c, f"b1={s['b1']:.4f} t={s['b1_t']:.2f} "
              f"karistirma%={s.get('karistirma_yuzdelik', float('nan')):.1f}", flush=True)
    return pd.DataFrame(satirlar)


def b4(n_esik=3.0):
    btc, r_btc, altlar = getiriler("1s", "spot")
    olay = olcum.olaylar(r_btc, K=n_esik)
    # tanımlayıcı ek (ön kayıt dışı): 1m verisinden β (olay öncesi 500 dakika)
    _, r_btc_1m, altlar_1m = getiriler("1m", "spot")
    xc, ozet, egriler = {}, [], {}
    for c, (df, r_alt) in altlar.items():
        rb = r_btc.reindex(r_alt.index)
        xc[c] = olcum.capraz_korelasyon(rb, r_alt, 120)
        close = df["close"].reindex(r_alt.index)
        s = olcum.b4_yetisme(close, rb, r_alt, olay)
        egriler[c] = s.pop("_egri", None)
        r1 = altlar_1m[c][1]
        rb1 = r_btc_1m.reindex(r1.index)
        # shift(1): t dakikasının açılış zamanındaki değer t−1 dakikasına kadarki veriyi kullanır
        beta_1m = (rb1.rolling(500).cov(r1) / rb1.rolling(500).var()).shift(1)
        s1m = olcum.b4_yetisme(close, rb, r_alt, olay, beta_disaridan=beta_1m)
        s1m.pop("_egri", None)
        k_max = int(xc[c].idxmax())
        ozet.append({"coin": c, "grup": veri.coin_grubu(c), "corr_k0": xc[c][0],
                     "corr_max_k_sn": k_max, "corr_max": xc[c][k_max],
                     "corr_k1": xc[c][1], "corr_k5": xc[c][5], "corr_k30": xc[c][30],
                     **s, **{f"beta1m_{k}": v for k, v in s1m.items()
                             if k in ("medyan_t50_sn", "medyan_t90_sn", "toplu_t50_sn", "toplu_t90_sn",
                                      "t90_ulasmayan_oran")}})
    return pd.DataFrame(ozet), pd.DataFrame(xc), egriler, len(olay)


def grafikler(xc: pd.DataFrame, egriler: dict):
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
    renk = {"Büyük": "#1f77b4", "Orta": "#2ca02c", "Küçük": "#d62728"}
    for c in xc.columns:
        g = veri.coin_grubu(c)
        ax[0].plot(xc.index[:31], xc[c].iloc[:31], color=renk[g], alpha=0.8, label=f"{c} ({g})")
        if egriler.get(c) is not None:
            ax[1].plot(np.arange(len(egriler[c])), egriler[c], color=renk[g], alpha=0.8)
    ax[0].set(title="corr(r_btc_t, r_alt_{t+k}), 1s spot", xlabel="k (saniye)", ylabel="korelasyon")
    ax[0].legend(fontsize=7, ncol=2)
    ax[1].axhline(0.5, ls="--", c="gray", lw=0.8)
    ax[1].axhline(0.9, ls="--", c="gray", lw=0.8)
    ax[1].set(title="BTC 3σ olayı sonrası alt hareketi / beklenen (β_1s), toplu",
              xlabel="olaydan sonra saniye", ylabel="oran")
    rapor.grafik_kaydet(fig, SONUC / "b4_gecikme_olcegi_1s.png")
    plt.close(fig)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    SONUC.mkdir(parents=True, exist_ok=True)

    if (SONUC / "b4_1s_ozet.csv").exists() and "--b4-yeniden" not in sys.argv:
        print("B4 önceki çalıştırmadan alındı (results/b4_1s_ozet.csv)", flush=True)
        n_olay = int(pd.read_csv(SONUC / "b4_1s_ozet.csv")["olay"].max())
    else:
        oz4, xc, egriler, n_olay = b4()
        oz4.to_csv(SONUC / "b4_1s_ozet.csv", index=False)
        xc.to_csv(SONUC / "b4_1s_capraz_korelasyon.csv")
        grafikler(xc, egriler)

    b2_1s = b1_b2("1s", "spot", 1000)
    b2_1m = b1_b2("1m", "spot", 1000)
    b2_1m_v = b1_b2("1m", "vadeli", 0)
    b2 = pd.concat([b2_1s, b2_1m])
    # ara BH: bilinmeyen 36 p değeri 1 kabul edilir (muhafazakâr; tam aile 60)
    p = np.concatenate([b2["b1_p_tek"].to_numpy(), np.ones(B2_AILE - len(b2))])
    anlamli, duz = istatistik.benjamini_hochberg(p, q=0.10)
    b2["bh_ara_duzeltilmis_p"] = duz[:len(b2)]
    b2["bh_ara_anlamli"] = anlamli[:len(b2)]
    b2.to_csv(SONUC / "b1_b2_spot_1s_1m.csv", index=False)
    b2_1m_v.to_csv(SONUC / "b1_b2_vadeli_1m_kontrol.csv", index=False)

    for _, r in b2.iterrows():
        rapor.kayit_ekle("S1", "B2", "b1>0 HAC tek yönlü (ana test)", r.coin, r.aralik,
                         f"b1={r.b1:.4f}, t={r.b1_t:.2f}, p={r.b1_p_tek:.3g}, karıştırma %{r.karistirma_yuzdelik:.1f}, "
                         f"yarılar {'geçti' if r.yarilar_gecti else 'kaldı'}, ara BH {'anlamlı' if r.bh_ara_anlamli else 'değil'}")
    for _, r in b2_1m_v.iterrows():
        rapor.kayit_ekle("S1", "B2", "vadeli kontrol (BH dışı)", r.coin, "1m",
                         f"b1={r.b1:.4f}, t={r.b1_t:.2f}")
    print("bitti; B4 olay sayısı:", n_olay)


if __name__ == "__main__":
    main()
