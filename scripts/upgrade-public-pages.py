#!/usr/bin/env python3
"""Upgrade existing HTML with copy buttons, list stats, Format nav, and site.js.

Does not wipe list pages. Does not run generate-tournament-lists.main().
"""

from __future__ import annotations

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
CSS_NEW = "/css/site.css?v=copy-sim"
JS_NEW = "/js/site.js?v=copy-sim"
COPY_BTN = '<button type="button" class="copy-sim" data-copy-sim>Copy for OPTCGSim</button>'
TEXT_DECK_TITLE_RE = re.compile(
    r'(<section class="text-deck">\s*<div class="section-title">)(.*?)(^\s*</div>)',
    re.S | re.M,
)
BROKEN_COPY_RE = re.compile(
    r'(<div class="muted">)([^<]*?)\s*<button type="button" class="copy-sim" data-copy-sim>Copy for OPTCGSim</button>\s*</div>\s*</div>',
    re.S,
)
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


def ensure_copy_button(text: str) -> str:
    text = text.replace(">Copy for sim<", ">Copy for OPTCGSim<")
    text = BROKEN_COPY_RE.sub(
        rf'\1\2</div>\n            {COPY_BTN}\n          </div>',
        text,
    )
    def add_btn(match: re.Match[str]) -> str:
        inner = match.group(2)
        if "data-copy-sim" in inner:
            return match.group(0)
        return f"{match.group(1)}{inner}\n            {COPY_BTN}\n{match.group(3)}"

    return TEXT_DECK_TITLE_RE.sub(add_btn, text)


def patch_nav_and_assets(text: str) -> str:
    text = re.sub(r'href="/css/site\.css(?:\?[^"]*)?"', f'href="{CSS_NEW}"', text)
    text = re.sub(r'src="/js/site\.js(?:\?[^"]*)?"', f'src="{JS_NEW}"', text)
    for old, new in NAV_OLD_PATTERNS:
        text = text.replace(old, new)
    if "/js/site.js" not in text:
        text = text.replace("</body>", f'  <script src="{JS_NEW}"></script>\n</body>')
    return ensure_copy_button(text)


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
    rows = meta_rows()
    n_leaders = len(gen.LEADERS)
    text = re.sub(
        r"All \d+ leader pages on this site\. Click a name or a card picture\.",
        f"All {n_leaders} leader pages on this site. Click a name or a card picture.",
        text,
        count=1,
    )
    if "Format &amp; banlist" not in text:
        text = text.replace(
            '<a class="home-ghost" href="/decklists/op17.html">All leader pages</a>',
            '<a class="home-ghost" href="/decklists/op17.html">All leader pages</a>\n          <a class="home-ghost" href="/format.html">Format &amp; banlist</a>',
            1,
        )
    text = patch_nav_and_assets(text)
    strip = render_meta_strip(rows)
    if 'id="meta"' in text:
        text = re.sub(r'        <section class="meta-strip" id="meta">.*?</section>\n', strip, text, count=1, flags=re.S)
    else:
        text = text.replace(
            '        <section id="decklists">',
            strip + "\n        <section id=\"decklists\">",
            1,
        )
    ol = '          <ol class="text-leader-list" aria-label="All leader pages">\n' + leader_list_html(rows) + "\n          </ol>"
    text = re.sub(
        r'          <ol class="text-leader-list" aria-label="All leader pages">.*?</ol>',
        ol,
        text,
        count=1,
        flags=re.S,
    )
    grid = '          <div class="leader-cards home-cards" aria-label="All leader card pictures" style="margin-top:18px">\n' + leader_cards_html() + "\n          </div>"
    text = re.sub(
        r'          <div class="leader-cards home-cards" aria-label="All leader card pictures"[^>]*>.*?</div>\n        </section>',
        grid + "\n        </section>",
        text,
        count=1,
        flags=re.S,
    )
    if 'href="/format.html"' not in text.split("footer")[-1]:
        text = text.replace(
            '<a href="/guides/">Guides</a>',
            '<a href="/format.html">Format</a> · <a href="/guides/">Guides</a>',
            1,
        )
    path.write_text(text)
    print("home leaders", n_leaders)


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
    grid = '          <div class="leader-cards" aria-label="All leader card pictures">\n' + leader_cards_html() + "\n          </div>"
    text = re.sub(
        r'          <div class="leader-cards" aria-label="All leader card pictures">.*?</div>',
        grid,
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
    # leftover html (guides, format)
    for path in ROOT.rglob("*.html"):
        if any(p in path.parts for p in (".git", "scripts", "node_modules", "shop", "discord-bot", "ballkeep")):
            continue
        text = path.read_text()
        new = patch_nav_and_assets(text)
        if new != text:
            path.write_text(new)
    print("upgraded html")


if __name__ == "__main__":
    main()
