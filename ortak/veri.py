"""Veri: indirme, önbellek, hizalama, kalite kontrol.

Kaynaklar (hepsi herkese açık, API anahtarı gerektirmez):
- data.binance.vision  : aylık/günlük toplu mum dosyaları (geçmiş için)
- api.binance.com      : spot REST (exchangeInfo, klines, bookTicker)
- fapi.binance.com     : USDT-M vadeli REST (exchangeInfo, klines, fundingRate)

Tüm zamanlar UTC. Mumlar `open_time` ile indekslenir. Yalnız tamamlanmış günler
kullanılır (bugünün yarım günü kullanılmaz).
"""
from __future__ import annotations

import io
import json
import time
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

KOK = Path(__file__).resolve().parents[1]
VERI_DIZINI = KOK / "data"

SPOT_REST = "https://api.binance.com"
VADELI_REST = "https://fapi.binance.com"
VISION = "https://data.binance.vision/data"

# Bölüm 2.9 coin evreni (ön kayıtsız değiştirilmez)
EVREN = {
    "Referans": ["BTC"],
    "Büyük": ["ETH", "SOL", "XRP", "BNB"],
    "Orta": ["DOGE", "ADA", "AVAX", "LINK"],
    "Küçük": ["NEAR", "ARB", "INJ", "PEPE"],
}

KLINE_SUTUNLARI = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore",
]

ARALIK_MS = {
    "1s": 1_000, "1m": 60_000, "3m": 180_000, "5m": 300_000, "15m": 900_000,
    "30m": 1_800_000, "1h": 3_600_000, "2h": 7_200_000, "4h": 14_400_000,
    "8h": 28_800_000, "1d": 86_400_000,
}

_oturum = requests.Session()
_oturum.headers["User-Agent"] = "kripto-arastirma/0.1 (yalniz-okuma)"


def coin_grubu(coin: str) -> str:
    for grup, coinler in EVREN.items():
        if coin in coinler:
            return grup
    raise KeyError(coin)


def tum_coinler() -> list[str]:
    return [c for coinler in EVREN.values() for c in coinler]


# ---------------------------------------------------------------- HTTP

def _get(url: str, params: dict | None = None, deneme: int = 5) -> requests.Response:
    for i in range(deneme):
        try:
            r = _oturum.get(url, params=params, timeout=30)
        except (requests.ConnectionError, requests.Timeout):
            if i == deneme - 1:
                raise
            time.sleep(5 * (i + 1))
            continue
        if r.status_code in (418, 429):
            bekle = int(r.headers.get("Retry-After", 10 * (i + 1)))
            time.sleep(bekle)
            continue
        if r.status_code >= 500:
            time.sleep(2 * (i + 1))
            continue
        return r
    r.raise_for_status()
    return r


def _get_json(url: str, params: dict | None = None):
    r = _get(url, params)
    r.raise_for_status()
    return r.json()


def _utc(t) -> pd.Timestamp:
    ts = pd.Timestamp(t)
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def _ms(t) -> int:
    return int(round(_utc(t).timestamp() * 1000))


def son_tam_gun() -> pd.Timestamp:
    """Bugünün 00:00 UTC'si: bundan önceki veriler tamamlanmış günlerdir."""
    return pd.Timestamp(datetime.now(timezone.utc).date(), tz="UTC")


# ---------------------------------------------------------------- borsa bilgisi

def borsa_bilgisi(piyasa: str = "spot", yenile: bool = False) -> dict:
    """exchangeInfo, günlük önbellekli. piyasa: 'spot' | 'vadeli'."""
    yol = VERI_DIZINI / "meta" / f"exchangeInfo_{piyasa}.json"
    if yol.exists() and not yenile:
        if time.time() - yol.stat().st_mtime < 86_400:
            return json.loads(yol.read_text(encoding="utf-8"))
    url = f"{SPOT_REST}/api/v3/exchangeInfo" if piyasa == "spot" else f"{VADELI_REST}/fapi/v1/exchangeInfo"
    veri = _get_json(url)
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps(veri), encoding="utf-8")
    return veri


# ---------------------------------------------------------------- mumlar

def _kline_df(satirlar) -> pd.DataFrame:
    df = pd.DataFrame(satirlar, columns=KLINE_SUTUNLARI)
    if df.empty:
        return df
    for c in KLINE_SUTUNLARI:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # data.binance.vision spot dosyaları 2025'ten beri mikrosaniye kullanıyor
    for c in ("open_time", "close_time"):
        mikro = df[c] > 1e14
        df.loc[mikro, c] = df.loc[mikro, c] // 1000
        df[c] = df[c].astype("int64")
    df.index = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df.index.name = "zaman"
    return df.drop(columns=["ignore"])


def _vision_zip(url: str) -> pd.DataFrame | None:
    r = _get(url)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        ad = z.namelist()[0]
        ham = pd.read_csv(z.open(ad), header=None)
    # vadeli dosyalarında başlık satırı olabilir
    if not str(ham.iloc[0, 0]).lstrip("-").isdigit():
        ham = ham.iloc[1:]
    ham = ham.iloc[:, :12]
    ham.columns = KLINE_SUTUNLARI
    return _kline_df(ham.values.tolist())


