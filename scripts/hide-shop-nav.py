#!/usr/bin/env python3
"""Strip Shop links from public HTML so the shop stays off the live nav."""

from __future__ import annotations

from pathlib import Path

ROOT = Path("/workspace")
SKIP = {".git", "scripts", "node_modules", "shop"}


def patch(text: str) -> str:
    original = text
    text = text.replace('\n        <a href="/shop/">Shop</a>', "")
    text = text.replace('        <a href="/shop/">Shop</a>\n', "")
    text = text.replace(' <a href="/shop/">Shop</a>', "")
    text = text.replace('<a href="/shop/">Shop</a> · ', "")
    text = text.replace(' · <a href="/shop/">Shop</a>', "")
    text = text.replace('<a href="/shop/">Shop</a>', "")
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
