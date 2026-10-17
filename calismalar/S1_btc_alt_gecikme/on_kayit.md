# S1 Ön Kayıt: BTC → Altcoin Gecikmesi (lead-lag)

- Durum: **ONAYLANDI** (kullanıcı onayı 2026-10-17). Ölçüm bu commit'ten sonra başlar.
- Yazım tarihi: 2026-10-17 (UTC)
- Bu belge commit'lendikten sonra değiştirilmez. Değişiklik gerekirse aşağıya tarihli "Ek" olarak eklenir ve gerekçesi yazılır.

## 1. Hipotez

BTC büyük bir hareket yaptığında altcoinler bu harekete gecikmeli tepki verir. Altcoin henüz yetişmemişken BTC yönünde işlem açılırsa maliyet sonrası kâr edilebilir.

**Sıfır hipotezi:** BTC'nin t mumundaki getirisi, altcoinin t+1 ve sonraki mumlardaki getirisini (altcoinin kendi geçmişi hesaba katıldıktan sonra) tahmin etmez; ya da tahmin eder ama etki gidiş-dönüş maliyetin 2 katından küçüktür.

**Ön beklentim (şüphe):** Büyük coinlerde gecikme birkaç saniye, 1m ve üstünde işlem fırsatı yok. Küçük coinlerde gecikme biraz daha uzun ama maliyet daha yüksek. En olası sonuç: Kapı 1'de durur.

## 2. Evren ve piyasa

