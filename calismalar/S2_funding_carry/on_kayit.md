# S2 Ön Kayıt: Funding Carry (cash-and-carry)

- Durum: **ONAYLANDI** (kullanıcı onayı 2026-10-17). Ölçüm bu commit'ten sonra başlar.
- Yazım tarihi: 2026-10-17 (UTC)
- Bu belge commit'lendikten sonra değiştirilmez. Değişiklik gerekirse aşağıya tarihli "Ek" olarak eklenir ve gerekçesi yazılır.

## 1. Hipotez

USDT-M perpetual'larda longlar çoğu zaman shortlara funding öder. Spotta coin alıp aynı miktarda vadelide short açan pozisyon, fiyat yönünden bağımsız olarak bu funding'i toplar ve maliyet sonrası USDT'de beklemekten (yıllık %4) daha iyi bir getiri/risk sunar.

**Ekonomik gerekçe:** Kaldıraçlı long talebi kaldıraç sağlayana prim öder (risk primi + hizmet ücreti), tahmin değildir.

**Sıfır hipotezi:** Ortalama funding sıfırdan büyük değildir; ya da büyüktür ama 4 bacak maliyeti ve sermayenin iki bacağa bölünmesi sonrası USDT getirisini geçmez.

**Ön beklentim:** BTC ve ETH'de uzun dönem ortalama pozitif ama rejime çok bağlı (yükseliş yıllarında yüksek, düşüş yıllarında sıfıra yakın). Sermaye üzerinden net getiri %4 civarında ya da altında olabilir; asıl soru V2 (eşikli) ve V3 (sepet) maliyete rağmen bunu iyileştiriyor mu.

## 2. Evren ve veri

