#!/usr/bin/env python3
"""Patch public HTML for crawlable internal links and basic on-page SEO.

Does not wipe decklist pages. Safe to re-run.
"""

from __future__ import annotations

import html
import importlib.util
import json
import re
from datetime import date
from pathlib import Path

spec = importlib.util.spec_from_file_location("genlists", "/workspace/scripts/generate-tournament-lists.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

sspec = importlib.util.spec_from_file_location("seocommon", "/workspace/scripts/seo_common.py")
seo = importlib.util.module_from_spec(sspec)
sspec.loader.exec_module(seo)

gspec = importlib.util.spec_from_file_location("seopages", "/workspace/scripts/generate-seo-pages.py")
seopages = importlib.util.module_from_spec(gspec)
gspec.loader.exec_module(seopages)

ROOT = gen.ROOT
SITE = seo.SITE
LEADERS = gen.LEADERS
BY_ID = {L["id"]: L for L in LEADERS}
BY_PAGE = {L["page"]: L for L in LEADERS}
BY_DIR = {L["dir"]: L for L in LEADERS}

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"', re.I)
CANON_RE = re.compile(r'<link rel="canonical" href="[^"]*"\s*/?>\s*', re.I)
OG_RE = re.compile(r'\n?  <meta (?:property="og:|name="twitter:)[^>]*>\s*', re.I)
JSONLD_RE = re.compile(r'\n?  <script type="application/ld\+json">.*?</script>\s*', re.S)
IMG_RE = re.compile(r"<img\b([^>]*)>", re.I)
SKIP_PARTS = {".git", "scripts", "node_modules", "discord-bot", "ballkeep"}
SKIP_FILES = {"shop/custom-leaders.html"}


def log(*args) -> None:
    print(*args, flush=True)


def load_index() -> dict:
    path = ROOT / "data/tournament-decks.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def public_html() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.html"):
        if any(part in p.parts for part in SKIP_PARTS):
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel in SKIP_FILES:
            continue
        out.append(p)
    return out


def leader_for_path(rel: str) -> dict | None:
    if rel in BY_PAGE:
        return BY_PAGE[rel]
    for L in LEADERS:
        if rel.startswith(L["dir"] + "/"):
            return L
    return None


def href_for_entry(leader: dict, entry: dict) -> str:
    return entry.get("href") or f"/{leader['dir']}/{entry['slug']}.html"


def event_siblings(index: dict, leader: dict, slug: str, limit: int = 5) -> list[tuple[str, str, str]]:
    rows = index.get(leader["id"]) or []
    current = next((r for r in rows if r.get("slug") == slug), None)
    if not current:
        return []
    event = (current.get("tournament") or "").strip()
    if not event:
        return []
    out = []
    for r in rows:
        if r.get("slug") == slug:
            continue
        if (r.get("tournament") or "").strip() != event:
            continue
        other = BY_ID.get(leader["id"])
        if not other:
            continue
        player = r.get("player") or "List"
        place = r.get("placing")
        place_s = f"{place}" if place is not None else "list"
        out.append((href_for_entry(leader, r), f"{player} — {leader['name']}", f"{event} · {place_s}"))
        if len(out) >= limit:
            break
    return out


def other_leaders_same_event(index: dict, leader: dict, slug: str, limit: int = 4) -> list[tuple[str, str, str]]:
    rows = index.get(leader["id"]) or []
    current = next((r for r in rows if r.get("slug") == slug), None)
    if not current:
        return []
    event = (current.get("tournament") or "").strip()
    date_s = (current.get("date") or "")[:10]
    if not event:
        return []
    out = []
    seen = set()
    for lid, items in index.items():
        if lid == leader["id"]:
            continue
        L = BY_ID.get(lid)
        if not L:
            continue
        for r in items:
            if (r.get("tournament") or "").strip() != event:
                continue
            if date_s and (r.get("date") or "")[:10] != date_s:
                continue
            if lid in seen:
                continue
            seen.add(lid)
            player = r.get("player") or L["name"]
            out.append((href_for_entry(L, r), f"{player} — {L['name']}", f"Same event · {L['name']}"))
            break
        if len(out) >= limit:
            break
    return out


