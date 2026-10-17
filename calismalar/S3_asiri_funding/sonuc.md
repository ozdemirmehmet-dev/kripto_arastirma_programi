# S3 Sonuç: Aşırı Funding Sonrası Ters Hareket

**Hüküm: Aşırı funding sonrasında ters hareket yok. Aşırı yüksek funding'den sonra altcoinler BTC'ye göre ortalamada düşmüyor, yükselmeye devam ediyor; bu ortalamayı da birkaç büyük mani olayı taşıyor. Aşırı düşük funding'den sonra etki sıfır. S3 Kapı 1'de kapandı: 0/2.**

## 1. Ön kayıt ve hipotez

- Ön kayıt: commit `85e32a5` (2026-10-18, kullanıcı onaylı, değişiklik yok). Ek yok.
- Hipotez: Aşırı yüksek funding → kalabalık long → düşüş. Aşırı düşük funding → yükseliş.
- Ön beklenti (ölçümden önce yazıldı): "kısa vadede ters hareketten çok momentum görülebilir". **Doğrulandı.**
- Ön kayıtta açık kalan iki uygulama ayrıntısı, sonuçlar görülmeden önce kodda sabitlendi (`kod/asama_b.py` başlığı):
  - Yüzdelik sıra *katı* hesaplandı. Funding sık sık taban orana eşit kaldığı için eşitlikler aşırı sayılmadı.
  - Giriş mumu = fundingTime'ın saat başı + 1 saat.

## 2. Veri

- Funding: S2 verisi, 13 coin, kesim 2026-10-17. Ek senaryo: LUNA ve FTT.
- Fiyat: USDT-M vadeli 1h (ana), spot 1h (kontrol). β, olay gününden önceki 90 günün günlük getirilerinden hesaplandı.
- Olaylar (13 coin, bağımsızlaştırılmış):
  - Aşırı yüksek: **827 olay**, 154 farklı takvim haftasına yayılıyor.
  - Aşırı düşük: **1.591 olay**, 277 hafta.
  - Coin başına aşırı yüksek 24–131, aşırı düşük 83–159 olay.
- Maliyet eşiği (2 × vadeli taker gidiş-dönüş, olay karışımına göre ağırlıklı): aşırı yüksek %0,34, aşırı düşük %0,34.

## 3. Aşama B ölçümleri

İşaretli getiri y: aşırı yüksekte −R (hipotez yönü düşüş), aşırı düşükte +R. Pozitif y hipotezi destekler. Getiriler beta ayarlı; BTC'de ham.

**Havuz, vadeli, ana evren:**

| Yön | h | Olay | Ort. y | Ham ort. y | Pozisyonun aldığı funding | Wild yüzdelik | İlk / ikinci yarı |
|---|---|---|---|---|---|---|---|
| Aşırı yüksek | 1g | 827 | −%0,81 | −%0,77 | +%0,14 | %0,3 | −%1,26 / −%0,45 |
| Aşırı yüksek | **3g** | 827 | **−%1,90** | −%2,47 | +%0,35 | %0,0 | −%2,76 / −%1,22 |
| Aşırı yüksek | 7g | 827 | −%3,72 | −%5,27 | +%0,72 | %0,0 | −%5,43 / −%2,35 |
| Aşırı düşük | 1g | 1.594 | −%0,04 | −%0,02 | +%0,03 | %38 | −%0,02 / −%0,04 |
| Aşırı düşük | **3g** | 1.591 | **−%0,04** | +%0,11 | +%0,06 | %44 | +%0,10 / −%0,10 |
| Aşırı düşük | 7g | 1.588 | +%0,01 | +%0,27 | +%0,08 | %51 | +%0,30 / −%0,13 |

