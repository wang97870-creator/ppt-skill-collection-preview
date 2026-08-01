#!/usr/bin/env python3
"""Build the public 11-scene Indonesia GIFF excerpt from the supplied master HTML."""

from pathlib import Path
import re
from bs4 import BeautifulSoup


SOURCE = Path("/Users/jiayiwang0106/Desktop/高中资料/HKU/Year 1/Peking U summer/最终 PPT/1 组 印度尼西亚.html")
TARGET = Path(__file__).resolve().parents[1] / "site/previews/indonesia-giff/index.html"


def main() -> None:
    soup = BeautifulSoup(SOURCE.read_text(encoding="utf-8"), "html.parser")

    scenes = soup.select("section.scene")
    if len(scenes) < 11:
        raise RuntimeError(f"Expected at least 11 scenes, found {len(scenes)}")

    team = soup.select_one("#opening .team-members")
    if team:
        team.decompose()

    keep_ids = {scene.get("id") for scene in scenes[:11]}
    for scene in scenes[11:]:
        scene.decompose()

    for trigger in soup.select("[data-go]"):
        if trigger.get("data-go") not in keep_ids:
            trigger.decompose()

    watermark_css = soup.new_tag("style")
    watermark_css.string = """
      .joy-watermark{
        position:absolute;z-index:90;right:24px;top:66px;
        padding:8px 12px;border:1px solid rgba(255,255,255,.55);
        border-radius:3px;background:rgba(7,20,34,.78);color:#fff;
        font:800 10px/1.1 Inter,Arial,sans-serif;letter-spacing:.14em;
        text-transform:uppercase;pointer-events:none;user-select:none;
        box-shadow:0 8px 24px rgba(0,0,0,.18);backdrop-filter:blur(8px)
      }
      @media(max-width:700px){.joy-watermark{right:12px;top:58px;font-size:8px;padding:6px 8px}}
    """
    soup.head.append(watermark_css)

    for scene in soup.select("section.scene"):
        watermark = soup.new_tag("div", attrs={"class": "joy-watermark", "aria-hidden": "true"})
        watermark.string = "COPYRIGHT RESERVED BY JOY"
        scene.append(watermark)

    main_script = next((script for script in soup.find_all("script") if script.string and "const scenes=" in script.string), None)
    if not main_script:
        raise RuntimeError("Could not find the main presentation script")

    js = main_script.string
    js = js.replace(
        "document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>document.getElementById(b.dataset.go).scrollIntoView({behavior:'smooth'}));",
        "document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>{const target=document.getElementById(b.dataset.go);if(target)target.scrollIntoView({behavior:'smooth'})});",
    )

    later_start = js.find("const discoveries=")
    sources_start = js.find("const sources=")
    if later_start == -1 or sources_start == -1 or sources_start <= later_start:
        raise RuntimeError("Could not isolate later-scene interaction block")
    js = js[:later_start] + js[sources_start:]

    map_start = js.find("const slideToScene=")
    update_pos = js.rfind("updateNotes();")
    if map_start == -1 or update_pos == -1 or update_pos <= map_start:
        raise RuntimeError("Could not replace the deck map")
    excerpt_map = """const excerptScenes=scenes.map(s=>s.id);
excerptScenes.forEach((id,i)=>{const target=document.getElementById(id);const b=document.createElement('button');b.className='deck-dot';b.textContent=i+1;b.title='Jump to '+target.dataset.title;b.onclick=()=>{closePanel('deckModal');target.scrollIntoView({behavior:'smooth'})};deckMap.appendChild(b)});
updateNotes();"""
    js = js[:map_start] + excerpt_map + js[update_pos + len("updateNotes();"):]
    main_script.string = js

    title = soup.find("title")
    if title:
        title.string = "Indonesia GIFF · Public 11-page excerpt"
    description = soup.find("meta", attrs={"name": "description"})
    if description:
        description["content"] = "Indonesia GIFF consulting presentation — public 11-page excerpt with copyright watermark."

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    output_html = re.sub(r"^[ \t]+$", "", str(soup), flags=re.MULTILINE)
    TARGET.write_text(output_html, encoding="utf-8")

    output_soup = BeautifulSoup(TARGET.read_text(encoding="utf-8"), "html.parser")
    output_scenes = output_soup.select("section.scene")
    output_marks = output_soup.select("section.scene > .joy-watermark")
    if len(output_scenes) != 11 or len(output_marks) != 11:
        raise RuntimeError(f"Output validation failed: {len(output_scenes)} scenes, {len(output_marks)} watermarks")
    forbidden = ["Jiang Guyue", "Wang Jiayi", "Wang Shuangsheng", "Jiang Hanqi", "Zhou Xiang"]
    output_text = TARGET.read_text(encoding="utf-8")
    if any(name in output_text for name in forbidden):
        raise RuntimeError("Team names remain in output")

    print(f"Built {TARGET} ({TARGET.stat().st_size / 1_000_000:.1f} MB)")
    print("Scenes:", ", ".join(scene.get("id", "") for scene in output_scenes))


if __name__ == "__main__":
    main()
