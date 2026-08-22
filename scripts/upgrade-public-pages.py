#!/usr/bin/env python3
"""Upgrade existing HTML with copy buttons, list stats, Format nav, and site.js.

Does not wipe list pages. Does not run generate-tournament-lists.main().
"""

from __future__ import annotations

import html
import importlib.util
import json
import re
from pathlib import Path

spec = importlib.util.spec_from_file_location("genlists", "/workspace/scripts/generate-tournament-lists.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

aspec = importlib.util.spec_from_file_location("analysis", "/workspace/scripts/add-leader-analysis.py")
ana = importlib.util.module_from_spec(aspec)
aspec.loader.exec_module(ana)

ROOT = gen.ROOT
LINE_RE = ana.LINE_RE
CSS_NEW = "/css/site.css?v=home-recent"
JS_NEW = "/js/site.js?v=home-recent"
NAV_OLD_PATTERNS = [
    (
        '        <a href="/decklists/op17.html">OP17</a>\n        <a href="/#community">Community</a>',
        '        <a href="/decklists/op17.html">Leaders</a>\n        <a href="/format.html">Format</a>\n        <a href="https://discord.gg/adZ2WUQ3D" target="_blank" rel="noopener">Discord</a>',
    ),
    (
        '        <a href="/decklists/op17.html">Leaders</a>\n        <a href="https://discord.gg/adZ2WUQ3D" target="_blank" rel="noopener">Discord</a>',
        '        <a href="/decklists/op17.html">Leaders</a>\n        <a href="/format.html">Format</a>\n        <a href="https://discord.gg/adZ2WUQ3D" target="_blank" rel="noopener">Discord</a>',
    ),
    (
        '        <a href="/decklists/op17.html" aria-current="page">OP17</a>\n        <a href="/#community">Community</a>',
        '        <a href="/decklists/op17.html" aria-current="page">Leaders</a>\n        <a href="/format.html">Format</a>\n        <a href="https://discord.gg/adZ2WUQ3D" target="_blank" rel="noopener">Discord</a>',
    ),
    (
        '        <a href="/decklists/op17.html" aria-current="page">Leaders</a>\n        <a href="/#community">Community</a>',
        '        <a href="/decklists/op17.html" aria-current="page">Leaders</a>\n        <a href="/format.html">Format</a>\n        <a href="https://discord.gg/adZ2WUQ3D" target="_blank" rel="noopener">Discord</a>',
    ),
]


def patch_lists_nav(text: str) -> str:
    text = text.replace('href="/#decklists">Decklists<', 'href="/lists.html">Lists<')
    text = text.replace(
        'href="/#decklists" aria-current="page">Decklists<',
        'href="/lists.html" aria-current="page">Lists<',
    )
    return text


def patch_nav_and_assets(text: str) -> str:
    text = re.sub(r'href="/css/site\.css(?:\?[^"]*)?"', f'href="{CSS_NEW}"', text)
    for old, new in NAV_OLD_PATTERNS:
        text = text.replace(old, new)
    text = patch_lists_nav(text)
    text = re.sub(r'src="/js/site\.js(?:\?[^"]*)?"', f'src="{JS_NEW}"', text)
    text = text.replace(">Copy for sim<", ">Copy to OP TCG SIM<")
    text = text.replace("for OPTCGSim.", "for OP TCG SIM.")
    if "/js/site.js" not in text:
        text = text.replace("</body>", f'  <script src="{JS_NEW}"></script>\n</body>')
    return text


def grouped_from_counts(leader: dict, counts: dict[str, int], cache: dict) -> tuple[list[dict], dict]:
    items = [
        {
            "count": 1,
            "id": leader["id"],
            "name": cache.get(leader["id"], {}).get("name") or leader["name"],
            "group": "Leader",
        }
    ]
    for cid, n in counts.items():
        meta = cache.get(cid) or {}
        cat = (meta.get("category") or "character").lower()
        if cat == "event":
            group = "Events"
        elif cat == "stage":
            group = "Stages"
        else:
            group = "Characters"
        items.append({"count": n, "id": cid, "name": meta.get("name") or cid, "group": group})
    return items, cache


def upgrade_list_page(path: Path, leader: dict, cache: dict) -> None:
    text = path.read_text()
    counts = ana.parse_deck(path, leader["id"])
    if counts and "<!-- DECK_STATS -->" not in text:
        items, _ = grouped_from_counts(leader, counts, cache)
        stats = gen.render_deck_stats(items, cache)
        if stats:
            marker = '        <section class="text-deck">'
            if marker in text:
                text = text.replace(marker, stats + "\n" + marker, 1)
            else:
                text = text.replace("</h2>", "</h2>\n" + stats, 1)
    text = patch_nav_and_assets(text)
    path.write_text(text)


def meta_rows() -> list[tuple[dict, int]]:
    rows = []
    for leader in gen.LEADERS:
        d = ROOT / leader["dir"]
        n = len(list(d.glob("*.html"))) if d.exists() else 0
        rows.append((leader, n))
    rows.sort(key=lambda r: (-r[1], r[0]["name"]))
    return rows


def render_meta_strip(rows: list[tuple[dict, int]]) -> str:
    current = [(L, n) for L, n in rows if not L.get("nav_op17")]
    total = sum(n for _, n in current) or 1
    top = current[:8]
    lis = []
    for leader, n in top:
        share = 100.0 * n / total
        lis.append(
            f'            <li><a href="/{leader["page"]}">{leader["name"]}</a>'
            f'<span class="share">{n} lists · {share:.0f}%</span></li>'
        )
    return f"""        <section class="meta-strip" id="meta">
          <div class="section-title">
            <h3>Lists on this site</h3>
            <a href="/format.html">Format →</a>
          </div>
          <p class="muted format-note">Counts are 50-card pages hosted here, not Limitless points. English events are still OP16; OP17 English is 28 August 2026.</p>
          <ol>
{chr(10).join(lis)}
          </ol>
        </section>
"""


def color_label(leader: dict) -> str:
    raw = (leader.get("color") or "").replace("color-", "")
    return "/".join(part.capitalize() for part in raw.split("-") if part)


def leader_list_html(rows: list[tuple[dict, int]]) -> str:
    by_id = {L["id"]: n for L, n in rows}
    items = []
    for leader in gen.LEADERS:
        bits = []
        if leader.get("nav_op17"):
            bits.append("OP17")
        bits.append(color_label(leader))
        bits.append(leader["id"])
        n = by_id.get(leader["id"], 0)
        if n:
            bits.append(f"{n} lists")
        elif leader.get("nav_op17"):
            bits.append("preview")
        items.append(
            f"""            <li>
              <a href="/{leader["page"]}">{leader["name"]}</a>
              <span class="muted">{" · ".join(bits)}</span>
            </li>"""
        )
    return "\n".join(items)


RECENT_LIMIT = 100


def collect_home_lists() -> list[dict]:
    index_path = ROOT / "data/tournament-decks.json"
    comm_path = ROOT / "data/community-decks.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    community = json.loads(comm_path.read_text()) if comm_path.exists() else {}
    rows = []
    seen = set()
    for leader in gen.LEADERS:
        for item in index.get(leader["id"]) or []:
            href = item.get("href") or ""
            if item.get("kind") == "sample" or not href:
                continue
            if not (ROOT / href.lstrip("/")).exists():
                continue
            if href in seen:
                continue
            seen.add(href)
            row = dict(item)
            row["leader"] = leader
            row["tournament_name"] = row.get("tournament_name") or row.get("tournament") or ""
            rows.append(row)
        for item in community.get(leader["id"]) or []:
            href = item.get("href") or ""
            if not href or href in seen:
                continue
            if not (ROOT / href.lstrip("/")).exists():
                continue
            seen.add(href)
            rows.append(
                {
                    "slug": item.get("slug"),
                    "href": href,
                    "player": item.get("player") or "Community",
                    "tournament_name": item.get("subtitle") or item.get("title") or "",
                    "placing": None,
                    "date": item.get("date") or "",
                    "kind": item.get("kind") or "web",
                    "title_override": item.get("title"),
                    "subtitle": item.get("subtitle")
                    or {"youtube": "YouTube list", "x": "X list", "web": "Community list"}.get(
                        item.get("kind"), "Community list"
                    ),
                    "leader": leader,
                }
            )
    return rows


def pick_recent_lists(rows: list[dict], limit: int = RECENT_LIMIT) -> list[dict]:
    by_leader: dict[str, list[dict]] = {}
    for row in rows:
        by_leader.setdefault(row["leader"]["id"], []).append(row)
    for lid, items in by_leader.items():
        items.sort(key=gen.date_sort_key, reverse=True)
    picked = []
    seen = set()
    for leader in gen.LEADERS:
        items = by_leader.get(leader["id"]) or []
        if not items:
            continue
        first = items[0]
        picked.append(first)
        seen.add(first["href"])
    rest = [row for row in rows if row["href"] not in seen]
    rest.sort(key=gen.date_sort_key, reverse=True)
    for row in rest:
        picked.append(row)
        if len(picked) >= limit:
            break
    picked.sort(key=gen.date_sort_key, reverse=True)
    return picked[:limit]


def recent_rows_html(rows: list[dict]) -> str:
    items = []
    for entry in rows:
        leader = entry["leader"]
        title, subtitle = gen.list_heading(entry, leader["name"])
        when = entry.get("date") or gen.ordinal(entry.get("placing")) or "List"
        img = gen.card_image_url(leader["id"])
        items.append(
            f"""            <li>
              <a class="recent-item {html.escape(leader['color'])}" href="{html.escape(entry['href'])}">
                <img class="recent-leader" src="{html.escape(img)}" alt="{html.escape(leader['name'])}" />
                <div class="recent-copy">
                  <div class="who">{html.escape(title)}</div>
                  <div class="muted meta">{html.escape(subtitle)}</div>
                </div>
                <div class="when">{html.escape(str(when))}</div>
              </a>
            </li>"""
        )
    return "\n".join(items)


def render_home_body() -> str:
    cards = leader_cards_html()
    return f"""        <!-- HOME_BODY -->
        <div class="home-jump">
          <a class="home-jump-leaders" href="/decklists/op17.html">Leaders</a>
          <a class="home-jump-recent" href="/lists.html">Lists</a>
        </div>
        <h2>One Piece Deck Base</h2>
        <p>Every leader on this site. Open a picture, or use Leaders and Lists above.</p>
        <div class="leader-cards home-cards" aria-label="All leader card pictures">
{cards}
        </div>
        <!-- /HOME_BODY -->"""


def render_lists_page() -> str:
    recent = pick_recent_lists(collect_home_lists())
    body = f"""        <div class="crumb"><a href="/">Home</a> / Lists</div>
        <h2>Lists</h2>
        <p>Newest 50-card lists first. At least one list from each leader, then the latest results.</p>
        <section id="recent">
          <div class="section-title">
            <h3>Recent lists</h3>
            <div class="muted">{len(recent)} lists</div>
          </div>
          <ul class="recent-list" aria-label="Recent decklists">
{recent_rows_html(recent)}
          </ul>
        </section>"""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Recent OPTCG lists | One Piece Deck Base</title>
  <meta name="description" content="The newest One Piece TCG decklists, with a small color-coded leader picture on every row." />
  <link rel="stylesheet" href="{CSS_NEW}" />
</head>
<body>
  <div class="wrap">
    <header>
      <a class="brand" href="/">
        <div class="logo">OP</div>
        <div>
          <h1>One Piece Deck Base</h1>
          <div class="subtitle">OPTCG decklists</div>
        </div>
      </a>
      <nav aria-label="Primary">
        <a href="/lists.html" aria-current="page">Lists</a>
        <a href="/decklists/op17.html">Leaders</a>
        <a href="/format.html">Format</a>
        <a href="https://discord.gg/adZ2WUQ3D" target="_blank" rel="noopener">Discord</a>
      </nav>
    </header>
    <main class="single">
      <div class="card hero">
{body}
      </div>
    </main>
    <footer>
      © <span id="year"></span> One Piece Deck Base — Fan site, not affiliated with Bandai or Shueisha.
      <a href="/decklists/op17.html">Leaders</a> · <a href="/lists.html">Lists</a> · <a href="/format.html">Format</a> · <a href="/guides/">Guides</a>
    </footer>
  </div>
  <script>
    document.getElementById('year').textContent = new Date().getFullYear();
  </script>
  <script src="{JS_NEW}"></script>
</body>
</html>
"""


def leader_cards_html() -> str:
    cards = []
    for leader in gen.LEADERS:
        img = gen.card_image_url(leader["id"])
        cards.append(
            f"""            <a class="leader-card-link" href="/{leader["page"]}">
              <img src="{img}" alt="{leader["name"]} leader card" />
              <div class="caption">{leader["name"]}</div>
            </a>"""
        )
    return "\n".join(cards)


def patch_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text()
    body = render_home_body()
    if "<!-- HOME_BODY -->" in text:
        text = re.sub(
            r"        <!-- HOME_BODY -->.*?        <!-- /HOME_BODY -->",
            body,
            text,
            count=1,
            flags=re.S,
        )
    else:
        text = re.sub(
            r"        <h2>One Piece Deck Base</h2>.*?(?=\n      </div>\n    </main>)",
            body,
            text,
            count=1,
            flags=re.S,
        )
    text = text.replace(
        "Leader pictures and recent 50-card lists.",
        "Leader pictures plus a Lists page with recent 50-card decks.",
    )
    text = text.replace('href="/#decklists"', 'href="/lists.html"')
    text = text.replace('href="/#recent"', 'href="/lists.html"')
    text = patch_nav_and_assets(text)
    path.write_text(text)
    lists_path = ROOT / "lists.html"
    lists_path.write_text(render_lists_page())
    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists() and "https://onepiecedeckbase.com/lists.html" not in sitemap.read_text():
        sitemap.write_text(
            sitemap.read_text().replace(
                "</urlset>",
                "  <url><loc>https://onepiecedeckbase.com/lists.html</loc></url>\n</urlset>\n",
                1,
            )
        )
    print("home leaders", len(gen.LEADERS), "lists page", RECENT_LIMIT)


def patch_op17() -> None:
    path = ROOT / "decklists/op17.html"
    text = path.read_text()
    rows = meta_rows()
    n = len(gen.LEADERS)
    text = patch_nav_and_assets(text)
    text = re.sub(r'<div class="muted">\d+ leaders</div>', f'<div class="muted">{n} leaders</div>', text, count=1)
    ol = '          <ol class="text-leader-list" aria-label="All leader pages">\n' + leader_list_html(rows) + "\n          </ol>"
    text = re.sub(
        r'          <ol class="text-leader-list" aria-label="All leader pages">.*?</ol>',
        ol,
        text,
        count=1,
        flags=re.S,
    )
    grid = (
        '          <div class="leader-cards" aria-label="All leader card pictures">\n'
        + leader_cards_html()
        + "\n          </div>"
    )
    text = re.sub(
        r'          <div class="leader-cards" aria-label="All leader card pictures">.*?\n        </section>',
        grid + "\n        </section>",
        text,
        count=1,
        flags=re.S,
    )
    path.write_text(text)
    print("leaders page", n)


def main() -> None:
    cache = gen.load_card_cache()
    for leader in gen.LEADERS:
        hub = ROOT / leader["page"]
        if hub.exists():
            hub.write_text(patch_nav_and_assets(hub.read_text()))
        d = ROOT / leader["dir"]
        if not d.exists():
            continue
        for path in d.glob("*.html"):
            upgrade_list_page(path, leader, cache)
    patch_home()
    patch_op17()
    n = 0
    for path in ROOT.rglob("*.html"):
        if any(p in path.parts for p in (".git", "scripts", "node_modules", "shop", "discord-bot", "ballkeep")):
            continue
        text = path.read_text()
        new = patch_lists_nav(text)
        if new != text:
            path.write_text(new)
            n += 1
    print("upgraded html", "lists-nav", n)


if __name__ == "__main__":
    main()
