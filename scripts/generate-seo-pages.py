#!/usr/bin/env python3
"""Build crawlable OPTCG topic and character pages plus a sitemap.

These pages are not in the primary nav. They exist so search engines can
find One Piece TCG / OPTCG / Bandai terms and character names, then route
people to real decklists. They are normal public HTML, not cloaked or hidden.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path("/workspace")
SITE = "https://onepiecedeckbase.com"

LEADERS = [
    ("Edward Newgate", "/decklists/op17/edward-newgate.html", "OP17 Red Whitebeard"),
    ("Shanks", "/decklists/op17/shanks.html", "OP17 Green Red-Haired"),
    ("Rocks D. Xebec", "/decklists/op17/rocks-d-xebec.html", "OP17 Blue Rocks Pirates"),
    ("Kaido", "/decklists/op17/kaido.html", "OP17 Purple Animal Kingdom"),
    ("Monkey D. Luffy", "/decklists/op17/monkey-d-luffy.html", "OP17 Black Straw Hat / Elbaph"),
    ("Charlotte Linlin", "/decklists/op17/charlotte-linlin.html", "OP17 Yellow Big Mom"),
    ("RG Luffy", "/decklists/rg-luffy.html", "Red/Green Monkey D. Luffy"),
    ("Nami", "/decklists/nami.html", "Blue/Yellow Nami"),
    ("Mihawk", "/decklists/mihawk.html", "Green Dracule Mihawk"),
    ("Portgas D. Ace", "/decklists/portgas-d-ace.html", "OP16 Red Whitebeard Pirates"),
    ("OP13 Ace", "/decklists/op13-ace.html", "OP13 Red/Blue Portgas D. Ace"),
    ("Imu", "/decklists/imu.html", "OP13 Black Mary Geoise"),
    ("Enel", "/decklists/enel.html", "OP15 Purple Sky Island"),
    ("Charlotte Katakuri", "/decklists/charlotte-katakuri.html", "OP11 Purple Big Mom Pirates"),
    ("Donquixote Rosinante", "/decklists/donquixote-rosinante.html", "OP12 Purple/Yellow Corazon"),
    ("Sabo", "/decklists/sabo.html", "OP13 Red/Black Revolutionary Army"),
    ("Gecko Moria", "/decklists/gecko-moria.html", "OP14 Black/Yellow Thriller Bark"),
    ("Nico Robin", "/decklists/nico-robin.html", "OP09 Purple/Yellow Straw Hat"),
]


def chrome(title: str, description: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}" />
  <link rel="canonical" href="{html.escape(SITE)}" />
  <link rel="stylesheet" href="/css/site.css" />
</head>
<body>
  <div class="wrap">
    <header>
      <a class="brand" href="/">
        <div class="logo">OP</div>
        <div>
          <h1>One Piece Deck Base</h1>
          <div class="subtitle">Decklists and community</div>
        </div>
      </a>
      <nav aria-label="Primary">
        <a href="/#decklists">Decklists</a>
        <a href="/decklists/op17.html">OP17</a>
        <a href="https://discord.gg/adZ2WUQ3D" target="_blank" rel="noopener">Discord</a>
      </nav>
    </header>
    <main class="single">
      <div class="card hero">
{body}
      </div>
    </main>
    <footer>
      © <span id="year"></span> One Piece Deck Base — Fan site for the Bandai ONE PIECE CARD GAME (OPTCG). Not affiliated with Bandai. <a href="/guides/">Guides</a>
    </footer>
  </div>
  <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</body>
</html>
"""


def leader_list() -> str:
    rows = []
    for name, href, meta in LEADERS:
        rows.append(
            f"""            <li>
              <a class="item" href="{html.escape(href)}">
                <div>
                  <div style="font-weight:700">{html.escape(name)}</div>
                  <div class="muted" style="font-size:13px">{html.escape(meta)}</div>
                </div>
                <div class="link">Lists →</div>
              </a>
            </li>"""
        )
    return "\n".join(rows)


