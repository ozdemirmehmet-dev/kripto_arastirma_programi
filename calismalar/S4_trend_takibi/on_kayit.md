# S4 Ön Kayıt: Günlük Grafikte Trend Takibi (zaman serisi momentumu)

- Durum: **ONAYLANDI** (kullanıcı onayı 2026-10-18, değişiklik yok). Ölçüm bu commit'ten sonra başlar.
- Yazım tarihi: 2026-10-18 (UTC)
- Bu belge commit'lendikten sonra değiştirilmez. Değişiklik gerekirse aşağıya tarihli "Ek" olarak eklenir ve gerekçesi yazılır.
- S1 ve S2'den taşınan dersler: (1) karıştırma/rastgele test, oynaklık kümelenmesini koruyacak şekilde tasarlanır; (2) "iki yarı" kriteri zamanla eriyen etkiyi yakalar ve korunur; (3) spot ile vadeli ayrı raporlanır.

## 1. Hipotez

Kriptoda başlamış trendler devam eder. Basit kırılım, hareketli ortalama ya da momentum işareti kuralları al-tut'a göre daha iyi bir getiri/risk sunar ve özellikle büyük düşüşlerden korur.

**Sıfır hipotezi:** Geçmiş N günlük getirinin işareti, sonraki M günlük getiriyi tahmin etmez; ya da tahmin eder ama fark gidiş-dönüş maliyetin 2 katından küçüktür.

**Ön beklentim:** Literatürde kriptoda zaman serisi momentumu en tutarlı etkilerden biri. Aşama B'de BTC ve ETH'de pozitif bir fark beklerim. Ama S2'de görüldüğü gibi etki 2020–2021'de yoğunlaşmış ve sonra zayıflamış olabilir; iki yarı kriteri kritik olacak.

## 2. Evren ve veri

