#!/usr/bin/env python3
"""Shared SEO chrome: canonical/OG tags, related-page links, nav, footer."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path("/workspace")
SITE = "https://onepiecedeckbase.com"
DEFAULT_OG = f"{SITE}/img/opdb-hero.jpg"
CSS_VER = "seo-links"

# Leader id -> nearby constructed pages (same color family, same set, or same character).
RELATED_LEADERS: dict[str, list[str]] = {
    "OP17-001": ["OP16-001", "OP13-002", "OP17-039"],
    "OP17-020": ["OP14-020", "OP13-001", "OP17-079"],
    "OP17-039": ["OP17-001", "OP17-058", "OP17-099"],
    "OP17-058": ["OP16-079", "OP17-039", "OP17-099"],
    "OP17-079": ["OP13-001", "OP16-022", "OP11-040"],
    "OP17-099": ["OP11-062", "OP08-058", "OP17-058"],
    "OP13-001": ["OP17-079", "OP16-022", "OP11-040"],
    "OP11-041": ["OP17-020", "OP13-001", "OP17-079"],
    "OP14-020": ["OP17-020", "OP13-001", "OP12-061"],
    "OP16-001": ["OP13-002", "OP17-001", "OP17-079"],
    "OP13-002": ["OP16-001", "OP17-001", "OP15-002"],
    "OP13-079": ["OP17-079", "OP16-080", "OP17-039"],
    "OP15-058": ["OP11-062", "OP16-060", "OP17-058"],
    "OP11-062": ["OP08-058", "OP17-099", "OP15-058"],
    "OP16-022": ["OP13-001", "OP17-079", "OP11-040"],
    "OP16-080": ["OP13-079", "OP16-041", "OP17-039"],
    "OP12-061": ["OP14-060", "OP14-020", "OP08-058"],
    "OP15-002": ["OP13-001", "OP13-002", "OP16-022"],
    "OP16-079": ["OP17-058", "OP17-079", "OP13-079"],
    "OP11-001": ["OP16-060", "OP17-001", "OP16-080"],
    "OP14-060": ["OP12-061", "OP08-058", "OP17-099"],
    "OP16-041": ["OP16-022", "OP16-080", "OP15-002"],
    "OP16-060": ["OP11-001", "OP15-058", "OP11-062"],
    "OP11-040": ["OP13-001", "OP16-022", "OP17-079"],
    "OP08-058": ["OP11-062", "OP17-099", "OP12-061"],
}

LEADER_GUIDE: dict[str, str] = {
    "edward-newgate": "edward-newgate",
    "shanks": "shanks",
    "rocks-d-xebec": "rocks-d-xebec",
    "kaido": "kaido",
    "monkey-d-luffy": "monkey-d-luffy",
    "charlotte-linlin": "charlotte-linlin",
    "rg-luffy": "monkey-d-luffy",
    "nami": "nami",
    "mihawk": "dracule-mihawk",
    "portgas-d-ace": "portgas-d-ace",
    "op13-ace": "portgas-d-ace",
    "imu": "imu",
    "enel": "enel",
    "charlotte-katakuri": "charlotte-katakuri",
    "gb-luffy": "monkey-d-luffy",
    "blackbeard": "marshall-d-teach",
    "rosinante": "rosinante",
    "lucy": "lucy",
    "yamato": "yamato",
    "koby": "koby",
    "doffy": "donquixote-doflamingo",
    "buggy": "buggy",
    "sengoku": "sengoku",
    "up-luffy": "up-luffy",
    "charlotte-pudding": "charlotte-pudding",
}

SHOP_PAGES = [
    ("/shop/", "Shop home"),
    ("/shop/sleeves.html", "Sleeves"),
    ("/shop/dice.html", "Dice"),
    ("/shop/playmats.html", "Playmats"),
    ("/shop/deck-boxes.html", "Deck boxes"),
    ("/shop/extras.html", "Table extras"),
]


def canonical_url(rel: str) -> str:
    rel = rel.lstrip("/")
    if rel in ("index.html", ""):
        return f"{SITE}/"
    if rel.endswith("/index.html"):
        return f"{SITE}/{rel[: -len('index.html')]}"
    return f"{SITE}/{rel}"


def leader_by_id(leaders: list[dict], lid: str) -> dict | None:
    return next((L for L in leaders if L["id"] == lid), None)


def leader_by_key(leaders: list[dict], key: str) -> dict | None:
    return next((L for L in leaders if L["key"] == key), None)


def og_image_for(rel: str, leaders: list[dict]) -> str:
    rel = rel.lstrip("/")
    for L in leaders:
        if rel == L["page"] or rel.startswith(L["dir"] + "/"):
            cid = L["id"]
            set_code = cid.split("-")[0]
            return f"https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/one-piece/{set_code}/{cid}_EN.webp"
    if rel.startswith("shop/"):
        return f"{SITE}/img/shop/sleeve-jet.jpg"
    return DEFAULT_OG


def social_tags(title: str, desc: str, url: str, image: str) -> str:
    t = html.escape(title)
    d = html.escape(desc[:300])
    u = html.escape(url, quote=True)
    img = html.escape(image, quote=True)
    return (
        f'  <meta property="og:site_name" content="One Piece Deck Base" />\n'
        f'  <meta property="og:type" content="website" />\n'
        f'  <meta property="og:title" content="{t}" />\n'
        f'  <meta property="og:description" content="{d}" />\n'
        f'  <meta property="og:url" content="{u}" />\n'
        f'  <meta property="og:image" content="{img}" />\n'
        f'  <meta name="twitter:card" content="summary_large_image" />\n'
        f'  <meta name="twitter:title" content="{t}" />\n'
        f'  <meta name="twitter:description" content="{d}" />\n'
        f'  <meta name="twitter:image" content="{img}" />\n'
    )


def breadcrumb_jsonld(crumbs: list[tuple[str, str]]) -> str:
    items = []
    for i, (name, href) in enumerate(crumbs, start=1):
        url = href if href.startswith("http") else SITE + (href if href.startswith("/") else "/" + href)
        items.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": name,
                "item": url,
            }
        )
    payload = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return f'  <script type="application/ld+json">{blob}</script>\n'


def list_row(href: str, title: str, note: str) -> str:
    return f"""            <li>
              <a class="item" href="{html.escape(href, quote=True)}">
                <div>
                  <div style="font-weight:700">{html.escape(title)}</div>
                  <div class="muted" style="font-size:13px">{html.escape(note)}</div>
                </div>
                <div class="link">Open →</div>
              </a>
            </li>"""


def crew_siblings(slug: str, characters: list, limit: int = 8) -> list[tuple[str, str]]:
    """Return (name, slug) for other character pages that share a constructed leader."""
    groups: dict[int, list[tuple[str, str]]] = {}
    slug_leaders: dict[str, list[int]] = {}
    for name, cslug, _blurb, related in characters:
        slug_leaders[cslug] = related
        if related:
            groups.setdefault(related[0], []).append((name, cslug))
    mine = slug_leaders.get(slug) or []
    seen = {slug}
    out: list[tuple[str, str]] = []
    for idx in mine:
        for name, cslug in groups.get(idx, []):
            if cslug in seen:
                continue
            seen.add(cslug)
            out.append((name, cslug))
            if len(out) >= limit:
                return out
    return out


def related_section(heading: str, note: str, rows: list[str]) -> str:
    if not rows:
        return ""
    return f"""        <!-- RELATED_LINKS -->
        <section class="related-links" style="margin-top:22px">
          <div class="section-title">
            <h3>{html.escape(heading)}</h3>
            <div class="muted">{html.escape(note)}</div>
          </div>
          <ul class="list">
{chr(10).join(rows)}
          </ul>
        </section>
        <!-- /RELATED_LINKS -->
