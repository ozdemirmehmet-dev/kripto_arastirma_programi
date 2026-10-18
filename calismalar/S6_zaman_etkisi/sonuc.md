# S6 Sonuç: Gün ve Saat Etkisi

**Hüküm: Saat dilimi, haftanın günü ve ABD açılışı etkilerinin hiçbiri çoklu test düzeltmesinden sonra anlamlı değil. Ayrıca saatlik ortalama getiriler maliyetin çok altında. S6 Kapı 1'de kapandı: 0/96; filtre adayı da çıkmadı.**

## 1. Ön kayıt ve hipotez

- Ön kayıt: commit `9f25bdd` (2026-10-18, kullanıcı onaylı, değişiklik yok). Ek yok.
- Hipotez: Belirli saatlerde (örn. ABD açılışı) ya da günlerde getiriler sistematik olarak farklıdır.
- Ön beklenti (ölçümden önce yazıldı): birkaç ham "anlamlı" sonuç tesadüfen çıkar, BH ve "her yılda aynı yön" sonrası hiçbiri kalmaz. Kalan olsa bile saatlik getiri maliyeti karşılamaz. **Doğrulandı.**

## 2. Veri

- BTC, ETH, SOL. Binance spot 1h, 2023-10-17 – 2026-10-17 (S1'de indirildi, eksik mum 0).
- Gözlem sayısı: her saat dilimi için 1.096 gün; haftanın her günü için 156–157 gün; ABD açılışı için 784 iş günü.
- ABD açılışı için yaz/kış saati `America/New_York` kurallarıyla hesaplandı. Kontrol örnekleri: 2024-03-08 (kış) 14:00 UTC, 2024-03-11 (yaz) 13:00 UTC, 2024-11-04 (kış) 14:00 UTC.
- Maliyet eşiği (tek başına strateji): 2 × vadeli taker gidiş-dönüş = %0,32.

## 3. Aşama B ölçümleri

Test: H0 ortalama = 0, iki yönlü; ISO haftası bloklu işaret çevirme, 9.999 tekrar. BH ailesi 96 test (3 coin × (24 saat + 7 gün + ABD açılışı)).

**Genel tablo.**
- Ham p < 0,05: **14/96.** Bağımsız testlerde tesadüfen ~5 beklenirdi, ama testler birbirine bağlı (aynı coinler, komşu saatler).
- En küçük ham p = 0,0025 (ETH saat 21). **BH sonrası en küçük düzeltilmiş p = 0,24. Anlamlı kalem yok.**
- Kriter bazında geçenler: her yılda aynı yön 34, iki yarı 33, rastgele test 14, BH **0**, maliyet 9.
- Maliyeti geçen 9 kalemin hepsi haftanın günü kalemi. Hiçbiri yıllar arasında tutarlı değil.

**En güçlü kalemler (ham p sırasıyla):**

| Coin | Kalem | Ortalama | Y1 / Y2 / Y3 | Ham p | BH p |
|---|---|---|---|---|---|
| ETH | Saat 21 UTC | +%0,067 | +%0,114 / +%0,032 / +%0,056 | 0,003 | 0,24 |
| BTC | Saat 21 UTC | +%0,036 | +%0,069 / +%0,011 / +%0,029 | 0,011 | 0,32 |
| BTC | Saat 08 UTC | +%0,031 | +%0,048 / +%0,029 / +%0,016 | 0,023 | 0,32 |
| BTC | Pazartesi | +%0,51 | +%1,09 / +%0,11 / +%0,35 | 0,027 | 0,32 |
| ETH | Saat 13 UTC | −%0,053 | −%0,093 / −%0,040 / −%0,027 | 0,029 | 0,32 |
| ETH | ABD açılışı | −%0,065 | −%0,121 / −%0,017 / −%0,058 | 0,044 | 0,32 |

- Saat 21 UTC üç coinde de pozitif (SOL +%0,055, ham p = 0,034). Bu saat, ABD borsalarının kapanışından hemen sonraya denk geliyor. Ancak etki Y1'de en güçlü, sonraki yıllarda Y1'in yarısından az.
- **ABD açılışı:** üç coinde de olay saati ortalaması hafif negatif (BTC −%0,028, ETH −%0,065, SOL −%0,043). BH sonrası anlamlı değil. Sonraki saat sıfıra yakın.
- **Haftanın günü:** günlük ortalamalar ±%0,7'ye kadar çıkıyor ama yıllar arasında işaret değiştiriyor. Örnek: SOL çarşamba +%1,42 / +%0,99 / −%0,29.
- Saatlik |ortalama| en fazla %0,067. Bu, maliyet eşiğinin **beşte biri**.

Ayrıntı: `results/kapi1.csv`, `results/abd_acilis_sonraki_saat.csv`.

## 4. Kapı durumu

**S6 Kapı 1'de durdu: 0/96.** BH 96 kalemin hiçbirinde geçilmedi. Filtre adayı ölçütü (1–4. kriterler, maliyet hariç) de BH yüzünden hiçbir kalemde sağlanmadı. Aşama C yapılmadı.

## 5. Strateji sonuçları

Yok.

## 6. Sınırlamalar

- 3 yıl, 3 coin. Saatlik ortalamalar çok gürültülü; bir saat diliminde ~1.100 gözlem var ve tek saatin std'si %0,37–1,22.
- ABD tatilleri ve yarım günler çıkarılmadı.
- Bu çalışmada **99 test/kırılım** kaydedildi (96 ana + 3 tanımlayıcı).

## 7. Tek cümlelik hüküm

**Kripto getirilerinde çoklu test sonrası ayakta kalan bir saat ya da gün etkisi yok; en güçlü aday (21:00 UTC) bile maliyetin beşte biri ve istatistiksel olarak tesadüften ayırt edilemiyor. S6'da fırsat yok.**

## Referans

- Kod: `calismalar/S6_zaman_etkisi/kod/asama_b.py`
- Sonuçlar: `calismalar/S6_zaman_etkisi/results/`
