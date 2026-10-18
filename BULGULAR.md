# Bulgular ve Dersler: Kripto Fırsat Araştırma Programı

> **Bu belge ne için?** Yeni bir fikir araştırmadan önce buraya bakın. Neyin denendiği, hangi parametrelerle, hangi veriyle ve neden tutmadığı burada. Ayrıca hangi tuzaklara düşüldüğü ve bir fikri yeniden denemeye değmesi için neyin farklı olması gerektiği de yazıyor. Amaç aynı sonuca ikinci kez zaman harcamamak.
>
> Program tarihi: 2026-10-17 – 2026-10-18. Veri kesimi: 2026-10-17 00:00 UTC. Borsa: Binance. Ayrıntılar her çalışmanın `sonuc.md` dosyasında.

---

## 1. Tek bakışta

| # | Fikir | Ne denendi (kısaca) | Sonuç | Durduğu yer | En iyi sonuç / eşik |
|---|---|---|---|---|---|
| S1 | BTC → altcoin gecikmesi | 12 altcoin, 1s–1h, gecikmeli regresyon, büyük BTC hareketi sonrası olay çalışması, ALT/BTC oranında dengeye dönüş | **Fırsat yok** | Kapı 1 (maliyet) | En iyi 1h ETH: 17,5 bps / eşik 32 bps (%55) |
| S2 | Funding carry (spot long + vadeli short) | 13 coin, 2019-09'dan funding geçmişi, basis, marj riski | **Fırsat yok** | Kapı 1 (iki yarı) | Tüm dönem %11–14/yıl, ama son 12 ay en iyi %4,6/yıl brüt |
| S3 | Aşırı funding sonrası ters hareket | 13 coin, 90 günlük yüzdelik, %95/%5 uçları, 1/3/7 gün | **Fırsat yok; etki ters yönde** | Kapı 1 | Yüksek funding sonrası düşüş değil, +%1,9 yükseliş (medyan ~0) |
| S4 | Günlük trend takibi (zaman serisi momentumu) | 13 coin, 1d, N = 20/60/120, M = 5/20 | **Güvenilir fırsat yok** | Kapı 1 (BH, iki yarı) | D çoğunda pozitif ama 2021'e bağımlı; BH sonrası 0/78 |
| S5 | Oynaklık hedefleme | BTC ve ETH al-tut, hedef %40, 20/60 gün | **Fırsat yok** | Kapı 1 (anlamlılık) | Alfa %1–4/yıl, bootstrap alt sınırı −%6 ile −%8 |
| S6 | Gün / saat etkisi | BTC, ETH, SOL, 1h, 3 yıl, 24 saat + 7 gün + ABD açılışı | **Fırsat yok** | Kapı 1 (BH) | En iyi saat 21:00 UTC: %0,067 / eşik %0,32 |

**Toplam:** 0 fırsat, 1.931 kayıtlı test/kırılım, 313 ön kayıtlı ana test. Hiçbir çalışma strateji testine (Aşama C) ulaşmadı.

---

## 2. Önce bunu okuyun: genel dersler