- Olay dışı funding anlarından sonra beta ayarlı getiri: 3 günde +%0,04. Olaylar bundan belirgin biçimde ayrışıyor, ama beklenen yönde değil.
- **Spot kontrolü aynı:** aşırı yüksek 3g −%1,94. **Delist dahil evren de aynı:** −%1,92.
- **Coin bazında (aşırı yüksek, 3g):** 13 coinin 13'ünde işaretli getiri negatif. En büyük: DOGE −%4,1, SOL −%4,2, NEAR −%4,1, AVAX −%3,8, ADA −%3,0. En küçük: BTC −%0,1, BNB −%0,3, ETH −%0,4.
- **Dağılım (aşırı yüksek, 3g, altcoin yönünde):**
  - Medyan yalnız +%0,14; olayların %51,5'i pozitif.
  - %5 ve %95 yüzdelikleri: −%11,4 / +%20,9.
  - En büyük %5'lik olay çıkarılınca ortalama +%1,90'dan **+%0,20'ye** iniyor. En büyük olay DOGE'de +%135.
  - Yıl bazında: 2021 +%5,1 (201 olay); diğer yıllar −%3,3 ile +%1,6 arası.

Ayrıntı: `results/kapi1.csv`, `results/ozet_tum.csv`, `results/coin_bazinda.csv`. Olay düzeyindeki ham tablo (`results/olaylar_ham.parquet`, 14 MB) git dışında; `asama_b.py --olc` ile yeniden üretilir.

## 4. Kapı durumu

| Yön | Olay ≥ 50 | İki yarı | Wild > %95 | BH | Maliyet | Kapı 1 |
|---|---|---|---|---|---|---|
| Aşırı yüksek | ✓ (827) | kaldı (ikisi de negatif) | kaldı (%0,0) | kaldı | kaldı (−%1,90 < %0,34) | **kaldı** |
| Aşırı düşük | ✓ (1.591) | kaldı | kaldı (%44) | kaldı | kaldı (−%0,04) | **kaldı** |

**S3 Kapı 1'de durdu: 0/2.** Aşama C yapılmadı.

## 5. Strateji sonuçları

Yok.

## 6. Sınırlamalar

- Olaylar piyasa çapında kümeleniyor. Haftalık bloklu wild bootstrap bunu hesaba katıyor; etkin bağımsız gözlem sayısı 154 hafta düzeyinde.
- Beta ayarlı getiri tek başına işlenebilir bir getiri değil; BTC hedge'i ek maliyet getirir. Kapı bunu gerektirmeden kaldığı için ayrıca hesaplanmadı.
- Yalnız Binance funding'i.
- Bu çalışmada **183 test/kırılım** kaydedildi.

## 7. Yan gözlem (fırsat değil)

Aşırı yüksek funding'den sonra altcoinin BTC'ye göre yükselmeye devam etmesi bir "mani devamı" etkisi gibi görünüyor. Ancak:

1. Hipotezin tersi ve **sonradan görüldü**. Bu yüzden kanıt değil, yalnız hipotez adayı.
2. Ortalama kalın kuyruktan geliyor: medyan +%0,14, en büyük %5 çıkarılınca +%0,2. Bu, maliyet eşiğinin (%0,34) ve long tarafın ödeyeceği funding'in (3 günde ~%0,35) altında.
3. Büyük ölçüde 2021'e bağlı.

Gerçekten test edilmek istenirse bu veri tekrar kullanılamaz. Bağımsız veri gerekir: başka borsaların (OKX, Bybit) funding geçmişi ya da ileriye dönük kâğıt üzerinde kayıt. Bu da yeni bir ön kayıt demek. Kalın kuyruk yapısı yüzünden ben önermiyorum.

## 8. Tek cümlelik hüküm

**Aşırı funding sonrası beklenen ters hareket yok; yüksek funding'i birkaç büyük yükselişin devamı izliyor ama tipik olay maliyeti karşılamıyor. S3'te fırsat yok.**

## Referans

- Kod: `calismalar/S3_asiri_funding/kod/asama_b.py`
- Sonuçlar: `calismalar/S3_asiri_funding/results/`