TOPICS = [
    {
        "slug": "one-piece",
        "title": "One Piece | OPTCG decklists",
        "h2": "One Piece",
        "desc": "One Piece Card Game decklists and leader pages for the Bandai OPTCG.",
        "copy": "One Piece Deck Base is a fan hub for the One Piece Card Game. Use it to open OP17 and current-format OPTCG decklists, then jump to official Bandai events when you want to play.",
    },
    {
        "slug": "one-piece-tcg",
        "title": "One Piece TCG decklists | OPTCG",
        "h2": "One Piece TCG",
        "desc": "One Piece TCG (OPTCG) decklists for OP17 leaders from the Bandai card game.",
        "copy": "The One Piece TCG, also called OPTCG or the ONE PIECE CARD GAME, is Bandai’s constructed format. This site keeps 50-card lists for the leaders people are actually registering.",
    },
    {
        "slug": "optcg",
        "title": "OPTCG decklists | One Piece Card Game",
        "h2": "OPTCG",
        "desc": "OPTCG is the One Piece Card Game from Bandai. Browse leader decklists here.",
        "copy": "OPTCG is the short name players use for the Bandai One Piece Card Game. If you searched OPTCG decklist, start with the OP17 leader pages and open any 50-card list.",
    },
    {
        "slug": "one-piece-card-game",
        "title": "ONE PIECE CARD GAME decklists | Bandai",
        "h2": "ONE PIECE CARD GAME",
        "desc": "Bandai ONE PIECE CARD GAME decklists, leaders, and tournament lists.",
        "copy": "The official English name is ONE PIECE CARD GAME. Bandai runs store play, Treasure Cups, and championships. This fan site stores decklists so you can copy a list before you go.",
    },
    {
        "slug": "bandai",
        "title": "Bandai One Piece TCG | OPTCG decklists",
        "h2": "Bandai",
        "desc": "Bandai publishes the One Piece Card Game. Find OPTCG decklists on One Piece Deck Base.",
        "copy": "Bandai Namco makes the One Piece Card Game. Official kits, events, and rules live on Bandai’s site. Decklists on this page are community copies for studying lists, not official pairings.",
    },
    {
        "slug": "bandai-one-piece-card-game",
        "title": "Bandai ONE PIECE CARD GAME | OPTCG",
        "h2": "Bandai ONE PIECE CARD GAME",
        "desc": "Decklists for the Bandai ONE PIECE CARD GAME, including OP17 leaders.",
        "copy": "Search traffic often uses the full phrase Bandai ONE PIECE CARD GAME. That is the same OPTCG format these leader pages cover: the six OP17 leaders plus Mihawk, Sabo, RG Luffy, Ace, Enel, Katakuri, Rosinante, Nico Robin, Gecko Moria, Imu, and Nami.",
    },
    {
        "slug": "op17",
        "title": "OP17 The World's Strongest Warriors | OPTCG",
        "h2": "OP17",
        "desc": "OP17 The World's Strongest Warriors leaders and decklists for the One Piece TCG.",
        "copy": "OP-17 The World's Strongest Warriors is the current English booster. The six OP17 leaders on this site are Edward Newgate, Shanks, Rocks D. Xebec, Kaido, Monkey D. Luffy, and Charlotte Linlin.",
    },
    {
        "slug": "optcg-decklists",
        "title": "OPTCG decklists | 50-card One Piece TCG lists",
        "h2": "OPTCG decklists",
        "desc": "50-card OPTCG decklists from Limitless events and YouTube profiles.",
        "copy": "Every list page on One Piece Deck Base is a full 50-card OPTCG deck: leader, characters, events, and stages. Open a leader, then open a row for the actual list.",
    },
    {
        "slug": "one-piece-tcg-meta",
        "title": "One Piece TCG meta | OP17 OPTCG",
        "h2": "One Piece TCG meta",
        "desc": "OP17 OPTCG meta leaders with tournament and community decklists.",
        "copy": "The early OP17 meta is still moving. Rocks, Kaido, Black Luffy, Linlin, and Shanks lead the OP17 pages. Current-format lists here include Mihawk, Sabo, RG Luffy, Ace, Enel, Katakuri, Rosinante, Nico Robin, Gecko Moria, Imu, and Nami — several of those 50-card lists now splash OP17 cards.",
    },
    {
        "slug": "treasure-cup",
        "title": "Treasure Cup One Piece TCG | OPTCG lists",
        "h2": "Treasure Cup",
        "desc": "Treasure Cup is a Bandai One Piece TCG tournament series. Browse related OPTCG lists.",
        "copy": "Treasure Cup is Bandai’s year-round constructed series for the One Piece Card Game. Some lists on this site come from Limitless events in that same OPTCG constructed format.",
    },
    {
        "slug": "championship",
        "title": "One Piece TCG Championship | OPTCG",
        "h2": "Championship",
        "desc": "Bandai One Piece TCG Championship format uses constructed OPTCG decks.",
        "copy": "Championship events use the official Bandai constructed rules. The decklists here are 50-card OPTCG lists you can study before a regional, store championship, or locals.",
    },
    {
        "slug": "starter-decks",
        "title": "One Piece TCG starter decks | OPTCG ST lists",
        "h2": "Starter decks",
        "desc": "OPTCG starter-deck cards show up inside constructed 50-card lists.",
        "copy": "Bandai starter decks (ST) feed constructed OPTCG. You will see ST cards inside the 50-card lists on this site, mixed with booster cards from OP and EB sets.",
    },
    {
        "slug": "one-piece-card-game-decklist",
        "title": "One Piece Card Game decklist | OPTCG",
        "h2": "One Piece Card Game decklist",
        "desc": "Find a One Piece Card Game decklist for Bandai OPTCG leaders on this fan site.",
        "copy": "If you searched One Piece Card Game decklist, start here. Open a leader, then open a row for a full 50-card OPTCG list from Limitless events or YouTube profiles.",
    },
    {
        "slug": "optcg-deck-list",
        "title": "OPTCG deck list | Bandai One Piece TCG",
        "h2": "OPTCG deck list",
        "desc": "OPTCG deck list pages for OP17 and current-format Bandai One Piece TCG leaders.",
        "copy": "An OPTCG deck list on this site is always 50 cards plus a leader. Use the leader pages below, then copy the text list with card pictures on hover.",
    },
    {
        "slug": "one-piece-tcg-deck-list",
        "title": "One Piece TCG deck list | OPTCG",
        "h2": "One Piece TCG deck list",
        "desc": "One Piece TCG deck list hub for Bandai OPTCG constructed format.",
        "copy": "One Piece TCG deck list searches should land on real lists, not empty keyword pages. Every leader row here opens tournament or community 50-card lists.",
    },
    {
        "slug": "op-tcg",
        "title": "OP TCG | One Piece Card Game decklists",
        "h2": "OP TCG",
        "desc": "OP TCG is another name for the Bandai One Piece Card Game. Browse OPTCG lists here.",
        "copy": "Players type OP TCG, OPTCG, and One Piece TCG for the same Bandai game. This fan site keeps constructed lists for OP17 and a few current-format leaders.",
    },
    {
        "slug": "onepiece-tcg",
        "title": "Onepiece TCG | OPTCG decklists",
        "h2": "Onepiece TCG",
        "desc": "Onepiece TCG (One Piece TCG) decklists for the Bandai card game.",
        "copy": "Onepiece TCG is the same search as One Piece TCG. Bandai’s English name is ONE PIECE CARD GAME. The lists on this site are 50-card constructed OPTCG decks.",
    },
    {
        "slug": "bandai-namco",
        "title": "Bandai Namco One Piece TCG | OPTCG",
        "h2": "Bandai Namco",
        "desc": "Bandai Namco publishes the One Piece Card Game. Find OPTCG decklists here.",
        "copy": "Bandai Namco owns the ONE PIECE CARD GAME. Official products and events stay on Bandai’s site. This page only points at fan-copied OPTCG decklists.",
    },
    {
        "slug": "optcg-leaders",
        "title": "OPTCG leaders | One Piece TCG",
        "h2": "OPTCG leaders",
        "desc": "OPTCG leader pages for OP17 and current-format One Piece TCG decks.",
        "copy": "OPTCG leaders on this site: the six OP17 leaders, then Mihawk, Sabo, RG Luffy, OP16 Ace, Enel, Katakuri, Donquixote Rosinante, Nico Robin, Gecko Moria, Imu, Nami, and OP13 Ace.",
    },
    {
        "slug": "one-piece-tcg-leaders",
        "title": "One Piece TCG leaders | OPTCG",
        "h2": "One Piece TCG leaders",
        "desc": "One Piece TCG leader list with links to 50-card OPTCG decklists.",
        "copy": "Each One Piece TCG leader has a color, life, and effect. Open a leader page for YouTube lists and Limitless tournament lists when those exist.",
    },
    {
        "slug": "constructed",
        "title": "One Piece TCG constructed | OPTCG 50-card",
        "h2": "Constructed",
        "desc": "Bandai One Piece TCG constructed format uses 50-card OPTCG decks.",
        "copy": "Constructed OPTCG is 50 cards plus a leader. Locals, Treasure Cups, and championships all use that rule. The lists here are copied in that format.",
    },
    {
        "slug": "locals",
        "title": "One Piece TCG locals | OPTCG lists",
        "h2": "Locals",
        "desc": "Store locals for the Bandai One Piece TCG use the same constructed OPTCG lists.",
        "copy": "Locals are weekly Bandai store events. Study a 50-card list here, then check the official events page for a shop near you.",
    },
    {
        "slug": "limitless",
        "title": "Limitless One Piece TCG lists | OPTCG",
        "h2": "Limitless",
        "desc": "Tournament OPTCG lists on this site are copied from Limitless Play events.",
        "copy": "Limitless Play is where many OPTCG events post standings. Tournament rows on this fan site link those 50-card lists. Card pictures still come from Limitless image hosting.",
    },
    {
        "slug": "red-optcg",
        "title": "Red One Piece TCG decks | OPTCG",
        "h2": "Red OPTCG",
        "desc": "Red One Piece TCG decks on this site start with OP17 Edward Newgate and OP16 Ace.",
        "copy": "Red OPTCG on this site is OP17 Edward Newgate / Whitebeard, OP16 Portgas D. Ace, OP13 Ace, red/black Sabo, plus red cards inside RG Luffy. Open those leader lists for 50-card decks.",
    },
    {
        "slug": "green-optcg",
        "title": "Green One Piece TCG decks | OPTCG",
        "h2": "Green OPTCG",
        "desc": "Green One Piece TCG decks: OP17 Shanks and Dracule Mihawk.",
        "copy": "Green OPTCG lists here are OP17 Shanks and green Mihawk. Both rest or control the board. Open a leader page for tournament and YouTube lists.",
    },
    {
        "slug": "blue-optcg",
        "title": "Blue One Piece TCG decks | OPTCG",
        "h2": "Blue OPTCG",
        "desc": "Blue One Piece TCG decks: OP17 Rocks D. Xebec and Nami.",
        "copy": "Blue OPTCG on this site is Rocks D. Xebec, the blue half of Nami, and red/blue OP13 Ace. Rocks is the main OP17 blue leader with recent Limitless lists.",
    },
    {
        "slug": "purple-optcg",
        "title": "Purple One Piece TCG decks | OPTCG",
        "h2": "Purple OPTCG",
        "desc": "Purple One Piece TCG decks: OP17 Kaido, Enel, and Katakuri.",
        "copy": "Purple OPTCG here is OP17 Kaido, OP15 Enel, OP11 Charlotte Katakuri, plus purple/yellow Donquixote Rosinante and Nico Robin. Open those leader pages for tournament 50-card lists.",
    },
    {
        "slug": "black-optcg",
        "title": "Black One Piece TCG decks | OPTCG",
        "h2": "Black OPTCG",
        "desc": "Black One Piece TCG decks: OP17 Monkey D. Luffy and OP13 Imu.",
        "copy": "Black OPTCG on this site is OP17 Monkey D. Luffy / Elbaph, OP13 Imu / Five Elders, red/black Sabo, and black/yellow Gecko Moria. Open those leader pages for blockers, trash, and recent Limitless lists.",
    },
    {
        "slug": "yellow-optcg",
        "title": "Yellow One Piece TCG decks | OPTCG",
        "h2": "Yellow OPTCG",
        "desc": "Yellow One Piece TCG decks start with OP17 Charlotte Linlin.",
        "copy": "Yellow OPTCG here is OP17 Charlotte Linlin / Big Mom, plus the yellow half of Nami, Rosinante, Nico Robin, and Gecko Moria. Linlin has a stack of recent tournament lists.",
    },
    {
        "slug": "straw-hat-crew",
        "title": "Straw Hat Crew One Piece TCG | OPTCG",
        "h2": "Straw Hat Crew",
        "desc": "Straw Hat Crew OPTCG pages: Monkey D. Luffy, Nami, and related lists.",
        "copy": "Straw Hat Crew searches should reach Black OP17 Luffy, RG Luffy, Nami, and Nico Robin. Those are the constructed OPTCG leaders tied to the crew on this site.",
    },
    {
        "slug": "red-hair-pirates",
        "title": "Red Hair Pirates One Piece TCG | OPTCG",
        "h2": "Red Hair Pirates",
        "desc": "Red Hair Pirates OPTCG lists live on the OP17 Shanks leader page.",
        "copy": "Red Hair Pirates / Red-Haired Pirates is the OP17 green Shanks package. Benn Beckman, Yasopp, Lucky Roux, and Rockstar searches should start on that leader page.",
    },
    {
        "slug": "whitebeard-pirates",
        "title": "Whitebeard Pirates One Piece TCG | OPTCG",
        "h2": "Whitebeard Pirates",
        "desc": "Whitebeard Pirates OPTCG lists live on OP17 Edward Newgate and OP16 Ace.",
        "copy": "Whitebeard Pirates OPTCG on this site is red OP17 Edward Newgate, red OP16 Portgas D. Ace, and red/blue OP13 Ace. Ace, Marco, Jozu, Izo, Vista, and Whitebeard searches belong there.",
    },
    {
        "slug": "rocks-pirates",
        "title": "Rocks Pirates One Piece TCG | OPTCG",
        "h2": "Rocks Pirates",
        "desc": "Rocks Pirates OPTCG lists live on the OP17 Rocks D. Xebec page.",
        "copy": "Rocks Pirates is the OP17 blue leader package. Rocks D. Xebec, Shakky, and God Valley names should open that constructed page.",
    },
    {
        "slug": "beast-pirates",
        "title": "Beast Pirates One Piece TCG | OPTCG",
        "h2": "Beast Pirates",
        "desc": "Beast Pirates / Animal Kingdom OPTCG lists live on OP17 Kaido.",
        "copy": "Beast Pirates OPTCG here is purple OP17 Kaido. King, Queen, Jack, Yamato, Ulti, and Page One searches should use that leader page.",
    },
    {
        "slug": "big-mom-pirates",
        "title": "Big Mom Pirates One Piece TCG | OPTCG",
        "h2": "Big Mom Pirates",
        "desc": "Big Mom Pirates OPTCG lists live on OP17 Charlotte Linlin and OP11 Katakuri.",
        "copy": "Big Mom Pirates OPTCG is yellow OP17 Charlotte Linlin and purple OP11 Charlotte Katakuri. Smoothie, Cracker, Perospero, and Big Mom searches belong there.",
    },
    {
        "slug": "four-emperors",
        "title": "Four Emperors One Piece TCG | OPTCG",
        "h2": "Four Emperors",
        "desc": "Four Emperors OPTCG leaders: Shanks, Kaido, Linlin, Luffy, and Whitebeard.",
        "copy": "The Four Emperors map onto several OPTCG leaders on this site: Shanks, Kaido, Charlotte Linlin, Monkey D. Luffy, and Edward Newgate.",
    },
    {
        "slug": "elbaph",
        "title": "Elbaph One Piece TCG | OPTCG",
        "h2": "Elbaph",
        "desc": "Elbaph OPTCG lists live on OP17 black Monkey D. Luffy.",
        "copy": "Elbaph / Elbaf OPTCG on this site is black OP17 Monkey D. Luffy. Loki, Harald, and giant-type cards show up in those 50-card lists.",
    },
    {
        "slug": "wano",
        "title": "Wano One Piece TCG | OPTCG",
        "h2": "Wano",
        "desc": "Wano names in the One Piece TCG often sit in Kaido, Luffy, and Newgate lists.",
        "copy": "Wano searches can start at purple Kaido, black Luffy, or red Newgate. Oden, Yamato, and the Beast Pirates are the usual OPTCG landing spots.",
    },
    {
        "slug": "marineford",
        "title": "Marineford One Piece TCG | OPTCG",
        "h2": "Marineford",
        "desc": "Marineford-era OPTCG names often land on Whitebeard and Luffy lists.",
        "copy": "Marineford searches should try Edward Newgate, OP16 Portgas D. Ace, and Monkey D. Luffy. Ace, Whitebeard, Garp, and the Admirals are linked from the character guide too.",
    },
    {
        "slug": "donquixote-rosinante",
        "title": "Donquixote Rosinante OPTCG | Corazon decklists",
        "h2": "Donquixote Rosinante",
        "desc": "OP12 purple/yellow Donquixote Rosinante (Corazon) OPTCG decklists.",
        "copy": "Donquixote Rosinante is the purple/yellow OP12-061 leader, also searched as Corazon. The page is a Law engine: spend a life to save Trafalgar Law, then DON!! −1 to cheapen a 4-cost or higher Law. This is not green/blue OP05-022 Rosinante.",
    },
    {
        "slug": "corazon",
        "title": "Corazon OPTCG | Donquixote Rosinante",
        "h2": "Corazon",
        "desc": "Corazon is Donquixote Rosinante in the One Piece TCG. Open OP12-061 lists.",
        "copy": "Corazon is the epithet search for Donquixote Rosinante. Open the purple/yellow OP12 leader page for 50-card OPTCG lists built around Trafalgar Law.",
    },
    {
        "slug": "sabo-optcg",
        "title": "Sabo OPTCG decklists | OP13 red/black",
        "h2": "Sabo",
        "desc": "OP13 red/black Sabo OPTCG decklists for the Bandai One Piece Card Game.",
        "copy": "Sabo on this site is red/black OP13-004, Dressrosa / Revolutionary Army. It is not ST13 Sabo. Recent 50-card lists include OP17 cards on top of the 8-cost Revolutionary package.",
    },
    {
        "slug": "gecko-moria-optcg",
        "title": "Gecko Moria OPTCG | Thriller Bark lists",
        "h2": "Gecko Moria",
        "desc": "OP14 black/yellow Gecko Moria OPTCG decklists, including OP17 updates.",
        "copy": "Gecko Moria is the black/yellow OP14-080 Thriller Bark leader. K.O. your own Thriller Bark character to pump the board, then trash 3 to gain a life. Recent lists splash OP17 cards.",
    },
    {
        "slug": "nico-robin-optcg",
        "title": "Nico Robin OPTCG | OP09 purple/yellow",
        "h2": "Nico Robin",
        "desc": "OP09 purple/yellow Nico Robin OPTCG decklists with OP17 card updates.",
        "copy": "Nico Robin is the purple/yellow OP09-062 Straw Hat leader. Banish damage, then trash a Trigger to rest a DON!!. Recent copies include OP17 cards. This is the archaeologist leader page, not a cameo in Black Luffy.",
    },
    {
        "slug": "dressrosa",
        "title": "Dressrosa One Piece TCG | OPTCG",
        "h2": "Dressrosa",
        "desc": "Dressrosa OPTCG lists: Sabo, Rosinante, and related Bandai One Piece TCG decks.",
        "copy": "Dressrosa names on this site land on red/black Sabo and purple/yellow Donquixote Rosinante. Law, Doflamingo, and Revolutionary Army searches can start on those leader pages.",
    },
    {
        "slug": "thriller-bark",
        "title": "Thriller Bark One Piece TCG | OPTCG",
        "h2": "Thriller Bark",
        "desc": "Thriller Bark OPTCG lists live on the OP14 Gecko Moria leader page.",
        "copy": "Thriller Bark Pirates OPTCG is black/yellow Gecko Moria. Perona, Hogback, Absalom, and Ryuma searches should open that constructed page.",
    },
    {
        "slug": "revolutionary-army",
        "title": "Revolutionary Army One Piece TCG | OPTCG",
        "h2": "Revolutionary Army",
        "desc": "Revolutionary Army OPTCG lists live on red/black OP13 Sabo.",
        "copy": "Revolutionary Army OPTCG on this site is red/black OP13 Sabo, with Dragon, Koala, and Ivankov names nearby. Open the Sabo leader page for 50-card lists.",
    },
    {
        "slug": "op17-updated-leaders",
        "title": "OP17 updated OPTCG leaders | One Piece TCG",
        "h2": "OP17 updated leaders",
        "desc": "Current-format OPTCG leaders whose 50-card lists now include OP17 cards.",
        "copy": "Besides the six OP17 leaders, recent Limitless lists for Sabo, Nico Robin, and Gecko Moria already include OP17 cards. Rosinante is the OP12 Law engine on this site. Open those leader pages for the newest 50-card lists.",
    },
    {
        "slug": "purple-yellow-optcg",
        "title": "Purple Yellow One Piece TCG | OPTCG",
        "h2": "Purple/Yellow OPTCG",
        "desc": "Purple/yellow OPTCG leaders: Donquixote Rosinante and Nico Robin.",
        "copy": "Purple/yellow dual-color OPTCG on this site is OP12 Donquixote Rosinante and OP09 Nico Robin. Both have constructed 50-card lists.",
    },
    {
        "slug": "red-black-optcg",
        "title": "Red Black One Piece TCG | OPTCG",
        "h2": "Red/Black OPTCG",
        "desc": "Red/black OPTCG lists live on the OP13 Sabo leader page.",
        "copy": "Red/black OPTCG here is OP13-004 Sabo. Open that leader page for Dressrosa / Revolutionary Army 50-card lists.",
    },
    {
        "slug": "black-yellow-optcg",
        "title": "Black Yellow One Piece TCG | OPTCG",
        "h2": "Black/Yellow OPTCG",
        "desc": "Black/yellow OPTCG lists live on OP14 Gecko Moria.",
        "copy": "Black/yellow OPTCG on this site is OP14 Gecko Moria / Thriller Bark. Open that leader page for tournament lists.",
    },
]


