#!/usr/bin/env python3
"""Create Rosinante, Sabo, Moria, and Robin hubs and fill them from Limitless."""

from __future__ import annotations

import html
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("genlists", "/workspace/scripts/generate-tournament-lists.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

aspec = importlib.util.spec_from_file_location("more", "/workspace/scripts/add-more-tournament-lists.py")
more = importlib.util.module_from_spec(aspec)
aspec.loader.exec_module(more)

ROOT = gen.ROOT
NEW_IDS = {"OP12-061", "OP13-004", "OP14-080", "OP09-062"}
BLURBS = {
    "OP12-061": "Purple/Yellow OP12 Donquixote Rosinante. Once per turn, spend a life to save Trafalgar Law from K.O., then DON!! −1 to play a 4-cost or higher Law for 2 less. Not green/blue OP05-022 Rosinante.",
    "OP13-004": "Red/Black OP13 Sabo. At 4+ life the leader is −1000. DON!! x1 plus an 8-cost character pumps the board. Dressrosa / Revolutionary Army — not ST13 Sabo.",
    "OP14-080": "Black/Yellow OP14 Gecko Moria. K.O. your own Thriller Bark character to give the board +1000, then trash 3 to gain a life.",
    "OP09-062": "Purple/Yellow OP09 Nico Robin. Banish damage, then trash a Trigger to rest a DON!!. Straw Hat archaeologist leader, not a cameo in Black Luffy.",
}
NOTES = {
    "OP12-061": "Purple/yellow OP12-061 Corazon. Not green/blue OP05-022 Rosinante.",
    "OP13-004": "Red/black OP13-004. The ST13 Sabo leader is separate and is not on this site.",
    "OP14-080": "Black/yellow Thriller Bark. Recent lists include OP17 cards.",
    "OP09-062": "Purple/yellow OP09 Robin. Recent lists include OP17 cards.",
}


def write_hub(leader: dict, card: dict) -> None:
    name = leader["name"]
    full = gen.display_name(card.get("name") or leader["name"])
    color = card.get("color") or ""
    types = card.get("types") or ""
    effect = card.get("effect") or ""
    img = card.get("image") or gen.card_image_url(leader["id"])
    crumb_href, crumb_label = leader["crumb"]
    pills = [
        f"{color} Leader" if color else "Leader",
        leader["id"],
    ]
    if card.get("life"):
        pills.append(f"{card['life']} Life")
    if card.get("power"):
        pills.append(f"{card['power']} Power")
    if card.get("attribute") and str(card.get("attribute")).strip() not in {"", "?"}:
        pills.append(card["attribute"])
    if types and str(types).strip() not in {"", "?"}:
        pills.append(types)
    pill_html = "\n              ".join(f'<span class="pill">{html.escape(p)}</span>' for p in pills)
    body = f"""        <div class="crumb"><a href="/">Home</a> / <a href="{html.escape(crumb_href)}">{html.escape(crumb_label)}</a> / {html.escape(name)}</div>
        <div class="leader-hero">
          <img src="{html.escape(img)}" alt="{html.escape(full)} leader" />
          <div>
            <h2>{html.escape(name)}</h2>
            <p>{html.escape(BLURBS[leader['id']])}</p>
            <div class="stat-row">
              {pill_html}
            </div>
            <div class="effect">{html.escape(effect)}</div>
            <p class="muted" style="margin-top:12px">{html.escape(NOTES[leader['id']])}</p>
          </div>
        </div>

        <!-- TOURNAMENT_DECKLISTS -->
        <section class="deck-index" style="margin-top:22px">
          <div class="section-title">
            <h3>Tournament decklists</h3>
            <div class="muted">0 lists</div>
          </div>
          <p class="muted">Fetching Limitless lists for this leader.</p>
        </section>
        <!-- /TOURNAMENT_DECKLISTS -->
"""
    page = gen.page_chrome(
        f"{name} decklist",
        f"{full} — {color} leader page and scraped tournament lists."[:160],
        leader["color"],
        leader["nav_op17"],
        body,
    )
    path = ROOT / leader["page"]
    path.write_text(page)
    print("hub page", path)


def fetch_new(index: dict) -> dict:
    target_ids = NEW_IDS
    print("fetching tournament pages for new leaders")
    tournaments = more.fetch_tournament_pages(pages=10)
    print("tournaments", len(tournaments))
    by_leader = gen.fetch_standings(tournaments, target_ids)
    cache = gen.load_card_cache()
    needed = set()
    planned = {}
    for leader in gen.LEADERS:
        lid = leader["id"]
        if lid not in target_ids:
            continue
        have = more.existing_stems(leader)
        picked = gen.select_lists(by_leader.get(lid) or [], limit=48)
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
            if len(fresh) >= 40:
                break
        planned[lid] = fresh
        print(lid, "new unique", len(fresh), "raw", len(by_leader.get(lid) or []))
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
            index.setdefault(lid, []).append(more.index_row(entry))
    return index


def main() -> None:
    cache = gen.ensure_cards(NEW_IDS, gen.load_card_cache())
    for leader in gen.LEADERS:
        if leader["id"] not in NEW_IDS:
            continue
        card = cache.get(leader["id"]) or {}
        write_hub(leader, card)
    index = more.load_index()
    index = fetch_new(index)
    more.save_index(index)
    more.rebuild_hubs(index)
    print("done")


if __name__ == "__main__":
    main()