def _rest_klines(sembol: str, aralik: str, bas_ms: int, son_ms: int, piyasa: str) -> pd.DataFrame:
    if piyasa == "spot":
        url, limit = f"{SPOT_REST}/api/v3/klines", 1000
    else:
        url, limit = f"{VADELI_REST}/fapi/v1/klines", 1500
    parcalar, t = [], bas_ms
    while t < son_ms:
        veri = _get_json(url, {"symbol": sembol, "interval": aralik, "startTime": t,
                               "endTime": son_ms - 1, "limit": limit})
        if not veri:
            break
        parcalar.extend(veri)
        t = veri[-1][0] + ARALIK_MS[aralik]
        time.sleep(0.05)
    return _kline_df(parcalar)


def _vision_yolu(piyasa: str) -> str:
    return "spot" if piyasa == "spot" else "futures/um"


def _ay_onbellek(piyasa, sembol, aralik, ay: pd.Timestamp) -> Path:
    return VERI_DIZINI / "klines" / piyasa / aralik / sembol / f"{ay:%Y-%m}.parquet"


def _gun_onbellek(piyasa, sembol, aralik, gun: pd.Timestamp) -> Path:
    return VERI_DIZINI / "klines" / piyasa / aralik / sembol / "gunluk" / f"{gun:%Y-%m-%d}.parquet"


def _parquet_yaz(df: pd.DataFrame, yol: Path) -> None:
    """Atomik yazma: yarım kalmış önbellek dosyası oluşmaz."""
    yol.parent.mkdir(parents=True, exist_ok=True)
    gecici = yol.with_suffix(".tmp")
    df.to_parquet(gecici)
    gecici.replace(yol)


def _ay_getir(piyasa, sembol, aralik, ay: pd.Timestamp) -> pd.DataFrame:
    yol = _ay_onbellek(piyasa, sembol, aralik, ay)
    if yol.exists():
        return pd.read_parquet(yol)
    url = (f"{VISION}/{_vision_yolu(piyasa)}/monthly/klines/{sembol}/{aralik}/"
           f"{sembol}-{aralik}-{ay:%Y-%m}.zip")
    df = _vision_zip(url)
    if df is None:  # toplu dosya yoksa REST ile tamamla
        son = ay + pd.offsets.MonthBegin(1)
        df = _rest_klines(sembol, aralik, _ms(ay), _ms(son), piyasa)
    _parquet_yaz(df, yol)
    return df


def _gun_getir(piyasa, sembol, aralik, gun: pd.Timestamp) -> pd.DataFrame:
    yol = _gun_onbellek(piyasa, sembol, aralik, gun)
    if yol.exists():
        return pd.read_parquet(yol)
    url = (f"{VISION}/{_vision_yolu(piyasa)}/daily/klines/{sembol}/{aralik}/"
           f"{sembol}-{aralik}-{gun:%Y-%m-%d}.zip")
    df = _vision_zip(url)
    if df is None:
        df = _rest_klines(sembol, aralik, _ms(gun), _ms(gun + pd.Timedelta(days=1)), piyasa)
    _parquet_yaz(df, yol)
    return df


def mumlar(sembol: str, aralik: str, bas, son=None, piyasa: str = "spot") -> pd.DataFrame:
    """[bas, son) aralığındaki tamamlanmış mumlar. son verilmezse dünün sonu.

    Tam geçmiş aylar aylık dosyadan, içinde bulunulan ay günlük dosyalardan gelir.
    """
    bas = _utc(bas)
    son = min(son_tam_gun() if son is None else _utc(son), son_tam_gun())
    bu_ay = son.normalize().replace(day=1)
    parcalar = []
    ay = bas.normalize().replace(day=1)
    while ay < bu_ay:
        parcalar.append(_ay_getir(piyasa, sembol, aralik, ay))
        ay = ay + pd.offsets.MonthBegin(1)
    gun = max(bas.normalize(), bu_ay)
    while gun < son:
        parcalar.append(_gun_getir(piyasa, sembol, aralik, gun))
        gun += pd.Timedelta(days=1)
    parcalar = [p for p in parcalar if not p.empty]
    if not parcalar:
        return pd.DataFrame(columns=KLINE_SUTUNLARI[:-1])
    df = pd.concat(parcalar)
    df = df[~df.index.duplicated(keep="first")].sort_index()
    return df[(df.index >= bas) & (df.index < son)]


def ilk_mum_zamani(sembol: str, piyasa: str = "spot") -> pd.Timestamp | None:
    """Sembolün borsadaki ilk günlük mumunun açılış zamanı (geçmiş uzunluğu için)."""
    url = f"{SPOT_REST}/api/v3/klines" if piyasa == "spot" else f"{VADELI_REST}/fapi/v1/klines"
    r = _get(url, {"symbol": sembol, "interval": "1d", "startTime": 0, "limit": 1})
    if r.status_code != 200:
        return None
    veri = r.json()
    return pd.Timestamp(veri[0][0], unit="ms", tz="UTC") if veri else None


