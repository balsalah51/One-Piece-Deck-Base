#!/usr/bin/env python3
"""Host complete OP17 50-card lists from public opdecks.xyz export textareas.

Does not invent cards. Does not wipe existing pages.
"""

from __future__ import annotations

import importlib.util
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path("/workspace")
UA = "OnePieceDeckBase/1.0 (+https://onepiecedeckbase.com; public OPTCG list scrape)"
SITE = "https://opdecks.xyz"
DECK_HREF_RE = re.compile(r'href="(/deck/[^"#?]+)"')
LEADER_HREF_RE = re.compile(r'href="(/leader/[^"#?]+)"')
TEXTAREA_RE = re.compile(r"<textarea[^>]*>(.*?)</textarea>", re.S)
DATE_RE = re.compile(r"Date</[^>]+>\s*([^<]+)", re.I)
PLAYER_RE = re.compile(r"Player</[^>]+>\s*([^<]+)", re.I)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", "replace")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def collect_deck_paths() -> list[str]:
    paths: list[str] = []
    pages = [SITE + "/", SITE + "/meta"]
    html = fetch(SITE + "/")
    leaders = sorted(set(LEADER_HREF_RE.findall(html)))
    try:
        meta = fetch(SITE + "/meta")
        leaders = sorted(set(leaders) | set(LEADER_HREF_RE.findall(meta)))
    except Exception as exc:  # noqa: BLE001
        print("meta fail", exc, flush=True)
    print("leader pages", len(leaders), flush=True)
    for href in DECK_HREF_RE.findall(html):
        if href not in paths:
            paths.append(href)
    for path in leaders:
        try:
            body = fetch(SITE + path)
        except Exception as exc:  # noqa: BLE001
            print("leader fail", path, exc, flush=True)
            continue
        for href in DECK_HREF_RE.findall(body):
            if href not in paths:
                paths.append(href)
        time.sleep(0.08)
    print("deck paths", len(paths), flush=True)
    return paths


def parse_date(text: str) -> str:
    m = DATE_RE.search(text)
    raw = clean(m.group(1)) if m else ""
    # 9/6/2026 or 8/19/2026
    m2 = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", raw)
    if m2:
        return f"{int(m2.group(3)):04d}-{int(m2.group(1)):02d}-{int(m2.group(2)):02d}"
    return raw[:10]


def main() -> None:
    gen = load("genlists", "/workspace/scripts/generate-tournament-lists.py")
    comm = load("commlists", "/workspace/scripts/add-community-lists.py")
    commsrc = load("commsrc", "/workspace/scripts/scrape-community-sources.py")
    more = load("morelists", "/workspace/scripts/add-more-tournament-lists.py")
    ana = load("analysis", "/workspace/scripts/add-leader-analysis.py")
    multi = load("multi", "/workspace/scripts/scrape-op17-multi.py")

    hosted = {L["id"] for L in gen.LEADERS}
    seen_raw = multi.existing_raws(gen, comm, ana)
    have_urls = multi.existing_source_urls()
    print("existing raw", len(seen_raw), flush=True)

    found: list[dict] = []
    seen: set[str] = set()
    paths = collect_deck_paths()
    for path in paths:
        url = SITE + path
        if url in have_urls:
            continue
        try:
            html = fetch(url)
        except Exception as exc:  # noqa: BLE001
            print("fail", path, exc, flush=True)
            continue
        box = TEXTAREA_RE.search(html)
        if not box:
            print("no export", path, flush=True)
            time.sleep(0.08)
            continue
        raw_text = box.group(1).replace("&nbsp;", " ")
        counts = comm.parse_raw(raw_text)
        lids = [cid for cid, n in counts.items() if cid in hosted and n == 1]
        lid = lids[0] if len(lids) == 1 else (lids[0] if lids else None)
        title_html = TITLE_RE.search(html)
        title = clean(title_html.group(1)) if title_html else path
        player_m = PLAYER_RE.search(html)
        player = clean(player_m.group(1)) if player_m else path.rstrip("/").split("-")[-1]
        day = parse_date(html)
        item = {
            "leader": lid,
            "kind": "web",
            "player": player,
            "title": title[:90],
            "subtitle": f"Public opdecks.xyz list · {day}" if day else "Public opdecks.xyz list",
            "source_url": url,
            "slug": gen.slugify(f"opdecks-{path.split('/')[-1]}")[:70],
            "raw": " ".join(f"{n}x{cid}" for cid, n in counts.items()),
            "cards": sum(n for cid, n in counts.items() if cid != lid) if lid else 0,
            "date": day,
        }
        if multi.item_ok(item, comm, gen, hosted, seen_raw):
            commsrc.record(found, item, seen)
            seen_raw.add(item["raw"])
            have_urls.add(url)
        time.sleep(0.08)

    (ROOT / "data/opdecks-xyz-log.json").write_text(
        json.dumps({"found": found}, indent=2, ensure_ascii=False) + "\n"
    )
    print("ready", len(found), flush=True)
    touched = commsrc.write_lists(found)
    index = more.load_index()
    more.rebuild_hubs(index, only_ids=touched or None)
    more.rewrite_sitemap()
    print("opdecks.xyz ingest done", len(found), "leaders", sorted(touched), flush=True)


if __name__ == "__main__":
    main()
