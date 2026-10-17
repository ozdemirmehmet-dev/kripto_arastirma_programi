# S1 Sonuç: BTC → Altcoin Gecikmesi

**Hüküm: BTC'den altcoinlere gecikme gerçek ama saniyeler düzeyinde. 1 dakika ve üstünde, maliyetten sonra işlenebilecek bir fırsat yok. S1 Kapı 1'de kapandı.**

## 1. Ön kayıt ve hipotez

- Ön kayıt: commit `6dff5d5` (2026-10-17). Ek 1, kullanıcı onaylı: commit `558f8b8` (rastgele test wild blok bootstrap ile; B3 ayrıntıları; B5 tanımları).
- Hipotez: BTC büyük bir hareket yaptığında altcoinler gecikmeli tepki verir. Altcoin yetişmeden BTC yönünde işlem açmak maliyet sonrası kâr getirir.
- Ön beklenti (ölçümden önce yazıldı): gecikme büyük coinlerde saniyeler düzeyinde, en olası sonuç Kapı 1'de durmak. **Beklenti doğrulandı.**

## 2. Veri

| Zaman dilimi | Dönem (UTC) | Piyasa | Mum / sembol | Eksik mum |
|---|---|---|---|---|
| 1s | 2026-10-03 – 10-17 | spot | 1.209.600 | 0 |
| 1m | 2025-10-17 – 2026-10-17 | spot + vadeli | 525.600 | 0 |
| 5m, 15m | 2024-10-17 – 2026-10-17 | spot | 210.240 / 70.080 | 0 |
| 1h | 2023-10-17 – 2026-10-17 | spot + vadeli | 26.304 | 0 |

- 13 sembol (BTC + 12 altcoin). Hiçbir coin çıkarılmadı. Vadelide PEPE = `1000PEPEUSDT`, fiyatı 1000'e bölündü.
- Spread: 2026-10-17 18:13–21:13 UTC arası 10 saniyede bir bookTicker (1.078 örnek). Vadeli yarım spread: Büyük/Orta 0,02–2,3 bps, Küçük 0,13–1,0 bps. Küçük grupta kayma tabanı %0,05 bağlayıcı. Spot PEPE'de yarım spread 12,8 bps; bir tick fiyatın %0,245'i.
- Kapı 1 maliyet eşiği (2 × vadeli taker gidiş-dönüş): Büyük/Orta **%0,32**, Küçük **%0,40**. B5 çift işlemde: %0,64 / %0,72.

## 3. Aşama B ölçümleri

### B4: Gecikme ölçeği (1s)
- `corr(r_btc_t, r_alt_{t+k})` zirvesi k = 0'da. k = 1'de 0,02–0,16, k = 5'te ≤ 0,02, k = 30'da ~0.
- BTC 3σ saniye olaylarından (19.437 olay) sonra altcoin, beklenen hareketin %90'ını medyan olarak şu sürede tamamlıyor: Büyük 1 sn, Orta 1–4 sn, Küçük 1–8 sn. Spot PEPE'de 40 sn çıktı; bu bir tick artefaktı.
- Ters yön (alt → BTC, 1 sn) de aynı büyüklükte (0,02–0,15). 1s'deki ilişki büyük ölçüde iki yönlü bir eşzamansızlık.
- Grafik: `results/b4_gecikme_olcegi_1s.png`. Ayrıntı: `results/ara_rapor_1.md`.

### B2: Gecikmeli regresyon `r_alt_{t+1} = α + b1·r_btc_t + b2·r_alt_t` (60 test, BH q = %10)

| Zaman dilimi | BH anlamlı | Wild %95 üstü | İki yarı tutarlı | Üçü birden | En büyük ekonomik büyüklük (b1 × 2σ) |
|---|---|---|---|---|---|
| 1s | 12/12 | 12/12 | 12/12 | 12 | %0,004 |
| 1m | 11/12 | 11/12 | 6/12 | 6 | %0,078 (spot PEPE, tick); vadelide %0,017 |
| 5m | 5/12 | 8/12 | 3/12 | 1 | %0,14 (AVAX, iki yarı tutarsız) |
| 15m | 1/12 | 2/12 | 2/12 | 1 | %0,05 (PEPE) |
| 1h | 0/12 | 0/12 | 0/12 | 0 | %0,04 |

İstatistiksel ilişki zaman dilimi büyüdükçe kayboluyor. Ön kayda göre B2 Kapı 1'i tek başına geçemez; maliyet kriteri B3 ile değerlendirilir. Spot ile vadeli 1m arasında büyük fark var (AVAX 0,216 → 0,006; PEPE 0,63 → 0,034). Spotta görülen gecikmenin önemli kısmı spot piyasanın mikro yapısından geliyor: kaba tick ve vadeliden sonra güncellenen fiyat.

### B3: Olay bazlı (K = 2σ, h = 3 mum, açılış→açılış; ana test, 48 test)

| Zaman dilimi | BTC olayı | Ortalama işaretli alt getirisi (bps, 12 coin aralığı) | Wild %95 üstü | BH anlamlı | İki yarı | Maliyet eşiğini geçen |
|---|---|---|---|---|---|---|
| 1m | 10.607 | 0,3 – 1,2 | 9 | 8 | 6 | **0** |
| 5m | 3.667 | 1,4 – 3,4 | 10 | 8 | 10 | **0** |
| 15m | 1.324 | −1,7 – 2,9 | 0 | 0 | 2 | **0** |
| 1h | 611 | 0,7 – 17,5 | 1 | 1 | 2 | **0** |

