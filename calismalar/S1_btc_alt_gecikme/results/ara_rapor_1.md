# S1 İlk Ara Rapor: 1s gecikme ölçeği ve 1m gecikmeli ilişki

- Tarih: 2026-10-17 (UTC). Ön kayıt commit: `6dff5d5`.
- Kapsam (ön kayıt §7): B4 (1s, spot), B1 + B2 (1s ve 1m, spot), 1m vadeli kontrolü. B3 (olay bazlı, maliyet kıyası) henüz yapılmadı.
- Veri: 1s 2026-10-03 – 10-17 (13 sembol × 1.209.600 mum), 1m 2025-10-17 – 2026-10-17 (spot ve vadeli, 13 × 525.600 mum). **Eksik mum: 0**, OHLC hatası: 0.
- Kayıt defteri: 72 satır (#1–#72; #37–#72 ön kayıt dışı ek).

## Kısa hüküm

**Gecikme saniyeler düzeyinde, 1 dakikada işlenebilir büyüklükte değil.** 1s'de BTC'den altcoine korelasyon 1. saniyede 0,05–0,16'ya, 5. saniyede ~0,01'e düşüyor. 1m'de vadelide istatistiksel olarak sıfırdan farklı bir ilişki birkaç coinde var. Ancak ekonomik büyüklüğü Kapı 1 maliyet eşiğinin **en iyi durumda ~1/20'si** (ADA, NEAR, ARB), çoğunda 1/50–1/300'ü. Spotta 1m'de görünen büyük etkiler (PEPE, AVAX, LINK) **vadelide kayboluyor**. Bunlar spot piyasasının mikro yapısından geliyor (kaba tick, vadeliye göre geç güncellenen spot fiyatı); işlenebilir bir fırsat değiller.

## B4: Gecikme ölçeği (1s, spot)

`corr(r_btc_t, r_alt_{t+k})`: Tüm coinlerde zirve k = 0'da. k = 1'de 0,02–0,16, k = 5'te ≤ 0,02, k = 30'da ~0.

BTC 3σ olayı (kümelenme sonrası 19.437 olay, 14 günde) sonrası altcoinin beklenen hareketi (β_1s · r_btc) tamamlama süresi:

| Grup | Medyan %50 süresi | Medyan %90 süresi | %90'a 120 sn'de ulaşmayan |
|---|---|---|---|
| Büyük (ETH, SOL, XRP, BNB) | 0–1 sn | 1 sn | %7–10 |
| Orta (DOGE, ADA, AVAX, LINK) | 0–3 sn | 1–4 sn | %8–12 |
| Küçük (NEAR, ARB, INJ) | 0–8 sn | 1–8 sn | %7–16 |
| PEPE (spot) | 40 sn | 40 sn | %36 |

- Toplu eğri (grafik: `b4_gecikme_olcegi_1s.png`) olay saniyesinde beklentinin %58–95'ine ulaşıyor. Sonraki ~10–20 saniyede beklentinin 1,2–2,1 katına çıkıyor. Bu fazla hareketin bir kısmı BTC'nin kendisinin aynı yönde devam etmesinden kaynaklanıyor. Bir kısmı da 1s'de β'nın düşük tahmin edilmesinden (Epps etkisi). Ek kontrol olarak ön kayıt dışında β 1m veriden alındı. Bu kontrolde %90 süresi Büyük/Orta için 2–4 sn, Küçük için 3–8 sn çıktı. Sonuç değişmiyor.
- PEPE'nin 40 sn'si gerçek bir gecikme değil. Spot PEPE'de 1 tick fiyatın **%0,245'i** (vadeli 1000PEPE'de %0,0025). Fiyat ancak bir tick'lik hareket birikince güncelleniyor.
- Ters yön de var: 1s'de `corr(r_alt_t, r_btc_{t+1})` 0,02–0,15, BTC → alt yönüyle aynı büyüklükte. 1s'deki "gecikme" büyük ölçüde iki yönlü ve eşzamansız işlem etkisi. Tek yönlü bir BTC liderliği değil.

## B1 + B2: Eşzamanlı ve gecikmeli ilişki

Regresyon `r_alt_{t+1} = α + b1·r_btc_t + b2·r_alt_t`, Newey-West HAC. "Ekonomik büyüklük" sütunu tanımlayıcıdır: 2σ'lık bir BTC mumundan sonraki mumda beklenen ek altcoin hareketi (b1 × 2σ_btc).

**1m, vadeli (işlem yapılacak piyasa; kontrol, BH dışı):**

| Coin | corr₀ | b1 | t | İki yarı | Ekonomik büyüklük | Kapı 1 maliyet eşiği |
|---|---|---|---|---|---|---|
| ETH | 0,86 | 0,027 | 2,4 | kaldı (işaret değişti) | %0,003 | %0,32 |
| SOL | 0,81 | 0,018 | 1,5 | geçti | %0,002 | %0,32 |
| XRP | 0,75 | 0,007 | 0,5 | kaldı | %0,001 | %0,32 |
| BNB | 0,78 | 0,016 | 2,3 | geçti | %0,002 | %0,32 |
| DOGE | 0,75 | 0,044 | 2,7 | geçti | %0,006 | %0,32 |
| ADA | 0,71 | 0,113 | 7,9 | geçti | %0,014 | %0,32 |
| AVAX | 0,72 | 0,006 | 0,6 | kaldı (işaret değişti) | %0,001 | %0,32 |
| LINK | 0,78 | 0,039 | 3,6 | kaldı | %0,005 | %0,32 |
| NEAR | 0,53 | 0,114 | 13,0 | kaldı | %0,014 | %0,40 |
| ARB | 0,60 | 0,131 | 12,4 | kaldı | %0,017 | %0,40 |
| INJ | 0,57 | 0,036 | 4,1 | kaldı | %0,005 | %0,40 |
| PEPE | 0,69 | 0,034 | 3,3 | geçti | %0,004 | %0,40 |

**1m, spot (ön kayıtlı ana test, BH ailesine giren):** 12 coinin 10'unda b1 ara BH'de anlamlı. Ara BH muhafazakâr hesaplandı: henüz ölçülmemiş 36 p değeri 1 kabul edildi. Bunların yalnız 6'sında iki yarı tutarlı (BNB, DOGE, ADA, NEAR, ARB, PEPE). Spot büyüklükler vadeliden çok büyük: PEPE 0,63'e karşı 0,034, AVAX 0,22'ye karşı 0,006, LINK 0,29'a karşı 0,04. En büyük ekonomik büyüklük spot PEPE'de: %0,078. Bu da eşiğin 1/5'i ve tick kaynaklı.

**1s, spot:** 12 coinin hepsinde b1 anlamlı, iki yarı tutarlı. Ekonomik büyüklük %0,001–0,004, eşiğin 1/100'ü.

Ayrıntılı tablolar: `b1_b2_spot_1s_1m.csv`, `b1_b2_vadeli_1m_kontrol.csv`, `b4_1s_ozet.csv`.

## Kapı durumu

- S1 **Aşama B'de**, Kapı 1 henüz değerlendirilmedi (B3 yapılmadı).
- B2 ön kayda göre tek başına Kapı 1'i geçemez. Yine de ekonomik büyüklük tablosu B3'te maliyet kriterinin geçilmesini çok olası dışı gösteriyor. 1m'de gereken hareket, ölçülenin en az ~20 katı.

## Yöntem sorunu: karıştırma testi fazla gevşek

Ön kayıttaki karıştırma kriteri, B2'de **her** kombinasyonda %100 verdi. HAC t değeri 0,5 olan XRP 1m'de bile sonuç aynı. Nedeni şu: günlük bloklar karıştırılınca BTC ile altcoinin ortak oynaklık kümelenmesi de bozuluyor. Böylece sıfır dağılımı gerçekte olması gerekenden çok daralıyor (testin hatası, verinin değil). B3 için planlanan "altcoin serisini 1 günlük bloklarla karıştır" testi de aynı zaafı taşıyor.

Karşılaştırma için ön kayıt dışı, tanımlayıcı bir **wild blok bootstrap** hesaplandı (sıfır altında kısıtlı modelin artıkları, blok başına ±1). Bu test ayırt edici: XRP 1m %67, SOL 1m %97, AVAX vadeli %70. Sonuçlar HAC ile tutarlı (`b2_wild_bootstrap_ek.csv`, kayıt defteri #37–#72).

**Öneri (onayınız gerekir):** Ön kayda tarihli bir Ek yazılsın. B2 ve B3'te "karıştırma %95" kriteri, wild blok bootstrap ile hesaplansın (B3'te olay getirileri için aynı mantık: blok başına işaret çevirme). Bu değişiklik kriteri **sıkılaştırır**, gevşetmez. Eski karıştırma sonuçları da raporda kalır.

## Spread ölçümü (devam ediyor)

3 saatlik örneklemenin ilk ~1,5 saati (537 örnek): vadeli yarım spread Küçük grupta 0,13–1,0 bps. Kayma tabanı (%0,05) bağlayıcı. Küçük grup vadeli gidiş-dönüş %0,20, Kapı 1 eşiği **%0,40**. Spot PEPE yarım spreadi 12,8 bps. Nihai özet örnekleme bitince `spread_ozet.csv` dosyasına yazılacak.

## Sıradaki adım (kararınıza bağlı)

Ön kayıt §7 gereği soruyorum: gecikme saniyeler düzeyinde. 1m'de ise istatistiksel ama ekonomik olarak önemsiz bir ilişki var. Seçenekler:

1. **Devam:** B3'ü (olay bazlı, maliyet kıyası) 1m'de çalıştır, ardından 5m/15m/1h'ye (B2 + B3) ve B5'e (ALT/BTC oranı) geç. Bu yol S1'i Kapı 1'de ön kayda uygun şekilde, eksiksiz kapatır. Tahmini 1–2 saat hesap.
2. **Kısa yol:** Yalnız 1m B3'ü çalıştır. Beklendiği gibi maliyetin altında kalırsa 5m/15m/1h'yi atla, S1'i kapat. B5 ayrı bir fikir olduğu için yine çalıştırılır.
3. **Dur:** S1'i bu ara raporla kapat.
