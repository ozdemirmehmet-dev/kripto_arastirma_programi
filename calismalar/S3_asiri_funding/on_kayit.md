# S3 Ön Kayıt: Aşırı Funding Sonrası Ters Hareket

- Durum: **ONAYLANDI** (kullanıcı onayı 2026-10-18, değişiklik yok). Ölçüm bu commit'ten sonra başlar.
- Yazım tarihi: 2026-10-18 (UTC)
- Bu belge commit'lendikten sonra değiştirilmez. Değişiklik gerekirse aşağıya tarihli "Ek" olarak eklenir ve gerekçesi yazılır.

## 1. Hipotez

Funding aşırı yüksekse piyasa long tarafında kalabalıktır ve kalabalık pozisyonlar sert bir düşüşle temizlenir (likidasyon zinciri). Aşırı negatif funding'de bunun tersi olur.

**Sıfır hipotezi:** Aşırı funding anlarından sonraki getiriler (BTC'nin genel hareketi çıkarıldıktan sonra) beklenen yönde değildir; ya da öyledir ama etki gidiş-dönüş maliyetin 2 katından küçüktür.

**Ön beklentim:** S2'de funding'in çok kalıcı olduğu ve aşırı değerlerin piyasa çapında kümelendiği görüldü (ör. 2022-11 FTX). Aşırı yüksek funding çoğunlukla güçlü yükseliş dönemlerinde oluyor. Bu yüzden kısa vadede ters hareketten çok momentum görülebilir. Bağımsız olay sayısı ve zaman kümelenmesi asıl zorluk olacak.

## 2. Evren ve veri

- Evren: 13 coin (Bölüm 2.9). Hayatta kalma için ek senaryo: LUNA ve FTT funding + vadeli fiyat geçmişi (S2'de indirildi), ayrıca raporlanır.
- Funding: S2'deki veri (commit `dd7cc8c` ile dondurulan önbellek), kesim 2026-10-17 00:00 UTC.
- Fiyat: USDT-M vadeli 1h (işlem piyasası) ve BTC vadeli 1h (beta ayarı için). Kontrol: spot 1h.
- S2 bu funding verisinin dağılımını ölçtü; funding'den sonraki **fiyat** hareketi henüz ölçülmedi.

## 3. Olay tanımı

- Her funding ödemesi anında (t = fundingTime), oranın **son 90 günün** ödemeleri içindeki yüzdelik sırası hesaplanır. Pencere t dahil, yalnız geçmiş veri kullanılır. İlk 90 gün olay üretmez.
- **Aşırı yüksek:** yüzdelik ≥ 95 **ve** oran > 0. **Aşırı düşük:** yüzdelik ≤ 5 **ve** oran < 0.
- **Bağımsız olay:** Aynı coinde ve aynı yönde bir olaydan sonraki 3 gün içinde gelen olaylar sayılmaz.
- **Zaman kümelenmesi:** Aynı takvim haftasında farklı coinlerde gelen olaylar ayrı sayılır, ama rastgele testte aynı bloğa konur (bkz. §5).
- Giriş zamanı: fundingTime'dan sonraki ilk 1h mumun açılışı.

## 4. Aşama B: Ölçümler (strateji yok)

1. Funding yüzdelik serisi ve olay sayıları (coin, yön, yıl bazında).
2. Olay sonrası h ∈ {1, 3, 7} günlük vadeli getiri `R_h = ln(open_{giriş+h} / open_{giriş})`.
3. **Beta ayarlı getiri** (altcoinler): `R_h − β · R_h^BTC`. β, son 90 günün günlük getirilerinden, olay anından önceki veriyle hesaplanır. BTC için ham getiri.
4. İşaretli getiri: aşırı yüksekte `y = −R` (beklenen düşüş), aşırı düşükte `y = +R`.
5. Karşılaştırma: olay olmayan funding anlarından sonraki ortalama işaretli getiri (aynı tanımla). Ayrıca yıl bazında.
6. Short tarafında funding'in alınması ve long tarafında ödenmesi ayrıca hesaplanır. Ana istatistik fiyat getirisidir; funding etkisi ek sütun olarak verilir.

**Ana testler (BH ailesi, q = %10):** 2 test: {aşırı yüksek, aşırı düşük} × havuzlanmış 13 coin × h = 3 gün × beta ayarlı işaretli getiri. Coin bazında ve h = 1, 7 sonuçları tanımlayıcıdır, BH'ye girmez, kayıt defterine yazılır.

## 5. Kapı 1 kriterleri (yön bazında: aşırı yüksek ve aşırı düşük ayrı)

1. **Olay sayısı:** En az **50 bağımsız olay** (Bölüm 6 ek kriteri).
2. **İki yarı:** Ortalama işaretli getiri, dönemin (2019-09 – 2026-10) zaman orta noktasından önce ve sonra pozitif. Küçüğü büyüğünün en az %50'si.
3. **Rastgele test:** Wild blok bootstrap, 9.999 tekrar. Blok = takvim haftası (ISO); aynı haftadaki tüm olaylar aynı işareti alır. Böylece piyasa çapındaki kümelenme korunur. Gözlenen ortalama %95. yüzdeliğin üstünde olmalı.
4. **Çoklu test:** BH (2 test) sonrası anlamlı.
5. **Maliyet:** Ortalama işaretli getiri ≥ 2 × vadeli gidiş-dönüş maliyet. Olayların coin grubu karışımına göre ağırlıklı: Büyük/Orta %0,32, Küçük %0,40.

## 6. Aşama C: Strateji (yalnız Kapı 1 geçerse; parametreler burada sabit)

- Aşırı yüksek funding → vadeli short. Aşırı düşük funding → vadeli long. Giriş: fundingTime'dan sonraki ilk 1h açılış.
- Çıkış: 3 gün sonra (72. saatin açılışı). Stop: girişten %10 aleyhte hareket (1h high/low ile, ortak motor kuralları).
- Funding: pozisyon süresince gerçek oranlar ödenir/alınır.
- Varyasyonlar (en fazla 5): **V1** eşik %95/%5, 3 gün, iki yön (ana) · **V2** eşik %90/%10 · **V3** 1 gün · **V4** 7 gün · **V5** yalnız short (aşırı yüksek).
- Örnek içi ilk %70, örnek dışı son %30 (takvim). Rastgele kıyas: aynı sayı, süre ve yön dağılımında 1.000 rastgele işlem.
- Kapı 2: genel kriterler (PF ≥ 1,2, ≥ 30 işlem, rastgeleye göre ≥ %95, coinlerin ≥ %60'ında pozitif).

## 7. Bilinen sınırlamalar (ölçümden önce yazıldı)

- Aşırı funding olayları piyasa çapında kümelenir. Etkin bağımsız olay sayısı 13 × olay sayısından çok daha az olabilir. Haftalık bloklu test bunu kısmen hesaba katar.
- Yalnız Binance funding'i. Diğer borsalardaki funding ve açık pozisyon verisi kullanılmıyor.
- Hayatta kalma yanlılığı: ana evren bugünkü coinler. LUNA/FTT ek senaryoda.
- %10 stop ve 3 günlük süre literatürden değil, programın Bölüm 6 önerisinden alındı; optimize edilmez.
