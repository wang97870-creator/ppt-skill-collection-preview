#!/usr/bin/env python3
"""Overlay the JOY copyright notice on every page of the public case PDF."""

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site/generated/case-competition-profissional-preview.pdf"
TARGET = ROOT / "site/generated/case-competition-profissional-preview.watermarked.pdf"


def overlay(width: float, height: float) -> BytesIO:
    stream = BytesIO()
    pdf = canvas.Canvas(stream, pagesize=(width, height))
    box_width = 184
    box_height = 13
    left = (width - box_width) / 2
    bottom = 5
    pdf.setFillColorRGB(7 / 255, 26 / 255, 51 / 255)
    pdf.rect(left, bottom, box_width, box_height, fill=1, stroke=0)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 6.8)
    pdf.drawCentredString(width / 2, bottom + 4.2, "COPYRIGHT RESERVED BY JOY")
    pdf.save()
    stream.seek(0)
    return stream


def main() -> None:
    reader = PdfReader(str(SOURCE))
    writer = PdfWriter()
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        mark = PdfReader(overlay(width, height)).pages[0]
        page.merge_page(mark, over=True)
        writer.add_page(page)
    with TARGET.open("wb") as handle:
        writer.write(handle)
    print(f"Watermarked {len(reader.pages)} PDF pages: {TARGET}")


if __name__ == "__main__":
    main()