# name, slug, blurb, related leader keys (index into LEADERS)
CHARACTERS = [
    ("Monkey D. Luffy", "monkey-d-luffy", "Straw Hat captain and the most-searched OPTCG name. Black OP17 Luffy and RG Luffy are the two constructed leaders on this site.", [4, 6]),
    ("Roronoa Zoro", "roronoa-zoro", "First mate and swordsman. Zoro cards show up in Mihawk and RG Luffy OPTCG lists.", [8, 6]),
    ("Nami", "nami", "Straw Hat navigator. Nami is the blue/yellow OPTCG leader; green Shanks lists also play Nami cards.", [7, 1]),
    ("Usopp", "usopp", "Sniper of the Straw Hats. Usopp cards appear in RG Luffy and Black Luffy OPTCG decklists.", [6, 4]),
    ("Sanji", "sanji", "Cook of the Thousand Sunny. Red Sanji is a staple in Edward Newgate Whitebeard lists.", [0, 6]),
    ("Tony Tony Chopper", "tony-tony-chopper", "Doctor of the crew. Chopper cards show up in Black Elbaph Luffy OPTCG lists.", [4]),
    ("Nico Robin", "nico-robin", "Archaeologist of the Straw Hats and the purple/yellow OP09 OPTCG leader. Recent lists include OP17 cards. Black Luffy lists may still play Robin as a character.", [17, 4, 6]),
    ("Franky", "franky", "Shipwright. Franky is a Straw Hat name searchers type; start from the Luffy leader pages.", [4, 6]),
    ("Brook", "brook", "Soul King of the Straw Hats. Brook cards appear in some RG Luffy OPTCG lists.", [6, 4]),
    ("Jinbe", "jinbe", "Helmsman and Fish-Man. Jinbe cards show up in Black Luffy and other OPTCG lists.", [4]),
    ("Shanks", "shanks", "Red-Haired Emperor and OP17 green leader. This is one of the main OPTCG pages on the site.", [1]),
    ("Benn Beckman", "benn-beckman", "First mate of the Red Hair Pirates. Look at the OP17 Shanks OPTCG lists.", [1]),
    ("Lucky Roux", "lucky-roux", "Red Hair Pirate. Shanks OPTCG decklists are the matching constructed pages.", [1]),
    ("Yasopp", "yasopp", "Usopp’s father and Red Hair sniper. Open the Shanks leader page for OPTCG lists.", [1]),
    ("Rockstar", "rockstar", "Red Hair Pirate who shows up as a card in green Shanks OPTCG lists.", [1]),
    ("Edward Newgate", "edward-newgate", "Whitebeard, OP17 red leader. YouTube OPTCG lists live on his page while Limitless standings catch up.", [0]),
    ("Whitebeard", "whitebeard", "The same person as Edward Newgate. Search Whitebeard OPTCG and you want the red OP17 leader page.", [0]),
    ("Portgas D. Ace", "portgas-d-ace", "Fire Fist Ace. OP16 red Ace and OP13 red/blue Ace are both constructed leaders here; Ace cards also show up in Edward Newgate lists.", [9, 10, 0]),
    ("Marco", "marco", "Phoenix of the Whitebeard Pirates. Marco is a common name in red Newgate and Ace OPTCG lists.", [0, 9, 10]),
    ("Jozu", "jozu", "Diamond Jozu of Whitebeard’s crew. See the Newgate OPTCG decklists.", [0]),
    ("Izo", "izo", "Whitebeard Pirate and gunner. Izo cards appear in OP17 Newgate lists.", [0]),
    ("Thatch", "thatch", "Whitebeard Pirate. Newgate OPTCG pages are the right constructed lists.", [0]),
    ("Vista", "vista", "Flower Sword Vista. Whitebeard OPTCG lists are under Edward Newgate.", [0]),
    ("Gol D. Roger", "gol-d-roger", "Pirate King. Roger cards show up as finishers in some Newgate and Rocks OPTCG lists.", [0, 2]),
    ("Silvers Rayleigh", "silvers-rayleigh", "Dark King and Roger’s first mate. Start from Roger-adjacent OPTCG lists on Newgate and Rocks.", [0, 2]),
    ("Kouzuki Oden", "kouzuki-oden", "Samurai of Wano. Oden cards appear in red Newgate OPTCG lists.", [0]),
    ("Rocks D. Xebec", "rocks-d-xebec", "Captain of the Rocks Pirates and OP17 blue leader. One of the most-played OPTCG decks right now.", [2]),
    ("Kaido", "kaido", "King of the Beasts and OP17 purple leader. Purple Kaido has a full stack of OPTCG tournament lists.", [3]),
    ("King", "king", "All-Star of the Beasts. King cards are common in purple Kaido OPTCG lists.", [3]),
    ("Queen", "queen", "All-Star of the Beasts. Queen cards show up next to Kaido in purple OPTCG lists.", [3]),
    ("Jack", "jack", "Drought Jack of the Beasts. See purple Kaido OPTCG decklists.", [3]),
    ("Yamato", "yamato", "Oden’s name successor. Yamato cards appear in Kaido OPTCG lists.", [3]),
    ("Ulti", "ulti", "Tobi Roppo. Ulti & Page One show up in purple Kaido OPTCG lists.", [3]),
    ("Page One", "page-one", "Tobi Roppo. Paired with Ulti in some Kaido OPTCG decklists.", [3]),
    ("Charlotte Linlin", "charlotte-linlin", "Big Mom and OP17 yellow leader. Yellow Linlin OPTCG lists are on her leader page.", [5]),
    ("Big Mom", "big-mom", "The same person as Charlotte Linlin. Yellow OPTCG lists live on the Linlin page.", [5]),
    ("Charlotte Katakuri", "charlotte-katakuri", "Sweet Commander. Purple OP11 Katakuri is a constructed leader here; yellow Linlin lists also play Katakuri cards.", [13, 5]),
    ("Charlotte Smoothie", "charlotte-smoothie", "Sweet Commander. Open the Linlin OPTCG page for yellow lists.", [5]),
    ("Charlotte Cracker", "charlotte-cracker", "Thousand Arms Cracker. Yellow Linlin OPTCG is the matching leader.", [5]),
    ("Charlotte Perospero", "charlotte-perospero", "First son of Big Mom. See Linlin OPTCG decklists.", [5]),
    ("Dracule Mihawk", "dracule-mihawk", "World’s Strongest Swordsman and green OPTCG leader. Mihawk has tournament lists on this site.", [8]),
    ("Trafalgar Law", "trafalgar-law", "Surgeon of Death. Law is the engine on purple/yellow Donquixote Rosinante; Law cards also show up in RG Luffy and Mihawk lists.", [14, 6, 8]),
    ("Eustass Kid", "eustass-kid", "Captain of the Kid Pirates. Kid is a common OPTCG search; start from the OP17 hub and RG Luffy.", [6, 4]),
    ("Killer", "killer", "Kid Pirates combatant. Related OPTCG lists sit with supernova packages on RG Luffy.", [6]),
    ("Jewelry Bonney", "jewelry-bonney", "Supernova captain. Bonney names often land next to other supernova OPTCG lists.", [6]),
    ("Marshall D. Teach", "marshall-d-teach", "Blackbeard. There is not a dedicated Teach leader page yet; start from OP17 and Kaido/Luffy lists.", [3, 4]),
    ("Blackbeard", "blackbeard", "Same person as Marshall D. Teach. Use the OP17 hub until a Teach leader page exists.", [4, 3]),
    ("Buggy", "buggy", "Warlord and Emperor. Buggy searches should still land on this OPTCG hub and the OP17 leaders.", [1, 4]),
    ("Crocodile", "crocodile", "Former Warlord. No Crocodile leader page yet; the OP17 decklist hub is the start.", [2, 5]),
    ("Donquixote Doflamingo", "donquixote-doflamingo", "Heavenly Demon. Dressrosa searches should try Sabo and Donquixote Rosinante, then green lists.", [15, 14, 8]),
    ("Boa Hancock", "boa-hancock", "Empress of Amazon Lily. Hancock searches can start at the OP17 hub.", [5, 4]),
    ("Gecko Moria", "gecko-moria", "Former Warlord and the black/yellow OP14 Thriller Bark OPTCG leader. Recent lists include OP17 cards.", [16]),
    ("Bartholomew Kuma", "bartholomew-kuma", "Tyrant and former Warlord. Start from the One Piece TCG hub on this site.", [4]),
    ("Monkey D. Garp", "monkey-d-garp", "Hero of the Marines and Luffy’s grandfather. Luffy OPTCG pages are the closest constructed lists.", [4, 6]),
    ("Monkey D. Dragon", "monkey-d-dragon", "Revolutionary Army leader. Luffy OPTCG pages are the related constructed lists.", [4]),
    ("Sabo", "sabo", "Chief of Staff of the Revolutionaries and the red/black OP13 OPTCG leader. Not ST13 Sabo. Ace and Luffy cards still show up in some red lists.", [15, 0, 6]),
    ("Akainu", "akainu", "Fleet Admiral Sakazuki. Marine searches can start at the OPTCG hub.", [4]),
    ("Aokiji", "aokiji", "Kuzan. Cross-guild and marine searches still belong on this OPTCG site hub.", [2]),
    ("Kizaru", "kizaru", "Borsalino. Admiral searches should land here, then move to a leader list.", [8]),
    ("Fujitora", "fujitora", "Issho. Another admiral name that should resolve to this OPTCG hub.", [8]),
    ("Coby", "coby", "Marine prodigy. Coby searches can start at Luffy-related OPTCG pages.", [4]),
    ("Smoker", "smoker", "White Hunter of the Marines. Use the OPTCG hub.", [7]),
    ("Rob Lucci", "rob-lucci", "CP0. Lucci is a popular OPTCG name; start from the hub if you do not see a dedicated leader.", [8, 4]),
    ("Perona", "perona", "Ghost Princess. Perona cards show up in Gecko Moria Thriller Bark lists and some Mihawk packages.", [16, 8]),
    ("Mr 2 Bon Kurei", "mr-2-bon-kurei", "Bentham. A fun OPTCG character name that should still reach this site.", [3, 5]),
    ("Emporio Ivankov", "emporio-ivankov", "Queen of the Kamabakka Kingdom. Related constructed lists start at Luffy pages.", [4]),
    ("Uta", "uta", "New Genesis. Uta cards appear in some red Newgate OPTCG lists.", [0]),
    ("Loki", "loki", "Prince of Elbaph. Black OP17 Luffy is the Elbaph OPTCG leader on this site.", [4]),
    ("Harald", "harald", "King of Elbaph. Black Luffy OPTCG lists are the Elbaph constructed pages.", [4]),
    ("Shakuyaku", "shakuyaku", "Shakky of the Rocks era. Blue Rocks D. Xebec is the matching OP17 OPTCG leader.", [2]),
    ("Luffy", "luffy", "Same search as Monkey D. Luffy. Black OP17 Luffy and RG Luffy are the constructed OPTCG leaders.", [4, 6]),
    ("Zoro", "zoro", "Same search as Roronoa Zoro. Mihawk and RG Luffy lists are the closest OPTCG pages.", [8, 6]),
    ("Mihawk", "mihawk", "Same search as Dracule Mihawk. Green Mihawk has tournament OPTCG lists on this site.", [8]),
    ("Newgate", "newgate", "Same person as Edward Newgate / Whitebeard. Red OP17 is the constructed page.", [0]),
    ("Xebec", "xebec", "Same search as Rocks D. Xebec. Blue OP17 is the constructed OPTCG leader.", [2]),
    ("Rocks", "rocks", "Short name for Rocks D. Xebec and the Rocks Pirates OPTCG package.", [2]),
    ("Linlin", "linlin", "Same person as Charlotte Linlin / Big Mom. Yellow OP17 is the constructed page.", [5]),
    ("Law", "law", "Same search as Trafalgar Law. Donquixote Rosinante is the Law-engine leader; RG Luffy and Mihawk lists also play Law cards.", [14, 6, 8]),
    ("Kid", "kid", "Same search as Eustass Kid. Start from RG Luffy and the OP17 hub.", [6, 4]),
    ("Ace", "ace", "Same search as Portgas D. Ace. OP16 Ace is the constructed red leader; OP13 Ace is the red/blue leader.", [9, 10]),
    ("Roger", "roger", "Same search as Gol D. Roger. Roger cards show up in Newgate and Rocks OPTCG lists.", [0, 2]),
    ("Oden", "oden", "Same search as Kouzuki Oden. Red Newgate OPTCG lists are the usual home.", [0]),
    ("Katakuri", "katakuri", "Same search as Charlotte Katakuri. Purple OP11 Katakuri is the constructed leader.", [13]),
    ("Beckman", "beckman", "Same search as Benn Beckman. Open OP17 Shanks OPTCG lists.", [1]),
    ("Rayleigh", "rayleigh", "Same search as Silvers Rayleigh. Newgate and Rocks pages are the closest lists.", [0, 2]),
    ("Enel", "enel", "God of Skypeia. Purple OP15 Enel is the constructed OPTCG leader on this site.", [12]),
    ("Lucci", "lucci", "Same search as Rob Lucci. Start from the hub, Mihawk, or Black Luffy pages.", [8, 4]),
    ("Doflamingo", "doflamingo", "Same search as Donquixote Doflamingo. Sabo and Rosinante are the Dressrosa constructed pages.", [15, 14, 8]),
    ("Hancock", "hancock", "Same search as Boa Hancock. Start from the OP17 hub and yellow/black lists.", [5, 4]),
    ("Teach", "teach", "Same search as Marshall D. Teach / Blackbeard. Use the OP17 hub until a Teach leader exists.", [3, 4]),
    ("Garp", "garp", "Same search as Monkey D. Garp. Luffy OPTCG pages are the closest constructed lists.", [4, 6]),
    ("Dragon", "dragon", "Same search as Monkey D. Dragon. Black Luffy OPTCG is the related constructed page.", [4]),
    ("Nefertari Vivi", "nefertari-vivi", "Princess of Alabasta. Straw Hat adjacent; start from Luffy and Nami OPTCG pages.", [4, 7]),
    ("Arlong", "arlong", "Fish-Man pirate from East Blue. Nami and Luffy OPTCG pages are the closest lists.", [7, 4]),
    ("Don Krieg", "don-krieg", "East Blue pirate. Use the One Piece TCG hub, then a red or black leader list.", [0, 4]),
    ("Kuro", "kuro", "Captain Kuro of the Black Cat Pirates. Start from the OPTCG hub.", [4, 8]),
    ("Alvida", "alvida", "Iron Mace Alvida. Early One Piece name; use the OPTCG hub and Luffy pages.", [4]),
    ("Helmeppo", "helmeppo", "Marine from Shells Town. Coby and Garp searches sit next to Luffy OPTCG pages.", [4]),
    ("Tashigi", "tashigi", "Marine swordsman. Smoker and Mihawk pages are the closest OPTCG starts.", [7, 8]),
    ("Sengoku", "sengoku", "Former Fleet Admiral. Marineford-era searches can start at Newgate and Luffy lists.", [0, 4]),
    ("Sakazuki", "sakazuki", "Fleet Admiral, also searched as Akainu. Use the OPTCG hub and Luffy pages.", [4]),
    ("Kuzan", "kuzan", "Former Admiral, also searched as Aokiji. Rocks and the hub are fair starts.", [2]),
    ("Borsalino", "borsalino", "Admiral Kizaru. Use the OPTCG hub, then a leader that matches your list.", [8]),
    ("Issho", "issho", "Admiral Fujitora. Another marine name that should resolve to this OPTCG hub.", [8]),
    ("Sentomaru", "sentomaru", "Marine scientist escort. Egghead-era searches can start at the OPTCG hub.", [4, 8]),
    ("Magellan", "magellan", "Warden of Impel Down. Poison searches can start at black Luffy or the hub.", [4]),
    ("Shiryu", "shiryu", "Blackbeard Pirates swordsman. Use the hub until a Teach leader page exists.", [3, 8]),
    ("Jesus Burgess", "jesus-burgess", "Champion of the Blackbeard Pirates. Start from the OP17 hub.", [3, 4]),
    ("Van Augur", "van-augur", "Blackbeard Pirates sniper. Use the OPTCG hub.", [3]),
    ("Lafitte", "lafitte", "Blackbeard Pirates navigator. Use the OPTCG hub.", [3]),
    ("Doc Q", "doc-q", "Blackbeard Pirates doctor. Use the OPTCG hub.", [3]),
    ("Shirahoshi", "shirahoshi", "Princess of the Ryugu Kingdom. Jinbe and Luffy OPTCG pages are related.", [4]),
    ("Neptune", "neptune", "King of the Ryugu Kingdom. Fish-Man searches can start at Jinbe/Luffy pages.", [4]),
    ("Fisher Tiger", "fisher-tiger", "Sun Pirates founder. Jinbe-related OPTCG searches start at Black Luffy.", [4]),
    ("Koala", "koala", "Revolutionary Army. Sabo is the constructed OPTCG leader; Dragon searches sit next to Luffy pages.", [15, 4]),
    ("Iceburg", "iceburg", "Mayor of Water 7. Franky-related searches can start at Luffy OPTCG pages.", [4]),
    ("Paulie", "paulie", "Galley-La shipwright. Water 7 names can start at the OPTCG hub.", [4]),
    ("Kalifa", "kalifa", "CP9. Lucci-adjacent searches can start at the hub or Mihawk.", [8, 4]),
    ("Kaku", "kaku", "CP9 and CP0. Lucci-adjacent OPTCG searches start at the hub.", [8, 4]),
    ("Blueno", "blueno", "CP9. Enies Lobby names can start at the OPTCG hub.", [8]),
    ("Jabra", "jabra", "CP9. Use the OPTCG hub.", [8]),
    ("Spandam", "spandam", "CP9 director. Use the OPTCG hub.", [4, 8]),
    ("Nico Olvia", "nico-olvia", "Robin’s mother. Nico Robin is the constructed OPTCG leader; Luffy pages are related.", [17, 4]),
    ("Jaguar D. Saul", "jaguar-d-saul", "Giant marine who saved Robin. Elbaph Luffy is the matching OP17 OPTCG leader.", [4]),
    ("Hogback", "hogback", "Thriller Bark doctor. Gecko Moria is the constructed OPTCG leader.", [16]),
    ("Absalom", "absalom", "Thriller Bark commander. Open the Gecko Moria OPTCG page.", [16]),
    ("Ryuma", "ryuma", "Legendary samurai zombie. Zoro and Mihawk OPTCG pages are the closest lists.", [8, 6]),
    ("Caesar Clown", "caesar-clown", "Scientist of Punk Hazard. Law-related searches can start at RG Luffy.", [6]),
    ("Monet", "monet", "Snow woman of Punk Hazard. Use the OPTCG hub.", [6, 7]),
    ("Vergo", "vergo", "Corazon’s former vice admiral cover. Law searches start at RG Luffy.", [6]),
    ("Kinemon", "kinemon", "Kozuki retainer. Wano searches can start at Kaido or Luffy OPTCG pages.", [3, 4]),
    ("Kouzuki Momonosuke", "kouzuki-momonosuke", "Shogun of Wano. Kaido and Luffy OPTCG pages are related constructed lists.", [3, 4]),
    ("Kouzuki Hiyori", "kouzuki-hiyori", "Princess of Wano. Nami and Wano-adjacent OPTCG lists are the start.", [7, 3]),
    ("Inuarashi", "inuarashi", "Duke of the Mokomo Dukedom. Wano / Luffy OPTCG pages are related.", [4, 3]),
    ("Nekomamushi", "nekomamushi", "Ruler of the Mokomo Dukedom. Wano / Luffy OPTCG pages are related.", [4, 3]),
    ("Raizo", "raizo", "Ninja of Wano. Start from Luffy or Kaido OPTCG pages.", [4, 3]),
    ("Kikunojo", "kikunojo", "Kozuki retainer. Wano searches can start at Kaido or Luffy.", [3, 4]),
    ("Shinobu", "shinobu", "Wano kunoichi. Use the OPTCG hub and Luffy pages.", [4]),
    ("Tama", "tama", "Kibi child of Wano. Yamato and Kaido OPTCG pages are nearby.", [3]),
    ("Who's Who", "whos-who", "Tobi Roppo. Purple Kaido OPTCG lists are the matching constructed pages.", [3]),
    ("Sasaki", "sasaki", "Tobi Roppo. Purple Kaido OPTCG lists are the matching constructed pages.", [3]),
    ("Black Maria", "black-maria", "Tobi Roppo. Purple Kaido OPTCG lists are the matching constructed pages.", [3]),
    ("Kurozumi Orochi", "kurozumi-orochi", "Shogun of Wano. Kaido OPTCG is the usual constructed start.", [3]),
    ("Denjiro", "denjiro", "Kozuki retainer. Wano searches can start at Kaido or Luffy.", [3, 4]),
    ("Kawamatsu", "kawamatsu", "Kozuki retainer. Wano searches can start at Luffy or Kaido.", [4, 3]),
    ("Ashura Doji", "ashura-doji", "Akazaya samurai. Wano searches can start at Kaido or Luffy.", [3, 4]),
    ("Hyogoro", "hyogoro", "Yakuza of Wano. Use the OPTCG hub and Luffy pages.", [4]),
    ("Pudding", "pudding", "Charlotte Pudding. Yellow Linlin OPTCG is the matching leader.", [5]),
    ("Charlotte Pudding", "charlotte-pudding", "Big Mom’s daughter. Yellow Linlin OPTCG lists are the constructed pages.", [5]),
    ("Charlotte Oven", "charlotte-oven", "Big Mom Pirate. Open the Linlin OPTCG page.", [5]),
    ("Charlotte Brulee", "charlotte-brulee", "Big Mom Pirate. Open the Linlin OPTCG page.", [5]),
    ("Streusen", "streusen", "Big Mom Pirates chef. Yellow Linlin OPTCG is the matching leader.", [5]),
    ("Prometheus", "prometheus", "Big Mom homie. Yellow Linlin OPTCG lists are the start.", [5]),
    ("Zeus", "zeus", "Big Mom / Nami thundercloud. Linlin and Nami OPTCG pages are related.", [5, 7]),
    ("Napoleon", "napoleon", "Big Mom homie. Yellow Linlin OPTCG is the matching leader.", [5]),
    ("Hera", "hera", "Big Mom homie. Yellow Linlin OPTCG is the matching leader.", [5]),
    ("Capone Bege", "capone-bege", "Fire Tank Pirates. Big Mom-adjacent searches can start at Linlin.", [5]),
    ("Cavendish", "cavendish", "Pretty Pirates captain. Supernova searches can start at RG Luffy.", [6]),
    ("Bartolomeo", "bartolomeo", "Barto Club. Straw Hat fan; start from Luffy OPTCG pages.", [4, 6]),
    ("Rebecca", "rebecca", "Dressrosa princess. Doflamingo-adjacent searches start at the hub.", [8, 2]),
    ("Kyros", "kyros", "Dressrosa gladiator. Use the OPTCG hub.", [8]),
    ("Sugar", "sugar", "Donquixote family. Doflamingo searches can start at the hub.", [8, 2]),
    ("Trebol", "trebol", "Donquixote executive. Use the OPTCG hub.", [8, 2]),
    ("Diamante", "diamante", "Donquixote executive. Use the OPTCG hub.", [8]),
    ("Pica", "pica", "Donquixote executive. Use the OPTCG hub.", [8]),
    ("Senor Pink", "senor-pink", "Donquixote family. Use the OPTCG hub.", [8, 2]),
    ("Baby 5", "baby-5", "Donquixote family. Use the OPTCG hub.", [8]),
    ("Sai", "sai", "Happo Navy. Dressrosa supernova-adjacent searches can start at RG Luffy.", [6]),
    ("Ideo", "ideo", "XXX Gym. Use the OPTCG hub or RG Luffy.", [6]),
    ("Hajrudin", "hajrudin", "Giant pirate. Elbaph Luffy is the OP17 constructed page.", [4]),
    ("Elizabello II", "elizabello-ii", "King of Prodence. Use the OPTCG hub.", [6]),
    ("Vegapunk", "vegapunk", "Scientist of Egghead. Start from the OPTCG hub and Luffy pages.", [4]),
    ("Shaka", "shaka", "Vegapunk satellite. Egghead searches can start at the hub.", [4]),
    ("Lilith", "lilith", "Vegapunk satellite. Egghead searches can start at the hub.", [4]),
    ("York", "york", "Vegapunk satellite. Egghead searches can start at the hub.", [4]),
    ("Atlas", "atlas", "Vegapunk satellite. Egghead searches can start at the hub.", [4]),
    ("Stussy", "stussy", "CP0. Lucci-adjacent searches can start at the hub.", [8, 2]),
    ("Jaygarcia Saturn", "jaygarcia-saturn", "Five Elders. Black Imu OPTCG lists are the matching constructed pages.", [11]),
    ("Marcus Mars", "marcus-mars", "Five Elders. Black Imu OPTCG lists are the matching constructed pages.", [11]),
    ("Topman Warcury", "topman-warcury", "Five Elders. Black Imu OPTCG lists are the matching constructed pages.", [11]),
    ("Ethanbaron V. Nusjuro", "ethanbaron-v-nusjuro", "Five Elders. Black Imu OPTCG lists are the matching constructed pages.", [11]),
    ("Shepherd Ju Peter", "shepherd-ju-peter", "Five Elders. Black Imu OPTCG lists are the matching constructed pages.", [11]),
    ("Imu", "imu", "Sovereign of Mary Geoise and black OP13 OPTCG leader. Five Elders lists live on the Imu page.", [11]),
    ("Figarland Garling", "figarland-garling", "Holy Knights / God Valley. Rocks and Shanks pages are related OPTCG lists.", [2, 1]),
    ("Figarland Shamrock", "figarland-shamrock", "Holy Knights. Shanks and Elbaph Luffy pages are related OPTCG lists.", [1, 4]),
    ("Gunko", "gunko", "Holy Knight. Elbaph Luffy is the matching OP17 constructed page.", [4]),
    ("Killingham", "killingham", "Holy Knight. Elbaph Luffy is the matching OP17 constructed page.", [4]),
    ("Scopper Gaban", "scopper-gaban", "Roger Pirates. Newgate, Rocks, and Elbaph Luffy are related OPTCG pages.", [0, 2, 4]),
    ("Dorry", "dorry", "Giant of Elbaph. Black OP17 Luffy is the Elbaph constructed leader.", [4]),
    ("Brogy", "brogy", "Giant of Elbaph. Black OP17 Luffy is the Elbaph constructed leader.", [4]),
    ("Colon", "colon", "Elbaph child. Black OP17 Luffy is the matching constructed page.", [4]),
    ("Ripley", "ripley", "Giant of Elbaph. Black OP17 Luffy is the matching constructed page.", [4]),
    ("Road", "road", "Giant of Elbaph. Black OP17 Luffy is the matching constructed page.", [4]),
    ("Goldberg", "goldberg", "Giant of Elbaph. Black OP17 Luffy is the matching constructed page.", [4]),
    ("Gerd", "gerd", "Giant of Elbaph. Black OP17 Luffy is the matching constructed page.", [4]),
    ("Jarul", "jarul", "Giant elder of Elbaph. Black OP17 Luffy is the matching constructed page.", [4]),
    ("Ida", "ida", "Giant of Elbaph. Black OP17 Luffy is the matching constructed page.", [4]),
    ("Gloriosa", "gloriosa", "Amazon Lily elder, Rocks era. Rocks D. Xebec is the matching OP17 leader.", [2]),
    ("Buckingham Stussy", "buckingham-stussy", "Rocks Pirates. Blue Rocks D. Xebec is the matching OP17 OPTCG leader.", [2]),
    ("Captain John", "captain-john", "Rocks Pirates. Blue Rocks D. Xebec is the matching OP17 OPTCG leader.", [2]),
    ("Wang Zhi", "wang-zhi", "Rocks Pirates. Blue Rocks D. Xebec is the matching OP17 OPTCG leader.", [2]),
    ("Ochoku", "ochoku", "Rocks Pirates. Blue Rocks D. Xebec is the matching OP17 OPTCG leader.", [2]),
    ("Red Hair", "red-hair", "Red Hair / Red-Haired Pirates OPTCG lists live on OP17 Shanks.", [1]),
    ("King of the Beasts", "king-of-the-beasts", "Kaido’s title. Purple OP17 Kaido is the constructed OPTCG page.", [3]),
    ("World's Strongest Man", "worlds-strongest-man", "Whitebeard’s title. Red OP17 Edward Newgate is the constructed page.", [0]),
    ("World's Strongest Swordsman", "worlds-strongest-swordsman", "Mihawk’s title. Green Mihawk OPTCG lists are on his leader page.", [8]),
    ("Pirate King", "pirate-king", "Gol D. Roger’s title, and Luffy’s goal. Roger and Luffy OPTCG pages are related.", [0, 4]),
    ("Fire Fist", "fire-fist", "Portgas D. Ace’s epithet. OP16 Ace and OP13 Ace are both constructed leaders; Ace cards also show up in Edward Newgate lists.", [9, 10, 0]),
    ("Surgeon of Death", "surgeon-of-death", "Trafalgar Law’s epithet. RG Luffy lists are a common home for Law cards.", [6]),
    ("Heavenly Demon", "heavenly-demon", "Doflamingo’s epithet. Use the OPTCG hub and green lists.", [8]),
    ("Tyrant", "tyrant", "Bartholomew Kuma’s epithet. Start from the One Piece TCG hub.", [4]),
    ("Hero of the Marines", "hero-of-the-marines", "Monkey D. Garp’s epithet. Luffy OPTCG pages are the closest lists.", [4, 6]),
    ("Dark King", "dark-king", "Silvers Rayleigh’s epithet. Newgate and Rocks pages are related OPTCG lists.", [0, 2]),
    ("All-Star King", "all-star-king", "King of the Beasts. Purple Kaido OPTCG lists are the constructed pages.", [3]),
    ("All-Star Queen", "all-star-queen", "Queen of the Beasts. Purple Kaido OPTCG lists are the constructed pages.", [3]),
    ("Drought Jack", "drought-jack", "Jack of the Beasts. Purple Kaido OPTCG lists are the constructed pages.", [3]),
    ("Sweet Commander", "sweet-commander", "Katakuri, Smoothie, and Cracker. Yellow Linlin OPTCG is the matching leader.", [5]),
    ("Red-Haired Shanks", "red-haired-shanks", "Full search for OP17 green Shanks. Open the Shanks leader page for OPTCG lists.", [1]),
    ("Blackbeard Pirates", "blackbeard-pirates", "Marshall D. Teach’s crew. Use the OP17 hub until a Teach leader page exists.", [3, 4]),
    ("Heart Pirates", "heart-pirates", "Trafalgar Law’s crew. Law cards show up in RG Luffy OPTCG lists.", [6]),
    ("Kid Pirates", "kid-pirates", "Eustass Kid’s crew. Start from RG Luffy and the OP17 hub.", [6, 4]),
    ("Sun Pirates", "sun-pirates", "Jinbe and Fisher Tiger. Black Luffy OPTCG is a related constructed page.", [4]),
    ("Revolutionary Army", "revolutionary-army", "Dragon, Sabo, Koala, Ivankov. Luffy OPTCG pages are the related lists.", [4, 0]),
    ("Marines", "marines", "Garp, Sengoku, admirals, Coby, Smoker. Start from the OPTCG hub, then a leader list.", [4, 8]),
    ("Warlords", "warlords", "Mihawk, Hancock, Doflamingo, Kuma, Moria, Crocodile, Buggy, Law, Jinbe. Open the matching leader or hub.", [8, 5]),
    ("Supernovas", "supernovas", "Luffy, Zoro, Law, Kid, Killer, Bonney, Bege, Urouge, Apoo, Hawkins. Start from Luffy and RG Luffy.", [4, 6]),
    ("Urouge", "urouge", "Supernova captain. Start from the OPTCG hub or RG Luffy.", [6]),
    ("Scratchmen Apoo", "scratchmen-apoo", "Supernova captain. Start from the OPTCG hub or Kaido-adjacent lists.", [3, 6]),
    ("Basil Hawkins", "basil-hawkins", "Supernova captain. Wano-era searches can start at Kaido.", [3, 6]),
    ("X Drake", "x-drake", "Supernova and marine. Wano / Kaido OPTCG pages are related.", [3, 6]),
    ("Bonney", "bonney", "Same search as Jewelry Bonney. Start from the OPTCG hub.", [6]),
    ("Carrot", "carrot", "Mink of the Mokomo Dukedom. Wano / Luffy OPTCG pages are related.", [4]),
    ("Pedro", "pedro", "Mink of Nox. Wano / Luffy OPTCG pages are related.", [4]),
    ("Wanda", "wanda", "Mink of the Mokomo Dukedom. Use the OPTCG hub and Luffy pages.", [4]),
    ("Inazuma", "inazuma", "Revolutionary. Ivankov-adjacent searches start at Luffy pages.", [4]),
    ("Hack", "hack", "Revolutionary fish-man. Use Luffy OPTCG pages.", [4]),
    ("Belo Betty", "belo-betty", "Revolutionary Army commander. Use Luffy OPTCG pages.", [4]),
    ("Karasu", "karasu", "Revolutionary Army commander. Use Luffy OPTCG pages.", [4]),
    ("Morley", "morley", "Revolutionary Army commander. Use Luffy OPTCG pages.", [4]),
    ("Lindbergh", "lindbergh", "Revolutionary Army commander. Use Luffy OPTCG pages.", [4]),
    ("Yamato Oden", "yamato-oden", "Yamato using Oden’s name. Purple Kaido OPTCG lists are related.", [3]),
    ("Onami", "onami", "Nami’s Wano alias. Nami is the constructed OPTCG leader.", [7]),
    ("O-Soba Mask", "o-soba-mask", "Sanji’s raid suit alias. Newgate and RG Luffy lists may play Sanji cards.", [0, 6]),
    ("Sogeking", "sogeking", "Usopp’s Sniper Island alias. Luffy OPTCG pages are related.", [4, 6]),
    ("Lucy", "lucy", "Luffy’s Dressrosa alias. Black Luffy and RG Luffy are the constructed pages.", [4, 6]),
    ("Straw Hat", "straw-hat", "Luffy’s epithet and crew name. Open the Luffy OPTCG leader pages.", [4, 6]),
    ("Gum-Gum", "gum-gum", "Luffy’s Devil Fruit name search. Open Monkey D. Luffy OPTCG lists.", [4, 6]),
    ("Haki", "haki", "OPTCG cards reference Haki in effects. Open any leader list to see constructed cards.", [4, 1]),
    ("DON", "don", "DON!! cards power OPTCG attacks. Every 50-card list on this site plays with DON!!.", [4, 1]),
    ("Leader card", "leader-card", "Every OPTCG deck starts with a leader. Open the leader pages below for 50-card lists.", [4, 1]),
    ("Donquixote Rosinante", "donquixote-rosinante", "Corazon, purple/yellow OP12 leader. Spend a life to save Trafalgar Law, then DON!! −1 to cheapen a 4-cost or higher Law. Not green/blue OP05-022 Rosinante.", [14]),
    ("Corazon", "corazon", "Epithet for Donquixote Rosinante. Open the purple/yellow OP12 OPTCG leader page.", [14]),
    ("Rosinante", "rosinante", "Same search as Donquixote Rosinante / Corazon. OP12-061 is the constructed leader on this site.", [14]),
    ("Robin", "robin", "Same search as Nico Robin. Purple/yellow OP09 is the constructed Straw Hat leader.", [17]),
    ("Moria", "moria", "Same search as Gecko Moria. Black/yellow OP14 is the Thriller Bark OPTCG leader.", [16]),
    ("Character card", "character-card", "OPTCG Character cards make up most of a 50-card list. Open a leader page to see them.", [1, 3]),
    ("Event card", "event-card", "OPTCG Event cards sit in the 50-card list next to Characters. Open any leader page.", [1, 5]),
    ("Stage card", "stage-card", "OPTCG Stage cards are uncommon but show up in some constructed lists on this site.", [7, 2]),
]


