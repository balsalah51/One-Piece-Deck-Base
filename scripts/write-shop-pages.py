#!/usr/bin/env python3
"""Write shop pages.

Live Amazon sleeves and dice are public and indexed. Playmats and custom
leaders stay unpublished (noindex, not linked from the public shop).
"""

from __future__ import annotations

import html
from pathlib import Path

ROOT = Path("/workspace")
DISCORD = "https://discord.gg/adZ2WUQ3D"
CSS = "/css/site.css?v=amazon-shop"
SITE = "https://onepiecedeckbase.com"

# Keep amzn.to URLs — they carry the Associates tag (opdb07-20).
SLEEVES = [
    {
        "name": "Dragon Shield Matte Jet",
        "blurb": "100 standard-size sleeves (63×88 mm). Black matte finish. Fits a 50-card OPTCG deck plus extras.",
        "url": "https://amzn.to/4qFzNrw",
        "mock": "Jet",
        "mock_class": "jet",
    },
    {
        "name": "Dragon Shield Dual Matte Red / Gold",
        "blurb": "100 standard-size Dual Matte sleeves. Red face, gold back (ART15065).",
        "url": "https://amzn.to/46s2YVu",
        "mock": "Red/Gold",
        "mock_class": "dual-rg",
    },
    {
        "name": "Dragon Shield Dual Matte Soul",
        "blurb": "100 standard-size Dual Matte sleeves. Metallic purple Dual Soul (ART15062).",
        "url": "https://amzn.to/4wMuTKw",
        "mock": "Soul",
        "mock_class": "soul",
    },
]

DICE = [
    {
        "name": "Power counter dice (+1000 / −1000)",
        "blurb": "32-piece set of +1000 to +6000 and −1000 to −6000 counters. Built for OPTCG power tracking.",
        "url": "https://amzn.to/46pbKUi",
        "mock": "+1000",
        "mock_class": "power",
    },
    {
        "name": "Official One Piece Premium Dice Set",
        "blurb": "Licensed dice in a collectible Monkey D. Luffy tin. Official Eiichiro Oda / Shueisha merchandise.",
        "url": "https://amzn.to/4xEOaiF",
        "mock": "Luffy",
        "mock_class": "luffy",
    },
    {
        "name": "Yiotfandoll 16 mm D6 (blue / black)",
        "blurb": "10 acrylic 16 mm six-siders. A cheap table set for life, DON!!, or kitchen-table counters.",
        "url": "https://amzn.to/4gQtpdA",
        "mock": "D6",
        "mock_class": "acrylic",
    },
]

