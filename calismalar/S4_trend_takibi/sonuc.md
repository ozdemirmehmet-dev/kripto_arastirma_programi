# S4 Sonuç: Günlük Grafikte Trend Takibi

**Hüküm: Geçmiş getirinin işareti sonraki getiriyi çoğu coinde pozitif yönde gösteriyor, ama bu ağırlıkla 2021 boğa piyasasından geliyor. Çoklu test düzeltmesinden sonra hiçbir kombinasyon anlamlı değil ve etki ikinci yarıda zayıf. S4 Kapı 1'de kapandı: 0/78.**

## 1. Ön kayıt ve hipotez

- Ön kayıt: commit `67c48cd` (2026-10-18, kullanıcı onaylı, değişiklik yok). Ek yok.
- Hipotez: Kriptoda başlamış trendler devam eder. Basit trend kuralları al-tut'a göre daha iyi bir getiri/risk sunar.
- Ön beklenti (ölçümden önce yazıldı): BTC ve ETH'de pozitif fark, ama etki 2020–2021'de yoğunlaşmış olabilir; iki yarı kriteri kritik olacak. **İkisi de doğrulandı.**

## 2. Veri

- Binance spot 1d. 13 coin, her coinin ilk günlük mumundan 2026-10-16'ya kadar (son tam gün).
- BTC ve ETH 2017-08-17'den başlıyor (3.348 gün); ARB ve PEPE 2023'ten (1.261–1.304 gün).
- Eksik gün: 0. OHLC hatası: 0.
- Maliyet eşiği (2 × spot taker gidiş-dönüş): Büyük/Orta %0,52, NEAR/INJ %0,60, ARB %0,62, PEPE %1,42 (spot yarım spreadi 12,8 bps).

## 3. Aşama B ölçümleri

**Tanım.**
- Sinyal: `s_t = sign(ln(close_t / close_{t−N}))`.
- İleri getiri: `y_t = ln(open_{t+1+M} / open_{t+1})`.
- `D = ort(y | s = +1) − ort(y | s = −1)`.
- Test: 60 günlük hareketli blok bootstrap, 9.999 tekrar. BH ailesi 78 test (13 coin × N ∈ {20, 60, 120} × M ∈ {5, 20}), q = %10.

**Genel tablo.**
- D 78 kombinasyonun 67'sinde pozitif.
- Medyan D: M = 5'te %1,1, M = 20'de %3,9. Bu nokta tahminleri maliyet eşiğinin çok üstünde.
- Ham p < 0,05 olan 17 kombinasyon var. En güçlüsü SOL N=120 M=5 (p = 0,004). **BH sonrası en küçük düzeltilmiş p 0,186; anlamlı kombinasyon yok.**
- İki yarı:

| | İlk yarı medyan D | İkinci yarı medyan D |
|---|---|---|
| M = 5 | %1,65 | %0,53 |
| M = 20 | %5,03 | %1,22 |

İki yarı kriterini geçen kombinasyon: 14/78.

**Kriter bazında geçenler (78 içinde):**

| N, M | İki yarı | Bootstrap %5 > 0 | BH | Maliyet | Kapı 1 |
|---|---|---|---|---|---|
| 20, 5 | 2 | 5 | 0 | 10 | 0 |
| 20, 20 | 4 | 5 | 0 | 12 | 0 |
| 60, 5 | 2 | 3 | 0 | 9 | 0 |
| 60, 20 | 3 | 0 | 0 | 11 | 0 |
| 120, 5 | 2 | 3 | 0 | 10 | 0 |
| 120, 20 | 1 | 1 | 0 | 9 | 0 |

**BTC ve ETH (M = 20):**

| | N = 20 | N = 60 | N = 120 |
|---|---|---|---|
| BTC D (ilk / ikinci yarı) | %3,5 (%5,4 / %1,4) | %1,9 (%3,4 / %0,3) | %2,1 (%0,9 / %3,3) |
| ETH D (ilk / ikinci yarı) | %4,5 (%5,3 / %3,3) | %2,9 (%5,1 / %0,5) | %2,9 (%5,0 / %0,5) |

ETH N=20 M=20 iki yarı ve bootstrap kriterlerini geçiyor (p = 0,013), ama 78'lik ailede BH sonrası p = 0,186.

**B2: Yıl bazında (N = 20, M = 20).** Tüm coinlerin medyan D'si yıllara göre:

| 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| %3,7 | −%8,4 | −%2,1 | −%1,1 | **%13,7** | −%2,6 | %2,3 | −%1,5 | %2,0 | −%1,5 |

Tüm dönemdeki pozitif D'nin büyük kısmı 2021'den geliyor. Diğer yıllarda işaret yıldan yıla değişiyor. BTC'de yıllık D −%4,2 ile +%8,4 arasında.

Ayrıntı: `results/b1_kapi1.csv`, `results/b2_yillar.csv`.

## 4. Kapı durumu

**S4 Kapı 1'de durdu: 0/78.** Ön kaydın Aşama C koşulu (bir N'de, M = 20, BTC ya da ETH dahil en az 3 coin) hiçbir N'de sağlanmadı.

Durduran kriterler:
- **BH:** 78'in 78'i kaldı.
- **İki yarı:** 64 kombinasyon kaldı.

Maliyet kriteri sorun değil: 61 kombinasyon eşiği geçiyor. Sorun etkinin istikrarı ve istatistiksel olarak ayırt edilebilirliği.

Aşama C (V1–V5) yapılmadı. Program kuralına göre S5 (oynaklık hedefleme) yalnız al-tut üzerine uygulanacak.

## 5. Strateji sonuçları

Yok. Kapı 1 geçilmedi.

## 6. Sınırlamalar

- **Güç sorunu:** Günlük veride 9 yıldan az geçmiş var; bağımsız trend dönemi sayısı az. 78 testin birbirine çok bağlı olması (aynı coin, örtüşen N ve M) BH'yi bu durumda muhafazakâr yapıyor. Bu, "etki yok" demek değil, **"bu veriyle güvenilir biçimde ayırt edilemiyor" demek.** Kural ölçümden önce konduğu için sonradan gevşetilmedi.
- Hayatta kalma yanlılığı: bugünkü 13 coin kullanıldı. V4'ün genişletilmiş evrenine gelinmedi.
- Yalnız spot ve long/short ayrımı olmayan ham ölçüm (Aşama B tanımı gereği).
- Bu çalışmada **668 test/kırılım** kaydedildi (78 ana test + yıl kırılımları).

## 7. Yan gözlem

Trend takibinin kriptodaki ünü büyük ölçüde 2020–2021 boğa piyasasına dayanıyor olabilir. Bu veride 2022 sonrası yıllarda işaretin istikrarlı bir faydası görünmüyor. Bunu "trend takibi çalışmaz" diye genellemek doğru değil. Daha uzun geçmişi olan başka piyasalarla (örn. vadeli emtia) karşılaştırmak bu programın kapsamı dışında.

## 8. Tek cümlelik hüküm

**Günlük trend sinyali çoğu coinde pozitif yönlü ama 2021'e bağımlı ve çoklu test sonrası anlamsız; S4'te güvenilir bir fırsat yok.**

## Referans

- Kod: `calismalar/S4_trend_takibi/kod/asama_b.py`
- Sonuçlar: `calismalar/S4_trend_takibi/results/`