- En yakın kombinasyon 1h ETH: 17,5 bps. İstatistiksel kriterlerin hepsini geçti (wild %99,6, BH p = 0,029, iki yarı tutarlı) ama eşiğin yalnız **%55'i**. Sonraki en yakın 1h ADA (%32). Diğer 46 kombinasyon eşiğin %25'inin altında.
- Vadeli kontrol: 1m'de 0,03–0,37 bps, 1h'de −5,8 ile 14,5 bps arası.
- Gap beşte birleri: 1m ve 5m'de en çok geride kalan altcoinler biraz daha fazla yetişiyor (5m: 4,8 bps, diğerleri 1,6 bps). Bu yönde küçük bir gerçek gecikme var, ama eşiğin 1/7'si. 15m ve 1h'de tersi oluyor: geride kalan yetişmiyor (1h: −11,5 bps, diğerleri +11,6 bps).
- Tanımlayıcı kontrol (ön kayıt dışı, `b3_momentum_kontrol.csv`): β ile hedge edilmiş altcoin getirisi 1m'de +0,5 bps, 5m'de +0,6, 15m'de +1,2, 1h'de **−5,8** bps. 1h'deki pozitif ortalamalar gecikme değil. BTC'nin kendisi büyük saatlik hareketten sonra aynı yönde devam ediyor (+9,3 bps); altcoinler de β ile onu izliyor.
- Grafik: `results/b3_maliyet_esigi.png`.

### B5: ALT/BTC oranında dengeye dönüş (1h, h = 24 saat; 12 test, ayrı BH ailesi)
- Olay sayısı 207–257 (her coinde ≥ 50). Ortalama getiri −49,6 ile +39,3 bps arasında ve işareti coinden coine değişiyor. Wild %95'i geçen coin yok (en yüksek LINK %94,97). BH sonrası anlamlı olan yok. Eşiği (64–72 bps) geçen yok.
- AR(1) yarı ömrü 118–173 saat (5–7 gün). Oran yavaş dönüyor ama 24 saatlik pozisyon getirisi sıfırdan ayırt edilemiyor. Vadeli sonuçlar aynı.
- z'nin 24 saatlik ortalama değişimi sıfıra doğru 0,23–0,39. Bu değişimin bir kısmı rolling pencerenin kaymasının mekanik sonucu; işlem getirisi değil.

## 4. Kapı durumu

| Ölçüm | Kapı 1'i geçen | Durduran kriter |
|---|---|---|
| B3 (gecikme stratejisinin ham etkisi) | **0 / 48** | Maliyet: hiçbir kombinasyon 2 × gidiş-dönüş eşiğine ulaşmadı (en iyi %55) |
| B5 (oran dengeye dönüşü) | **0 / 12** | Rastgele test, BH ve iki yarı; maliyet |

**S1 Kapı 1'de durdu.** Aşama C (strateji testi) yapılmadı.

## 5. Strateji sonuçları

Yok. Kapı 1 geçilmedi.

## 6. Sınırlamalar

- Ön kayda uygun olarak ana ölçüm spot fiyatla yapıldı. İşlem vadelide düşünülüyor. Vadeli kontrolleri spot sonuçlarından daha zayıf, yani hüküm vadelide daha da kesin.
- 1s verisi yalnız 14 gün ve yalnız spot (vadeli 1s verisi yok).
- Spread tek bir akşam, 3 saat boyunca ölçüldü. Kayma Büyük/Orta için sabit %0,03, Küçük için %0,05 tabanı. Gerçek kayma daha yüksek olabilir; bu durum hükmü değiştirmez, güçlendirir.
- Bugün listede olan coinler kullanıldı (hayatta kalma yanlılığı). İlişki ölçümü olduğu için etkisi sınırlı.
- Tek borsa (Binance).
- Ön kayıttaki karıştırma testi B2'de ayırt edici değildi (her yerde %100). Ek 1 ile wild blok bootstrap'e geçildi. Eski sonuçlar kayıt defterinde duruyor.
- Bu çalışmada **816 test** kaydedildi (`KAYIT_DEFTERI.md`). Bu kadar test arasında bir kombinasyonun tesadüfen öne çıkması beklenir. 1h ETH'nin istatistiksel kriterleri geçmesi bu açıdan da temkinle okunmalı.

## 7. Yan gözlem (fırsat değil, hipotez adayı)

Ön kayıt dışı, tanımlayıcı: BTC'de 3σ'lık bir saatlik hareketten sonra BTC'nin kendisi sonraki 3 saatte ortalama **+19 bps** aynı yönde devam ediyor (310 olay, wild %99,6). Ancak etki ilk yarıda 26 bps, ikinci yarıda 12 bps; iki yarı kriterini geçmiyor. Bu bir BTC momentum etkisi, S1'in hipotezi değil. 816 testin içinden sonradan seçildiği için kanıt sayılmaz. İncelenmek istenirse yeni bir ön kayıtla ve S1'in kullanmadığı veriyle test edilmeli; örneğin 2019-09 – 2023-10 arası 1h verisi. Konu olarak S4'e (trend takibi) daha yakın.

## 8. Tek cümlelik hüküm

**BTC → altcoin gecikmesi saniyeler içinde kapanıyor. 1m–1h arasında ölçülen en iyi etki, gidiş-dönüş maliyetin 2 katının yarısına bile ulaşmıyor. S1'de fırsat yok.**

## Referans

- Kod: `calismalar/S1_btc_alt_gecikme/kod/` (`olcum.py`, `ara_rapor_1.py`, `kapi1.py`, `momentum_kontrol.py`)
- Sonuçlar: `calismalar/S1_btc_alt_gecikme/results/` (`kapi1_b2.csv`, `kapi1_b3.csv`, `kapi1_b5.csv`, `b3/`, `ara_rapor_1.md`)