"""


RELATED_BLOCK_RE = re.compile(
    r"\s*<!-- RELATED_LINKS -->.*?<!-- /RELATED_LINKS -->\n?",
    re.S,
)


def strip_related(text: str) -> str:
    return RELATED_BLOCK_RE.sub("\n", text)


def parse_crumbs(text: str) -> list[tuple[str, str]]:
    m = re.search(r'<div class="crumb">(.*?)</div>', text, re.S)
    if not m:
        return [("Home", "/")]
    inner = m.group(1)
    crumbs: list[tuple[str, str]] = []
    for am in re.finditer(r'<a href="([^"]+)">([^<]+)</a>', inner):
        crumbs.append((html.unescape(am.group(2).strip()), am.group(1)))
    tail = re.sub(r"<a[^>]*>.*?</a>", "", inner)
    tail = re.sub(r"\s*/\s*", " ", tail)
    tail = re.sub(r"<[^>]+>", "", tail).strip(" \n/")
    if tail:
        crumbs.append((html.unescape(tail), ""))
    if not crumbs:
        crumbs = [("Home", "/")]
    return crumbs


FOOTER_LINKS = (
    '      <a href="/guides/">Guides</a> · '
    '<a href="/decklists/op17.html">Leaders</a> · '
    '<a href="/format.html">Format</a> · '
    '<a href="/shop/">Shop</a> · '
    '<a href="/privacy.html">Privacy</a>'
)