def nav_html(current: str) -> str:
    def item(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if key == current else ""
        extra = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        return f'        <a href="{href}"{cur}{extra}>{label}</a>'

    return "\n".join(
        [
            item("/#recent", "Recent lists", "recent"),
            item("/decklists/op17.html", "Leaders", "leaders"),
            item("/format.html", "Format", "format"),
            item("/shop/", "Shop", "shop"),
            item(DISCORD, "Discord", "discord"),
        ]
    )


def product_card(item: dict) -> str:
    name = html.escape(item["name"])
    blurb = html.escape(item["blurb"])
    url = html.escape(item["url"], quote=True)
    mock = html.escape(item["mock"])
    klass = html.escape(item["mock_class"], quote=True)
    return f"""          <article class="shop-card">
            <div class="shop-mock {klass}">{mock}</div>
            <div style="font-weight:800">{name}</div>
            <p class="shop-note">{blurb}</p>
            <a class="shop-buy" href="{url}" target="_blank" rel="sponsored noopener noreferrer">View on Amazon</a>
          </article>"""


def product_grid(items: list[dict]) -> str:
    return '        <div class="shop-grid">\n' + "\n".join(product_card(p) for p in items) + "\n        </div>"


def chrome(title: str, desc: str, canonical: str, body: str, *, indexable: bool, amazon: bool) -> str:
    robots = "" if indexable else '  <meta name="robots" content="noindex, nofollow" />\n'
    canon = f'  <link rel="canonical" href="{html.escape(canonical, quote=True)}" />\n' if indexable else ""
    amazon_line = (
        "      As an Amazon Associate I earn from qualifying purchases.\n"
        if amazon
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}" />
{robots}{canon}  <link rel="stylesheet" href="{CSS}" />
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
{nav_html("shop")}
      </nav>
    </header>
    <main class="single">
      <div class="card hero">
{body}
      </div>
    </main>
    <footer>
      © <span id="year"></span> One Piece Deck Base — Fan site, not affiliated with Bandai or Shueisha.
{amazon_line}      <a href="/shop/">Shop</a> · <a href="/privacy.html">Privacy</a> · <a href="{DISCORD}" target="_blank" rel="noopener">Discord</a>
    </footer>
  </div>
  <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
  <script src="/js/site.js?v=amazon-shop"></script>
</body>
</html>
"""


def write(rel: str, title: str, desc: str, canonical: str, body: str, *, indexable: bool, amazon: bool = False) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(chrome(title, desc, canonical, body, indexable=indexable, amazon=amazon))
    print("wrote", rel, "indexable" if indexable else "unpublished")


index_body = f"""        <div class="crumb"><a href="/">Home</a> / Shop</div>
        <h2>Shop</h2>
        <p>Sleeves and dice for the table.</p>
        <div class="section-title" style="margin-top:22px">
          <h3>Sleeves</h3>
          <a href="/shop/sleeves.html">All sleeves →</a>
        </div>
        <p class="muted">Standard 63×88 mm Dragon Shield packs. Enough for a 50-card OPTCG list.</p>
{product_grid(SLEEVES)}
        <div class="section-title" style="margin-top:28px">
          <h3>Dice</h3>
          <a href="/shop/dice.html">All dice →</a>
        </div>
        <p class="muted">Power counters, the official Luffy tin, and a cheap acrylic D6 set.</p>
{product_grid(DICE)}
        <p class="amazon-disclosure-line">As an Amazon Associate I earn from qualifying purchases.</p>"""

sleeves_body = f"""        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / Sleeves</div>
        <h2>Sleeves</h2>
        <p>Dragon Shield standard-size packs (63×88 mm). Open Amazon for live price and stock.</p>
{product_grid(SLEEVES)}
        <p class="amazon-disclosure-line">As an Amazon Associate I earn from qualifying purchases.</p>"""

dice_body = f"""        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / Dice</div>
        <h2>Dice</h2>
        <p>Power counters and table dice. Check your locals if custom dice are allowed in official events. Open Amazon for live price and stock.</p>
{product_grid(DICE)}
        <p class="amazon-disclosure-line">As an Amazon Associate I earn from qualifying purchases.</p>"""

playmats_body = f"""        <div class="crumb"><a href="/">Home</a> / Shop / Playmats</div>
        <h2>Playmats</h2>
        <p>This category is not on the public shop. Fan-made mats are ordered on Discord when they come back.</p>
        <p class="muted">The live shop is <a href="/shop/sleeves.html">sleeves</a> and <a href="/shop/dice.html">dice</a> on Amazon.</p>
        <a class="discord" href="{DISCORD}" style="margin-top:18px">Ask on Discord</a>"""

custom_body = f"""        <div class="crumb"><a href="/">Home</a> / Shop / Custom leaders</div>
        <h2>Custom leaders</h2>
        <p>This category is not on the public shop. Custom leader prints are paused.</p>
        <p class="muted">The live shop is <a href="/shop/sleeves.html">sleeves</a> and <a href="/shop/dice.html">dice</a> on Amazon.</p>
        <a class="discord" href="{DISCORD}" style="margin-top:18px">Ask on Discord</a>"""


def ensure_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text()
    added = 0
    for url in (
        f"{SITE}/shop/",
        f"{SITE}/shop/sleeves.html",
        f"{SITE}/shop/dice.html",
    ):
        if url not in text:
            text = text.replace("</urlset>", f"  <url><loc>{url}</loc></url>\n</urlset>", 1)
            added += 1
    if added:
        path.write_text(text)
    print("sitemap shop urls", "added" if added else "present")


def main() -> None:
    write(
        "shop/index.html",
        "Shop | Sleeves and dice | One Piece Deck Base",
        "OPTCG sleeves and dice via Amazon.",
        f"{SITE}/shop/",
        index_body,
        indexable=True,
        amazon=True,
    )
    write(
        "shop/sleeves.html",
        "Dragon Shield sleeves | One Piece Deck Base shop",
        "Standard 63×88 mm Dragon Shield sleeves for OPTCG.",
        f"{SITE}/shop/sleeves.html",
        sleeves_body,
        indexable=True,
        amazon=True,
    )
    write(
        "shop/dice.html",
        "OPTCG dice | One Piece Deck Base shop",
        "Power counter dice and One Piece dice via Amazon.",
        f"{SITE}/shop/dice.html",
        dice_body,
        indexable=True,
        amazon=True,
    )
    write(
        "shop/playmats.html",
        "Playmats | One Piece Deck Base shop",
        "Fan-made One Piece TCG playmats. Not currently in the public shop.",
        f"{SITE}/shop/playmats.html",
        playmats_body,
        indexable=False,
    )
    write(
        "shop/custom-leaders.html",
        "Custom leaders | One Piece Deck Base shop",
        "Custom OPTCG leader prints. Not currently in the public shop.",
        f"{SITE}/shop/custom-leaders.html",
        custom_body,
        indexable=False,
    )
    ensure_sitemap()
    print("shop pages ready")


if __name__ == "__main__":
    main()
