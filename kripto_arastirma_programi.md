# Kripto Fırsat Araştırma Programı

Sen bu projede bir **kantitatif araştırmacısın**. Görevin, aşağıdaki fikirlerin her birinde işlem maliyetlerinden sonra da yaşayan, tekrarlanabilir bir avantaj (fırsat) olup olmadığını **tarafsız şekilde** ölçmek.

**Bu proje yalnızca araştırma projesidir.**
- Mevcut çalışan bot ayrı bir projede çalışmaya devam ediyor. Ona, onun koduna ve onun planına **dokunma**.
- Gerçek emir gönderme, API anahtarı isteme, canlı hesaba bağlanma **YOK**.
- Bir fırsat bulunursa çıktı bir **"Fırsat Kartı"** olur (Bölüm 11). Kullanıcı bu kartı bot projesine kendisi taşır.

Bir fikrin "fırsat yok" sonucuyla kapanması da başarılı bir sonuçtur. Amaç fırsat bulmak değil, **doğruyu bulmaktır**. Sonuçları güzelleştirme, olumsuz sonucu saklama.

---

## 0. Önceki çalışmadan dersler (bunları tekrar yaşama)

Bu programdan önce bir YouTube stratejisi (UT Bot + RSI Bands + WaveTrend, 5m–4h) test edildi ve **avantaj bulunamadı**. Öğrenilenler:

1. **Kısa zaman dilimlerinde maliyet her şeyi yutar.** 5m'de stop girişe ~%0,2 uzaktaydı, gidiş-dönüş maliyet ~%0,26'ydı. Maliyet riskin kendisi kadar büyüktü.
2. **Sadece fiyattan türetilen göstergeler birbirinin bağımsız teyidi değildir.** Hepsi aynı geçmiş fiyattan hesaplanır.
3. **Heikin Ashi ve benzeri sentetik fiyatlarla yapılan backtest sonucu olduğundan iyi gösterir.** İşlemler daima gerçek fiyatlarla simüle edilir.
4. **Maliyetsiz sonuç sıfırsa, çıkış kuralıyla oynamak sonucu kurtarmaz.** Önce girişin avantajı ölçülmeli.
5. **Ön kayıt, örnek dışı test ve rastgele giriş kıyası** olmadan hiçbir sonuca güvenme.

Bu yüzden bu programda:
- **Önce ölçüm, sonra strateji.** Her çalışma, strateji kurulmadan önce "ham etki var mı ve maliyetten büyük mü?" sorusuyla başlar.
- **Tercihen fiyat dışı veri** (funding oranı, spot-vadeli farkı) ve **az işlem yapan** yaklaşımlar.
- Bir fikrin arkasında **ekonomik bir neden** olmalı: kimin, neden, sistematik olarak para kaybettiği ya da bir risk primi ödediği açıklanabilmeli.

---

## 1. Proje yapısı

```
kripto-arastirma/
├── README.md                    # programın özeti, çalışmaların durumu tablosu
├── KAYIT_DEFTERI.md             # yapılan HER testin listesi (çoklu test sayımı için)
├── ortak/
│   ├── veri.py                  # indirme, önbellek, hizalama, kalite kontrol
│   ├── maliyet.py               # komisyon, spread, kayma, funding modelleri
│   ├── backtest.py              # ortak motor (sinyal → gerçek fiyatla dolum)
│   ├── istatistik.py            # HAC, bootstrap, karıştırma, BH düzeltmesi
│   └── rapor.py                 # tablo ve grafik yardımcıları
├── data/                        # git DIŞINDA (.gitignore)
├── calismalar/
│   ├── S1_btc_alt_gecikme/
│   ├── S2_funding_carry/
│   ├── S3_asiri_funding/
│   ├── S4_trend_takibi/
│   ├── S5_oynaklik_hedefleme/
│   └── S6_zaman_etkisi/
│       ├── on_kayit.md          # ölçüm başlamadan ÖNCE yazılır ve commit'lenir
│       ├── kod/
│       ├── results/
│       └── sonuc.md             # Türkçe hüküm
└── firsat_kartlari/             # yalnız tüm kapıları geçen fikirler
```

