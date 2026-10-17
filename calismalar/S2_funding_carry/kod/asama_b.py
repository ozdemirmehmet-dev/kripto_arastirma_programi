"""S2 Aşama B ölçümleri ve Kapı 1 (ön kayıt commit 33bd974, §4–§5). Strateji yok.

Veri kesimi: 2026-10-17 00:00 UTC. Günlük funding = o UTC gününde ödenen oranların toplamı
(aralık 8 saatten farklı olsa da toplam doğru yıllıklanır). İlk (yarım) gün atılır.

Çalıştırma:
  .venv/Scripts/python -m calismalar.S2_funding_carry.kod.asama_b --funding   (B1, B2, B4, test, Kapı 1)
  .venv/Scripts/python -m calismalar.S2_funding_carry.kod.asama_b --basis     (B3)
  .venv/Scripts/python -m calismalar.S2_funding_carry.kod.asama_b --kayit     (kayıt defteri)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from calismalar.S2_funding_carry.kod.fiyat_indir import KESIM, fiyatlar, vadeli_sembol
from ortak import istatistik, maliyet, rapor, veri

SONUC = Path(__file__).resolve().parents[1] / "results"
S1_SPREAD = veri.KOK / "calismalar" / "S1_btc_alt_gecikme" / "results" / "spread_ozet.csv"
COINLER = veri.tum_coinler()
Q = 0.10
BLOK_GUN = 30
TUTMALAR = (7, 30, 90)


# ---------------------------------------------------------------- veri

def funding(coin: str) -> pd.Series:
    f = pd.read_parquet(veri.VERI_DIZINI / "funding" / f"{vadeli_sembol(coin)}.parquet")
    f = f[f.index < KESIM]
    return f["fundingRate"].astype(float)


def gunluk(oran: pd.Series) -> pd.Series:
    g = oran.groupby(oran.index.floor("D")).sum()
    return g.iloc[1:]  # ilk gün yarım


def maliyet_modeli() -> maliyet.MaliyetModeli:
    sp = pd.read_csv(S1_SPREAD)
    return maliyet.MaliyetModeli(olculen_yarim_spread={
        (r.coin, r.piyasa): r.ortalama_yarim_spread for r in sp.itertuples()})


def btc_rejim() -> tuple[pd.Series, pd.Series]:
    d = veri.mumlar("BTCUSDT", "1d", "2019-01-01", KESIM, "spot")
    yil = d.groupby(d.index.year).agg(acilis=("open", "first"), kapanis=("close", "last"))
    getiri = yil["kapanis"] / yil["acilis"] - 1
    return pd.Series(np.where(getiri > 0, "yükseliş", "düşüş"), index=getiri.index), getiri


# ---------------------------------------------------------------- B1, B2, B4, test

def olc_funding():
    m = maliyet_modeli()
    rejim, btc_yil = btc_rejim()
    ozet, yillar, kalicilik = [], [], []
    for c in COINLER:
        oran = funding(c)
        f = gunluk(oran)
        grup = veri.coin_grubu(c)
        s = {"coin": c, "grup": grup, "ilk_gun": f.index[0].date(), "son_gun": f.index[-1].date(),
             "gun": len(f), "odeme": len(oran),
             "yillik_ort": f.mean() * 365, "yillik_medyan": f.median() * 365,
             "pozitif_odeme_orani": float((oran > 0).mean()),
             "negatif_en_uzun_gun": en_uzun_negatif(f)}
        # B1 rejim
        for r in ("yükseliş", "düşüş"):
            yil_listesi = rejim[rejim == r].index
            fr = f[f.index.year.isin(yil_listesi)]
            s[f"yillik_ort_{r}"] = fr.mean() * 365 if len(fr) else np.nan
        # test (block sign-flip, 30 gün)
        t = istatistik.blok_isaret_cevirme(f.to_numpy(), BLOK_GUN, 1000)
        s.update({"isaret_yuzdelik": t["yuzdelik"], "isaret_p": t["p"]})
        # iki yarı (zaman orta noktası)
        orta = f.index[0] + (f.index[-1] - f.index[0]) / 2
        a, b = f[f.index < orta].mean() * 365, f[f.index >= orta].mean() * 365
        s.update({"ilk_yari_yillik": a, "ikinci_yari_yillik": b,
                  "yarilar_gecti": bool(a > 0 and b > 0 and min(a, b) / max(a, b) >= 0.5)})
        # B4 maliyet
        c4 = m.carry_4_bacak(c, grup)
        s["bacak4_maliyet"] = c4
        for T in TUTMALAR:
            yillik_mal = maliyet.yillik_maliyet(c4, T)
            s[f"yillik_maliyet_{T}g"] = yillik_mal
            s[f"net_notional_{T}g"] = s["yillik_ort"] - yillik_mal
            s[f"net_sermaye_1x_{T}g"] = (s["yillik_ort"] - yillik_mal) / 2
            s[f"net_sermaye_2x_{T}g"] = (s["yillik_ort"] - yillik_mal) * 2 / 3
        s["kapi1_esik"] = 2 * maliyet.yillik_maliyet(c4, 30)
        s["bacak4_maliyet_maker"] = 2 * (m.tek_yon(c, grup, "spot", "maker") + m.tek_yon(c, grup, "vadeli", "maker"))
        ozet.append(s)
        # B1 yıl kırılımı
        for y, fy in f.groupby(f.index.year):
            oy = oran[oran.index.year == y]
            yillar.append({"coin": c, "yil": y, "gun": len(fy), "yillik_ort": fy.mean() * 365,
                           "yillik_medyan": fy.median() * 365, "pozitif_odeme_orani": float((oy > 0).mean()),
                           "rejim": rejim.get(y), "btc_yil_getiri": btc_yil.get(y)})
        # B2 kalıcılık
        for h in (1, 3, 7):
            gelecek = sum(f.shift(-k) for k in range(1, h + 1)).rename("y")
            mdl = istatistik.newey_west_ols(gelecek, f.rename("f").to_frame(),
                                            gecikme=max(h, int(np.floor(4 * (len(f) / 100) ** (2 / 9)))))
            kalicilik.append({"coin": c, "h_gun": h, "corr": float(f.corr(f.shift(-h))),
                              "egim": float(mdl.params["f"]), "egim_t": float(mdl.tvalues["f"]),
                              "r2": float(mdl.rsquared), "n": int(mdl.nobs)})
        print(c, f"yıllık ort %{s['yillik_ort'] * 100:.2f}", f"eşik %{s['kapi1_esik'] * 100:.2f}", flush=True)

    oz = pd.DataFrame(ozet)
    oz["bh_anlamli"], oz["bh_p"] = istatistik.benjamini_hochberg(oz["isaret_p"].to_numpy(), Q)
    oz["k_yarilar"] = oz["yarilar_gecti"]
    oz["k_rastgele"] = oz["isaret_yuzdelik"] > 95
    oz["k_bh"] = oz["bh_anlamli"]
    oz["k_maliyet"] = oz["yillik_ort"] >= oz["kapi1_esik"]
    oz["kapi1"] = oz[["k_yarilar", "k_rastgele", "k_bh", "k_maliyet"]].all(axis=1)
    oz["maliyet_orani"] = oz["yillik_ort"] / oz["kapi1_esik"]
    oz.to_csv(SONUC / "b1_b4_kapi1_ozet.csv", index=False)
    pd.DataFrame(yillar).to_csv(SONUC / "b1_yillar.csv", index=False)
    pd.DataFrame(kalicilik).to_csv(SONUC / "b2_kalicilik.csv", index=False)
    # kalite: aşırı oranlar ve 8h dışı aralıklar
    asiri, araliklar = [], []
    for c in COINLER:
        oran = funding(c)
        for t, v in oran[oran.abs() > 0.01].items():
            asiri.append({"coin": c, "zaman": t, "oran": v})
        ar = veri.funding_araligi_saat(oran.to_frame()).dropna().round(2)
        for h, g in ar[ar != 8].groupby(ar[ar != 8]):
            araliklar.append({"coin": c, "aralik_saat": h, "adet": len(g), "ilk": g.index[0], "son": g.index[-1]})
    pd.DataFrame(asiri).to_csv(SONUC / "funding_asiri_oranlar.csv", index=False)
    pd.DataFrame(araliklar).to_csv(SONUC / "funding_8h_disi_araliklar.csv", index=False)
    print("Kapı 1 geçen:", int(oz["kapi1"].sum()), "/ 13")


def en_uzun_negatif(f: pd.Series) -> int:
    en, simdi = 0, 0
    for v in (f < 0).to_numpy():
        simdi = simdi + 1 if v else 0
        en = max(en, simdi)
    return en


# ---------------------------------------------------------------- B3 basis

def olc_basis():
    yuzdelikler = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
    ozet, enler = [], []
    for c in COINLER:
        sp, vd = fiyatlar(c, "spot"), fiyatlar(c, "vadeli")
        d = pd.concat({"s": sp["close"], "f": vd["close"], "f_high": vd["high"], "f_open": vd["open"]},
                      axis=1, join="inner")
        basis = d["f"] / d["s"] - 1
        # aylık yeniden dengeleme varsayımı: short bacak her ayın ilk açılışında yeniden açılır
        ay = d.index.tz_localize(None).to_period("M")
        f_giris = d["f_open"].groupby(ay).transform("first")
        hareket = d["f_high"] / f_giris - 1  # short bacak aleyhine en kötü hareket (mum içi)
        s = {"coin": c, "mum": len(d), "ilk": d.index[0], "son": d.index[-1],
             "basis_ort": basis.mean(), "basis_std": basis.std()}
        s.update({f"basis_p{int(q * 100):02d}": basis.quantile(q) for q in yuzdelikler})
        for kal in (1, 2):
            kullanim = kal * hareket  # marjın tükenen oranı (izole, bakım %1 hariç)
            likidasyon = hareket >= (1 / kal - 0.01)
            s[f"marj_kullanim_max_{kal}x"] = kullanim.max()
            s[f"likidasyon_ay_{kal}x"] = int(likidasyon.groupby(ay).any().sum())
        ozet.append(s)
        en10 = basis.nlargest(10)
        for t, b in en10.items():
            enler.append({"coin": c, "zaman": t, "basis": b, "yon": "en_yuksek",
                          "marj_kullanim_1x": float(hareket.loc[t]), "marj_kullanim_2x": float(2 * hareket.loc[t])})
        for t, b in basis.nsmallest(10).items():
            enler.append({"coin": c, "zaman": t, "basis": b, "yon": "en_dusuk",
                          "marj_kullanim_1x": float(hareket.loc[t]), "marj_kullanim_2x": float(2 * hareket.loc[t])})
        print(c, f"basis medyan %{s['basis_p50'] * 100:.3f}", f"max marj 2x {s['marj_kullanim_max_2x']:.2f}",
              flush=True)
    pd.DataFrame(ozet).to_csv(SONUC / "b3_basis_ozet.csv", index=False)
    pd.DataFrame(enler).to_csv(SONUC / "b3_basis_en_genis.csv", index=False)


# ---------------------------------------------------------------- kayıt defteri

def kayit():
    oz = pd.read_csv(SONUC / "b1_b4_kapi1_ozet.csv")
    for r in oz.itertuples():
        rapor.kayit_ekle("S2", "B", "günlük funding ort > 0, 30g blok işaret çevirme (ana test)", r.coin, "1d",
                         f"yıllık %{r.yillik_ort * 100:.2f}, eşik %{r.kapi1_esik * 100:.2f}, yüzdelik %{r.isaret_yuzdelik:.1f}, "
                         f"BH p={r.bh_p:.3g}, yarılar %{r.ilk_yari_yillik * 100:.1f}/%{r.ikinci_yari_yillik * 100:.1f}, "
                         f"Kapı 1 {'GEÇTİ' if r.kapi1 else 'kaldı'}")
    for r in pd.read_csv(SONUC / "b1_yillar.csv").itertuples():
        rapor.kayit_ekle("S2", "B1", f"tanımlayıcı yıl {r.yil} ({r.rejim})", r.coin, "1d",
                         f"yıllık %{r.yillik_ort * 100:.2f}, pozitif ödeme %{r.pozitif_odeme_orani * 100:.0f}")
    for r in pd.read_csv(SONUC / "b2_kalicilik.csv").itertuples():
        rapor.kayit_ekle("S2", "B2", f"tanımlayıcı kalıcılık h={r.h_gun}g", r.coin, "1d",
                         f"corr={r.corr:.3f}, eğim={r.egim:.3f} (t={r.egim_t:.1f})")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    SONUC.mkdir(parents=True, exist_ok=True)
    if "--funding" in sys.argv:
        olc_funding()
    if "--basis" in sys.argv:
        olc_basis()
    if "--kayit" in sys.argv:
        kayit()


if __name__ == "__main__":
    main()
