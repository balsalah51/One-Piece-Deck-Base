#!/usr/bin/env python3
"""Pull new lists dated 2026-08-20+ from Limitless, X, and public deck pages.

Does not wipe existing list pages. Rebuilds hubs, consensus lists, and the homepage.
"""

from __future__ import annotations

import importlib.util

SINCE = "2026-08-17"


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    more = load("morelists", "/workspace/scripts/add-more-tournament-lists.py")
    commsrc = load("commsrc", "/workspace/scripts/scrape-community-sources.py")
    analysis = load("analysis", "/workspace/scripts/add-leader-analysis.py")
    up = load("upgrade", "/workspace/scripts/upgrade-public-pages.py")

    print("=== Limitless Play since", SINCE, "===")
    index = more.load_index()
    index = more.fetch_more(
        index,
        pages=8,
        extra_limit=400,
        per_event=99,
        since=SINCE,
    )
    more.save_index(index)

    print("=== X / YouTube / OnePieceDB ===")
    commsrc.main()

    index = more.load_index()
    more.rebuild_hubs(index)
    more.rewrite_sitemap()

    print("=== consensus aggregates ===")
    analysis.main()

    print("=== homepage / public pages ===")
    up.patch_home()
    up.patch_op17()
    print("ingest done")


if __name__ == "__main__":
    main()