- Evren: Bölüm 2.9'un 13 coini (`EVREN_KONTROLU.md`).
- Veri: Binance **spot 1d** mumlar, her coinin ilk günlük mumundan 2026-10-17 00:00 UTC'ye. BTC ve ETH 2017-08-17'den, ARB ve PEPE 2023'ten başlar.
- Long/short varyasyonları için USDT-M **vadeli 1d** mumlar ve funding geçmişi (S2'de indirildi). Short bacakta funding gerçek oranla hesaplanır.
- **Hayatta kalma yanlılığı (Bölüm 2.8, V4 için zorunlu):** V4 (kesitsel momentum) ana evrende ve ek bir "genişletilmiş evren"de çalıştırılır. Genişletilmiş evren = ana evren + data.binance.vision'da spot 1d verisi bulunan, listeden çıkmış şu USDT çiftleri: LUNA (2022-05'e kadar), FTT (2022-11'e kadar), ve erişilebilirse sonradan çıkarılan diğer büyük çiftler. Bir coin listeden çıktığı gün son kapanışından satılmış sayılır. Veri bulunamazsa sınırlama açıkça yazılır.
- Kalite kontrol: eksik gün, tekrar, OHLC tutarlılığı. Eksik günler doldurulmaz.

## 3. Maliyet

| | Tek yön | Gidiş-dönüş |
|---|---|---|
| Spot, Büyük/Orta (taker %0,10 + kayma %0,03) | %0,13 | %0,26 |
| Spot, Küçük (kayma = max(2 × S1'de ölçülen spot yarım spread, %0,05)) | %0,15 (PEPE %0,355) | %0,30 (PEPE %0,71) |
| Vadeli, Büyük/Orta (taker %0,05 + %0,03) | %0,08 | %0,16 |
| Vadeli, Küçük | %0,10 | %0,20 |

Ek senaryolar: maker ve 1,5x maliyet. Nakitte beklenen sermaye getiri kazanmaz (muhafazakâr). Karşılaştırma: al-tut (aynı coin, aynı dönem, aynı maliyet modeli).

## 4. Aşama B: Ölçümler (strateji yok)

Getiri: `r_t = ln(close_t / close_{t−1})`. Karar t kapanışında, sonraki dönem t+1 açılışından başlar.

**B1. İşaret → sonraki getiri:** Her coin, N ∈ {20, 60, 120} ve M ∈ {5, 20} için:
- Sinyal: `s_t = sign(ln(close_t / close_{t−N}))`.
- İleri getiri: `y_t = ln(open_{t+1+M} / open_{t+1})`.
- **Ana istatistik:** `D = ort(y | s = +1) − ort(y | s = −1)`.
- Ayrıca `ort(y | s = +1)` ve `ort(y | s = −1)` ayrı ayrı (B2).

**B2.** Pozitif geçmiş getiri sonrası ve negatif geçmiş getiri sonrası ortalama getiriler, yıl bazında da.

**Anlamlılık testi (her coin × N × M):** Hareketli blok bootstrap. (s_t, y_t) çiftleri 60 günlük bloklar halinde örneklenir, 9.999 tekrar. Örtüşen M günlük pencereler ve oynaklık kümelenmesi bloklar içinde korunur.
- Tek yönlü p = P(D* ≤ 0), merkezlenmemiş bootstrap dağılımında.
- "Rastgele test %95" kriteri = D*'nin %5. yüzdeliği > 0.
- BH ailesi: 13 coin × 3 N × 2 M = **78 test**, q = %10.

## 5. Kapı 1 kriterleri (coin × N × M bazında)

1. **İki yarı:** D, coinin verisinin ilk ve ikinci yarısında pozitif. Küçüğü büyüğünün en az %50'si.
2. **Bootstrap:** D*'nin %5. yüzdeliği > 0.
3. **Çoklu test:** BH (78 test, q = %10) sonrası anlamlı.
4. **Maliyet:** D ≥ 2 × spot gidiş-dönüş maliyet (Büyük/Orta %0,52, Küçük %0,60, PEPE %1,42). Gerekçe: bir sinyal değişimi en fazla bir gidiş-dönüş işlem doğurur.

**Aşama C'ye geçiş:** En az bir N değerinde, BTC ya da ETH dahil en az 3 coinde (M = 20 için) Kapı 1 geçilmeli. Tek coinde geçen bir etki çoklu test açısından zayıf sayılır.

## 6. Aşama C: Strateji (yalnız Kapı 1 geçerse; parametreler burada sabit)

Her varyasyon tek coinde çalışır. Long-only (spot) ve long/short (vadeli, funding dahil) ayrı raporlanır.
- **V1, kırılım:** Kapanış önceki 50 günün en yükseğini aşınca al; önceki 20 günün en düşüğünün altına inince sat (long/short'ta short'a geç).
- **V2, hareketli ortalama:** Kapanış 100 günlük basit ortalamanın üstündeyse pozisyonda, altındaysa nakitte (long/short'ta short).
- **V3, momentum işareti:** Son 60 günlük getiri pozitifse pozisyonda, değilse nakitte (short).
- **V4, kesitsel momentum:** Her pazartesi (karar pazar kapanışında), son 30 günde en çok yükselen 3 coin eşit ağırlıkla alınır. Yalnız long. Ana evren + genişletilmiş evren.
- **V5, birleşik:** V1, V2 ve V3'ten en az 2'si "pozisyonda" diyorsa pozisyonda.

Ortak kurallar:
- Karar kapanışta, işlem sonraki açılışta (ortak motor `ortak/backtest.pozisyon_backtest`).
- Tam pozisyon (ağırlık 1), kaldıraç yok.
- Örnek içi ilk %70, örnek dışı son %30 (coin bazında). V4'te ortak takvim, ayrım 2017-08-17 – 2026-10-17'nin %70 noktası.
- Walk-forward: 6 aylık test pencereleri, önceki 12 ay eğitim. Parametreler sabit; eğitim yalnız tanımlayıcı.
- Rastgele kıyas: aynı piyasada kalma oranı ve aynı segment uzunluklarıyla 1.000 rastgele pozisyon serisi.

## 7. Kapı 2 kriterleri (S4'e özel; Bölüm 7 "başarı tanımı ön kayıtta sabitlenir")

Örnek dışı dönemde, long-only, spot, taker:
1. **Sharpe > al-tut Sharpe'ı** **ve** **en büyük düşüş ≤ al-tut'un en büyük düşüşünün %70'i.**
2. Örnek dışı dönem en az 12 ay.
3. Rastgele pozisyon kıyasında %95. yüzdeliğin üstünde (metrik: Sharpe).
4. Coinlerin en az %60'ında kriter 1 sağlanıyor.

Ayrıca raporlanır: al-tut ile korelasyon, piyasada kalma süresi, işlem sayısı, toplam maliyet, maker ve 1,5x maliyet sonuçları.

## 8. Bilinen sınırlamalar (ölçümden önce yazıldı)

- Günlük veride 9 yıldan az geçmiş var; bağımsız trend dönemi sayısı az. Sonuçlar birkaç büyük boğa/ayı döngüsüne bağımlı olabilir.
- Hayatta kalma yanlılığı V1–V3, V5 için de var (bugünkü coinler); V4 için genişletilmiş evrenle kısmen giderilir.
- S1'in yan gözlemi (BTC'de büyük saatlik hareket sonrası devam) S4'ün kapsamı dışındadır. Burada yalnız günlük kurallar test edilir.
- Bu çalışmanın verisinin bir kısmı (2023-10 sonrası 1h, S1) ve funding (S2) daha önce görüldü. Günlük getiri–sinyal ilişkisi henüz ölçülmedi.
