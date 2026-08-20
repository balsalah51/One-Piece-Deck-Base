#!/usr/bin/env python3
"""Append extra unique Limitless tournament lists and rebuild leader hub HTML.

Does not wipe community list pages. Does not run generate-tournament-lists.main().
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import importlib.util

spec = importlib.util.spec_from_file_location("genlists", "/workspace/scripts/generate-tournament-lists.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

cspec = importlib.util.spec_from_file_location("commlists", "/workspace/scripts/add-community-lists.py")
comm = importlib.util.module_from_spec(cspec)
cspec.loader.exec_module(comm)

ROOT = gen.ROOT
EXTRA_LIMIT = 32
PAGES = 12
PER_PAGE = 40
HUB_BLOCK_RE = re.compile(
    r"        <!-- (?:COMMUNITY_DECKLISTS|TOURNAMENT_DECKLISTS) -->.*?        <!-- /TOURNAMENT_DECKLISTS -->",
    re.S,
)
NEWGATE_TOURNAMENT = """        <!-- TOURNAMENT_DECKLISTS -->
        <section class="deck-index" style="margin-top:22px">
          <div class="section-title">
            <h3>Tournament decklists</h3>
            <div class="muted">0 lists</div>
          </div>
          <p class="muted">Still no Limitless tournament results for OP17-001. Use the YouTube lists above until events start posting this leader.</p>
        </section>
        <!-- /TOURNAMENT_DECKLISTS -->"""


def load_index() -> dict:
    path = ROOT / "data/tournament-decks.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_index(index: dict) -> None:
    (ROOT / "data/tournament-decks.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")


def existing_stems(leader: dict) -> set[str]:
    d = ROOT / leader["dir"]
    if not d.exists():
        return set()
    return {p.stem for p in d.glob("*.html")}


def known_tournament_ids(index: dict) -> set[str]:
    ids: set[str] = set()
    for items in index.values():
        for item in items or []:
            url = item.get("source_url") or ""
            m = re.search(r"/tournament/([^/]+)/", url)
            if m:
                ids.add(m.group(1))
    return ids


def prune_duplicate_lists(index: dict) -> dict:
    cleaned: dict[str, list] = {}
    for leader in gen.LEADERS:
        lid = leader["id"]
        items = index.get(lid) or []
        stems = existing_stems(leader)
        kept = []
        seen = set()
        for item in items:
            slug = item.get("slug") or ""
            kind = item.get("kind")
            path = ROOT / leader["dir"] / f"{slug}.html"
            if kind == "sample":
                if path.exists():
                    path.unlink()
                    print("removed sample", path)
                continue
            if slug.endswith("-2") and slug[:-2] in stems:
                if path.exists():
                    path.unlink()
                    print("removed duplicate", path)
                continue
            if slug in seen:
                continue
            if not path.exists():
                continue
            seen.add(slug)
            kept.append(item)
        cleaned[lid] = kept
        print(lid, "kept", len(kept), "of", len(items))
    return cleaned


def community_entries(leader: dict) -> list[dict]:
    out = []
    for item in comm.COMMUNITY.get(leader["id"], []):
        href = f"/{leader['dir']}/{item['slug']}.html"
        if not (ROOT / leader["dir"] / f"{item['slug']}.html").exists():
            continue
        out.append(
            {
                "href": href,
                "title": item["title"],
                "subtitle": item.get("subtitle") or "",
                "kind": item.get("kind"),
            }
        )
    return out


def tournament_entries(leader: dict, items: list[dict]) -> list[dict]:
    out = []
    for item in items:
        kind = item.get("kind")
        if kind == "sample":
            continue
        slug = item.get("slug") or ""
        path = ROOT / leader["dir"] / f"{slug}.html"
        if not path.exists():
            continue
        entry = dict(item)
        entry["tournament_name"] = entry.get("tournament_name") or entry.get("tournament") or "Limitless event"
        out.append(entry)
    return out


def rebuild_hubs(index: dict) -> None:
    for leader in gen.LEADERS:
        lid = leader["id"]
        page_path = ROOT / leader["page"]
        page = page_path.read_text()
        comm_lists = community_entries(leader)
        tour_lists = tournament_entries(leader, index.get(lid) or [])
        if lid == "OP17-001":
            tournament_html = NEWGATE_TOURNAMENT
        else:
            tournament_html = gen.render_index_section(leader, tour_lists)
        combined = comm.community_section(leader, comm_lists, tournament_html)
        page = re.sub(
            r"        <!-- COMMUNITY_DECKLISTS -->.*?        <!-- /COMMUNITY_DECKLISTS -->\n?",
            "",
            page,
            count=1,
            flags=re.S,
        )
        m = HUB_BLOCK_RE.search(page)
        if m:
            page = page[: m.start()] + combined + page[m.end() :]
        else:
            page = gen.insert_section(page, combined, gen.render_pool_heading(leader))
        page_path.write_text(page)
        print(
            "hub",
            leader["page"],
            "community",
            len(comm_lists),
            "tournament",
            0 if lid == "OP17-001" else len(tour_lists),
        )


def index_row(entry: dict) -> dict:
    return {
        "slug": entry["slug"],
        "href": entry["href"],
        "player": entry.get("player"),
        "tournament": entry.get("tournament_name"),
        "placing": entry.get("placing"),
        "date": entry.get("date"),
        "kind": entry.get("kind"),
        "source_url": entry.get("source_url"),
    }


def fetch_tournament_pages(pages: int = PAGES, per_page: int = PER_PAGE) -> list:
    seen = []
    ids = set()
    for page in range(1, pages + 1):
        batch = gen.http_json(
            f"https://play.limitlesstcg.com/api/tournaments?game=OP&limit={per_page}&page={page}"
        )
        added = 0
        for tourney in batch or []:
            tid = tourney.get("id")
            if not tid or tid in ids:
                continue
            ids.add(tid)
            seen.append(tourney)
            added += 1
        print("page", page, "new", added, "unique", len(seen))
    return seen


def fetch_more(index: dict, pages: int = PAGES) -> dict:
    target_ids = {L["id"] for L in gen.LEADERS}
    print("fetching tournament pages", pages)
    tournaments = fetch_tournament_pages(pages=pages)
    seen = known_tournament_ids(index)
    fresh_events = [t for t in tournaments if t.get("id") not in seen]
    print("tournaments", len(tournaments), "new events", len(fresh_events), "already indexed", len(seen))
    by_leader = gen.fetch_standings(fresh_events, target_ids)
    cache = gen.load_card_cache()
    needed = set()
    planned: dict[str, list] = {}
    for leader in gen.LEADERS:
        lid = leader["id"]
        have = existing_stems(leader)
        picked = gen.select_lists(by_leader.get(lid) or [], limit=EXTRA_LIMIT + 24)
        fresh = []
        for entry in picked:
            slug = gen.planned_slug(entry)
            if slug in have:
                continue
            href = f"/{leader['dir']}/{slug}.html"
            entry = dict(entry)
            entry["slug"] = slug
            entry["href"] = href
            fresh.append(entry)
            have.add(slug)
            for item in gen.flatten_cards(entry["decklist"]):
                needed.add(item["id"])
            if len(fresh) >= EXTRA_LIMIT:
                break
        planned[lid] = fresh
        print(lid, "new unique", len(fresh))
    cache = gen.ensure_cards(needed, cache)
    for leader in gen.LEADERS:
        lid = leader["id"]
        fresh = planned.get(lid) or []
        if not fresh:
            continue
        out_dir = ROOT / leader["dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        for entry in fresh:
            page = gen.render_deck_page(leader, entry, cache)
            (out_dir / f"{entry['slug']}.html").write_text(page)
            index.setdefault(lid, []).append(index_row(entry))
    return index


def main() -> None:
    index = load_index()
    index = fetch_more(index, pages=PAGES)
    save_index(index)
    rebuild_hubs(index)
    print("done")


if __name__ == "__main__":
    main()