# ---------------------------------------------------------------- funding

def funding_gecmisi(sembol: str, yenile: bool = False) -> pd.DataFrame:
    """USDT-M funding oranı geçmişi. İndeks: fundingTime (UTC, ödemenin yapıldığı an).

    Ödeme anı = oranın kesinleştiği an; oran bu andan ÖNCE bilinmez kabul edilir
    (tahmini oran kullanılmaz). Bu nedenle sinyaller fundingTime'dan sonra kullanır.
    """
    yol = VERI_DIZINI / "funding" / f"{sembol}.parquet"
    eski = pd.read_parquet(yol) if yol.exists() else None
    if eski is not None and not yenile and time.time() - yol.stat().st_mtime < 6 * 3600:
        return eski
    # startTime=0 Binance'te "gönderilmedi" sayılır ve yalnız son 500 kayıt döner; 1 ile başla
    bas = 1 if eski is None or eski.empty else int(eski["fundingTime"].iloc[-1]) + 1
    satirlar = []
    while True:
        veri = _get_json(f"{VADELI_REST}/fapi/v1/fundingRate",
                         {"symbol": sembol, "startTime": bas, "limit": 1000})
        if not veri:
            break
        satirlar.extend(veri)
        if len(veri) < 1000:
            break
        bas = veri[-1]["fundingTime"] + 1
        time.sleep(0.2)
    yeni = pd.DataFrame(satirlar)
    if not yeni.empty:
        yeni["fundingTime"] = yeni["fundingTime"].astype("int64")
        yeni["fundingRate"] = yeni["fundingRate"].astype(float)
        if "markPrice" in yeni:
            yeni["markPrice"] = pd.to_numeric(yeni["markPrice"], errors="coerce")
        yeni.index = pd.to_datetime(yeni["fundingTime"], unit="ms", utc=True)
        yeni.index.name = "zaman"
    df = yeni if eski is None else pd.concat([eski, yeni])
    df = df[~df.index.duplicated(keep="last")].sort_index()
    _parquet_yaz(df, yol)
    return df


def funding_araligi_saat(df: pd.DataFrame) -> pd.Series:
    """Ardışık funding ödemeleri arasındaki süre (saat). 8 dışı aralıkları bulmak için."""
    return df.index.to_series().diff().dt.total_seconds() / 3600


# ---------------------------------------------------------------- spread

def anlik_spread(sembol: str, piyasa: str = "spot") -> dict:
    """Tek anlık en iyi alış/satış (bookTicker). Ortalama spread için tekrar örneklenir."""
    url = f"{SPOT_REST}/api/v3/ticker/bookTicker" if piyasa == "spot" \
        else f"{VADELI_REST}/fapi/v1/ticker/bookTicker"
    v = _get_json(url, {"symbol": sembol})
    bid, ask = float(v["bidPrice"]), float(v["askPrice"])
    orta = (bid + ask) / 2
    return {"zaman": pd.Timestamp.now(tz="UTC"), "bid": bid, "ask": ask,
            "yarim_spread": (ask - bid) / 2 / orta}


# ---------------------------------------------------------------- kalite ve hizalama

def kalite_kontrol(df: pd.DataFrame, aralik: str) -> dict:
    """Eksik mum, tekrar, sıralama, sıfır hacim ve OHLC tutarlılığı."""
    if df.empty:
        return {"mum": 0}
    adim = pd.Timedelta(milliseconds=ARALIK_MS[aralik])
    farklar = df.index.to_series().diff().dropna()
    bosluk = farklar[farklar > adim]
    beklenen = int((df.index[-1] - df.index[0]) / adim) + 1
    ohlc_hatali = ((df["high"] < df[["open", "close"]].max(axis=1)) |
                   (df["low"] > df[["open", "close"]].min(axis=1))).sum()
    return {
        "mum": len(df),
        "baslangic": df.index[0],
        "bitis": df.index[-1],
        "beklenen_mum": beklenen,
        "eksik_mum": beklenen - len(df),
        "bosluk_sayisi": len(bosluk),
        "en_uzun_bosluk": bosluk.max() if len(bosluk) else pd.Timedelta(0),
        "tekrar": int(df.index.duplicated().sum()),
        "sirali": bool(df.index.is_monotonic_increasing),
        "sifir_hacim_orani": float((df["volume"] == 0).mean()),
        "ohlc_hatali": int(ohlc_hatali),
    }


def log_getiri(df: pd.DataFrame, sutun: str = "close") -> pd.Series:
    return np.log(df[sutun]).diff()


def hizala(seriler: dict[str, pd.Series], yontem: str = "inner") -> pd.DataFrame:
    """Aynı zaman ızgarasına hizalar. Varsayılan: yalnız hepsinin olduğu mumlar."""
    return pd.concat(seriler, axis=1, join=yontem).sort_index()
