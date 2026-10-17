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
| S1 BTC → altcoin gecikmesi | Ön kayıt taslağı | — | — | 0 |
| S2 Funding carry | Ön kayıt taslağı | — | — | 0 |
| S4 Günlük trend takibi | Başlamadı | — | — | 0 |
| S3 Aşırı funding sonrası ters hareket | Başlamadı | — | — | 0 |
| S5 Oynaklık hedefleme | Başlamadı | — | — | 0 |
| S6 Gün/saat etkisi | Başlamadı | — | — | 0 |

> Eğitim ve araştırma amaçlıdır, yatırım tavsiyesi değildir.
