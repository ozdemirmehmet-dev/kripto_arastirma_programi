# S5 Ön Kayıt: Oynaklık Hedefleme (al-tut üzerine pozisyon büyüklüğü katmanı)

- Durum: **ONAYLANDI** (kullanıcı onayı 2026-10-18, değişiklik yok). Ölçüm bu commit'ten sonra başlar.
- Yazım tarihi: 2026-10-18 (UTC)
- Bu belge commit'lendikten sonra değiştirilmez. Değişiklik gerekirse aşağıya tarihli "Ek" olarak eklenir ve gerekçesi yazılır.
- Kapsam: Program Bölüm 8'e göre S5, S4 Kapı 2'yi geçtiyse S4'ün en iyi varyasyonu üzerine de uygulanacaktı. S4 Kapı 1'de kapandığı için **yalnız BTC ve ETH al-tut** üzerine uygulanır.

## 1. Hipotez

Pozisyonu son dönemin oynaklığıyla ters orantılı büyütmek riski azaltır, getiriyi aynı oranda azaltmaz. Dalgalı dönemde küçültmek, sakin dönemde büyütmek demektir. Sonuçta al-tut'a göre Sharpe yükselir ve en büyük düşüş azalır.

**Ekonomik gerekçe:** Oynaklık kendini sürdürür, ama getiri oynaklıkla aynı oranda artmaz. Yüksek oynaklık dönemleri, alınan risk başına daha az getiri sunar.

**Sıfır hipotezi:** Oynaklıkla ölçeklenmiş pozisyonun al-tut'a göre alfası (risk ayarlı ek getirisi) sıfırdan büyük değildir; ya da büyüktür ama yeniden dengeleme maliyetinin 2 katından küçüktür.

**Ön beklentim:** Oynaklığın kalıcılığı kesin çıkar. Asıl soru, kriptoda yüksek oynaklık dönemlerinin daha düşük risk ayarlı getiri sunup sunmadığı. 2021 gibi hem oynak hem çok kârlı dönemler bunu bozabilir. Düşüşü azaltması muhtemel, Sharpe'ı artırması belirsiz.

## 2. Veri ve evren

