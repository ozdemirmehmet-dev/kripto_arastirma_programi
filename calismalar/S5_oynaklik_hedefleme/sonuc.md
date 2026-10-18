# S5 Sonuç: Oynaklık Hedefleme (al-tut üzerine)

**Hüküm: Oynaklık katmanı BTC ve ETH'de ortalama pozisyonu küçülterek riski azaltıyor, ama risk başına getiriyi istatistiksel olarak artırmıyor. Alfa sıfırdan ayırt edilemiyor. S5 Kapı 1'de kapandı: 0/4.**

## 1. Ön kayıt ve hipotez

- Ön kayıt: commit `19b967a` (2026-10-18, kullanıcı onaylı, değişiklik yok). Ek yok.
- Kapsam: S4 Kapı 1'de kapandığı için yalnız BTC ve ETH al-tut üzerine.
- Hipotez: Pozisyonu son dönemin oynaklığıyla ters orantılı büyütmek, getiriyi aynı oranda azaltmadan riski azaltır. Böylece Sharpe yükselir.
- Ön beklenti (ölçümden önce yazıldı): oynaklık kalıcılığı kesin çıkar. Sharpe'a etkisi belirsiz, 2021 gibi dönemler bunu bozabilir. **İkisi de doğrulandı.**

## 2. Veri

- BTC ve ETH, Binance spot 1d, 2017-08-17 – 2026-10-16. Eksik gün 0.
- Haftalık ızgara pazartesi 00:00 UTC. Hafta sayısı: V20 için 474, V60 için 468.
- Katman: hedef yıllık oynaklık %40. Tahmin son 20 (V20) ya da 60 (V60) günün std'si × √365. w = min(1, %40 / tahmin). Kaldıraç yok, nakit getiri kazanmıyor.

## 3. Aşama B ölçümleri

### B1: Oynaklık kalıcılığı

| | V20 | V60 |
|---|---|---|
| BTC: korelasyon (R²) | 0,44 (0,19) | 0,43 (0,18) |
| ETH: korelasyon (R²) | 0,36 (0,13) | 0,34 (0,12) |

Tahmin sonraki haftanın oynaklığını kısmen açıklıyor. Kalıcılık var ama haftalık ölçekte orta düzeyde.

### B2: Oynaklık dilimine göre risk başına getiri

Haftalar, tahminin geçmişe dayalı (genişleyen pencere) beşte birlik dilimlerine ayrıldı. Sonraki haftanın ortalama / std oranı:

| | Dilim 1 (en sakin) | 2 | 3 | 4 | Dilim 5 (en oynak) |
|---|---|---|---|---|---|
| BTC V20 | 0,07 | 0,26 | 0,00 | 0,06 | 0,28 |
| BTC V60 | 0,14 | 0,03 | 0,07 | 0,14 | 0,51 |
| ETH V20 | 0,14 | 0,17 | 0,12 | −0,03 | 0,01 |
| ETH V60 | 0,12 | −0,03 | 0,16 | 0,21 | 0,25 |

Hipotezin dayanağı ("oynak dönemlerde risk başına getiri düşük") bu veride **tutmuyor**. BTC'de en oynak dilim en iyi oranı veriyor. ETH'de belirgin bir düzen yok.

Dikkat: Genişleyen eşikler yüzünden en oynak dilimde az hafta var (17–34). Erken yıllar daha oynaktı.

### B3: Katmanın alfası (maliyetsiz, ana ölçüm)

Regresyon: `g = α + b · R` (haftalık), α yıllıklandırıldı. Bootstrap: 12 haftalık bloklar, 9.999 tekrar.

| | BTC V20 | BTC V60 | ETH V20 | ETH V60 |
|---|---|---|---|---|
| Ortalama ağırlık | 0,74 | 0,71 | 0,59 | 0,55 |
| α (yıllık) | %1,1 | %2,6 | %3,8 | %1,8 |
| Bootstrap α %5 alt sınırı | −%7,8 | −%6,0 | −%6,4 | −%5,7 |
| BH p | 0,42 | 0,42 | 0,42 | 0,42 |
| α ilk / ikinci yarı | %0,1 / %3,4 | %1,5 / %3,4 | %1,3 / %10,8 | %4,4 / %2,5 |
| Yıllık devir (0,10 eşikli) | 3,6 | 1,2 | 4,0 | 1,0 |
| Kapı 1 maliyet eşiği (2 × yıllık maliyet) | %0,92 | %0,32 | %1,03 | %0,27 |
| Sharpe: al-tut → katmanlı (haftalık, maliyetsiz) | 0,83 → 0,80 | 0,78 → 0,79 | 0,70 → 0,72 | 0,71 → 0,71 |

## 4. Kapı durumu

| | İki yarı | Bootstrap | BH | Maliyet | Kapı 1 |
|---|---|---|---|---|---|
| BTC V20 | kaldı | kaldı | kaldı | ✓ | kaldı |
| BTC V60 | kaldı | kaldı | kaldı | ✓ | kaldı |
| ETH V20 | kaldı | kaldı | kaldı | ✓ | kaldı |
| ETH V60 | ✓ | kaldı | kaldı | ✓ | kaldı |

**S5 Kapı 1'de durdu: 0/4.** Maliyet sorun değil, çünkü katman ucuz. Sorun, alfanın gürültüden ayırt edilememesi. Aşama C yapılmadı.

## 5. Strateji sonuçları

Yok.

## 6. Sınırlamalar

- Yalnız iki coin ve ~9 yıl. Bağımsız oynaklık rejimi sayısı az; bootstrap aralıkları geniş.
- Nakde faiz verilmedi. Verilseydi katmanlı biraz daha iyi görünürdü (ortalama ağırlık 0,55–0,74, yani sermayenin %26–45'i nakitte). Ancak bu bir risk primi değil, USDT getirisi; kapı ölçümünün konusu değil.
- Maksimum düşüş Aşama C metriği olduğu için ölçülmedi. Ortalama ağırlık 1'in altında olduğundan düşüşün mekanik olarak azalması beklenir. Aynı azalma sabit bir ağırlıkla (örn. her zaman %60–70 pozisyon) da elde edilebilir. Testin ölçtüğü şey bu mekanik etkinin ötesinde bir fayda olup olmadığıydı; yok.
- Bu çalışmada **28 test/kırılım** kaydedildi.

## 7. Tek cümlelik hüküm

**Oynaklık hedefleme BTC ve ETH'de pozisyonu küçültmekten öte bir fayda sağlamıyor; risk ayarlı ek getiri sıfırdan ayırt edilemiyor. S5'te fırsat yok.**

## Referans

- Kod: `calismalar/S5_oynaklik_hedefleme/kod/asama_b.py`
- Sonuçlar: `calismalar/S5_oynaklik_hedefleme/results/`