def related_leader_rows(leader: dict) -> list[str]:
    rows = []
    for lid in seo.RELATED_LEADERS.get(leader["id"], []):
        other = BY_ID.get(lid)
        if not other or other["id"] == leader["id"]:
            continue
        rows.append(
            seo.list_row(
                "/" + other["page"],
                f"{other['name']} decklists",
                f"{other['id']} · related constructed leader",
            )
        )
    return rows


def character_siblings(slug: str, limit: int = 8) -> list[str]:
    rows = []
    for name, cslug in seo.crew_siblings(slug, seopages.CHARACTERS, limit=limit):
        rows.append(
            seo.list_row(
                f"/guides/characters/{cslug}.html",
                name,
                "Same OPTCG family · character guide",
            )
        )
    return rows


def topic_siblings(slug: str, limit: int = 8) -> list[str]:
    topics = seopages.TOPICS
    idx = next((i for i, t in enumerate(topics) if t["slug"] == slug), None)
    if idx is None:
        return []
    rows = []
    n = len(topics)
    for off in range(1, n):
        other = topics[(idx + off) % n]
        if other["slug"] == slug:
            continue
        rows.append(
            seo.list_row(
                f"/guides/{other['slug']}.html",
                other["h2"],
                "More One Piece TCG guides",
            )
        )
        if len(rows) >= limit:
            break
    return rows


def deck_related_html(rel: str, index: dict) -> str:
    leader = leader_for_path(rel)
    if not leader:
        return ""
    slug = Path(rel).stem
    rows: list[str] = []
    rows.append(
        seo.list_row(
            "/" + leader["page"],
            f"More {leader['name']} lists",
            f"{leader['id']} hub · every 50-card list for this leader",
        )
    )
    guide = seo.LEADER_GUIDE.get(leader["key"])
    if guide:
        rows.append(
            seo.list_row(
                f"/guides/characters/{guide}.html",
                f"{leader['name']} character guide",
                "Names, crew, and related OPTCG leaders",
            )
        )
    for href, title, note in event_siblings(index, leader, slug):
        rows.append(seo.list_row(href, title, note))
    for href, title, note in other_leaders_same_event(index, leader, slug):
        rows.append(seo.list_row(href, title, note))
    rows.extend(related_leader_rows(leader)[:3])
    rows.append(seo.list_row("/format.html", "OPTCG format and banlist", "Standard rules, banned cards, rotation"))
    rows.append(seo.list_row("/shop/sleeves.html", "Sleeves for a 50-card list", "Shop · Dragon Shield packs"))
    return seo.related_section("Related pages", "More lists and guides", rows)


def hub_related_html(leader: dict) -> str:
    rows = related_leader_rows(leader)
    rows.append(seo.list_row("/decklists/op17.html", "All leader pages", "Every constructed leader on this site"))
    guide = seo.LEADER_GUIDE.get(leader["key"])
    if guide:
        rows.append(
            seo.list_row(
                f"/guides/characters/{guide}.html",
                f"{leader['name']} character guide",
                "Crew names mapped to this leader",
            )
        )
    rows.append(seo.list_row("/guides/", "One Piece TCG guides", "Topics and character pages"))
    rows.append(seo.list_row("/format.html", "Format and banlist", "Standard constructed rules"))
    rows.append(seo.list_row("/#recent", "Recent lists", "Newest 50-card results"))
    return seo.related_section("Related pages", "Other leaders and guides", rows)


def shop_related_html(rel: str) -> str:
    rows = []
    for href, label in seo.SHOP_PAGES:
        target = "shop/index.html" if href == "/shop/" else href.lstrip("/")
        if target == rel:
            continue
        rows.append(seo.list_row(href, label, "Amazon shop · OPTCG table gear"))
    rows.append(seo.list_row("/decklists/op17.html", "Leader decklists", "50-card OPTCG lists"))
    return seo.related_section("Also in the shop", "Other gear pages", rows)