def topic_body(topic: dict) -> str:
    return f"""        <div class="crumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / {html.escape(topic["h2"])}</div>
        <h2>{html.escape(topic["h2"])}</h2>
        <p>{html.escape(topic["copy"])}</p>
        <section style="margin-top:18px">
          <div class="section-title">
            <h3>OPTCG leader pages</h3>
            <div class="muted">One Piece TCG</div>
          </div>
          <ul class="list">
{leader_list()}
          </ul>
        </section>
        <p class="muted" style="margin-top:18px">Fan site. Not affiliated with Bandai or Shueisha. <a href="/guides/">More One Piece TCG guides</a>.</p>"""


def character_body(name: str, blurb: str, related: list[int]) -> str:
    rows = []
    for i in related:
        n, href, meta = LEADERS[i]
        rows.append(
            f"""            <li>
              <a class="item" href="{html.escape(href)}">
                <div>
                  <div style="font-weight:700">{html.escape(n)} decklists</div>
                  <div class="muted" style="font-size:13px">{html.escape(meta)} · OPTCG</div>
                </div>
                <div class="link">Open →</div>
              </a>
            </li>"""
        )
    if not rows:
        rows.append(
            f"""            <li>
              <a class="item" href="/decklists/op17.html">
                <div>
                  <div style="font-weight:700">All OP17 leader pages</div>
                  <div class="muted" style="font-size:13px">One Piece TCG hub</div>
                </div>
                <div class="link">Open →</div>
              </a>
            </li>"""
        )
    return f"""        <div class="crumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / <a href="/guides/characters/">Characters</a> / {html.escape(name)}</div>
        <h2>{html.escape(name)}</h2>
        <p>{html.escape(blurb)}</p>
        <section style="margin-top:18px">
          <div class="section-title">
            <h3>Related OPTCG decklists</h3>
            <div class="muted">One Piece Card Game</div>
          </div>
          <ul class="list">
{chr(10).join(rows)}
          </ul>
        </section>
        <p class="muted" style="margin-top:18px"><a href="/guides/characters/">All character guides</a> · <a href="/guides/">One Piece TCG guides</a></p>"""