Git ile çalış. Her ön kayıt, sonuç görülmeden önce ayrı bir commit olsun. Commit mesajında hangi çalışma ve hangi aşama olduğu yazsın.

---

## 2. Ortak yöntem (tüm çalışmalar için geçerli)

### 2.1 Aşamalar ve kapılar

Her çalışma aşağıdaki sırayla ilerler. Bir kapıyı geçemeyen çalışma orada durur ve `sonuc.md` yazılarak kapanır.

| Aşama | Ne yapılır | Kapı |
|---|---|---|
| **A. Ön kayıt** | Hipotez, veri, ölçümler, eşikler ve kapı kriterleri yazılır ve commit'lenir. | Yok |
| **B. Ölçüm** | Strateji yok. Ham etki ölçülür: var mı, ne kadar büyük, maliyetten büyük mü? | **Kapı 1** |
| **C. Strateji testi** | En basit işlem kuralı, en fazla 5 ön kayıtlı varyasyon. | **Kapı 2** |
| **D. Sağlamlık** | Farklı dönemler, coinler, maliyet senaryoları, parametre komşuları. | **Kapı 3** |
| **E. İleri test** | Kâğıt üzerinde canlı sinyal kaydı (en az 4 hafta). Yalnız sinyal kaydı, emir yok. | **Kapı 4** |
| **F. Fırsat Kartı** | Bölüm 11'deki şablonla teslim. | — |

Her kapıdan sonra kullanıcıya kısa bir ara rapor ver ve bir sonraki aşamaya geçmek için **onay al**.

### 2.2 Genel kapı kriterleri (çalışmaya özel kriterler bunlara eklenir)

**Kapı 1 (ölçüm):**
- Etki, verinin **iki yarısında da** aynı yönde ve benzer büyüklükte.
- Karıştırma/rastgele testinde **%95. yüzdeliğin** üstünde.
- Çoklu test düzeltmesinden sonra da anlamlı (Bölüm 2.6).
- Beklenen hareket ya da getiri, gidiş-dönüş **maliyetin en az 2 katı**.

**Kapı 2 (strateji):**
- Örnek dışı dönemde maliyet sonrası **profit factor ≥ 1,2** (ya da sürekli pozisyon stratejilerinde **Sharpe ≥ 0,5**).
- Örnek dışı dönemde **en az 30 işlem** (sürekli pozisyon stratejilerinde en az 12 aylık örnek dışı dönem).
- Rastgele giriş/pozisyon kıyasında **%95. yüzdeliğin** üstünde.
- Coinlerin **en az %60'ında** pozitif.

**Kapı 3 (sağlamlık):**
- Parametre komşularında (her parametre ±%25) sonuç işaret değiştirmiyor.
- Maliyetler **1,5 katına** çıkınca hâlâ pozitif.
- Walk-forward pencerelerinin **en az %60'ı** pozitif.
- En kötü düşüş ve en uzun düşüşte kalma süresi raporlanmış ve kullanıcıya açıkça gösterilmiş.

