#!/usr/bin/env python3
"""Host complete OP17-splash lists from public TCG PORTAL shop-battle pages.

Limitless 8/28–29 events have no submitted lists. This pulls the newest
published Japanese results (8/25–26 as of the scrape) plus any later dates.
Does not invent cards. Does not wipe existing pages.
"""

from __future__ import annotations

import importlib.util
import json
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path("/workspace")
UA = "OnePieceDeckBase/1.0 (+https://onepiecedeckbase.com; public OPTCG list scrape)"
API = "https://tcg-portal.jp/api/onepiece/tournament-results"
ALT_RE = re.compile(r'alt="[^"]*\(((?:OP|ST|EB|PRB)\d{2}-\d{3})\)"')
HREF_RE = re.compile(r'href="/onepiece/cards/((?:OP|ST|EB|PRB)\d{2}-\d{3})"')
SINCE = "2026-08-25"


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", "replace")


def collect_rows() -> list[dict]:
    rows = []
    page = 1
    while page <= 8:
        data = get_json(f"{API}?page={page}&limit=50")
        batch = data.get("tournamentDecks") or []
        if not batch:
            break
        stop = False
        for row in batch:
            day = (row.get("date") or "")[:10]
            if day and day < SINCE:
                stop = True
                break
            rows.append(row)
        print("portal page", page, "kept", len(rows), "stop", stop)
        if stop:
            break
        page += 1
        time.sleep(0.1)
    return rows


def counts_from_html(html: str) -> dict[str, int]:
    hits = ALT_RE.findall(html)
    if len(set(hits)) < 6:
        hits = HREF_RE.findall(html)
    counts: dict[str, int] = {}
    for cid in hits:
        counts[cid] = counts.get(cid, 0) + 1
    return counts


def collect_lists(gen, commsrc) -> list[dict]:
    hosted = {L["id"] for L in gen.LEADERS}
    print("=== TCG PORTAL ===")
    rows = collect_rows()
    print("rows", len(rows), Counter((r.get("date") or "")[:10] for r in rows))

    found = []
    seen: set[str] = set()
    for row in rows:
        if not row.get("deckId") and not row.get("deckData"):
            continue
        pid = row["id"]
        url = f"https://tcg-portal.jp/onepiece/tournament-results/{pid}"
        try:
            html = fetch(url)
        except Exception as exc:  # noqa: BLE001
            print("fail", pid, exc)
            continue
        counts = counts_from_html(html)
        lids = [cid for cid, n in counts.items() if cid in hosted and n == 1]
        lid = lids[0] if len(lids) == 1 else None
        if not lid:
            ones = [cid for cid, n in counts.items() if n == 1]
            lid = ones[0] if ones else None
        main_n = sum(n for cid, n in counts.items() if cid != lid) if lid else 0
        has_op17 = any(cid.startswith("OP17-") for cid in counts)
        banned = [cid for cid in counts if cid in gen.BANNED_CARDS]
        print(pid, (row.get("date") or "")[:10], lid, "cards", main_n, "op17", has_op17, "banned", banned)
        if not lid or counts.get(lid) != 1 or main_n != 50 or banned:
            time.sleep(0.1)
            continue
        if lid not in hosted:
            print("skip unhosted", lid, "op17", has_op17)
            time.sleep(0.1)
            continue
        shop = (row.get("shop") or {}).get("name") or row.get("location") or "TCG PORTAL"
        event = row.get("tournamentName") or "Shop battle"
        guide = (row.get("deckGuide") or {}).get("name") or lid
        day = (row.get("date") or "")[:10]
        item = {
            "leader": lid,
            "kind": "web",
            "player": shop,
            "title": f"{guide} {event} winner — {shop}",
            "subtitle": f"Public TCG PORTAL list · {day}",
            "source_url": url,
            "slug": gen.slugify(f"tcgportal-{day}-{shop}-{pid[-6:]}")[:70],
            "raw": " ".join(f"{n}x{cid}" for cid, n in counts.items()),
            "cards": main_n,
            "date": day,
        }
        commsrc.record(found, item, seen)
        time.sleep(0.12)

    log_path = ROOT / "data/tcgportal-log.json"
    log_path.write_text(json.dumps({"hosted": found}, indent=2, ensure_ascii=False) + "\n")
    print("ready", len(found), "log", log_path)
    return found


def main() -> None:
    gen = load("genlists", "/workspace/scripts/generate-tournament-lists.py")
    commsrc = load("commsrc", "/workspace/scripts/scrape-community-sources.py")
    more = load("morelists", "/workspace/scripts/add-more-tournament-lists.py")
    ana = load("analysis", "/workspace/scripts/add-leader-analysis.py")
    up = load("upgrade", "/workspace/scripts/upgrade-public-pages.py")

    found = collect_lists(gen, commsrc)

    print("=== Limitless since 2026-08-26 ===")
    index = more.load_index()
    index = more.fetch_more(
        index,
        pages=6,
        extra_limit=400,
        per_event=99,
        since="2026-08-26",
    )
    more.save_index(index)

    print("=== write portal lists ===")
    commsrc.write_lists(found)
    index = more.load_index()
    more.rebuild_hubs(index)
    more.rewrite_sitemap()
    print("=== consensus ===")
    ana.main()
    print("=== homepage ===")
    up.patch_home()
    up.patch_op17()
    seo = load("seo", "/workspace/scripts/generate-seo-pages.py")
    seo.main()
    buy = load("tcgbuy", "/workspace/scripts/add-tcgplayer-buy.py")
    buy.main()
    seofix = load("seofix", "/workspace/scripts/enhance-seo.py")
    seofix.main()
    print("tcgportal + limitless recrape done")


if __name__ == "__main__":
    main()
