# Coin Evreni Kontrolü

Kontrol tarihi (UTC): 2026-10-17 16:09. Geçmiş uzunluğu 2026-10-17 itibarıyla. Kaynak: Binance exchangeInfo, ilk günlük mum, fapi fundingInfo.

| grup | coin | spot_sembol | spot_durum | spot_ilk_gun | spot_gecmis_yil | vadeli_sembol | vadeli_durum | vadeli_ilk_gun | vadeli_gecmis_yil | funding_aralik_saat |
|---|---|---|---|---|---|---|---|---|---|---|
| Referans | BTC | BTCUSDT | TRADING | 2017-08-17 | 9,17 | BTCUSDT | TRADING | 2019-09-08 | 7,11 | 8 |
| Büyük | ETH | ETHUSDT | TRADING | 2017-08-17 | 9,17 | ETHUSDT | TRADING | 2019-11-27 | 6,89 | 8 |
| Büyük | SOL | SOLUSDT | TRADING | 2020-08-11 | 6,18 | SOLUSDT | TRADING | 2020-09-14 | 6,09 | 8 |
| Büyük | XRP | XRPUSDT | TRADING | 2018-05-04 | 8,45 | XRPUSDT | TRADING | 2020-01-06 | 6,78 | 8 |
| Büyük | BNB | BNBUSDT | TRADING | 2017-11-06 | 8,94 | BNBUSDT | TRADING | 2020-02-10 | 6,68 | 8 |
| Orta | DOGE | DOGEUSDT | TRADING | 2019-07-05 | 7,29 | DOGEUSDT | TRADING | 2020-07-10 | 6,27 | 8 |
| Orta | ADA | ADAUSDT | TRADING | 2018-04-17 | 8,50 | ADAUSDT | TRADING | 2020-01-31 | 6,71 | 8 |
| Orta | AVAX | AVAXUSDT | TRADING | 2020-09-22 | 6,07 | AVAXUSDT | TRADING | 2020-09-23 | 6,06 | 8 |
| Orta | LINK | LINKUSDT | TRADING | 2019-01-16 | 7,75 | LINKUSDT | TRADING | 2020-01-17 | 6,75 | 8 |
| Küçük | NEAR | NEARUSDT | TRADING | 2020-10-14 | 6,01 | NEARUSDT | TRADING | 2020-10-15 | 6,00 | 8 |
| Küçük | ARB | ARBUSDT | TRADING | 2023-03-23 | 3,57 | ARBUSDT | TRADING | 2023-03-23 | 3,57 | 8 |
| Küçük | INJ | INJUSDT | TRADING | 2020-10-21 | 5,99 | INJUSDT | TRADING | 2022-08-17 | 4,17 | 8 |
| Küçük | PEPE | PEPEUSDT | TRADING | 2023-05-05 | 3,45 | 1000PEPEUSDT | TRADING | 2023-05-05 | 3,45 | 8 |

## Notlar

- PEPE: vadeli sembolü farklı → `1000PEPEUSDT` (fiyat ve adet 1000 katlı; spot ile karşılaştırırken ölçeklenmeli)
- `funding_aralik_saat` yalnız bugünkü ayardır. Geçmişte aralığın değiştiği dönemler S2'de funding verisinden ayrıca kontrol edilir.
- Listeden çıkmış coin yok; evrende değişiklik gerekmiyor.
