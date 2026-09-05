#!/usr/bin/env python3
"""Turn public Reddit/X deck photos into hosted 50-card ID lists.

Only writes a page when the photo (or the same post's text overlay/comment)
yields a complete NxSET-NNN list for a leader hub. Does not invent cards.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path("/workspace")


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Photo/comment conversions checked against data/card-cache.json.
# raw is the exact 50-card dump read from the source image or matching comment.
TRANSCRIPTS = [
    {
        "leader": "OP16-060",
        "kind": "reddit",
        "player": "According-Pin5742",
        "title": "Sengoku locals test - r/OnePieceTCG",
        "subtitle": "List read from the public CardKaizoku screenshot · 2026-08-28",
        "source_url": "https://www.reddit.com/r/OnePieceTCG/comments/1w0xvqg/could_this_work_in_locals/",
        "slug": "reddit-sengoku-1w0xvqg",
        "date": "2026-08-28",
        "raw": (
            "1xOP16-060 4xOP16-064 3xOP16-067 2xOP16-070 3xOP17-075 4xOP17-074 "
            "4xOP16-066 3xOP16-075 3xOP16-063 4xOP16-065 3xOP16-073 3xOP17-059 "
            "2xOP15-077 3xOP17-076 2xOP16-076 3xOP16-077 2xOP09-077 2xOP16-078"
        ),
        "cards": 50,
        "photo": "data/reddit-media/2026-08-28-could-this-work-in-locals-1.jpg",
    },
    {
        "leader": "OP08-058",
        "kind": "reddit",
        "player": "DreadSteed",
        "title": "OP17 Pudding - r/OnePieceTCG photo + comment",
        "subtitle": "List read from the public Reddit deck photo and matching comment IDs · 2026-08-15",
        "source_url": "https://www.reddit.com/r/OnePieceTCG/comments/1vp5syc/op17_pudding_decklist_in_comments/",
        "slug": "reddit-pudding-1vp5syc",
        "date": "2026-08-15",
        "raw": (
            "1xOP08-058 4xOP11-070 4xST34-003 3xOP08-062 4xST34-001 3xPRB02-010 "
            "4xOP11-067 4xOP17-104 4xOP17-109 4xOP17-102 4xOP17-103 4xOP17-112 "
            "2xOP13-076 4xOP15-078 2xOP07-077"
        ),
        "cards": 50,
        "photo": "data/reddit-media/2026-08-15-op17-pudding-decklist-in-comments-1.jpg",
    },
    {
        "leader": "OP09-062",
        "kind": "web",
        "player": "Flame Flame Winner Utrecht",
        "title": "Flame Flame Winner Utrecht - Nico Robin",
        "subtitle": "Submitted 50-card list · 2026-09-04",
        "source_url": "https://onepiecedeckbase.com/decklists/nico-robin/submitted-flame-flame-winner-utrecht-2026-09-04.html",
        "slug": "submitted-flame-flame-winner-utrecht-2026-09-04",
        "date": "2026-09-04",
        "raw": (
            "1xOP09-062 4xOP17-112 3xOP16-119 3xOP17-110 4xOP17-114 4xOP17-106 "
            "4xOP17-102 3xOP05-073 4xOP17-074 4xOP17-107 4xOP17-109 3xOP17-111 "
            "4xOP17-113 2xST34-003 4xOP09-078"
        ),
        "cards": 50,
        "photo": "data/user-media/2026-09-04-nico-robin-flame-flame-winner-utrecht.jpg",
    },
]


def main() -> None:
    commsrc = load("commsrc", "/workspace/scripts/scrape-community-sources.py")
    gen = load("genlists", "/workspace/scripts/generate-tournament-lists.py")
    comm = load("commlists", "/workspace/scripts/add-community-lists.py")

    ready = []
    for item in TRANSCRIPTS:
        counts = comm.parse_raw(item["raw"])
        lid = item["leader"]
        main_n = sum(n for cid, n in counts.items() if cid != lid)
        banned = [cid for cid in counts if cid in gen.BANNED_CARDS]
        print(item["slug"], "cards", main_n, "leader", counts.get(lid), "banned", banned)
        if counts.get(lid) != 1 or main_n != 50 or banned:
            raise SystemExit(f"bad transcript {item['slug']}")
        ready.append(item)

    print("=== write photo transcripts ===")
    commsrc.write_lists(ready)
    log_path = ROOT / "data/image-transcript-log.json"
    log_path.write_text(json.dumps({"hosted": ready}, indent=2, ensure_ascii=False) + "\n")
    print("wrote", log_path, "lists", len(ready))


if __name__ == "__main__":
    main()
