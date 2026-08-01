#!/usr/bin/env python3
"""Add a visible rights watermark to every Consulting Deck Studio slide."""

from pathlib import Path
from bs4 import BeautifulSoup


TARGET = Path(__file__).resolve().parents[1] / "site/previews/consulting-deck-studio/index.html"


def main() -> None:
    soup = BeautifulSoup(TARGET.read_text(encoding="utf-8"), "html.parser")
    slides = soup.select("section.slide")
    if not slides:
        raise RuntimeError("No studio slides found")

    for old in soup.select(".joy-watermark"):
        old.decompose()

    style = soup.new_tag("style")
    style.string = """
      .joy-watermark{
        position:absolute;z-index:90;right:22px;bottom:18px;
        padding:8px 12px;border:1px solid rgba(255,255,255,.55);
        border-radius:3px;background:rgba(7,20,34,.82);color:#fff;
        font:800 10px/1.1 Inter,Arial,sans-serif;letter-spacing:.14em;
        text-transform:uppercase;pointer-events:none;user-select:none;
        box-shadow:0 8px 24px rgba(0,0,0,.18);backdrop-filter:blur(8px)
      }
      @media(max-width:700px){.joy-watermark{right:12px;bottom:12px;font-size:8px;padding:6px 8px}}
    """
    soup.head.append(style)

    for slide in slides:
        mark = soup.new_tag("div", attrs={"class": "joy-watermark", "aria-hidden": "true"})
        mark.string = "COPYRIGHT RESERVED BY JOY"
        slide.append(mark)

    TARGET.write_text(str(soup), encoding="utf-8")
    print(f"Added {len(slides)} watermarks to {TARGET}")


if __name__ == "__main__":
    main()