def character_related_extra(slug: str) -> str:
    rows = character_siblings(slug)
    if not rows:
        return ""
    rows.append(seo.list_row("/guides/characters/", "All character guides", "Every name mapped to an OPTCG list"))
    return seo.related_section("Related character guides", "Same crew or constructed family", rows)


def topic_related_extra(slug: str) -> str:
    rows = topic_siblings(slug)
    rows.append(seo.list_row("/guides/characters/", "Character guides", "Names from the manga mapped to OPTCG lists"))
    rows.append(seo.list_row("/decklists/op17.html", "All leader pages", "Constructed OPTCG hubs"))
    return seo.related_section("More guides", "Same series of One Piece TCG pages", rows)


def insert_related(text: str, block: str) -> str:
    if not block:
        return text
    text = seo.strip_related(text)
    markers = [
        '        <p class="muted" style="margin-top:22px">',
        '        <p class="muted" style="margin-top:18px">',
        '        <p class="amazon-disclosure-line">',
        "        <!-- CARD_POOL_HEADING -->",
        "      </div>\n    </main>",
    ]
    for mark in markers:
        if mark in text:
            return text.replace(mark, block + mark, 1)
    return text.replace("</main>", block + "    </main>", 1)


def page_title_desc(text: str, rel: str) -> tuple[str, str]:
    tm = TITLE_RE.search(text)
    dm = DESC_RE.search(text)
    title = html.unescape(tm.group(1).strip()) if tm else ""
    desc = html.unescape(dm.group(1).strip()) if dm else ""
    h2 = re.search(r"<h2>(.*?)</h2>", text, re.S)
    h2t = re.sub(r"<[^>]+>", "", h2.group(1)).strip() if h2 else ""
    first_p = re.search(r"<p>(.*?)</p>", text, re.S)
    ptxt = re.sub(r"<[^>]+>", " ", first_p.group(1) if first_p else "")
    ptxt = re.sub(r"\s+", " ", ptxt).strip()

    leader = leader_for_path(rel)
    if rel in BY_PAGE and leader:
        title = f"{leader['name']} OPTCG decklists ({leader['id']}) | One Piece Deck Base"
        desc = desc or f"{leader['name']} 50-card One Piece TCG lists. Open tournament and community decks for {leader['id']}."
    elif leader and rel.startswith(leader["dir"] + "/"):
        if title in ("Home", "Untitled", "") or len(title) < 8:
            title = h2t or title or "OPTCG decklist"
        if "OPTCG" not in title and "One Piece Deck Base" not in title:
            title = f"{title} | OPTCG"
        if not desc:
            desc = f"{leader['name']} OPTCG decklist. {ptxt}"[:160]
    elif rel == "index.html":
        title = title or "One Piece TCG Decklists (OPTCG) | One Piece Deck Base"
        desc = desc or "OPTCG decklists for the Bandai ONE PIECE CARD GAME. Leader pictures and recent 50-card lists."
    elif not title or title in ("Home", "Untitled"):
        title = f"{h2t or 'One Piece TCG'} | One Piece Deck Base"
    if not desc:
        desc = (ptxt or title)[:160]
    if len(desc) > 170:
        desc = desc[:157].rstrip() + "…"
    return title, desc


def ensure_head(text: str, rel: str, title: str, desc: str) -> str:
    url = seo.canonical_url(rel)
    image = seo.og_image_for(rel, LEADERS)
    crumbs = seo.parse_crumbs(text)
    if crumbs[-1][1] == "":
        crumbs[-1] = (crumbs[-1][0], url.replace(SITE, "") or "/")
    extras = (
        f'  <link rel="canonical" href="{html.escape(url, quote=True)}" />\n'
        + seo.social_tags(title, desc, url, image)
        + seo.breadcrumb_jsonld(crumbs)
    )
    text = CANON_RE.sub("", text)
    text = OG_RE.sub("", text)
    text = JSONLD_RE.sub("", text)
    if TITLE_RE.search(text):
        text = TITLE_RE.sub(f"<title>{html.escape(title)}</title>", text, count=1)
    else:
        text = text.replace("</head>", f"  <title>{html.escape(title)}</title>\n</head>", 1)
    if DESC_RE.search(text):
        text = DESC_RE.sub(f'<meta name="description" content="{html.escape(desc)}"', text, count=1)
    else:
        text = text.replace("</title>", f'</title>\n  <meta name="description" content="{html.escape(desc)}" />', 1)
    if "</head>" in text:
        text = text.replace("</head>", extras + "</head>", 1)
    elif "</title>" in text:
        text = text.replace("</title>", "</title>\n" + extras.rstrip("\n"), 1)
    return text