**Kapı 4 (ileri test):**
- En az 4 haftalık kâğıt üzerinde sinyal kaydının sonuçları, backtestin beklenen dağılımının içinde (alt %10'un altında değil).
- Sinyaller ile backtest motorunun aynı veride ürettiği sinyaller birebir eşleşiyor (kod tutarlılığı).

### 2.3 Zaman ve geleceği görme yasağı
- Tüm veriler UTC.
- Karar, mum **kapanışında** verilir. İşlem **bir sonraki mumun açılışında** gerçek fiyatla yapılır.
- Funding gibi periyodik veriler, **yayınlandığı andan sonra** kullanılabilir. Yayın zamanını veriden doğrula.
- Göstergelerde, ölçümlerde ve z-skorlarında yalnız geçmiş pencereler (rolling, expanding) kullanılır. Tüm veriden hesaplanan ortalama ya da standart sapma **yasak**.

### 2.4 Maliyet modeli (`ortak/maliyet.py`)

Varsayılan değerler aşağıda. Çalışma başında Binance'in güncel standart komisyon oranlarını kontrol et; farklıysa güncel olanı kullan ve ön kayda yaz.

| Kalem | Spot | Vadeli (USDT-M perpetual) |
|---|---|---|
| Taker komisyon | %0,10 | %0,05 |
| Maker komisyon | %0,10 (BNB'siz) | %0,02 |
| Kayma, büyük coinler | %0,03 | %0,03 |
| Kayma, küçük coinler | Ölçülen yarım spread × 2, en az %0,05 | Aynı |
| Funding | — | Gerçek geçmiş funding verisi |
| Kaldıraçlı long borç faizi | Modellenecekse ön kayda yaz | — |

**Ana senaryo taker'dır.** Maker yalnız ek senaryo olarak raporlanır, kapılar taker'a göre değerlendirilir.

### 2.5 Örnek dışı test ve walk-forward
- İlk **%70** örnek içi (parametre ve varyasyon seçimi), son **%30** örnek dışı (tek bakış).
- Örnek dışı veriye bakıldıktan sonra o çalışmada **parametre değiştirilemez**. Değişiklik gerekiyorsa bu yeni bir çalışmadır ve yeni, görülmemiş veri gerektirir.
- Walk-forward: 6 aylık test pencereleri, eğitim için önceki 12 ay (veri yetmiyorsa 6 ay; ön kayda yaz).

### 2.6 Çoklu test kontrolü
- `KAYIT_DEFTERI.md` dosyasına yapılan **her** test bir satır olarak eklenir: tarih, çalışma, varyasyon, coin, zaman dilimi, sonuç.
- Bir çalışmanın içindeki anlamlılık testlerine **Benjamini-Hochberg** düzeltmesi uygulanır (yanlış keşif oranı %10).
- Programın sonunda toplam test sayısı raporlanır. Çok test edilip az şey bulunduysa bulunanlar da şüpheyle karşılanır.

### 2.7 Rastgele kıyas
Her strateji, **aynı sayıda** ve **aynı süre dağılımına** sahip rastgele işlemlerle 1000 kez karşılaştırılır. Sürekli pozisyon stratejilerinde rastgele kıyas, aynı ortalama piyasada kalma oranına sahip rastgele pozisyon serileridir. Strateji, rastgele simülasyonların yüzde kaçından iyi olduğuyla raporlanır.

### 2.8 Hayatta kalma yanlılığı (survivorship bias)
Bugün listede olan coinlerle geçmişi test etmek, batan coinleri (LUNA, FTT vb.) dışarıda bırakır ve sonucu iyimser gösterir.
- Tek coinlik çalışmalarda: raporla ve geç.
- **Çok coinli çalışmalarda (özellikle S4 kesitsel momentum ve S3)**: mümkünse delist edilmiş coinlerin verisini de dahil et. Bulunamıyorsa bu sınırlamayı sonuçta açıkça yaz.

### 2.9 Coin evreni

| Grup | Coinler (USDT) | Not |
|---|---|---|
| Referans | BTC | |
| Büyük | ETH, SOL, XRP, BNB | Yüksek likidite |
| Orta | DOGE, ADA, AVAX, LINK | Yüksek beta |
| Küçük | NEAR, ARB, INJ, PEPE | Düşük likidite, yüksek maliyet |

Başlamadan önce her sembolün Binance spot ve USDT-M vadeli piyasada işlem gördüğünü ve geçmiş uzunluğunu kontrol et. Listeden çıkmış ya da adı değişmiş coinleri raporla. Yerine aynı gruptan bir coin ancak ön kayda yazılarak eklenebilir.

---

## 3. Çalışma sırası ve öncelik

| Sıra | Çalışma | Fikir sahibi | Neden bu sırada |
|---|---|---|---|
| 1 | **S1:** BTC → altcoin gecikmesi | Kullanıcı | Kullanıcının fikri; Aşama B çok hızlı, cevap ilk ölçümde netleşir. |
| 2 | **S2:** Funding carry | Claude | Tahmine dayanmayan, yapısal bir getiri kaynağı. Veri ücretsiz. |
| 3 | **S4:** Günlük trend takibi | Claude | Kriptoda en çok belgelenmiş etki; az işlem, düşük maliyet. |
| 4 | **S3:** Aşırı funding sonrası ters hareket | Claude | S2'nin verisini kullanır. |
| 5 | **S5:** Oynaklık hedefleme | Claude | Tek başına strateji değil; S4 ve al-tut üzerine eklenir. |
| 6 | **S6:** Gün/saat etkisi | Claude | En ucuz test; diğerleri için filtre adayı. |

S1 ve S2 paralel yürütülebilir. S5, S4'ün Aşama C'si bitmeden başlamaz.

---

## 4. S1: BTC → Altcoin Gecikmesi (lead-lag)

### Hipotez
BTC büyük bir hareket yaptığında altcoinler bu harekete **gecikmeli** tepki verir. Altcoin henüz yetişmemişken BTC yönünde işlem açılırsa maliyet sonrası kâr edilebilir.

### Ekonomik gerekçe ve şüphe
Altcoinlerin BTC ile birlikte ve daha sert hareket ettiği (yüksek beta) iyi bilinir. Ancak bu eşzamanlı ilişki kâr getirmez. Kâr için **gecikme** gerekir. Likit piyasalarda bu gecikme hızlı algoritmik botlar tarafından saniyeler içinde kapatılır. Beklenti: büyük coinlerde gecikme saniyeler düzeyinde, küçük coinlerde biraz daha uzun ama maliyet daha yüksek.

### Veri
| Zaman dilimi | Süre | Amaç |
|---|---|---|
| 1s (Binance saniyelik mum) | Son 14 gün | Gecikmenin gerçek ölçeği |
| 1m | 1 yıl | Ana ölçüm |
| 5m, 15m | 2 yıl | |
| 1h | 3 yıl | |

Ayrıca her coin için birkaç saatlik emir defteri ya da işlem verisinden ortalama spread ölç.

### Aşama B: Ölçümler
Getiri: `r_t = ln(close_t / close_{t-1})`

1. **Eşzamanlı ilişki:** `corr(r_btc_t, r_alt_t)` ve beta (`r_alt_t = α + β·r_btc_t`). Kullanıcının gözlemini doğrular, ama işlem fırsatı değildir.
2. **Gecikmeli ilişki:** `corr(r_btc_t, r_alt_{t+k})`, k = 1, 2, 3, 5, 10. Regresyon: `r_alt_{t+1} = α + b1·r_btc_t + b2·r_alt_t`, Newey-West standart hataları. **Ters yön** de ölçülür: `corr(r_alt_t, r_btc_{t+1})`.
3. **Olay bazlı:** "Büyük BTC hareketi" = mum getirisi > son 500 mumun standart sapmasının 2 katı (ayrıca 3 katı).
   - Yetişme farkı: `gap_t = r_alt_t − β_rolling · r_btc_t`
   - Sonraki 1, 3, 5, 10 mumdaki ortalama altcoin getirisi, BTC yönüne göre işaretli.
   - Olaylar `gap`'e göre beşe bölünür: en çok geride kalanlar yetişiyor mu?
4. **Gecikme ölçeği (1s):** 0–120 saniye arası hangi gecikmede korelasyon en yüksek? Büyük BTC hareketinden sonra altcoin, beklenen hareketin %50'sini ve %90'ını ortalama kaç saniyede tamamlıyor? Grup bazında grafik.
5. **Ek ölçüm, ALT/BTC oranında dengeye dönüş:** `ln(alt/btc)` oranının 30 günlük z-skoru (1h veri). z ±2'yi aştıktan sonraki 1, 6, 24 saatte oran sıfıra dönüyor mu? Yarı ömür (half-life).

### İlk ara rapor (Aşama B'nin ortasında)
1s gecikme ölçümü ve 1m gecikmeli korelasyon bitince kullanıcıya kısa özet ver. Gecikme birkaç saniyeyse ve 1m'de anlamlı ilişki yoksa, diğer zaman dilimlerine devam edilip edilmeyeceğini sor.

### Kapı 1 ek kriteri
- Olay bazlı ölçümde en az **200 olay**.

### Aşama C: Strateji (yalnız Kapı 1 geçerse)
Büyük BTC hareketi + altcoin `gap` en düşük beşte birlikte → bir sonraki açılışta BTC yönünde işlem. Sabit süre çıkışı (3 mum, önceden seçilmiş). Stop: olay mumunun ters ucu. Varyasyonlar: eşik 2σ/3σ, çıkış 1/3/5 mum, gap filtresi açık/kapalı (en fazla 5).

---

## 5. S2: Funding Carry (cash-and-carry)

### Hipotez
Perpetual vadelilerde long tarafı çoğu zaman kalabalıktır ve longlar shortlara funding öder. Spotta coin alıp aynı miktarda vadelide short açan bir pozisyon, fiyat yönünden bağımsız olarak bu funding'i toplar.

### Ekonomik gerekçe
Kaldıraçlı long talebi, kaldıraç sağlayan tarafa bir prim ödetir. Bu bir tahmin değil, bir **risk primi ve hizmet ücretidir**. Riskler: funding'in negatife dönmesi, borsa riski, spot-vadeli fiyat farkının (basis) geçici açılması, iki bacağın komisyonu.

### Veri
- Tüm coinler için Binance USDT-M **funding oranı geçmişi** (8 saatlik, varsa daha sık), en uzun mevcut süre.
- Aynı dönemin spot ve vadeli 1h fiyatları (basis hesabı için).
- Not: Bazı coinlerde funding aralığı 8 saatten farklı olabilir; veriden kontrol et.

### Aşama B: Ölçümler
1. Coin bazında yıllıklandırılmış ortalama funding, medyan, pozitif dönem oranı. Yıllara ve piyasa rejimlerine göre (yükseliş/düşüş yılı) ayrı.
2. Funding'in kalıcılığı: bugünkü funding, sonraki 1, 3, 7 günün funding'ini ne kadar tahmin ediyor? (otokorelasyon)
3. Basis (vadeli/spot − 1) dağılımı ve en geniş açıldığı anlar.
4. **Brüt getiri − maliyet:** Pozisyonu açma-kapama maliyeti (4 bacak: spot alış, vadeli satış, kapanışta tersleri) ortalama tutma süresine bölünerek yıllık maliyete çevrilir. Net yıllık getiri.

### Aşama C: Strateji varyasyonları
- **V1, sürekli:** Tüm süre boyunca pozisyonda kal.
- **V2, eşikli:** Son 3 günlük ortalama funding, yıllık %X'in üstündeyse aç, %Y'nin altına inince kapat. X ve Y ön kayıtta sabitlenir (örneğin %10 / %3).
- **V3, sepet:** Her hafta en yüksek funding'li 3 coinde pozisyon. Değişimde komisyon ödenir.
- Getiri spot bacağı ve vadeli bacağın toplam değer değişimi + funding − tüm maliyetler. Vadeli bacakta kaldıraç 1x–2x; likidasyon fiyatı ve marj ihtiyacı modellenir.

### Kapı 2 için özel ölçütler
Bu strateji bir "tahmin" stratejisi olmadığı için profit factor yerine **net yıllık getiri, Sharpe ve en kötü 30 günlük getiri** esas alınır. Karşılaştırma: aynı dönemde **USDT'de beklemek** (risksiz getiri, ön kayda yazılan sabit bir oranla, örneğin yıllık %4).

### Raporlanması zorunlu riskler
- Funding'in negatif olduğu en uzun dönem ve o dönemdeki kayıp.
- Basis'in en geniş açıldığı an ve bunun marj ihtiyacına etkisi.
- Borsa riski: tüm sermaye tek borsada; bu risk sayıyla ölçülemez, ama raporda açıkça yazılır.

---

## 6. S3: Aşırı Funding Sonrası Ters Hareket

### Hipotez
Funding aşırı yüksekse piyasa long tarafında kalabalıktır ve kalabalık pozisyonlar genellikle sert düşüşle temizlenir (likidasyon zinciri). Aşırı negatif funding'de tersi.

### Veri
S2'nin funding verisi + 1h ve 1d fiyatlar.

### Aşama B: Ölçümler
1. Her coin için funding'in **geçmişe dayalı** yüzdelik sırası (rolling 90 gün). Örneğin "son 90 günün en yüksek %5'i".
2. Aşırı yüksek ve aşırı düşük funding olaylarından sonraki 1, 3, 7 günlük getiri. Normal dönemlerin getirisiyle karşılaştır.
3. Aynı ölçüm BTC'nin piyasa yönüne göre ayrıştırılarak: genel piyasa hareketi çıkarılınca (altcoinlerde beta ayarlı getiri) etki kalıyor mu?
4. Olaylar birbirine yakın kümelenir. Bağımsız olay sayısını hesapla: aynı coinde 3 gün içinde tekrar eden olaylar tek olay sayılır.

### Kapı 1 ek kriteri
- En az **50 bağımsız olay**.

### Aşama C: Strateji
Aşırı yüksek funding → short (vadeli) ya da spotta pozisyondan çık. Aşırı düşük funding → long. Sabit süre çıkışı (3 gün) ve stop. Short tarafında funding ödemesi maliyete dahil (bu durumda short taraf funding **alır**). Varyasyonlar: eşik %5/%10, süre 1/3/7 gün, sadece long / sadece short / ikisi.

---

## 7. S4: Günlük Grafikte Trend Takibi (zaman serisi momentumu)

### Hipotez
Kriptoda başlamış trendler devam etme eğilimindedir. Basit kırılım ya da hareketli ortalama kuralları, al-tut'a göre daha iyi bir getiri/risk oranı sağlar; özellikle büyük düşüşlerden korur.

### Ekonomik gerekçe
Yatırımcıların yeni bilgiye geç tepki vermesi, sürü davranışı ve kaldıraçlı pozisyonların zincirleme kapanması. Kriptoda akademik literatürde en tutarlı bulunan etkilerden biri. Az işlem yaptığı için maliyet düşük. Zayıf yanı: yatay piyasalarda art arda küçük kayıplar.

### Veri
1d mumlar, mevcut en uzun süre (BTC ve ETH için 2017'den itibaren). Hayatta kalma yanlılığına dikkat (Bölüm 2.8).

### Aşama B: Ölçümler
1. Geçmiş N günlük getirinin işareti, sonraki M günlük getiriyi tahmin ediyor mu? N = 20, 60, 120. M = 5, 20. Tüm coinlerde, bootstrap güven aralığıyla.
2. Pozitif geçmiş getiri sonrası ve negatif geçmiş getiri sonrası ortalama getiri farkı.

### Aşama C: Strateji varyasyonları (her biri tek coinde, long-only ve long/short ayrı)
- **V1, kırılım:** 50 günlük en yüksek kırılınca al, 20 günlük en düşük kırılınca sat.
- **V2, hareketli ortalama:** Kapanış 100 günlük ortalamanın üstündeyse pozisyonda, altındaysa nakitte.
- **V3, momentum işareti:** Son 60 günlük getiri pozitifse pozisyonda.
- **V4, kesitsel momentum:** Her hafta, son 30 günde en çok yükselen 3 coini al (eşit ağırlık). Bu varyasyon için hayatta kalma yanlılığı kontrolü zorunlu.
- **V5, birleşik:** V1, V2 ve V3'ün oylaması (en az 2'si "pozisyonda" diyorsa).

### Kapı 2 için özel ölçütler
Sürekli pozisyon stratejisi olduğu için profit factor yerine şunlar esas alınır:
- Al-tut'a göre Sharpe oranı
- En büyük düşüş
- Al-tut ile korelasyon
- Piyasada kalma süresi

**Başarı tanımı ön kayıtta sabitlenir.** Önerilen: örnek dışı dönemde Sharpe al-tut'tan yüksek **ve** en büyük düşüş al-tut'un en fazla %70'i.

---

## 8. S5: Oynaklık Hedefleme (pozisyon büyüklüğü katmanı)

### Hipotez
Pozisyonu son dönemin oynaklığıyla ters orantılı büyütmek (dalgalı dönemde küçült, sakin dönemde büyüt), getiriyi pek değiştirmeden riski azaltır ve Sharpe'ı artırır.

### Ekonomik gerekçe
Oynaklık kendini sürdürür (bugün dalgalıysa yarın da dalgalı olma ihtimali yüksek), ama getiri oynaklıkla aynı oranda artmaz. Bu yüzden yüksek oynaklık dönemleri, alınan risk başına daha az getiri sunar.

### Uygulama
Tek başına strateji değil. İki şeyin üzerine eklenir:
1. BTC ve ETH al-tut
2. S4'ün en iyi varyasyonu (S4 Kapı 2'yi geçtiyse; geçmediyse sadece al-tut)

- Hedef yıllık oynaklık: %40 (ön kayıtta sabit).
- Oynaklık tahmini: son 20 ve 60 günlük günlük getiri standart sapması (iki varyasyon).
- Ağırlık: `hedef / tahmin`, en fazla 1x (kaldıraç yok).
- Yeniden dengeleme haftalık. Ağırlık değişimi %10'dan küçükse işlem yapılmaz (maliyeti azaltmak için).

### Ölçülecek
Sharpe, en büyük düşüş, en kötü ay, toplam getiri. Hepsi katmanlı ve katmansız versiyonla yan yana. Maliyet dahil.

---

## 9. S6: Gün ve Saat Etkisi

### Hipotez
Belirli saatlerde (örneğin ABD borsalarının açılış saatleri, 13:30–15:00 UTC) ya da günlerde (hafta sonu, pazartesi) getiriler sistematik olarak farklıdır.

### Veri
1h mumlar, 3 yıl; ana coinler (BTC, ETH, SOL).

### Aşama B: Ölçümler
1. Her saat dilimi (24) ve her gün (7) için ortalama getiri, medyan, oynaklık.
2. Tesadüf kontrolü: 24 + 7 test yapıldığı için Benjamini-Hochberg düzeltmesi **zorunlu**. Ayrıca yıllara göre: aynı saat her yıl mı öne çıkıyor?
3. ABD yaz/kış saati geçişleri hesaba katılarak "ABD açılışı" olay zamanı ayrıca ölçülür.

### Kapı 1 ek kriteri
- Etki, test edilen 3 yılın **her birinde** aynı yönde.

### Not
Bu çalışmanın en olası faydalı sonucu tek başına bir strateji değil, diğer stratejiler için **zamanlama filtresi** önerisidir. Kapı 1'i geçerse Aşama C, başka bir çalışmanın stratejisine filtre olarak eklenerek yapılır.

---

## 10. Raporlama

### Her çalışmanın `sonuc.md` dosyası
1. Ön kaydın commit numarası ve hipotez
2. Veri özeti: hangi coinler, hangi dönem, eksikler, çıkarılanlar
3. Aşama B ölçüm tabloları ve grafikleri
4. Hangi kapıda durdu, hangi kriterde ve neden
5. Varsa strateji sonuçları: örnek içi / örnek dışı / walk-forward / rastgele kıyas / maliyet senaryoları
6. Sınırlamalar
7. **Tek cümlelik Türkçe hüküm**

### Program özeti (`README.md`)
Her çalışma için bir satır:

| Çalışma | Durum | Ulaştığı kapı | Hüküm | Test sayısı |
|---|---|---|---|---|

Tüm çalışmalar bitince: toplam test sayısı, bulunan fırsat sayısı ve çoklu test açısından bu sonucun ne kadar güvenilir olduğu.

---

## 11. Fırsat Kartı (bot projesine teslim formatı)

Yalnız **4 kapının hepsini** geçen bir fikir için `firsat_kartlari/<ad>.md` olarak yazılır. Kullanıcı bu kartı bot projesine taşır. Kart, bot tarafındaki ekibin kodu okumadan stratejiyi birebir uygulayabileceği kadar açık olmalı.

```markdown
# Fırsat Kartı: <kısa ad>

## Özet
- Tek cümle: ne yapıyor, neden çalışıyor
- Çalışma: S?, ön kayıt commit: ...

## Kurallar (birebir)
- Piyasa / semboller / zaman dilimi
- Giriş koşulu (formüllerle)
- Çıkış koşulu
- Stop
- Pozisyon büyüklüğü
- Karar ve dolum zamanlaması (kapanışta karar, sonraki açılışta işlem vb.)

## Parametreler
| Parametre | Değer | Komşularda sonuç |

## Kanıtlar
| Dönem | Getiri | Sharpe | Max DD | İşlem | Kazanma | PF | Rastgeleye göre yüzdelik |
| Örnek içi | | | | | | | |
| Örnek dışı | | | | | | | |
| Walk-forward | | | | | | | |
| İleri test (kâğıt) | | | | | | | |

## Maliyet varsayımları ve hassasiyet
- Taker / maker / 1,5x maliyet sonuçları

## Bilinen zayıflıklar
- Hangi piyasa koşulunda kaybeder
- En kötü düşüş ve süresi
- Kapasite sınırı (hangi pozisyon büyüklüğünde kayma sonucu bozar)

## Bot için uygulama notları
- Gereken veri akışları
- Gereken hesap türü (spot / vadeli / ikisi)
- Canlıda izlenmesi gereken metrikler ve "durdur" koşulları
  (örneğin: canlı sonuçlar backtest dağılımının alt %5'ine düşerse dur)

## Referans
- Kod: calismalar/S?/kod/...
- Rapor: calismalar/S?/sonuc.md
```

---

## 12. Başlangıç adımları

1. Proje yapısını oluştur. `.gitignore`'a `data/` ekle. İlk commit.
2. `ortak/` modüllerini yaz. Maliyet modelini ve backtest motorunu basit bir testle doğrula: al-tut sonucu, elle hesaplanan değerle birebir eşleşmeli.
3. Coin evrenini kontrol et (Bölüm 2.9) ve sonucu kullanıcıya göster.
4. **S1 ve S2'nin ön kayıtlarını** yaz, kullanıcıya göster, onay al, commit'le.
5. S1 Aşama B'ye 1s ve 1m verisiyle başla. S2'nin funding verisini paralelde indir.
6. S1 ilk ara raporunu ver.

Her ara raporda kısa ve net ol: ne ölçüldü, ne bulundu, hangi kapıda, sıradaki adım ne. Olumsuz sonucu yumuşatma.

> Bu çalışma eğitim ve araştırma amaçlıdır, yatırım tavsiyesi değildir. Geçmiş performans gelecekteki sonuçların garantisi değildir.
