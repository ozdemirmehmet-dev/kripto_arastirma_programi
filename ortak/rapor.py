"""Rapor yardımcıları: markdown tablo, grafik kaydı, kayıt defterine satır ekleme."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parents[1]
KAYIT_DEFTERI = KOK / "KAYIT_DEFTERI.md"


def _hucre(v, ondalik: int) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if isinstance(v, (float, np.floating)):
        return f"{v:,.{ondalik}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    if isinstance(v, pd.Timestamp):
        return v.strftime("%Y-%m-%d")
    return str(v).replace("|", "\\|")


def md_tablo(df: pd.DataFrame, ondalik: int = 4, indeks: bool = True) -> str:
    """Türkçe ondalık biçimli (1.234,56) markdown tablo."""
    d = df.reset_index() if indeks else df
    basliklar = [str(c) for c in d.columns]
    satirlar = ["| " + " | ".join(basliklar) + " |", "|" + "---|" * len(basliklar)]
    for _, r in d.iterrows():
        satirlar.append("| " + " | ".join(_hucre(v, ondalik) for v in r.to_numpy()) + " |")
    return "\n".join(satirlar)


def yuzde(x: float, ondalik: int = 2) -> str:
    return "—" if x is None or np.isnan(x) else f"%{x * 100:.{ondalik}f}".replace(".", ",")


def grafik_kaydet(fig, yol: Path | str) -> Path:
    yol = Path(yol)
    yol.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(yol, dpi=120, bbox_inches="tight")
    return yol


def kayit_ekle(calisma: str, asama: str, varyasyon: str, coin: str, zaman_dilimi: str,
               sonuc: str) -> int:
    """KAYIT_DEFTERI.md'ye bir test satırı ekler, satır numarasını döndürür."""
    metin = KAYIT_DEFTERI.read_text(encoding="utf-8")
    numaralar = [int(m) for m in re.findall(r"^\| (\d+) \|", metin, flags=re.M)]
    no = max(numaralar, default=0) + 1
    tarih = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    hucreler = [str(no), tarih, calisma, asama, varyasyon, coin, zaman_dilimi, sonuc]
    satir = "| " + " | ".join(h.replace("|", "\\|") for h in hucreler) + " |\n"
    if not metin.endswith("\n"):
        metin += "\n"
    KAYIT_DEFTERI.write_text(metin + satir, encoding="utf-8")
    return no
