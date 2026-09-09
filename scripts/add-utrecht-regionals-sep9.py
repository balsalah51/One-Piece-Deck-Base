#!/usr/bin/env python3
"""Host complete Utrecht Regionals Top 8 lists from r/OnePieceTCG 1wbn1t7.

Does not invent cards. Does not run generate-tournament-lists.main() or
enhance-seo.main(). Skips lists that already match hosted EU Final pages.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path("/workspace")
REDDIT = "https://www.reddit.com/r/OnePieceTCG/comments/1wbn1t7/utrecht_regionals_2026_top_8_decklists/"

# Verified from the public BountyLog Top 8 graphics. Quantities sum to 1 leader + 50 main.
LISTS = [
    {
        "leader": "OP17-079",
        "kind": "reddit",
        "player": "Svinci",
        "title": "Utrecht Regionals 2026 1st - Svinci Monkey.D.Luffy",
        "subtitle": "List read from the public r/OnePieceTCG Top 8 graphic · 2026-09-09",
        "source_url": REDDIT,
        "slug": "reddit-luffy-regionals-svinci-1wbn1t7",
        "date": "2026-09-09",
        "raw": (
            "1xOP17-079 4xOP17-086 4xOP17-094 4xOP17-080 4xOP17-081 4xOP17-082 "
            "4xOP17-087 2xOP17-091 4xOP17-095 4xOP17-089 4xOP15-088 4xOP17-119 "
            "3xOP17-093 2xOP17-098 3xST14-017"
        ),
        "cards": 50,
    },
    {
        "leader": "OP09-062",
        "kind": "reddit",
        "player": "Polar",
        "title": "Utrecht Regionals 2026 Top 8 - Polar Nico Robin",
        "subtitle": "List read from the public r/OnePieceTCG Top 8 graphic · 2026-09-09",
        "source_url": REDDIT,
        "slug": "reddit-robin-regionals-polar-1wbn1t7",
        "date": "2026-09-09",
        "raw": (
            "1xOP09-062 4xOP17-113 2xST34-003 4xOP17-074 4xOP17-107 4xOP17-109 "
            "2xOP17-111 3xOP05-073 4xOP17-102 4xOP17-106 4xOP17-114 2xOP17-110 "
            "4xOP16-119 4xOP17-112 4xOP09-078 1xOP07-076"
        ),
        "cards": 50,
    },
    {
        "leader": "OP15-058",
        "kind": "reddit",
        "player": "park777",
        "title": "Utrecht Regionals 2026 Top 4 - park777 Enel",
        "subtitle": "List read from the public r/OnePieceTCG Top 8 graphic · 2026-09-09",
        "source_url": REDDIT,
        "slug": "reddit-enel-regionals-park777-1wbn1t7",
        "date": "2026-09-09",
        "raw": (
            "1xOP15-058 3xOP12-071 4xOP15-061 3xOP15-066 4xOP15-067 3xOP15-071 "
            "3xST10-010 4xOP10-067 3xOP07-064 1xOP13-076 2xOP15-074 4xOP15-075 "
            "4xOP15-076 4xOP15-077 4xOP15-078 3xOP05-077 1xOP09-077"
        ),
        "cards": 50,
    },
    {
        "leader": "OP14-020",
        "kind": "reddit",
        "player": "Josh Graham",
        "title": "Utrecht Regionals 2026 Top 4 - Josh Graham Mihawk",
        "subtitle": "List read from the public r/OnePieceTCG Top 8 graphic · 2026-09-09",
        "source_url": REDDIT,
        "slug": "reddit-mihawk-regionals-josh-graham-1wbn1t7",
        "date": "2026-09-09",
        "raw": (
            "1xOP14-020 4xOP07-022 4xOP12-034 4xST32-001 3xOP06-033 4xOP12-023 "
            "3xOP14-033 3xOP17-031 4xST32-002 3xOP13-031 3xST32-003 3xOP17-022 "
            "4xOP01-055 3xOP06-038 3xOP08-036 2xOP14-039"
        ),
        "cards": 50,
    },
    {
        "leader": "OP16-001",
        "kind": "reddit",
        "player": "BetterCallSaul",
        "title": "Utrecht Regionals 2026 Top 8 - BetterCallSaul Ace",
        "subtitle": "List read from the public r/OnePieceTCG Top 8 graphic · 2026-09-09",
        "source_url": REDDIT,
        "slug": "reddit-ace-regionals-bettercallsaul-1wbn1t7",
        "date": "2026-09-09",
        "raw": (
            "1xOP16-001 4xOP13-016 2xOP10-005 3xOP17-016 4xOP16-015 4xOP16-017 "
            "1xEB01-002 3xOP16-011 4xOP16-014 4xOP16-004 4xOP17-006 4xOP16-003 "
            "4xOP17-005 3xOP16-020 2xOP17-017 4xOP16-021"
        ),
        "cards": 50,
    },
]


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    gen = load("genlists", "/workspace/scripts/generate-tournament-lists.py")
    comm = load("commlists", "/workspace/scripts/add-community-lists.py")
    commsrc = load("commsrc", "/workspace/scripts/scrape-community-sources.py")
    more = load("morelists", "/workspace/scripts/add-more-tournament-lists.py")
    ana = load("analysis", "/workspace/scripts/add-leader-analysis.py")
    up = load("upgrade", "/workspace/scripts/upgrade-public-pages.py")
    seo = load("seofix", "/workspace/scripts/enhance-seo.py")

    needed = set()
    parsed = []
    for item in LISTS:
        counts = comm.parse_raw(item["raw"])
        needed.update(counts)
        parsed.append((item, counts))
    cache = gen.ensure_cards(needed, gen.load_card_cache())

    ready = []
    for item, counts in parsed:
        lid = item["leader"]
        main_n = sum(n for cid, n in counts.items() if cid != lid)
        banned = [cid for cid in counts if cid in gen.BANNED_CARDS]
        missing = [cid for cid in counts if cid not in cache]
        print(
            item["slug"],
            "cards",
            main_n,
            "leader",
            counts.get(lid),
            "banned",
            banned,
            "missing",
            missing,
        )
        if counts.get(lid) != 1 or main_n != 50 or banned or missing:
            raise SystemExit(f"bad list {item['slug']}")
        ready.append(item)

    print("=== write Utrecht Regionals Top 8 community lists ===")
    touched = commsrc.write_lists(ready)
    print("touched", sorted(touched))

    print("=== rebuild all hubs newest-first ===")
    index = more.load_index()
    more.save_index(index)
    more.rebuild_hubs(index)

    print("=== consensus ===")
    ana.main()

    print("=== homepage / search / sitemap ===")
    index = more.load_index()
    seo.rewrite_sitemap(seo.href_lookup(seo.load_index()))
    seo.write_search_page(index)
    up.patch_home()
    up.patch_op17()

    log_path = ROOT / "data/utrecht-regionals-sep9-log.json"
    log = {
        "hosted": [
            {
                "slug": item["slug"],
                "leader": item["leader"],
                "player": item["player"],
                "date": item["date"],
                "source_url": item["source_url"],
                "raw": item["raw"],
            }
            for item in ready
        ],
        "skipped_already_hosted": [
            {
                "player": "Trec",
                "leader": "OP14-041",
                "matches": "opdeck-boa-op17-west-eu-final-sep06-trecore",
            },
            {
                "player": "Cyde",
                "leader": "OP14-020",
                "matches": "opdeck-mihawk-op17-west-eu-final-sep06-clydetcg",
            },
            {
                "player": "arenasCV",
                "leader": "OP13-004",
                "matches": "opdeck-sabo-op17-west-bandai-utrecht-sep05-adriannarenas",
            },
        ],
        "notes": [
            "Source: r/OnePieceTCG 1wbn1t7 Utrecht Regionals 2026 Top 8 BountyLog graphics.",
            "Trec / Cyde / arenasCV match already-hosted EU Final OPDeckGuide lists; not duplicated.",
        ],
    }
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n")
    print("wrote", log_path)


if __name__ == "__main__":
    main()
