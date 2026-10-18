# S6 Ön Kayıt: Gün ve Saat Etkisi

- Durum: **ONAYLANDI** (kullanıcı onayı 2026-10-18, değişiklik yok). Ölçüm bu commit'ten sonra başlar.
- Yazım tarihi: 2026-10-18 (UTC)
- Bu belge commit'lendikten sonra değiştirilmez. Değişiklik gerekirse aşağıya tarihli "Ek" olarak eklenir ve gerekçesi yazılır.

## 1. Hipotez

Belirli saatlerde (örn. ABD borsalarının açılışı) ya da günlerde (hafta sonu, pazartesi) kripto getirileri sistematik olarak farklıdır.

**Sıfır hipotezi:** Her saat diliminin ve her haftanın gününün ortalama getirisi sıfırdır; ya da sıfırdan farklıdır ama yıllara göre tutarlı değildir ya da maliyeti karşılamaz.

**Ön beklentim:** 24 + 7 + 1 testte birkaç ham "anlamlı" sonuç tesadüfen çıkar. BH ve "her yılda aynı yön" kriterinden sonra hiçbirinin kalmaması en olası sonuç. Kalan olursa bile saatlik ortalama getiri (%0,01–0,05 düzeyi) tek başına işlem maliyetini karşılamaz. Programın öngördüğü gibi en fazla bir "filtre adayı" çıkar.

## 2. Veri

- BTC, ETH, SOL. Binance spot 1h, 2023-10-17 00:00 – 2026-10-17 00:00 UTC (3 yıl). S1'de indirildi, eksik mum 0.
- Saatlik getiri: `r = ln(close / open)`, aynı mum içinde.
- Günlük getiri (haftanın günü için): UTC gün başı açılıştan gün sonu kapanışa, `ln(close_23:00 / open_00:00)`.
- Not: Bu veri S1'de BTC–altcoin gecikmesi için kullanıldı; saat ve gün ortalamaları henüz ölçülmedi.
- Test yılları: Y1 = 2023-10-17 – 2024-10-16, Y2 = 2024-10-17 – 2025-10-16, Y3 = 2025-10-17 – 2026-10-16.

## 3. Aşama B: Ölçümler (strateji yok)

**B1. Saat dilimi (24):** Her UTC saati için saatlik getirinin ortalaması, medyanı, std'si ve gözlem sayısı.

**B2. Haftanın günü (7):** Her gün için günlük getirinin ortalaması, medyanı ve std'si.

**B3. ABD açılışı (yaz/kış saati düzeltmeli):**
- NYSE açılışı 09:30 New York saatidir. Bu an yaz saatinde (EDT) 13:30 UTC'ye, kış saatinde (EST) 14:30 UTC'ye denk gelir; geçişler `America/New_York` saat dilimi kurallarıyla hesaplanır.
- Olay mumu = açılışı içeren 1h mum (yaz 13:00, kış 14:00 UTC). Yalnız pazartesi–cuma; ABD tatilleri çıkarılmaz (sınırlama).
- Olay mumu getirisi bir test. Sonraki 1 saatin getirisi tanımlayıcı.

**Anlamlılık testi (her coin × her kalem):**
- H0: ortalama = 0, iki yönlü.
- Sıfır dağılımı: aynı ISO haftasındaki gözlemlerin aynı rastgele işareti aldığı haftalık blok işaret çevirme, 9.999 tekrar.
- p = P(|ortalama*| ≥ |gözlenen|). "Rastgele test %95" = |gözlenen|, |ortalama*| dağılımının %95. yüzdeliğinin üstünde.
- BH ailesi: 3 coin × (24 saat + 7 gün + 1 ABD açılışı) = **96 test**, q = %10.

## 4. Kapı 1 kriterleri (her coin × kalem)

1. **Her yılda aynı yön** (Bölüm 9 ek kriteri): ortalama Y1, Y2 ve Y3'ün üçünde de aynı işarette.
2. **İki yarı:** ilk ve ikinci 18 ayda aynı işaret. Küçüğü büyüğünün en az %50'si.
3. **Rastgele test:** iki yönlü %95.
4. **Çoklu test:** BH (96 test, q = %10) sonrası anlamlı.
5. **Maliyet (tek başına strateji olarak):** |ortalama| ≥ 2 × vadeli taker gidiş-dönüş = **%0,32**. Vadeli seçildi çünkü negatif etkiler için short gerekir.

**Filtre adayı:** 1–4'ü geçip 5'te kalan kalemler "filtre adayı" olarak raporlanır. Program Bölüm 9'a göre bir filtre ancak başka bir çalışmanın stratejisine Aşama C'de eklenebilir; o çalışmanın Kapı 2'yi geçmiş olması gerekir. Şu an S1–S4 Kapı 1'de kapandı; S5 sonuçlanmadı. Bu yüzden bir filtre adayı çıkarsa yalnız raporlanır. S5 Kapı 2'yi geçerse, kullanıcı onayıyla ve ayrı bir Ek'le S5'e eklenmesi değerlendirilir.

## 5. Aşama C (yalnız tek başına Kapı 1 geçen bir kalem varsa; sabit)

- Etki yönünde vadeli pozisyon: saat etkisinde ilgili saatin açılışında gir, kapanışında çık. Gün etkisinde ilgili UTC gününün açılışında gir, kapanışında çık.
- Örnek içi Y1 + Y2'nin ilk yarısı (%70 noktası), örnek dışı son %30. Rastgele kıyas: aynı sayıda rastgele saat/gün, 1.000 kez.
- Kapı 2: genel kriterler (PF ≥ 1,2, ≥ 30 işlem, rastgeleye göre ≥ %95). Coinlerin ≥ %60'ında pozitif olmalı, yani 3 coinin en az 2'sinde.

## 6. Bilinen sınırlamalar (ölçümden önce yazıldı)

- Yalnız 3 yıl ve 3 coin. Saat ortalamaları çok gürültülü; bir saat diliminde yılda ~365 gözlem var.
- Spot fiyatla ölçülüp maliyet vadeli üzerinden değerlendiriliyor. S1'e göre büyük coinlerde spot–vadeli farkı 1h'de ihmal edilebilir.
- ABD tatilleri ve yarım günler çıkarılmadı.
- 96 test yapılıyor. Program sonunda toplam test sayısıyla birlikte değerlendirilecek.
