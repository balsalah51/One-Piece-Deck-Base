#!/usr/bin/env python3
"""Add created dates to community and YouTube list blurbs.

Uses dates already stored in data/community-decks.json, then slug dates
(tcgportal-2026-09-02, aug26). Does not invent dates. Does not wipe lists.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import importlib.util

ROOT = Path("/workspace")
HUB_BLOCK_RE = re.compile(
    r"        <!-- COMMUNITY_DECKLISTS -->.*?        <!-- /COMMUNITY_DECKLISTS -->",
    re.S,
)
ROW_SUB_RE = re.compile(
    r'(href="(/decklists/[^"]+\.html)")([\s\S]*?<div class="muted" style="font-size:13px">)(.*?)(</div>)'
)
HERO_SUB_RE = re.compile(r"(<h2>.*?</h2>\n        <p>)(.*?)(</p>)", re.S)
ISO_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def unescape(text: str) -> str:
    return (
        text.replace("&amp;", "&")
        .replace("&#x27;", "'")
        .replace("&quot;", '"')
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def collect_dates(comm, gen) -> dict[str, str]:
    by_href: dict[str, str] = {}
    extra = json.loads((ROOT / "data/community-decks.json").read_text())
    for leader in gen.LEADERS:
        items = list(comm.COMMUNITY.get(leader["id"], []))
        items.extend(extra.get(leader["id"]) or [])
        for item in items:
            href = item.get("href") or f"/{leader['dir']}/{item.get('slug')}.html"
            day = item.get("date") or comm.date_from_slug(item.get("slug") or href)
            if day and href not in by_href:
                by_href[href] = day
            if day and item.get("slug"):
                by_href.setdefault(f"/{leader['dir']}/{item['slug']}.html", day)
    return by_href


def patch_hub(path: Path, dates: dict[str, str], comm) -> int:
    text = path.read_text()
    block_m = HUB_BLOCK_RE.search(text)
    if not block_m:
        return 0
    block = block_m.group(0)
    changed = 0

    def repl(m: re.Match) -> str:
        nonlocal changed
        href = m.group(2)
        old = unescape(m.group(4))
        day = dates.get(href) or comm.date_from_slug(href)
        new = comm.dated_subtitle(old, day)
        if new == old:
            return m.group(0)
        changed += 1
        return f"{m.group(1)}{m.group(3)}{escape(new)}</div>"

    new_block = ROW_SUB_RE.sub(repl, block)
    if new_block != block:
        path.write_text(text[: block_m.start()] + new_block + text[block_m.end() :])
    return changed


def patch_list_page(href: str, day: str, comm) -> bool:
    path = ROOT / href.lstrip("/")
    if not path.exists() or not day:
        return False
    text = path.read_text()
    m = HERO_SUB_RE.search(text)
    if not m:
        return False
    old = unescape(m.group(2))
    new = comm.dated_subtitle(old, day)
    if new == old:
        return False
    path.write_text(text[: m.start()] + m.group(1) + escape(new) + m.group(3) + text[m.end() :])
    return True


def fill_json_dates(comm) -> int:
    path = ROOT / "data/community-decks.json"
    data = json.loads(path.read_text())
    filled = 0
    for _lid, items in data.items():
        for item in items:
            if item.get("date"):
                continue
            day = comm.date_from_slug(item.get("slug") or item.get("href") or "")
            if not day:
                continue
            item["date"] = day
            filled += 1
    if filled:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return filled


def main() -> None:
    comm = load("commlists", "/workspace/scripts/add-community-lists.py")
    gen = load("genlists", "/workspace/scripts/generate-tournament-lists.py")
    filled = fill_json_dates(comm)
    dates = collect_dates(comm, gen)
    hub_n = 0
    for leader in gen.LEADERS:
        path = ROOT / leader["page"]
        if path.exists():
            hub_n += patch_hub(path, dates, comm)
    list_n = 0
    for href, day in dates.items():
        if patch_list_page(href, day, comm):
            list_n += 1
    print("json dates filled", filled, "hub blurbs", hub_n, "list blurbs", list_n, "dated hrefs", len(dates))


if __name__ == "__main__":
    main()