- Referans: BTCUSDT. Altcoinler: ETH, SOL, XRP, BNB (Büyük); DOGE, ADA, AVAX, LINK (Orta); NEAR, ARB, INJ, PEPE (Küçük). Evren kontrolü: `EVREN_KONTROLU.md` (13 sembolün hepsi spot ve USDT-M'de TRADING; PEPE vadelide `1000PEPEUSDT`).
- **Ölçüm fiyatı:** Spot mumlar. 1s mum yalnız spotta var (data.binance.vision'da vadeli 1s yok, kontrol edildi).
- **Kontrol:** 1m ve 1h ölçümleri USDT-M vadeli mumlarla tekrarlanır. Spot ve vadeli sonuçları aynı yönde değilse bu raporlanır.
- **İşlem piyasası (Aşama C'ye gelinirse):** USDT-M perpetual. Gerekçe: BTC düşüşünde altcoin short gerekir, spotta short yok; vadeli komisyon daha düşük.

## 3. Veri

| Zaman dilimi | Dönem (UTC, yarı açık [bas, son)) | Amaç |
|---|---|---|
| 1s | 2026-10-03 – 2026-10-17 (14 gün) | Gecikmenin gerçek ölçeği |
| 1m | 2025-10-17 – 2026-10-17 (1 yıl) | Ana ölçüm |
| 5m, 15m | 2024-10-17 – 2026-10-17 (2 yıl) | |
| 1h | 2023-10-17 – 2026-10-17 (3 yıl) | Ana ölçüm (ALT/BTC oranı dahil) |

- ARB ve PEPE'nin geçmişi 3,4–3,6 yıl; 1h dönemi için yeterli.
- Kalite kontrol: `ortak/veri.kalite_kontrol` (eksik mum, tekrar, OHLC tutarlılığı). Eksik mumlar **doldurulmaz**; getiriler yalnız ardışık iki mumun ikisi de varsa hesaplanır. BTC ile altcoin iç birleşimle (inner join) hizalanır.
- **Spread ölçümü:** Aşama B başında 3 saat boyunca 10 saniyede bir, 13 sembolün spot ve vadeli `bookTicker`'ı örneklenir. Coin başına ortalama ve medyan yarım spread. Küçük grubun kayması = max(2 × ortalama yarım spread, %0,05).

## 4. Maliyet varsayımları

Binance standart oranları 2026-10-17'de kontrol edildi: spot maker/taker %0,10 / %0,10 (Binance resmi ücret sayfası); USDT-M maker/taker %0,02 / %0,05 (resmi futures ücret tablosu sayfadan okunamadı, ikincil kaynaklarla doğrulandı; varsayılan değerle aynı). BNB indirimi kullanılmaz.

| Grup | Tek yön (vadeli taker + kayma) | Gidiş-dönüş | Kapı 1 eşiği (2 × gidiş-dönüş) |
|---|---|---|---|
| Büyük / Orta | %0,05 + %0,03 = %0,08 | %0,16 | **%0,32** |
| Küçük | %0,05 + max(2·yarım spread, %0,05) | ≥ %0,20 | **≥ %0,40** (ölçülen spreadle kesinleşir) |

Spot taker senaryosu (gidiş-dönüş %0,26 büyük coinlerde) ek olarak raporlanır. Funding, sabit 3 mumluk (en fazla 1 saat) işlemlerde ihmal edilmez: tutma süresi bir funding anını kesiyorsa gerçek oran uygulanır.

## 5. Aşama B: Ölçümler (strateji yok)

Getiri: `r_t = ln(close_t / close_{t-1})`. Zaman dilimleri: 1s, 1m, 5m, 15m, 1h.

**B1. Eşzamanlı ilişki** (bilgi amaçlı, kapıya girmez): `corr(r_btc_t, r_alt_t)` ve OLS beta. Her coin × zaman dilimi.

**B2. Gecikmeli ilişki** (ana test):
- `corr(r_btc_t, r_alt_{t+k})`, k = 1, 2, 3, 5, 10.
- Regresyon: `r_alt_{t+1} = α + b1·r_btc_t + b2·r_alt_t + ε`, Newey-West HAC standart hata (gecikme = floor(4(n/100)^(2/9))).
- Ters yön: `corr(r_alt_t, r_btc_{t+1})` ve simetrik regresyon.
- **Anlamlılık testi = b1'in tek yönlü p değeri (H1: b1 > 0).** BH ailesi: 12 coin × 5 zaman dilimi = **60 test**, q = %10.

**B3. Olay bazlı** (1m, 5m, 15m, 1h):
- Olay: `|r_btc_t| > K · σ_t`, σ_t = son 500 mumun (t−499…t) getirisinin standart sapması. K = 2 (ana) ve K = 3 (ek).
- Aynı yönde art arda olay mumları: yalnız ilki olay sayılır (kümelenme). Ardından en az 10 mum olaysız geçmeden yeni olay yok.
- β_rolling: son 500 mumun (t−500…t−1, olay mumu hariç) OLS betası.
- Yetişme farkı: `gap_t = r_alt_t − β_rolling · r_btc_t`.
- **Ölçülen:** BTC yönüyle işaretli sonraki h mumun altcoin getirisi `s_h = sign(r_btc_t) · ln(close_alt_{t+h} / close_alt_t)`, h = 1, 3, 5, 10. Ayrıca işlemle aynı zamanlamayla: t+1 açılışından t+1+h açılışına (Kapı 1'deki maliyet kıyası bununla yapılır, çünkü işlem kapanışta değil sonraki açılışta olur).
- Olaylar işaretli `gap`'e göre beşe bölünür (`sign(r_btc)·gap`, en negatif = en çok geride kalan). En çok geride kalan beşte birlik ile diğerleri karşılaştırılır.
- **Anlamlılık testi:** K = 2, h = 3, açılıştan açılışa ortalama işaretli getiri > 0; olay tarihleri sabit tutulup altcoin getiri serisi 1 günlük bloklarla karıştırılarak (1000 kez) sıfır dağılımı. BH ailesi: 12 coin × 4 zaman dilimi = **48 test**. Diğer h ve K değerleri tanımlayıcıdır, BH'ye girmez ama kayıt defterine yazılır.

**B4. Gecikme ölçeği (1s):**
- `corr(r_btc_t, r_alt_{t+k})`, k = 0…120 saniye; en yüksek korelasyonun k'si.
- Büyük BTC hareketi (1s'de K = 3, 500 saniyelik σ) sonrası: altcoinin beklenen hareketi `β_rolling · r_btc` olarak alınır; kümülatif hareketin bu beklentinin %50'sine ve %90'ına ulaştığı medyan süre (saniye). Grup bazında grafik.

**B5. ALT/BTC oranında dengeye dönüş (1h):**
- `x_t = ln(alt_t / btc_t)`, z_t = 30 günlük (720 mum) rolling z-skoru (yalnız geçmiş pencere).
- `|z_t| > 2` olaylarından sonra 1, 6, 24 saatte z'nin değişimi (sıfıra doğru = pozitif). Kümelenme: aynı coinde 24 saat içinde tekrar eden olay tek sayılır.
- Yarı ömür: `Δz_t = a + b·z_{t−1}` (AR(1)).
- Bu ölçüm ayrı bir fikirdir (ortalamaya dönüş, BTC yönünde işlem değil). Kapı 1'e kendi başına girer: 12 test, ayrı BH ailesi.

## 6. Kapı 1 kriterleri

Bir coin × zaman dilimi kombinasyonu Kapı 1'i geçer, **ancak** aşağıdakilerin **hepsi** sağlanırsa:

1. **İki yarı tutarlılığı:** Ana istatistik (B2'de b1, B3'te K=2/h=3 ortalama işaretli getiri) verinin ilk ve ikinci yarısında aynı işarette ve küçüğü büyüğünün en az %50'si.
2. **Karıştırma testi:** Gözlenen değer karıştırma dağılımının %95. yüzdeliğinin üstünde.
3. **Çoklu test:** BH düzeltmesinden sonra q = %10'da anlamlı (B2: 60'lık aile; B3: 48'lik aile; B5: 12'lik aile).
4. **Maliyet:** B3'te açılıştan açılışa ortalama işaretli getiri (gap filtresi olmadan, h = 3) ≥ 2 × gidiş-dönüş maliyet (bölüm 4). B2 tek başına Kapı 1'i geçemez; B2 anlamlıysa maliyet kriteri B3 üzerinden değerlendirilir.
5. **Olay sayısı:** B3'te en az **200 olay** (kümelenme sonrası).

En az bir kombinasyon geçerse Aşama C'ye geçmek için kullanıcıdan onay istenir. Hiçbiri geçmezse S1 Kapı 1'de kapanır ve `sonuc.md` yazılır.

## 7. Ara rapor ve durma noktası

1s gecikme ölçümü (B4) ve 1m gecikmeli korelasyon (B2, 1m) bitince kullanıcıya kısa özet verilir. Gecikme birkaç saniyeyse ve 1m'de anlamlı ilişki yoksa, 5m/15m/1h'ye devam edilip edilmeyeceği sorulur.

## 8. Aşama C taslağı (yalnız Kapı 1 geçerse; parametreler burada sabitlenir)

- Giriş: B3 olayı (K = 2) **ve** altcoin `gap` en çok geride kalan beşte birde → t+1 açılışında BTC yönünde vadeli işlem.
- Beşte bir sınırı yalnız örnek içi veriden (ilk %70) hesaplanır ve örnek dışında sabit tutulur.
- Çıkış: 3 mum sonra açılışta (sabit süre). Stop: olay mumunun ters ucu (long için olay mumu low'u, short için high'ı; altcoinin kendi olay mumu).
- Varyasyonlar (en fazla 5, burada sabit): **V1** K=2, çıkış 3, gap filtresi açık (ana) · **V2** K=3, çıkış 3, gap açık · **V3** K=2, çıkış 1, gap açık · **V4** K=2, çıkış 5, gap açık · **V5** K=2, çıkış 3, gap kapalı.
- Örnek içi %70 / örnek dışı %30, örnek dışına tek bakış. Rastgele kıyas: aynı sayıda, aynı süre ve yön dağılımında 1000 rastgele işlem.
- Kapı 2: genel kriterler (Bölüm 2.2): örnek dışı PF ≥ 1,2, ≥ 30 işlem, rastgeleye göre ≥ %95, coinlerin ≥ %60'ında pozitif.

## 9. Bilinen sınırlamalar (ölçümden önce yazıldı)

- Spot fiyatla ölçüp vadelide işlem varsayımı: 1m ve 1h'de vadeli kontrolü yapılır, 1s'de yapılamaz.
- 1s mumlar son işlem fiyatıdır, orta fiyat değildir; spread içi zıplama (bid-ask bounce) küçük coinlerde sahte negatif otokorelasyon üretebilir. B4 yalnız gecikme ölçeği içindir, işlem kararı için kullanılmaz.
- Hayatta kalma yanlılığı: Bugün listede olan coinler kullanılıyor. S1 için etkisi sınırlı (ilişki ölçümü, coin seçimi sonuca bağlı değil), sonuçta yazılır.
- Kümelenme kuralları ve 500 mumluk pencere ölçümden önce seçildi; değiştirilmez.