def patch_nav_footer(text: str) -> str:
    text = text.replace('href="/#decklists"', 'href="/#recent"')
    text = text.replace('href="#decklists"', 'href="/#recent"')
    text = re.sub(
        r'<a href="/#recent"(?: aria-current="page")?>Decklists</a>',
        '<a href="/#recent">Recent lists</a>',
        text,
    )
    if 'href="/guides/"' not in text.split("<nav", 1)[-1].split("</nav>", 1)[0] if "<nav" in text else "":
        text = text.replace(
            '        <a href="/format.html">Format</a>\n        <a href="/shop/">Shop</a>',
            '        <a href="/format.html">Format</a>\n        <a href="/guides/">Guides</a>\n        <a href="/shop/">Shop</a>',
        )
        text = text.replace(
            '        <a href="/format.html" aria-current="page">Format</a>\n        <a href="/shop/">Shop</a>',
            '        <a href="/format.html" aria-current="page">Format</a>\n        <a href="/guides/">Guides</a>\n        <a href="/shop/">Shop</a>',
        )
        text = text.replace(
            '        <a href="/format.html">Format</a>\n        <a href="/shop/" aria-current="page">Shop</a>',
            '        <a href="/format.html">Format</a>\n        <a href="/guides/">Guides</a>\n        <a href="/shop/" aria-current="page">Shop</a>',
        )
    text = re.sub(r'href="/css/site\.css(?:\?[^"]*)?"', f'href="/css/site.css?v={seo.CSS_VER}"', text)
    if 'href="/guides/">Guides</a>' not in text.split("<footer", 1)[-1] if "<footer" in text else "":
        text = text.replace(
            '      <a href="/shop/">Shop</a> · <a href="/privacy.html">Privacy</a>',
            seo.FOOTER_LINKS,
        )
        if 'href="/guides/">Guides</a>' not in (text.split("<footer", 1)[-1] if "<footer" in text else ""):
            text = re.sub(
                r"(<footer>\s*)",
                r"\1" + seo.FOOTER_LINKS + "\n",
                text,
                count=1,
            )
    return text


def ensure_img_alt(text: str) -> str:
    def repl(m: re.Match) -> str:
        attrs = m.group(1)
        if re.search(r"\balt\s*=", attrs, re.I):
            attrs2 = re.sub(r'\balt=""', 'alt="One Piece TCG card"', attrs)
            attrs2 = re.sub(r"\balt=''", "alt='One Piece TCG card'", attrs2)
            return f"<img{attrs2}>"
        src = re.search(r'\bsrc="([^"]+)"', attrs)
        name = Path(src.group(1)).stem.replace("-", " ") if src else "One Piece TCG"
        if "opdb-hero" in (src.group(1) if src else ""):
            name = "One Piece Deck Base hero art"
        return f'<img{attrs} alt="{html.escape(name)}" />' if attrs.endswith("/") else f'<img{attrs} alt="{html.escape(name)}">'

    return IMG_RE.sub(repl, text)


def homepage_org_jsonld() -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "One Piece Deck Base",
        "url": SITE + "/",
        "description": "OPTCG decklists for the Bandai ONE PIECE CARD GAME.",
    }
    return (
        '  <script type="application/ld+json">'
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + "</script>\n"
    )