- BTC ve ETH, Binance spot 1d, 2017-08-17 – 2026-10-16 (S4'te indirildi, eksik gün 0).
- Günlük getiri `r_t = ln(close_t / close_{t−1})`.
- Not: Bu veri S4'te trend sinyali için kullanıldı; oynaklık–getiri ilişkisi henüz ölçülmedi.

## 3. Katmanın tanımı (Bölüm 8'den, sabit)

- **Hedef yıllık oynaklık:** %40.
- **Oynaklık tahmini:** son 20 günün (V20) ya da son 60 günün (V60) günlük getiri standart sapması × √365. t günü dahil, yalnız geçmiş veri.
- **Ağırlık:** `w = min(1, %40 / tahmin)`. Kaldıraç yok; kalan kısım nakitte (USDT) ve getiri kazanmaz (muhafazakâr).
- **Yeniden dengeleme:** haftalık. Karar pazar kapanışında, işlem pazartesi açılışında. |yeni w − mevcut w| < 0,10 ise işlem yapılmaz.
- **Maliyet:** spot taker; işlem gören notional başına %0,13 tek yön (%0,10 komisyon + %0,03 kayma). Ek senaryolar: maker ve 1,5x.
- **Karşılaştırma:** aynı coinin al-tut'u (w = 1, tek giriş maliyeti).

## 4. Aşama B: Ölçümler (strateji öncesi, maliyetsiz)

Haftalık veri: pazartesi açılışından sonraki pazartesi açılışına getiri. Her coin ve tahmin penceresi (V20, V60) için:

**B1. Oynaklık kalıcılığı:** Haftalık tahmin, sonraki haftanın gerçekleşen oynaklığını (7 günlük getiri std × √365) ne kadar açıklıyor? Korelasyon, eğim ve R². Tanımlayıcı.

**B2. Rejime göre risk başına getiri:** Haftalar, o haftaki tahminin geçmişe dayalı (genişleyen pencere) beşte birlik dilimlerine ayrılır. Her dilimde sonraki haftanın ortalama getirisi, std'si ve oranları. Tanımlayıcı.

**B3. Ana ölçüm: oynaklık katmanının alfası (maliyetsiz).**
- Haftalık yönetilen getiri: `g_t = w_{t−1} · R_t`. R_t al-tut haftalık getirisi, w_{t−1} hafta başındaki ağırlık; maliyetsiz ve 0,10 eşiksiz.
- Regresyon: `g_t = α + b · R_t + ε`.
- **Ana istatistik:** α (yıllıklandırılmış). α > 0 ise katman al-tut'a göre risk ayarlı ek getiri sağlıyor.

**Anlamlılık testi:** (g_t, R_t) haftalık çiftleri 12 haftalık hareketli bloklarla 9.999 kez bootstrap edilir. Her tekrarda α* hesaplanır.
- "Rastgele test %95" = α*'nın %5. yüzdeliği > 0.
- p = P(α* ≤ 0).
- BH ailesi: 2 coin × 2 pencere = **4 test**, q = %10.

## 5. Kapı 1 kriterleri (coin × pencere bazında)

1. **İki yarı:** α, verinin ilk ve ikinci yarısında pozitif. Küçüğü büyüğünün en az %50'si.
2. **Bootstrap:** α*'nın %5. yüzdeliği > 0.
3. **Çoklu test:** BH (4 test, q = %10) sonrası anlamlı.
4. **Maliyet:** Yıllık α ≥ 2 × yıllık yeniden dengeleme maliyeti. Bu maliyet, B3'teki ağırlık serisinin 0,10 eşiği uygulanmış haliyle hesaplanan ortalama yıllık devir × %0,13'tür.

Aşama C'ye geçiş: en az bir pencerede BTC **ve** ETH'nin ikisi de Kapı 1'i geçmeli.

## 6. Aşama C: Strateji (yalnız Kapı 1 geçerse; parametreler burada sabit)

- §3'teki katman maliyetlerle birlikte, ortak motorla (`ortak/backtest.pozisyon_backtest`) çalıştırılır. Ağırlık serisi hedef ağırlık olarak verilir.
- Örnek içi ilk %70, örnek dışı son %30 (takvim, coin bazında). Parametre seçimi yok.
- Raporlanan metrikler (katmanlı ve katmansız yan yana, maliyet dahil): Sharpe, en büyük düşüş ve süresi, en kötü ay, toplam ve yıllık getiri, ortalama ağırlık, yıllık devir.
- Rastgele kıyas: stratejinin haftalık ağırlık serisi 12 haftalık bloklar halinde 1.000 kez karıştırılır. Ağırlık dağılımı ve ortalama piyasada kalma korunur, zamanlama bozulur.

## 7. Kapı 2 kriterleri (S5'e özel)

Örnek dışı dönemde, maliyet dahil, taker:
1. **Sharpe(katmanlı) > Sharpe(al-tut)** **ve** **en büyük düşüş(katmanlı) ≤ en büyük düşüş(al-tut)**.
2. Örnek dışı dönem en az 12 ay.
3. Rastgele ağırlık kıyasında Sharpe %95. yüzdeliğin üstünde.
4. BTC ve ETH'nin ikisinde de kriter 1 sağlanıyor (2 coinin %60'ı = 2).

## 8. Bilinen sınırlamalar (ölçümden önce yazıldı)

- Yalnız iki coin; bağımsız oynaklık rejimi sayısı az.
- Nakitteki sermayeye faiz verilmiyor. Bu katmanlıyı dezavantajlı gösterir. Ek senaryo olarak nakde yıllık %4 verilmiş sonuç da raporlanır, ama kapı kararına girmez.
- %40 hedef ve 20/60 gün pencereleri programın önerisi; optimize edilmez.
- Katman, S4'ün başarısız trend sinyalleriyle birleştirilmez.