def guides_index(topic_links: list[tuple[str, str]], char_links: list[tuple[str, str]]) -> str:
    topics = "\n".join(
        f'            <li><a class="item" href="{html.escape(href)}"><div style="font-weight:700">{html.escape(label)}</div><div class="link">Open →</div></a></li>'
        for label, href in topic_links
    )
    chars = "\n".join(
        f'            <li><a class="item" href="{html.escape(href)}"><div style="font-weight:700">{html.escape(label)}</div><div class="link">Open →</div></a></li>'
        for label, href in char_links
    )
    return f"""        <div class="crumb"><a href="/">Home</a> / Guides</div>
        <h2>One Piece TCG guides</h2>
        <p>Topic and character pages that link to the 50-card lists on this site.</p>
        <section style="margin-top:18px">
          <div class="section-title"><h3>Topics</h3><div class="muted">Bandai / OPTCG</div></div>
          <ul class="list">
{topics}
          </ul>
        </section>
        <section style="margin-top:18px">
          <div class="section-title"><h3>Characters</h3><div class="muted">{len(char_links)} names</div></div>
          <ul class="list">
{chars}
          </ul>
        </section>"""


def characters_index(char_links: list[tuple[str, str]]) -> str:
    chars = "\n".join(
        f'            <li><a class="item" href="{html.escape(href)}"><div style="font-weight:700">{html.escape(label)}</div><div class="link">Open →</div></a></li>'
        for label, href in char_links
    )
    return f"""        <div class="crumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / Characters</div>
        <h2>One Piece TCG characters</h2>
        <p>Character names from One Piece, mapped to OPTCG leader decklists on this Bandai One Piece Card Game fan site.</p>
        <ul class="list" style="margin-top:18px">
{chars}
        </ul>"""