1. **2020–2021 boğa piyasası sonuçları şişiriyor.** S2 (funding primi), S3 (yüksek funding sonrası yükseliş) ve S4 (trend sinyali) ağırlıkla 2021'den geliyor; sonraki yıllarda zayıf ya da yok. Yeni bir fikirde tüm dönem ortalamasına güvenmeyin. **Yıl bazında kırılım ve "iki yarı" kriteri şart.**
2. **Kısa zaman dilimlerinde etki gerçek, ama maliyet çok daha büyük.** S1'de 1 saniyelik gecikme kesin var, ama 1 dakikada etki maliyetin 1/20'si bile değil. S6'da saatlik ortalamalar maliyetin beşte biri. Vadeli taker gidiş-dönüş ~%0,16; Kapı 1 bunun 2 katını ister. **1m–1h ölçeğinde %0,3'ün üstünde ortalama hareket üretmeyen bir fikir, ölçmeye bile değmez.**
3. **Spot fiyatın mikro yapısı sahte etki üretir.** S1'de spot 1m'de güçlü görünen gecikme (PEPE, AVAX, LINK) vadelide kayboldu. Nedenleri: kaba tick ve vadeliden sonra güncellenen spot fiyat. **İşlem vadelide yapılacaksa ölçümü de vadelide yapın ya da en azından vadeli kontrolü koyun.**
4. **Ortalamayı kalın kuyruk taşıyabilir.** S3'te +%1,9'luk ortalamanın medyanı +%0,14'tü. En büyük %5'lik olay çıkarılınca +%0,2'ye indi. **Her olay çalışmasında medyanı, yüzdelikleri ve en büyük olaylar çıkarılmış ortalamayı raporlayın.**
5. **Çoklu test gerçek bir sorun.** S4'te 17, S6'da 14 ham "anlamlı" sonuç vardı. Kendi BH ailelerinde hiçbiri kalmadı. Ham p < 0,05 görünce heyecanlanmayın.
6. **Rastgele test tasarımı kritik.** Blok karıştırma testi, oynaklık kümelenmesini bozduğu için S1'de her yerde %100 verdi; işe yaramazdı. **Oynaklığı koruyan testler kullanın:** wild (blok) bootstrap, blok işaret çevirme ya da hareketli blok bootstrap. Bkz. §5.
7. **Sonradan görülen etki kanıt değildir.** S1 ve S3'teki yan gözlemler ancak yeni bir ön kayıt ve **bağımsız veriyle** test edilebilir. Aynı veriyle "doğrulama" yapılmaz (bkz. §6 veri kullanım haritası).

---

## 3. Çalışma bazında ayrıntılar

### S1: BTC → altcoin gecikmesi
- **Ayrıntı:** [sonuç](calismalar/S1_btc_alt_gecikme/sonuc.md), [ara rapor](calismalar/S1_btc_alt_gecikme/results/ara_rapor_1.md). Ön kayıt `6dff5d5`, Ek 1 `558f8b8`.
- **Denenen:**
  - **Coinler:** ETH, SOL, XRP, BNB, DOGE, ADA, AVAX, LINK, NEAR, ARB, INJ, PEPE.
  - **Veri:** 1s (14 gün), 1m (1 yıl), 5m ve 15m (2 yıl), 1h (3 yıl). Spot ana ölçüm, vadeli kontrol.
  - **B2:** `r_alt_{t+1} = α + b1·r_btc_t + b2·r_alt_t` (HAC).
  - **B3:** BTC 2σ/3σ olayı sonrası 1/3/5/10 mum, gap beşte birleri.
  - **B4:** 1s gecikme ölçeği.
  - **B5:** ALT/BTC z-skoru (720 saat), |z| > 2 sonrası 24 saat.
- **Bulunan:**
  - Gecikme **saniyeler** düzeyinde: korelasyon 1. saniyede 0,05–0,16'ya, 5. saniyede ~0,01'e iniyor. %90 yetişme Büyük coinlerde 1 sn, Küçüklerde 1–8 sn.
  - 1s'deki ilişki iki yönlü (alt → BTC de aynı büyüklükte).
  - B3 0/48: en iyisi 1h ETH, 17,5 bps (eşik 32). 1m'de 0,3–1,2 bps, 5m'de 1,4–3,4 bps.
  - 1h'deki pozitif ortalama gecikme değil, BTC momentumu: beta ile hedge edilince −5,8 bps.
  - B5 (oran dengeye dönüşü) 0/12: yarı ömür 5–7 gün, 24 saatlik getiri sıfırdan ayırt edilemiyor.
- **Neden olmadı:** Gecikme hızlı botlarca saniyeler içinde kapatılıyor. Dakika ve üstünde kalan etki maliyetin çok altında.
- **Yeniden denemeye değmesi için:** saniye altı veri ve maker emirlerle (komisyon ~0, spread yakalama) çalışan bir altyapı gerekir. Bu artık başka bir oyun: HFT/piyasa yapıcılığı. Dakika ölçeğinde **tekrar denemeyin.**

### S2: Funding carry
- **Ayrıntı:** [sonuç](calismalar/S2_funding_carry/sonuc.md). Ön kayıt `33bd974`.
- **Denenen:**
  - **Veri:** 13 coin, her coinin ilk funding gününden (BTC 2019-09) itibaren.
  - **Ölçümler:** yıllıklandırılmış ortalama, yıl ve rejim kırılımı, kalıcılık, basis, marj riski.
  - **Maliyet:** 4 bacak maliyetiyle net getiri; 7, 30 ve 90 günlük tutma varsayımları.
