# S2 Sonuç: Funding Carry (cash-and-carry)

**Hüküm: Funding primi 2020–2021'de yüksekti, sonra belirgin biçimde eridi. Son 12 ayda hiçbir coinde maliyeti ve USDT getirisini karşılayacak düzeyde değil. S2 Kapı 1'de kapandı: 0/13.**

## 1. Ön kayıt ve hipotez

- Ön kayıt: commit `33bd974` (2026-10-17). Ek yok.
- Hipotez: USDT-M perpetual'larda longlar shortlara sistematik olarak funding öder. Spot long + vadeli short pozisyonu bu primi toplar ve maliyet sonrası USDT'de beklemekten (yıllık %4) iyi bir getiri/risk sunar.
- Ön beklenti (ölçümden önce yazıldı): BTC ve ETH'de uzun dönem ortalama pozitif ama rejime çok bağlı. Sermaye üzerinden net getiri %4 civarında ya da altında. **Beklenti doğrulandı; son dönem beklenenden de zayıf.**

## 2. Veri

- Funding: `fapi/v1/fundingRate`, 13 coin, her coinin ilk funding gününden 2026-10-17 00:00 UTC'ye kadar. BTC 2019-09'dan başlıyor (2.593 gün); ARB ve PEPE 2023'ten (1.260–1.303 gün). Günlük funding = o UTC gününde ödenen oranların toplamı; ilk (yarım) gün atıldı.
- Funding aralığı: 12 coinde tüm dönem 8 saat. SOL'da FTX çöküşü sırasında (2022-11-09 – 11-18) 4 saat (3 kez) ve 2 saat (98 kez) aralıklar var. Toplama yöntemi bunu doğru yıllıklandırıyor.
- Aşırı oranlar (|oran| > %1/dönem, silinmedi): SOL'da 11 kayıt (2022-11-09/11, −%1,1 ile −%2,0 arası), INJ'de 2 kayıt (2026-02-19/20, −%1,1 ile −%1,2 arası).
- Fiyat: spot ve vadeli 1h mumlar, aynı dönem. Spotta birkaç saatlik borsa kesintisi boşlukları var (en uzun 6 saat). Vadelide SOL, XRP ve NEAR'da birer adet 3 günlük boşluk var. Basis yalnız iki piyasanın da mumu olan saatlerden hesaplandı.
- Rejim (ön kayıtta sabit, BTC takvim yılı getirisi): yükseliş yılları 2019, 2020, 2021, 2023, 2024; düşüş yılları 2022, 2025, 2026 (yılbaşından 2026-10-16'ya).
- Maliyet: spot %0,10 ve vadeli %0,05 taker komisyon. Kayma Büyük/Orta için %0,03, Küçük için max(2 × ölçülen yarım spread, %0,05); spread S1'de ölçüldü. 4 bacak maliyeti Büyük/Orta için %0,42, NEAR/INJ %0,50, ARB %0,51. PEPE'de spot yarım spread 12,8 bps olduğu için %0,91.

## 3. Aşama B ölçümleri

### B1: Funding dağılımı (yıllıklandırılmış, notional üzerinden)

| Coin | Tüm dönem | Medyan | Pozitif ödeme | Yükseliş yılları | Düşüş yılları | 2025 | Son 12 ay |
|---|---|---|---|---|---|---|---|
| BTC | %11,5 | %8,2 | %86 | %16,2 | %4,2 | %5,1 | %3,3 |
| ETH | %13,7 | %8,6 | %86 | %21,3 | %2,6 | %4,9 | %2,5 |
| SOL | %0,2 | %6,8 | %71 | %12,1 | −%13,7 | %0,4 | −%0,5 |
| XRP | %14,4 | %9,1 | %80 | %23,7 | %1,2 | %3,5 | −%0,0 |
| BNB | −%0,1 | %0,0 | %27 | %3,1 | −%4,5 | −%2,1 | %2,1 |
| DOGE | %12,4 | %8,9 | %82 | %19,4 | %3,7 | %4,3 | %3,0 |
| ADA | %13,4 | %10,4 | %80 | %21,8 | %1,6 | %4,1 | %1,9 |
| AVAX | %6,8 | %7,2 | %71 | %13,9 | −%1,5 | %0,1 | −%0,3 |
| LINK | %13,6 | %9,9 | %82 | %19,5 | %5,3 | %5,1 | %4,6 |
| NEAR | %10,4 | %9,5 | %79 | %19,0 | %0,4 | %2,1 | %3,5 |
| ARB | %8,5 | %7,6 | %82 | %13,7 | %3,4 | %4,9 | %1,9 |
| INJ | −%1,9 | %4,3 | %63 | %1,3 | −%4,8 | %0,8 | −%10,4 |
| PEPE | %8,6 | %7,9 | %76 | %16,1 | %1,6 | %3,8 | −%0,7 |

- Yıl bazında büyük coinlerin çoğu: 2021'de %30–48, 2024'te %12–14, 2025'te %3,5–5, 2026'da %−0,1 ile %4,6 arası. Prim düşüş yıllarında düşük (BTC 2022 %4,2, 2025 %5,1, 2026 %2,9) ve yükseliş yıllarında yüksek. Ancak yükseliş yıllarının primi de **zamanla** azalıyor: BTC'de 2021'de %30,6, 2024'te %11,9.
- En uzun kesintisiz negatif funding dönemi: INJ 57 gün, BNB 40, NEAR 33, AVAX 32, SOL 28; BTC 11, ETH 13 gün.
- Ayrıntı: `results/b1_yillar.csv`.

### B2: Kalıcılık
- Günlük funding çok kalıcı. `corr(f_d, f_{d+1})` 0,61–0,84 arası (SOL 0,49); 7 gün sonrası için 0,08–0,59.
- Funding düzeyi kısa vadede iyi tahmin ediliyor. Bu bilgi eşikli bir stratejiye (V2) yarardı, ama düzeyin kendisi düşük. Ayrıntı: `results/b2_kalicilik.csv`.

### B3: Basis (vadeli / spot − 1, 1h)
- Medyan her coinde −%0,03 ile −%0,06 arası. %1–%99 aralığı büyük coinlerde yaklaşık ±%0,1–0,3; PEPE'de ±%0,8 (spot tick kaynaklı).
- En geniş anlar:
  - SOL, FTX çöküşü (2022-11-09): −%24.
  - AVAX (2021-02-11) ve DOGE (2020-12-21): +%7,4.
  - BTC: en fazla +%3,3 (2019-09-24).
- **Marj riski** (ön kayıt Aşama C varsayımı: izole marj, aylık yeniden dengeleme, %1 bakım marjı). Short bacak her ayın ilk açılışında yeniden açılırsa, ay içinde fiyatın iki katına çıkması 1x'te likidasyon demek. Likidasyon olan ay sayısı:
  - 1x: BTC 0, ETH 1, NEAR 11, AVAX 8, SOL 7, DOGE 6, XRP 5.
  - 2x: büyüklerde 3–19 ay.
  - DOGE'de ay içi en kötü hareket +%1.796 (2021 başı).
  - Spot bacağın kârı bunu dengeler, ama izole marjda dengelemek için ay sonunu beklemek gerekir.
- Ayrıntı: `results/b3_basis_ozet.csv`, `results/b3_basis_en_genis.csv`.

### B4: Brüt getiri − maliyet (tüm dönem ortalamasıyla)
- 30 günlük tutmada yıllık 4 bacak maliyeti: Büyük/Orta %5,1, Küçük %6,1–6,2, PEPE %11,1.
- Tüm dönem ortalamasıyla sermaye üzerinden net (1x, 30 gün): XRP %4,7, ETH %4,3, LINK %4,3, ADA %4,1, DOGE %3,6, BTC %3,2. SOL, BNB, INJ ve PEPE negatif. 2x'te en iyisi XRP: %6,2.
- Bu rakamlar 2020–2021'in yüksek primini içeriyor. **Son 12 ayın düzeyiyle hesaplanınca (en iyi LINK, %4,6 brüt) 1x net getiri her coinde negatif** (en iyisi LINK: (%4,6 − %5,1) / 2 ≈ −%0,3), USDT'nin %4'ünün çok altında.

### Anlamlılık testi (günlük ortalama > 0; 30 günlük blok işaret çevirme, 1.000 kez; BH 13 test)
- 10 coin %95'in üstünde ve BH sonrası anlamlı: BTC, ETH, XRP, DOGE, ADA, AVAX, LINK, NEAR, ARB, PEPE (p ≤ 0,004).
- Anlamlı olmayanlar: SOL %50, BNB %49, INJ %27.

## 4. Kapı durumu

| Coin | Yıllık ort. | Kapı 1 eşiği | İki yarı (ilk / ikinci) | Rastgele | BH | Maliyet | Kapı 1 |
|---|---|---|---|---|---|---|---|
| BTC | %11,5 | %10,2 | %15,9 / %7,1 → **kaldı** | ✓ | ✓ | ✓ | kaldı |
| ETH | %13,7 | %10,2 | %20,2 / %7,2 → **kaldı** | ✓ | ✓ | ✓ | kaldı |
| XRP | %14,4 | %10,2 | %21,9 / %7,0 → **kaldı** | ✓ | ✓ | ✓ | kaldı |
| DOGE | %12,4 | %10,2 | %16,7 / %8,0 → **kaldı** | ✓ | ✓ | ✓ | kaldı |
| ADA | %13,4 | %10,2 | %19,9 / %6,9 → **kaldı** | ✓ | ✓ | ✓ | kaldı |
| LINK | %13,6 | %10,2 | %18,9 / %8,4 → **kaldı** | ✓ | ✓ | ✓ | kaldı |
| AVAX | %6,8 | %10,2 | %8,6 / %5,1 ✓ | ✓ | ✓ | **kaldı** | kaldı |
| NEAR | %10,4 | %12,2 | %12,9 / %7,8 ✓ | ✓ | ✓ | **kaldı** | kaldı |
| ARB | %8,5 | %12,4 | %13,7 / %3,4 → kaldı | ✓ | ✓ | **kaldı** | kaldı |
| PEPE | %8,6 | %22,2 | %15,8 / %1,4 → kaldı | ✓ | ✓ | **kaldı** | kaldı |
| SOL | %0,2 | %10,2 | −%4,9 / %5,4 → kaldı | kaldı | kaldı | kaldı | kaldı |
| BNB | −%0,1 | %10,2 | %1,3 / −%1,5 → kaldı | kaldı | kaldı | kaldı | kaldı |
| INJ | −%1,9 | %12,2 | −%1,2 / −%2,6 → kaldı | kaldı | kaldı | kaldı | kaldı |

**S2 Kapı 1'de durdu: 0/13.** Altı coin maliyet eşiğini tüm dönem ortalamasıyla geçiyor. Ama hepsi iki yarı kriterinde kalıyor, çünkü ikinci yarıdaki prim ilk yarının yarısından az. Bu bir teknik ayrıntı değil, sonucun özü: carry'nin getirisi geçmişte kalmış dönemden geliyor.

Not: BTC'de yarıların oranı 0,45, sınır 0,50'ye yakın. Ancak son 12 ayın düzeyi (%3,3) eşiğin üçte biri olduğundan sınırdaki bu durum hükmü değiştirmiyor.

V3 (sepet) ön kayda göre en az 3 coinin Kapı 1'i geçmesini gerektiriyordu; test edilmedi. Aşama C yapılmadı.

## 5. Strateji sonuçları

Yok. Kapı 1 geçilmedi.

## 6. Sınırlamalar

- Yalnız Binance funding'i. Başka borsalardaki ve diğer sembollerdeki funding farkları kapsam dışı.
- Maliyet: taker, BNB indirimi yok. Maker senaryosunda 4 bacak maliyeti %0,36 (Büyük/Orta); eşik %8,8'e iner. Son 12 ay düzeyi bunun da çok altında, hüküm değişmez.
- Marj analizi basitleştirilmiş: izole marj, %1 sabit bakım marjı, aylık yeniden dengeleme. Portfolio margin modellenmedi.
- Hayatta kalma yanlılığı: bugünkü 13 coin kullanıldı. LUNA ve FTT funding verisi indirildi, ama yalnız V3 ek senaryosunda kullanılacaktı; V3'e gelinmedi.
- Bu çalışmada **137 test/kırılım** kaydedildi (13 ana test + yıl ve kalıcılık kırılımları).

## 7. Yan gözlem (fırsat değil)

Funding çok kalıcı (1 günlük otokorelasyon ~0,8) ve zaman zaman çok yüksek düzeylere çıkıyor (2021'de yıllık %30–48). Primin "her zaman açık" toplanması artık işe yaramıyor. Yalnız yüksek funding dönemlerinde açılan bir pozisyon (ön kayıttaki V2) bu ölçüm kapısının dışında kaldı. Bu dönemlerin ne kadar sık ve ne kadar uzun sürdüğü, S3'ün (aşırı funding) verisiyle birlikte değerlendirilebilir. Bu bir öneri değil; ayrı bir ön kayıt gerektirir.

## 8. Tek cümlelik hüküm

**Funding carry'nin primi 2021'den bu yana eridi; son 12 ayda en iyi coinde bile yıllık %4,6 brüt, yani maliyet ve sermaye bölünmesinden sonra USDT'de beklemenin altında. S2'de fırsat yok.**

## Referans

- Kod: `calismalar/S2_funding_carry/kod/` (`funding_indir.py`, `fiyat_indir.py`, `asama_b.py`)
- Sonuçlar: `calismalar/S2_funding_carry/results/` (`b1_b4_kapi1_ozet.csv`, `b1_yillar.csv`, `b2_kalicilik.csv`, `b3_basis_*.csv`)
