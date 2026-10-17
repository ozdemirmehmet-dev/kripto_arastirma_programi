"""S3 Aşama B ölçümleri ve Kapı 1 (ön kayıt commit 85e32a5, §3–§5). Strateji yok.

Uygulama ayrıntıları (ön kayıtta açık kalan; sonuçlar görülmeden önce sabitlendi):
- Yüzdelik sıra KATI hesaplanır: aşırı yüksek = penceredeki (son 90 gün, t dahil) ödemelerin
  en az %95'inden KESİN büyük ve oran > 0; aşırı düşük = en az %95'inden kesin küçük ve oran < 0.
  Gerekçe: funding sık sık taban orana (%0,01) eşit kalır. Eşitlikler "≤" ile sayılsaydı
  sakin dönemlerde sıradan ödemeler aşırı sayılırdı.
- Giriş mumu = floor_saat(fundingTime) + 1 saat (fundingTime ms kaymalı gelir; "sonraki ilk mum").
- h günlük getiri = ln(open[giriş + 24h·h] / open[giriş]); gereken mum yoksa olay o h için atılır.
- β: olay gününden önceki 90 günün günlük (vadeli 1h'den UTC gün sonu kapanışı) getirileri.
- Olmayan (olay dışı) funding anları için aynı beta ayarlı getiri, karşılaştırma için.

Çalıştırma: .venv/Scripts/python -m calismalar.S3_asiri_funding.kod.asama_b [--olc] [--kayit]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from calismalar.S2_funding_carry.kod.fiyat_indir import KESIM, vadeli_sembol
from ortak import istatistik, maliyet, rapor, veri

SONUC = Path(__file__).resolve().parents[1] / "results"
COINLER = veri.tum_coinler()
EK_COINLER = ["LUNA", "FTT"]
PENCERE = pd.Timedelta(days=90)
UFUKLAR = (1, 3, 7)
ANA_H = 3
DONEM_BAS, DONEM_SON = pd.Timestamp("2019-09-10", tz="UTC"), KESIM
Q = 0.10
TEKRAR = 9999


# ---------------------------------------------------------------- veri

def funding(sembol: str) -> pd.Series:
    f = pd.read_parquet(veri.VERI_DIZINI / "funding" / f"{sembol}.parquet")
    return f.loc[f.index < KESIM, "fundingRate"].astype(float)


def fiyat_1h(sembol: str, piyasa: str, bas: pd.Timestamp, olcek: float = 1.0) -> pd.DataFrame:
    df = veri.mumlar(sembol, "1h", bas.normalize(), KESIM, piyasa)
    if olcek != 1.0:
        df[["open", "close"]] = df[["open", "close"]] / olcek
    return df[["open", "close"]]


def semboller(coin: str, piyasa: str) -> tuple[str, float]:
    if piyasa == "vadeli":
        return vadeli_sembol(coin), (1000.0 if coin == "PEPE" else 1.0)
    return f"{coin}USDT", 1.0


# ---------------------------------------------------------------- olaylar

def katı_yuzdelikler(oran: pd.Series) -> pd.DataFrame:
    t = oran.index
    v = oran.to_numpy()
    bas_idx = np.searchsorted(t, t - PENCERE, side="right")
    alt, ust, n = np.full(len(v), np.nan), np.full(len(v), np.nan), np.zeros(len(v), int)
    ilk_gecerli = t[0] + PENCERE
    for i in range(len(v)):
        if t[i] < ilk_gecerli:
            continue
        w = v[bas_idx[i]:i + 1]
        ust[i] = np.mean(w < v[i]) * 100  # v'den kesin küçük olanların payı
        alt[i] = np.mean(w > v[i]) * 100  # v'den kesin büyük olanların payı
        n[i] = len(w)
    return pd.DataFrame({"oran": v, "kucuk_pay": ust, "buyuk_pay": alt, "pencere_n": n}, index=t)


def olaylar(y: pd.DataFrame, yon: str, sogu=pd.Timedelta(days=3)) -> pd.DatetimeIndex:
    if yon == "yuksek":
        aday = y[(y["kucuk_pay"] >= 95) & (y["oran"] > 0)].index
    else:
        aday = y[(y["buyuk_pay"] >= 95) & (y["oran"] < 0)].index
    secilen, son = [], None
    for t in aday:
        if son is None or t - son > sogu:
            secilen.append(t)
            son = t
    return pd.DatetimeIndex(secilen)


# ---------------------------------------------------------------- getiriler

def gunluk_getiri(df: pd.DataFrame) -> pd.Series:
    c = df["close"].groupby(df.index.floor("D")).last()
    return np.log(c).diff()


def olay_getirileri(zamanlar: pd.DatetimeIndex, alt: pd.DataFrame, btc: pd.DataFrame,
                    beta: pd.Series | None, oran: pd.Series) -> pd.DataFrame:
    giris = zamanlar.floor("h") + pd.Timedelta(hours=1)
    ao, bo = alt["open"], btc["open"]
    ot = oran.index
    cs = np.concatenate([[0.0], np.cumsum(oran.to_numpy())])
    satirlar = []
    for t, g in zip(zamanlar, giris):
        s = {"zaman": t, "giris": g, "oran": oran.loc[t]}
        b = beta.get(t.floor("D"), np.nan) if beta is not None else 0.0
        s["beta"] = b
        for h in UFUKLAR:
            c = g + pd.Timedelta(days=h)
            ra = np.log(ao.get(c, np.nan) / ao.get(g, np.nan))
            rb = np.log(bo.get(c, np.nan) / bo.get(g, np.nan))
            s[f"R_h{h}"] = ra
            s[f"Radj_h{h}"] = ra - b * rb if beta is not None else ra
            # tutma süresinde ödenen funding toplamı (giriş ≤ ödeme < çıkış)
            s[f"funding_toplam_h{h}"] = float(cs[ot.searchsorted(c, "left")] - cs[ot.searchsorted(g, "left")])
        satirlar.append(s)
    return pd.DataFrame(satirlar).set_index("zaman") if satirlar else pd.DataFrame()


def wild_hafta(y: np.ndarray, zaman: pd.DatetimeIndex, tohum=None) -> dict:
    y = np.asarray(y, float)
    iso = zaman.isocalendar()
    kod = pd.factorize(iso["year"].astype(str) + "-" + iso["week"].astype(str))[0]
    s = np.bincount(kod, weights=y)
    w = istatistik.rng(tohum).choice([-1.0, 1.0], size=(TEKRAR, len(s)))
    sifir = (w @ s) / len(y)
    return {"wild_yuzdelik": istatistik.yuzdelik(float(y.mean()), sifir),
            "wild_p": float((np.sum(sifir >= y.mean()) + 1) / (TEKRAR + 1)), "hafta_blok": len(s)}


def iki_yari(y: pd.Series) -> dict:
    orta = DONEM_BAS + (DONEM_SON - DONEM_BAS) / 2
    a, b = y[y.index < orta].mean(), y[y.index >= orta].mean()
    return {"ilk_yari": a, "ikinci_yari": b, "n_ilk": int((y.index < orta).sum()),
            "n_ikinci": int((y.index >= orta).sum()),
            "yarilar_gecti": bool(a > 0 and b > 0 and min(a, b) / max(a, b) >= 0.5)}


# ---------------------------------------------------------------- ana ölçüm

def coin_olaylari(coin: str, piyasa: str, btc: pd.DataFrame, rb_gun: pd.Series) -> pd.DataFrame:
    fs = vadeli_sembol(coin) if coin not in EK_COINLER else f"{coin}USDT"
    oran = funding(fs)
    yz = katı_yuzdelikler(oran)
    sembol, olcek = semboller(coin, piyasa) if coin not in EK_COINLER else (f"{coin}USDT", 1.0)
    alt = fiyat_1h(sembol, piyasa, oran.index[0], olcek)
    if coin == "BTC":
        beta = None
    else:
        ra_gun = gunluk_getiri(alt)
        d = pd.concat([ra_gun, rb_gun], axis=1, keys=["a", "b"], sort=True).dropna()
        beta = (d["a"].rolling(90, min_periods=60).cov(d["b"]) / d["b"].rolling(90, min_periods=60).var()).shift(1)
    parcalar = []
    for yon in ("yuksek", "dusuk"):
        z = olaylar(yz, yon)
        t = olay_getirileri(z, alt, btc, beta, oran)
        if t.empty:
            continue
        t["yon"] = yon
        isaret = -1.0 if yon == "yuksek" else 1.0
        for h in UFUKLAR:
            t[f"y_h{h}"] = isaret * t[f"Radj_h{h}"]
            t[f"yham_h{h}"] = isaret * t[f"R_h{h}"]
            # pozisyon yönü d = isaret; alınan funding = −d · Σoran
            t[f"funding_alinan_h{h}"] = -isaret * t[f"funding_toplam_h{h}"]
        parcalar.append(t)
    # karşılaştırma: olay dışı tüm ödeme anları (yüzdelik tanımlı olanlar)
    tum = yz.dropna(subset=["kucuk_pay"]).index
    olay_anlari = pd.DatetimeIndex(np.concatenate([p.index.values for p in parcalar])) if parcalar else []
    disi = tum.difference(olay_anlari)
    k = olay_getirileri(disi, alt, btc, beta, oran)
    k["yon"] = "olay_disi"
    parcalar.append(k)
    out = pd.concat(parcalar)
    out["coin"] = coin
    out["grup"] = veri.coin_grubu(coin) if coin not in EK_COINLER else "Ek"
    out["piyasa"] = piyasa
    return out


def olc():
    m = maliyet.MaliyetModeli()
    hepsi = []
    for piyasa in ("vadeli", "spot"):
        btc = fiyat_1h(*(("BTCUSDT", piyasa, pd.Timestamp("2019-09-10", tz="UTC"))))
        rb_gun = gunluk_getiri(btc)
        coinler = COINLER + (EK_COINLER if piyasa == "vadeli" else [])
        for c in coinler:
            try:
                hepsi.append(coin_olaylari(c, piyasa, btc, rb_gun))
                print(piyasa, c, "tamam", flush=True)
            except Exception as e:
                print(piyasa, c, "HATA:", e, flush=True)
    t = pd.concat(hepsi)
    t.to_parquet(SONUC / "olaylar_ham.parquet")
    ozetle(t, m)


def ozetle(t: pd.DataFrame, m: maliyet.MaliyetModeli):
    def esik(grup):
        return 2 * m.gidis_donus("X", grup if grup in ("Büyük", "Orta", "Referans") else "Küçük", "vadeli")

    satirlar = []
    ana_evren = t["coin"].isin(COINLER)
    for piyasa in ("vadeli", "spot"):
        for evren_adi, evren in (("ana", ana_evren), ("ek_delist_dahil", pd.Series(True, index=t.index))):
            if piyasa == "spot" and evren_adi != "ana":
                continue
            for yon in ("yuksek", "dusuk"):
                for h in UFUKLAR:
                    d = t[(t.piyasa == piyasa) & evren & (t.yon == yon)].dropna(subset=[f"y_h{h}"])
                    if len(d) < 2:
                        continue
                    y = d[f"y_h{h}"].sort_index()
                    s = {"piyasa": piyasa, "evren": evren_adi, "yon": yon, "h": h, "olay": len(d),
                         "coin_sayisi": d["coin"].nunique(), "ortalama": y.mean(), "medyan": y.median(),
                         "ham_ortalama": d[f"yham_h{h}"].mean(),
                         "funding_alinan_ort": d[f"funding_alinan_h{h}"].mean(),
                         "esik": float(np.mean([esik(g) for g in d["grup"]]))}
                    s.update(wild_hafta(y.to_numpy(), y.index))
                    s.update(iki_yari(y))
                    satirlar.append(s)
    oz = pd.DataFrame(satirlar)
    # olay dışı karşılaştırma (beta ayarlı getiri ortalaması, işaretsiz)
    kars = []
    for piyasa in ("vadeli", "spot"):
        for h in UFUKLAR:
            d = t[(t.piyasa == piyasa) & ana_evren & (t.yon == "olay_disi")]
            kars.append({"piyasa": piyasa, "h": h, "n": int(d[f"Radj_h{h}"].notna().sum()),
                         "Radj_ort": d[f"Radj_h{h}"].mean()})
    pd.DataFrame(kars).to_csv(SONUC / "olay_disi_karsilastirma.csv", index=False)

    ana = oz[(oz.piyasa == "vadeli") & (oz.evren == "ana") & (oz.h == ANA_H)].copy()
    ana["bh_anlamli"], ana["bh_p"] = istatistik.benjamini_hochberg(ana["wild_p"].to_numpy(), Q)
    ana["k_olay"] = ana["olay"] >= 50
    ana["k_yarilar"] = ana["yarilar_gecti"]
    ana["k_wild"] = ana["wild_yuzdelik"] > 95
    ana["k_bh"] = ana["bh_anlamli"]
    ana["k_maliyet"] = ana["ortalama"] >= ana["esik"]
    ana["kapi1"] = ana[["k_olay", "k_yarilar", "k_wild", "k_bh", "k_maliyet"]].all(axis=1)
    ana.to_csv(SONUC / "kapi1.csv", index=False)
    oz.to_csv(SONUC / "ozet_tum.csv", index=False)

    # coin bazında (tanımlayıcı)
    cb = []
    for (c, piyasa, yon), d in t[t.yon != "olay_disi"].groupby(["coin", "piyasa", "yon"]):
        for h in UFUKLAR:
            dd = d.dropna(subset=[f"y_h{h}"])
            cb.append({"coin": c, "piyasa": piyasa, "yon": yon, "h": h, "olay": len(dd),
                       "ortalama": dd[f"y_h{h}"].mean(), "ham_ortalama": dd[f"yham_h{h}"].mean()})
    pd.DataFrame(cb).to_csv(SONUC / "coin_bazinda.csv", index=False)
    print(ana[["yon", "olay", "ortalama", "esik", "wild_yuzdelik", "bh_p", "ilk_yari", "ikinci_yari", "kapi1"]])


def kayit():
    ana = pd.read_csv(SONUC / "kapi1.csv")
    for r in ana.itertuples():
        rapor.kayit_ekle("S3", "B", f"aşırı {r.yon} funding, h=3g, beta ayarlı, havuz (ana test)", "13 coin", "1h",
                         f"olay={r.olay}, ort=%{r.ortalama * 100:.3f}, eşik=%{r.esik * 100:.2f}, wild %{r.wild_yuzdelik:.1f}, "
                         f"BH p={r.bh_p:.3g}, yarılar %{r.ilk_yari * 100:.3f}/%{r.ikinci_yari * 100:.3f}, "
                         f"Kapı 1 {'GEÇTİ' if r.kapi1 else 'kaldı'}")
    oz = pd.read_csv(SONUC / "ozet_tum.csv")
    for r in oz.itertuples():
        if r.piyasa == "vadeli" and r.evren == "ana" and r.h == ANA_H:
            continue
        rapor.kayit_ekle("S3", "B", f"tanımlayıcı {r.yon} h={r.h}g ({r.piyasa}, {r.evren})", "havuz", "1h",
                         f"olay={r.olay}, ort=%{r.ortalama * 100:.3f}, wild %{r.wild_yuzdelik:.1f}")
    for r in pd.read_csv(SONUC / "coin_bazinda.csv").itertuples():
        rapor.kayit_ekle("S3", "B", f"tanımlayıcı coin {r.yon} h={r.h}g ({r.piyasa})", r.coin, "1h",
                         f"olay={r.olay}, ort=%{r.ortalama * 100:.3f}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    SONUC.mkdir(parents=True, exist_ok=True)
    if "--olc" in sys.argv:
        olc()
    if "--kayit" in sys.argv:
        kayit()


if __name__ == "__main__":
    main()
