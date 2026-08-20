#!/usr/bin/env python3
"""Strip Shop links and shop-era copy from public HTML."""

from __future__ import annotations

from pathlib import Path

ROOT = Path("/workspace")
SKIP = {".git", "scripts", "node_modules", "shop"}
COMMUNITY = '        <a href="/#community">Community</a>'
DISCORD = '        <a href="https://discord.gg/adZ2WUQ3D" target="_blank" rel="noopener">Discord</a>'


def patch(text: str) -> str:
    original = text
    text = text.replace('\n        <a href="/shop/">Shop</a>', "")
    text = text.replace('        <a href="/shop/">Shop</a>\n', "")
    text = text.replace(' <a href="/shop/">Shop</a>', "")
    text = text.replace('<a href="/shop/">Shop</a> · ', "")
    text = text.replace(' · <a href="/shop/">Shop</a>', "")
    text = text.replace('<a href="/shop/">Shop</a>', "")
    text = text.replace(
        "Decklists, community, and custom gear",
        "OPTCG decklists",
    )
    if COMMUNITY in text:
        if DISCORD in text:
            text = text.replace("\n" + COMMUNITY, "")
            text = text.replace(COMMUNITY + "\n", "")
        else:
            text = text.replace(COMMUNITY, DISCORD)
    return text if text != original else original


def main() -> None:
    n = 0
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP for part in path.parts):
            continue
        text = path.read_text()
        updated = patch(text)
        if updated != text:
            path.write_text(updated)
            n += 1
    print("patched", n, "html files")


if __name__ == "__main__":
    main()