def patch_canonical(page: str, url: str) -> str:
    return page.replace(
        f'<link rel="canonical" href="{html.escape(SITE)}" />',
        f'<link rel="canonical" href="{html.escape(url)}" />',
        1,
    )


def write_page(rel: str, title: str, desc: str, body: str) -> str:
    path = ROOT / rel.lstrip("/")
    path.parent.mkdir(parents=True, exist_ok=True)
    url = SITE + ("/" if rel == "guides/index.html" else "/" + rel)
    if rel.endswith("/index.html"):
        url = SITE + "/" + rel[: -len("index.html")]
    page = patch_canonical(chrome(title, desc, body), url)
    path.write_text(page)
    return url


def existing_html_urls() -> list[str]:
    urls = []
    for p in sorted(ROOT.rglob("*.html")):
        if any(part in p.parts for part in (".git", "scripts", "node_modules", "shop")):
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel.endswith("index.html"):
            url = SITE + "/" if rel == "index.html" else SITE + "/" + rel[: -len("index.html")]
        else:
            url = SITE + "/" + rel
        urls.append(url)
    return urls


def main() -> None:
    slugs = [c[1] for c in CHARACTERS]
    if len(slugs) != len(set(slugs)):
        raise SystemExit("duplicate character slugs")
    topic_slugs = [t["slug"] for t in TOPICS]
    if len(topic_slugs) != len(set(topic_slugs)):
        raise SystemExit("duplicate topic slugs")
    topic_links = []
    urls = []
    for topic in TOPICS:
        rel = f"guides/{topic['slug']}.html"
        url = write_page(rel, topic["title"], topic["desc"], topic_body(topic))
        topic_links.append((topic["h2"], "/" + rel))
        urls.append(url)

    char_links = []
    for name, slug, blurb, related in CHARACTERS:
        rel = f"guides/characters/{slug}.html"
        title = f"{name} One Piece TCG | OPTCG decklists"
        desc = f"{name} in the One Piece TCG (OPTCG, Bandai ONE PIECE CARD GAME). Open related 50-card decklists."
        url = write_page(rel, title, desc, character_body(name, blurb, related))
        char_links.append((name, "/" + rel))
        urls.append(url)

    write_page(
        "guides/index.html",
        "One Piece TCG guides | OPTCG | Bandai",
        "Guides for One Piece TCG, OPTCG, Bandai, and character names, linking to real decklists.",
        guides_index(topic_links, char_links),
    )
    write_page(
        "guides/characters/index.html",
        "One Piece TCG characters | OPTCG",
        "One Piece character names mapped to OPTCG decklists on One Piece Deck Base.",
        characters_index(char_links),
    )

    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /shop/\nSitemap: https://onepiecedeckbase.com/sitemap.xml\n"
    )

    all_urls = existing_html_urls()
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in all_urls:
        sitemap.append(f"  <url><loc>{html.escape(url)}</loc></url>")
    sitemap.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap))
    print("topics", len(TOPICS), "characters", len(CHARACTERS), "sitemap", len(all_urls))


if __name__ == "__main__":
    main()