- **Bulunan:**
  - Tüm dönem ortalaması: BTC %11,5, ETH %13,7, XRP %14,4, LINK %13,6/yıl.
  - Yıl bazında: 2021'de %30–48; 2024'te ~%12–14; 2025'te %3,5–5.
  - Son 12 ayda en iyi coin LINK %4,6/yıl brüt. 1x'te sermaye üzerinden net getiri her coinde negatif.
  - Funding çok kalıcı: 1 günlük otokorelasyon ~0,8.
  - SOL, BNB ve INJ'de ortalama funding sıfıra yakın ya da negatif.
- **Neden olmadı:** Prim eridi. Sermayenin iki bacağa bölünmesi (1x'te getiri yarıya iner) ve 4 bacak maliyeti, kalan primi USDT'nin %4'ünün altına itiyor.
- **Ek risk bulgusu:** Aylık yeniden dengelemeyle izole 1x short bacak, mani aylarında likide oluyor (NEAR'da 11 ay, AVAX'ta 8, SOL'da 7). DOGE'de ay içi en kötü hareket +%1.796.
- **Yeniden denemeye değmesi için:**
  - Funding'in yeniden yükselmesi (yıllık %15+ düzeyi süreklileşirse), **ya da**
  - Fırsatçı bir V2 (yalnız funding > %10/yıl iken açık). Bu S2'de Kapı 1 nedeniyle test edilmedi. Yeni bir ön kayıt ve başka borsa verisiyle (OKX/Bybit) denenebilir.
  - Portfolio margin ile sermaye verimini artırmak da maliyet tablosunu değiştirir.

### S3: Aşırı funding sonrası ters hareket
- **Ayrıntı:** [sonuç](calismalar/S3_asiri_funding/sonuc.md). Ön kayıt `85e32a5`.
- **Denenen:**
  - **Olay tanımı:** funding'in son 90 gündeki katı yüzdeliği ≥ %95 (ve oran > 0) ya da ≤ %5 (ve oran < 0). Aynı coinde 3 gün içindeki tekrarlar tek olay.
  - **Ölçüm:** vadeli 1h, beta ayarlı 1/3/7 günlük getiri. 827 aşırı yüksek, 1.591 aşırı düşük olay.
- **Bulunan:**
  - **Ters hareket yok.** Aşırı yüksek funding'den sonra altcoinler BTC'ye göre yükseliyor: 3 günde +%1,9, 13 coinin 13'ünde aynı yön. Ama medyan +%0,14 ve sonuç 2021'e bağlı.
  - Aşırı düşük funding sonrası etki sıfır.
  - Spot kontrolü ve LUNA/FTT dahil evren aynı sonucu veriyor.
- **Neden olmadı:** Kalabalık long pozisyonlar kısa vadede temizlenmiyor; maniler sürüyor. "Kalabalık işlem → çöküş" sezgisi bu veride ortalamada geçerli değil.
- **Yeniden denemeye değmesi için:** "mani devamı" yönü (yüksek funding sonrası long) sonradan görüldü ve kalın kuyruklu. Long taraf ayrıca funding ödüyor (3 günde ~%0,35). **Önerilmez.** Denenecekse yalnız bağımsız veriyle (başka borsa ya da ileriye dönük kayıt) ve medyan bazlı bir kriterle.

### S4: Günlük trend takibi
- **Ayrıntı:** [sonuç](calismalar/S4_trend_takibi/sonuc.md). Ön kayıt `67c48cd`.
- **Denenen:**
  - **Veri:** 13 coin, spot 1d (BTC ve ETH 2017-08'den).
  - **Sinyal:** `sign(ln(close_t / close_{t−N}))`, N ∈ {20, 60, 120}.
  - **İleri getiri:** M ∈ {5, 20} gün, açılıştan açılışa.
  - **İstatistik:** D = ort(y | +) − ort(y | −). Test: 60 günlük blok bootstrap.
- **Bulunan:**
  - D, 78 kombinasyonun 67'sinde pozitif. M = 20'de medyan D %3,9 (maliyet eşiği %0,52).
  - Ham p < 0,05 olan 17 test var; BH sonrası 0.
  - M = 20'de ilk yarı medyan D %5,0, ikinci yarı %1,2.
  - Yıl bazında medyan D: 2021'de %13,7; diğer yıllar −%8,4 ile +%3,7 arası, işaret yıldan yıla değişiyor.
- **Neden olmadı:** Etki 2021'e bağımlı. 9 yıllık günlük veri, birbiriyle ilişkili 78 test için yeterli istatistiksel güç sağlamıyor. Bu "etki yok" değil, **"bu veriyle güvenilir biçimde ayırt edilemiyor"** demek.
- **Yeniden denemeye değmesi için:** Daha az test (tek önceden seçilmiş N/M) ve havuzlanmış bir test, ama **yeni veriyle** (örn. önümüzdeki 1–2 yılın ileriye dönük kaydı). Aynı 2017–2026 verisiyle parametre değiştirerek tekrar denemek veri madenciliği olur. **V1–V5 (kırılım, MA100 vb.) hiç test edilmedi**, çünkü Kapı 1 geçilmedi.

### S5: Oynaklık hedefleme
- **Ayrıntı:** [sonuç](calismalar/S5_oynaklik_hedefleme/sonuc.md). Ön kayıt `19b967a`.
- **Denenen:**
  - **Kapsam:** BTC ve ETH al-tut, haftalık yeniden dengeleme.
  - **Ağırlık:** w = min(1, %40 / σ_tahmin), σ_tahmin 20 ya da 60 günlük.
  - **İstatistik:** alfa = `g = α + b·R` regresyonunun sabiti.
- **Bulunan:**
  - Alfa yıllık %1,1–3,8, ama bootstrap %5 alt sınırı −%6 ile −%8 (BH p = 0,42).
  - Sharpe neredeyse değişmiyor (0,83 → 0,80; 0,70 → 0,72).
  - Oynaklık kalıcılığı orta düzeyde: haftalık korelasyon 0,34–0,44.
  - BTC'de en oynak dilim risk başına en iyi getiriyi verdi; hipotezin dayanağı tutmadı.
- **Neden olmadı:** Kriptoda yüksek oynaklık dönemleri (örn. 2021) aynı zamanda en kârlı dönemler. Katman yalnız ortalama pozisyonu (0,55–0,74) düşürüyor; aynı etki sabit bir pozisyon büyüklüğüyle de elde edilir.
- **Yeniden denemeye değmesi için:** Ancak başarılı bir sinyal stratejisinin üzerine bir risk katmanı olarak (program kuralı buydu). Al-tut üzerine **tekrar denemeyin.**

### S6: Gün / saat etkisi
- **Ayrıntı:** [sonuç](calismalar/S6_zaman_etkisi/sonuc.md). Ön kayıt `9f25bdd`.
- **Denenen:**
  - **Veri:** BTC, ETH, SOL; spot 1h; 2023-10 – 2026-10.
  - **Kalemler:** 24 saat dilimi, 7 gün, ABD açılışı (yaz/kış saati düzeltmeli).
  - **Test:** haftalık blok işaret çevirme, iki yönlü; BH 96 test.
- **Bulunan:**
  - Ham p < 0,05 olan 14 kalem; BH sonrası 0.
  - 21:00 UTC üç coinde de pozitif (ETH %0,067/saat), ama Y1'de yoğun.
  - ABD açılış saati hafif negatif, anlamlı değil.
  - Haftanın günü ortalamaları yıllar arasında işaret değiştiriyor.
- **Neden olmadı:** İstatistiksel olarak tesadüften ayırt edilemiyor; ekonomik olarak da maliyetin beşte biri.
- **Yeniden denemeye değmesi için:** Yalnız Kapı 2'yi geçmiş başka bir stratejiye zamanlama filtresi olarak. Bağımsız strateji olarak **tekrar denemeyin.**

---

## 4. Veri ve teknik tuzaklar (ikinci kez düşmeyin)

| Tuzak | Ne oldu | Çözüm (kodda var) |
|---|---|---|
| Binance `fundingRate` `startTime=0` | 0 "gönderilmedi" sayılıyor, yalnız **son 500 kayıt** dönüyor | `startTime=1` ile başla ve sayfala (`ortak/veri.funding_gecmisi`) |
| data.binance.vision spot zaman damgası | 2025'ten beri spot dosyaları **mikrosaniye** kullanıyor | `> 1e14` ise 1000'e böl (`ortak/veri._kline_df`) |
| Vadeli 1s mum | data.binance.vision'da **yok**; REST'te de `1s` geçersiz | 1s yalnız spotta |
| PEPE vadeli sembolü | `1000PEPEUSDT`, fiyat 1000 katlı | Spotla eşlerken 1000'e böl |
| Spot PEPE tick | 1 tick = fiyatın **%0,245'i**, yarım spread 12,8 bps | Spot PEPE ölçümleri ayrıklıktan bozulur; vadeli kullan. Maliyette piyasaya göre ayrı spread (`MaliyetModeli`, `(coin, piyasa)` anahtarı) |
| Spot ARB/ADA tick | Görece kaba (~%0,05) | Aynı uyarı |
| Funding aralığı | SOL'da 2022-11 FTX döneminde 4h ve 2h aralıklar; FTT'de de var | Yıllıklandırmayı oranların **toplamıyla** yap, ödeme sayısıyla değil |
| Funding eşitlikleri | Funding sık sık taban orana (%0,01) eşit kalıyor | Yüzdelikte **katı** karşılaştırma (`<`, `>`); aksi halde sakin dönemler "aşırı" görünür |
| fundingTime ms kayması | `08:00:00.003` gibi geliyor | Giriş = saat başı + 1 saat |
| Vadeli 1h boşlukları | SOL, XRP ve NEAR'da birer adet 3 günlük boşluk; spotta birkaç saatlik kesintiler | Tam ızgaraya yeniden indeksle, doldurma; eksik olayı at |
| Yarım yazılmış önbellek | İndirme süreci öldürülünce parquet yarım kalabiliyordu | Atomik yazma (`ortak/veri._parquet_yaz`) |
| Ağ kesintisi | DNS hatası indirmeyi düşürdü | `_get` bağlantı hatalarında yeniden dener |
| data.binance.vision hızı | Dosya başına birkaç saniye | Farklı dosya kümelerini paralel süreçlerle indir |
| Blok karıştırma testi | Oynaklık kümelenmesini bozuyor, her yerde %100 veriyor | Wild blok bootstrap / blok işaret çevirme |
| 1s'de β (Epps etkisi) | Eşzamansız işlem yüzünden β düşük tahmin ediliyor | 1m β ile kontrol |
| pandas 3 `concat` | DatetimeIndex sıralama uyarısı | `sort=True` açıkça yaz |

---

## 5. Hazır altyapı (yeni fikirde yeniden kullanın)

- `ortak/veri.py`: Binance spot/vadeli mumlar (data.binance.vision + REST, aylık/günlük önbellek), funding geçmişi, exchangeInfo, bookTicker spread, kalite kontrol, hizalama.
- `ortak/maliyet.py`: komisyon + kayma modeli. Küçük coinlerde ölçülen spread, piyasaya göre ayrı spread, 4 bacak carry maliyeti, 1,5x senaryo.
- `ortak/backtest.py`: kapanışta karar / sonraki açılışta dolum yapan pozisyon motoru (funding dahil, elle hesapla doğrulandı) ve olay işlem motoru (sabit süre + stop, boşluk kuralı).
- `ortak/istatistik.py`: Newey-West OLS, blok bootstrap, karıştırma testi, Benjamini-Hochberg, blok işaret çevirme, rastgele işlem ve pozisyon kıyası, yarı ömür, rolling z.
- `ortak/rapor.py`: Türkçe biçimli markdown tablo, grafik kaydı, kayıt defterine satır ekleme.
- `calismalar/S1_btc_alt_gecikme/kod/olcum.py`: wild blok bootstrap (regresyon ve ortalama), olay kümeleme, iki yarı kontrolü.
- `calismalar/S1_btc_alt_gecikme/kod/spread_olcumu.py`: 13 sembol spot ve vadeli spread örnekleyici.
- `tests/test_ortak.py`: 15 birim testi.

Ölçülmüş spread (2026-10-17, 3 saat): `calismalar/S1_btc_alt_gecikme/results/spread_ozet.csv`.

---

## 6. Veri kullanım haritası (hangi ilişki hangi veriyle görüldü)

Bir sonraki çalışma aynı veriyle aynı ilişkiye bakarsa örnek dışı test yapılmış sayılmaz.

| Veri | Dönem | Görülen ilişkiler |
|---|---|---|
| Spot + vadeli 1s / 1m | 2026-10-03 – 10-17 / 2025-10-17 – 2026-10-17 | BTC → alt gecikmesi (S1) |
| Spot 5m, 15m | 2024-10-17 – 2026-10-17 | BTC → alt gecikmesi (S1) |
| Spot + vadeli 1h | 2023-10-17 – 2026-10-17 | BTC → alt gecikmesi, BTC saatlik momentumu (yan gözlem), ALT/BTC oranı (S1); saat/gün etkisi (S6, BTC/ETH/SOL) |
| Spot + vadeli 1h | coin başı – 2026-10-17 (tümü) | Basis ve marj riski (S2), aşırı funding sonrası getiri (S3). **BTC'nin büyük saatlik hareket sonrası devamı yalnız 2023-10 sonrasında görüldü.** |
| Funding | 2019-09 – 2026-10-17 (tümü) | Dağılım, kalıcılık (S2); aşırı uçlar sonrası fiyat (S3) |
| Spot 1d | 2017-08 – 2026-10-16 (tümü) | Trend işareti (S4), oynaklık–getiri (S5) |

**Temiz kalan veri:** 2026-10-17 sonrası her şey (ileriye dönük kayıt); başka borsaların (OKX, Bybit vb.) verisi; 2019-09 – 2023-10 arası 1h veride BTC'nin büyük hareket sonrası saatlik devamı.

---

## 7. Hipotez adayları (kanıt değil)

| Aday | Kaynak | Gözlem | Durum |
|---|---|---|---|
| BTC'de büyük (3σ) saatlik hareket sonrası kısa devam | S1 §7 | Sonraki 3 saatte +19 bps (310 olay); ilk yarı 26, ikinci yarı 12 bps | Sonradan görüldü. Test için 2019-09 – 2023-10 1h verisi temiz. S4'ün (trend) alanına yakın. |
| Yüksek funding sonrası altcoin "mani devamı" | S3 §7 | 3 günde +%1,9, ama medyan +%0,14; en büyük %5 çıkarılınca +%0,2 | Kalın kuyruk ve 2021 bağımlı. Önerilmez. |
| Fırsatçı funding carry (yalnız yüksek funding'de) | S2 §7 | Funding çok kalıcı; zaman zaman %30+/yıl | S2'de test edilmedi. Başka borsa verisi ve yeni ön kayıt gerekir. |

---

## 8. Yeni fikir için hızlı eleme listesi

Ön kayıt yazmadan önce:

1. **Buradaki tabloda var mı?** Aynı fikir ya da yakın bir türevi (§1, §3) denendiyse, "yeniden denemeye değmesi için" maddesi sağlanıyor mu?
2. **Beklenen hareket maliyetin 2 katını geçer mi?** Vadeli taker gidiş-dönüş Büyük/Orta %0,16, Küçük %0,20; spot %0,26–0,31, PEPE spot %0,71. Kapı 1 bunun 2 katını ister.
3. **Ekonomik neden var mı?** Kim, neden sistematik olarak para kaybediyor ya da prim ödüyor?
4. **Etki 2021 olmadan da var mı?** Yıl bazında kırılım planlayın.
5. **Hangi piyasada işlem?** Ölçümü o piyasada yapın; spot mikro yapısına dikkat.
6. **Rastgele test oynaklığı koruyor mu?** (§2 madde 6)
7. **Kaç test yapılacak?** BH ailesini küçük tutun; önceden tek bir ana test seçin.
8. **Veri temiz mi?** §6'ya bakın; görülmüş veriyle "doğrulama" yapılmaz.
9. **Ortalama yanında medyan ve kuyruk çıkarılmış ortalama** raporlanacak mı?

---

## 9. Maliyet referansı (2026-10-17)

| | Komisyon (taker / maker) | Kayma (tek yön) |
|---|---|---|
| Spot | %0,10 / %0,10 (BNB'siz) | Büyük/Orta %0,03; Küçük max(2 × yarım spread, %0,05); spot PEPE %0,255 |
| USDT-M vadeli | %0,05 / %0,02 | Büyük/Orta %0,03; Küçük %0,05 (taban bağlayıcı) |

Funding carry 4 bacak: Büyük/Orta %0,42, NEAR/INJ %0,50, ARB %0,51, PEPE %0,91.

---

> Eğitim ve araştırma amaçlıdır, yatırım tavsiyesi değildir.