- Evren: Bölüm 2.9'un 13 coini (`EVREN_KONTROLU.md`). PEPE vadelide `1000PEPEUSDT`: funding oranı ölçekten bağımsız, fiyat 1000'e bölünerek spotla eşlenir.
- **Funding:** `fapi/v1/fundingRate`, her coinin mevcut en uzun geçmişi (BTC 2019-09'dan). Oran, `fundingTime` anında kesinleşmiş kabul edilir; o andan önce kullanılmaz (tahmini/anlık oran kullanılmaz).
- **Funding aralığı:** Veriden doğrulanır (ardışık kayıt farkı). 8 saatten farklı aralıklar (4h, 1h) coin ve dönem bazında raporlanır. Yıllıklandırma aralıktan bağımsız yapılır: belli bir süredeki oranların **toplamı** × (365 / gün sayısı).
- **Fiyatlar:** Aynı dönemin spot ve vadeli 1h mumları. Basis = vadeli kapanış / spot kapanış − 1.
- **Hayatta kalma yanlılığı:** Ana evren bugünkü 13 coindir. V3 (sepet) için ek senaryo: listeden çıkmış LUNA(USDT, 2022-05), FTT(USDT, 2022-11) ve erişilebilirse diğer çıkarılmış USDT-M perpetual'ların funding ve fiyat geçmişi eklenerek V3 tekrarlanır. Veri bulunamazsa bu sınırlama sonuçta açıkça yazılır.
- Kalite kontrol: tekrar, boşluk, aşırı değerler (|oran| > %1 / dönem) listelenir, silinmez.

## 3. Maliyet varsayımları

Binance standart oranları 2026-10-17'de kontrol edildi (spot %0,10/%0,10; USDT-M maker/taker %0,02/%0,05). BNB indirimi yok. Ana senaryo taker.

| | Spot tek yön | Vadeli tek yön | 4 bacak (aç + kapa) |
|---|---|---|---|
| Büyük / Orta (kayma %0,03) | %0,13 | %0,08 | **%0,42** |
| Küçük (kayma = max(2·yarım spread, %0,05), S1 spread ölçümünden) | ≥ %0,15 | ≥ %0,10 | **≥ %0,50** |

- Ek senaryolar: maker (spot %0,10, vadeli %0,02, aynı kayma) ve 1,5x maliyet.
- **Risksiz getiri (karşılaştırma):** USDT'de bekleme, sabit **yıllık %4**.
- Vadeli marjdaki USDT ve spot bacağı ek faiz kazanmaz (muhafazakâr).

## 4. Aşama B: Ölçümler (strateji yok)

**B1. Funding dağılımı:** Coin bazında yıllıklandırılmış ortalama, medyan, pozitif dönem oranı. Tüm dönem + takvim yıllarına göre + rejime göre. Rejim tanımı (önceden sabit): BTC'nin takvim yılı getirisi > 0 ise "yükseliş yılı", değilse "düşüş yılı".

**B2. Kalıcılık:** Günlük toplam funding serisi f_d. `corr(f_d, f_{d+h})` ve `f_{d+1..d+h}` toplamının `f_d` üzerine regresyonu (HAC), h = 1, 3, 7 gün.

**B3. Basis:** 1h basis dağılımı (yüzdelikler), en geniş açıldığı 10 an ve o anlarda 1x / 2x short bacağın marj kullanım oranı.

**B4. Brüt getiri − maliyet:** 4 bacak maliyeti, varsayılan tutma süreleri **7, 30, 90 gün** için yıllıklandırılır (`maliyet × 365 / tutma`). Net yıllık = yıllık ortalama funding − yıllık maliyet. Notional üzerinden ve sermaye üzerinden (1x: sermayenin 1/2'si notional; 2x: 2/3'ü) ayrı.

**Anlamlılık testi (coin başına 1 test):** Günlük funding serisinin ortalaması > 0. Sıfır dağılımı: 30 günlük bloklar halinde rastgele işaret çevirme (block sign-flip), 1000 kez. BH ailesi: **13 test**, q = %10. B1 alt kırılımları (yıl, rejim) ve B2 tanımlayıcıdır, BH'ye girmez, kayıt defterine yazılır.

## 5. Kapı 1 kriterleri (coin bazında)

1. **İki yarı:** Günlük ortalama funding, coinin funding geçmişinin ilk ve ikinci yarısında pozitif ve küçüğü büyüğünün en az %50'si.
2. **Rastgele test:** Gözlenen ortalama, işaret çevirme dağılımının %95. yüzdeliğinin üstünde.
3. **Çoklu test:** BH (13 test, q = %10) sonrası anlamlı.
4. **Maliyet:** Yıllık ortalama funding (notional üzerinden) ≥ 2 × yıllıklandırılmış 4 bacak maliyeti, **30 günlük tutma** varsayımıyla. Büyük/Orta coinlerde eşik: 2 × %0,42 × 365/30 ≈ **yıllık %10,2**.

Kapı 1'i geçen coin yoksa S2 kapanır. V3 (sepet) en az 3 coin Kapı 1'i geçerse test edilir.

## 6. Aşama C: Strateji (yalnız Kapı 1 geçerse; parametreler burada sabit)

Ortak kurallar:
- Pozisyon: 1 birim sermaye. Spot long notional = vadeli short notional (delta nötr).
- **Kaldıraç:** Ana senaryo **1x** (sermayenin 1/2'si spot, 1/2'si vadeli marj). Ek senaryo 2x (2/3 spot, 1/3 marj).
- Karar 1h mum kapanışında, işlem sonraki 1h açılışında, iki bacak aynı mumun açılış fiyatıyla.
- Getiri = spot bacak değer değişimi + vadeli bacak değer değişimi + alınan/ödenen funding − tüm komisyon ve kayma.
- **Likidasyon:** İzole marj, bakım marjı oranı %1 (muhafazakâr sabit). 1h high ile short bacağın marj oranı izlenir; likidasyon fiyatına değerse marj kaybedilir, spot bacak sonraki açılışta satılır.
- **Yeniden dengeleme:** Ayda bir (ayın ilk günü 00:00 UTC) bacaklar hedef orana geri çekilir; aktarılan tutar iki bacak maliyetiyle hesaplanır.

Varyasyonlar:
- **V1, sürekli:** Coinin funding geçmişinin başından sonuna pozisyonda.
- **V2, eşikli:** Son 3 günlük (72 saat) funding toplamının yıllıklandırılmışı > **%10** ise aç, < **%3** ise kapat.
- **V3, sepet:** Her pazartesi 00:00 UTC (karar pazar 23:00 mumunun kapanışında), son 7 günlük funding toplamı en yüksek **3 coin**, eşit ağırlık. Bir coinin 7 günlük yıllıklandırılmış funding'i ≤ 0 ise o pay nakitte kalır. Değişen coinlerde 4 bacak maliyeti ödenir. Evren o tarihte vadelisi işlem gören coinler.
- **V4 (ek, kapı dışı):** V2'nin 2x kaldıraçlı hali. V1–V3 2x sonuçları da raporlanır, kapılar 1x'e göre değerlendirilir.

**Örnek içi / örnek dışı:**
- V1, V2: her coinin kendi funding geçmişinin ilk %70'i örnek içi, son %30'u örnek dışı.
- V3: 2020-01-01 – 2026-10-17 arası; ayrım tarihi **2024-10-03** (%70).
- Parametreler (eşikler, 3 coin, 7 gün) bu belgede sabit; örnek içinde seçim yapılmaz, örnek içi yalnız tanımlayıcıdır.

**Rastgele kıyas:** V2 ve V3 için aynı piyasada kalma oranına ve aynı segment uzunluklarına sahip 1000 rastgele pozisyon serisi (segment sırası karıştırılarak). V1 sürekli pozisyon olduğundan rastgele kıyası anlamsızdır; V1'in kıyası USDT %4'tür.

## 7. Kapı 2 kriterleri (S2'ye özel; Bölüm 5'in "profit factor yerine" kuralı)

Örnek dışı dönemde, 1x, taker:
1. Sermaye üzerinden **net yıllık getiri > %4** (USDT beklemesi).
2. **Sharpe ≥ 0,5** (günlük getiriden, risksiz oran düşülmeden; ayrıca %4 düşülmüş hali raporlanır).
3. **En kötü 30 günlük getiri ≥ −%5.**
4. Örnek dışı dönem **en az 12 ay**.
5. V2 ve V3'te rastgele pozisyon kıyasında **%95. yüzdeliğin** üstünde.
6. V1 ve V2'de coinlerin **en az %60'ında** pozitif net getiri.

## 8. Raporlanması zorunlu riskler

- Funding'in negatif olduğu en uzun kesintisiz dönem (coin bazında) ve o dönemde pozisyonun kaybı.
- Basis'in en geniş açıldığı an, marj kullanım oranı ve 2x'te likidasyona uzaklık.
- Likidasyon olayları (varsa) ve maliyeti.
- Borsa riski: tüm sermaye tek borsada (Binance). Sayıyla ölçülemez; raporda açıkça yazılır.

## 9. Bilinen sınırlamalar (ölçümden önce yazıldı)

- Spot ve vadeli bacaklar aynı mumun açılışında dolduruluyor varsayılır; gerçekte iki emir arasında kısa bir fiyat riski var. Kayma bunun bir kısmını karşılar.
- Portfolio margin / çapraz teminat (spotu marj olarak kullanma) modellenmez; bu sermaye verimini düşük gösterir (muhafazakâr).
- %1 bakım marjı ve aylık yeniden dengeleme basitleştirmedir.
- Funding verisi yalnız Binance; başka borsalardaki fırsatlar kapsam dışı.
