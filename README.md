# Kripto Fırsat Araştırma Programı

Yalnız araştırma projesi. Gerçek emir yok, API anahtarı yok, canlı hesap yok.
Ana talimat: [kripto_arastirma_programi.md](kripto_arastirma_programi.md).

Amaç: altı fikrin her birinde işlem maliyetinden sonra da yaşayan, tekrarlanabilir bir avantaj olup olmadığını tarafsız ölçmek. "Fırsat yok" da geçerli bir sonuçtur.

## Kurulum

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest tests
```

Veri `data/` altında önbelleklenir ve git dışındadır.

## Yapı

- `ortak/` — veri, maliyet, backtest motoru, istatistik, rapor yardımcıları
- `calismalar/S?_*/` — her çalışmanın `on_kayit.md`, `kod/`, `results/`, `sonuc.md` dosyaları
- `KAYIT_DEFTERI.md` — yapılan her testin listesi (çoklu test sayımı)
- `firsat_kartlari/` — yalnız dört kapının hepsini geçen fikirler

## Çalışmaların durumu

| Çalışma | Durum | Ulaştığı kapı | Hüküm | Test sayısı |
|---|---|---|---|---|
| S1 BTC → altcoin gecikmesi | Kapandı | Kapı 1'de durdu | Gecikme saniyeler düzeyinde; 1m–1h'de en iyi etki maliyet eşiğinin %55'i. Fırsat yok. ([sonuç](calismalar/S1_btc_alt_gecikme/sonuc.md)) | 816 |
| S2 Funding carry | Kapandı | Kapı 1'de durdu | Prim 2021'den beri eridi; son 12 ayda en iyi coin yıllık %4,6 brüt, USDT %4'ün altında. Fırsat yok. ([sonuç](calismalar/S2_funding_carry/sonuc.md)) | 137 |
| S4 Günlük trend takibi | Kapandı | Kapı 1'de durdu | Sinyal çoğu coinde pozitif ama 2021'e bağımlı; BH sonrası 0/78 anlamlı, ikinci yarıda zayıf. Güvenilir fırsat yok. ([sonuç](calismalar/S4_trend_takibi/sonuc.md)) | 668 |
| S3 Aşırı funding sonrası ters hareket | Başlamadı | — | — | 0 |
| S5 Oynaklık hedefleme | Başlamadı | — | — | 0 |
| S6 Gün/saat etkisi | Başlamadı | — | — | 0 |

> Eğitim ve araştırma amaçlıdır, yatırım tavsiyesi değildir.
