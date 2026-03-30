"""Gera PDF simples do certificado (UTF-8 com DejaVu embutido no fpdf2, senao fallback)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import fpdf
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from app.config import settings


def _register_dejavu(pdf: FPDF) -> bool:
    font_root = Path(fpdf.__file__).resolve().parent / "font"
    reg = font_root / "DejaVuSans.ttf"
    bold = font_root / "DejaVuSans-Bold.ttf"
    if reg.is_file():
        pdf.add_font("DejaVu", "", str(reg))
        if bold.is_file():
            pdf.add_font("DejaVu", "B", str(bold))
        else:
            pdf.add_font("DejaVu", "B", str(reg))
        return True
    return False


def build_certificate_pdf(*, holder_name: str, serial: str, issued_iso: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    has_dejavu = _register_dejavu(pdf)
    if has_dejavu:
        pdf.set_font("DejaVu", "B", 20)
    else:
        pdf.set_font("helvetica", "B", 16)
    pdf.cell(
        0,
        16,
        "Certificado de conclusao",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    if has_dejavu:
        pdf.set_font("DejaVu", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)
    pdf.ln(8)
    pdf.multi_cell(0, 8, "Certifica-se que", align="C")
    pdf.ln(4)
    if has_dejavu:
        pdf.set_font("DejaVu", "B", 14)
    else:
        pdf.set_font("helvetica", "B", 14)
        holder_name = holder_name.encode("ascii", "replace").decode("ascii")
    pdf.multi_cell(0, 10, holder_name, align="C")
    if has_dejavu:
        pdf.set_font("DejaVu", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)
    pdf.ln(6)
    course_line = f"concluiu o percurso: {settings.course_display_name}."
    if not has_dejavu:
        course_line = course_line.encode("ascii", "replace").decode("ascii")
    pdf.multi_cell(0, 8, course_line, align="C")
    pdf.ln(12)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(
        0,
        6,
        f"Serial: {serial}",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.cell(
        0,
        6,
        f"Emitido em (UTC): {issued_iso}",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    raw = pdf.output()
    if raw is None:
        return b""
    if isinstance(raw, (bytes, bytearray)):
        return bytes(raw)
    return str(raw).encode("latin-1", errors="replace")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