def patch_file(path: Path, index: dict) -> tuple[bool, str]:
    rel = path.relative_to(ROOT).as_posix()
    orig = path.read_text()
    text = orig
    leader = leader_for_path(rel)

    if rel == "index.html":
        text = text.replace('alt="OPDB"', 'alt="One Piece Deck Base, an OPTCG decklist site"')
        if 'href="/guides/"' not in text.split("home-leaders-intro", 1)[-1][:800]:
            text = text.replace(
                "<p>Pick a picture. Each page has lists for that leader.</p>",
                '<p>Pick a picture. Each page has lists for that leader. Character names live in the <a href="/guides/">guides</a>.</p>',
                1,
            )

    block = ""
    if leader and rel.startswith(leader["dir"] + "/") and rel != leader["page"]:
        block = deck_related_html(rel, index)
    elif leader and rel == leader["page"]:
        block = hub_related_html(leader)
    elif rel.startswith("shop/") and rel != "shop/custom-leaders.html":
        block = shop_related_html(rel)
    elif rel.startswith("guides/characters/") and not rel.endswith("index.html"):
        slug = Path(rel).stem
        block = character_related_extra(slug)
    elif rel.startswith("guides/") and rel not in ("guides/index.html", "guides/characters/index.html"):
        slug = Path(rel).stem
        block = topic_related_extra(slug)
    elif rel == "decklists/op17.html":
        rows = [
            seo.list_row("/#recent", "Recent lists", "Newest 50-card results on the homepage"),
            seo.list_row("/format.html", "Format and banlist", "Standard constructed rules"),
            seo.list_row("/guides/", "One Piece TCG guides", "Topics and character names"),
            seo.list_row("/shop/", "Shop", "Sleeves, dice, playmats, deck boxes"),
        ]
        block = seo.related_section("Related pages", "Around the site", rows)
    elif rel == "format.html":
        rows = [
            seo.list_row("/decklists/op17.html", "All leader pages", "Constructed OPTCG hubs"),
            seo.list_row("/guides/constructed.html", "Constructed guide", "What 50-card OPTCG means"),
            seo.list_row("/guides/", "More guides", "Topics and character pages"),
        ]
        block = seo.related_section("Related pages", "Lists and guides", rows)

    if block:
        text = insert_related(text, block)

    text = patch_nav_footer(text)
    text = ensure_img_alt(text)
    title, desc = page_title_desc(text, rel)
    text = ensure_head(text, rel, title, desc)
    if rel == "index.html" and "WebSite" not in text:
        text = text.replace("</head>", homepage_org_jsonld() + "</head>", 1)

    if text != orig:
        path.write_text(text)
        return True, "patched"
    return False, "ok"


def rewrite_sitemap() -> None:
    skip = SKIP_PARTS
    urls = []
    today = date.today().isoformat()
    for p in sorted(public_html()):
        rel = p.relative_to(ROOT).as_posix()
        url = seo.canonical_url(rel)
        urls.append(url)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        lines.append(f"  <url><loc>{html.escape(url)}</loc><lastmod>{today}</lastmod></url>")
    lines.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("\n".join(lines))
    log("sitemap", len(urls), "lastmod", today)


def audit(paths: list[Path]) -> None:
    missing_title = missing_desc = missing_canon = missing_alt = weak_title = 0
    for p in paths:
        text = p.read_text()
        tm = TITLE_RE.search(text)
        title = tm.group(1).strip() if tm else ""
        if not title or title in ("Home", "Untitled"):
            missing_title += 1
        elif len(title) < 12:
            weak_title += 1
        if not DESC_RE.search(text):
            missing_desc += 1
        if not CANON_RE.search(text):
            missing_canon += 1
        for m in IMG_RE.finditer(text):
            attrs = m.group(1)
            if not re.search(r"\balt\s*=", attrs, re.I) or re.search(r'\balt=""', attrs):
                missing_alt += 1
                break
    log(
        "audit pages",
        len(paths),
        "no/weak title",
        missing_title,
        "short title",
        weak_title,
        "no desc",
        missing_desc,
        "no canonical",
        missing_canon,
        "img missing alt",
        missing_alt,
    )


def main() -> None:
    index = load_index()
    paths = public_html()
    log("scan", len(paths), "html pages")
    audit(paths)
    changed = 0
    for p in paths:
        ok, _why = patch_file(p, index)
        if ok:
            changed += 1
    log("patched", changed)
    rewrite_sitemap()
    audit(public_html())
    log("seo enhance done")


if __name__ == "__main__":
    main()
