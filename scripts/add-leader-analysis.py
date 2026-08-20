#!/usr/bin/env python3
"""Add a community take and a consensus 50-card list to every leader hub."""

from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path

import importlib.util

spec = importlib.util.spec_from_file_location("genlists", "/workspace/scripts/generate-tournament-lists.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

ROOT = gen.ROOT
LINE_RE = re.compile(
    r'<span class="qty">(\d+)x</span>.*?<span class="muted card-id">([^<]+)</span>',
    re.S,
)
BLOCK_RE = re.compile(
    r"        <!-- LEADER_ANALYSIS -->.*?        <!-- /CONSENSUS_LIST -->\n?",
    re.S,
)
TARGET = 50

TAKES = {
    "OP17-001": (
        "Red OP17 Edward Newgate is a Whitebeard beatstick that keeps 8000-power bodies on the board. "
        "Core lists play 4 Sanji, 4 Portgas D. Ace, 4 Izo, 4 ten-cost Edward Newgate, 4 Kouzuki Oden, plus Marco, Uta, and Moby Dick. "
        "Flex is Namule/Curiel search, Rakuyo beatdown, or an Ivankov/Zoro package."
    ),
    "OP17-020": (
        "Green OP17 Shanks rests the board and plays Red Hair Pirates. "
        "Every list locks Benn Beckman, Yasopp, and the ten-cost Shanks; most also play Limejuice, Lucky Roux, Crone Oli, and rest events. "
        "The split is staying in-theme versus splashing Perona, Smoker, and Law like Mihawk."
    ),
    "OP17-039": (
        "Blue OP17 Rocks D. Xebec is the densest Limitless pile on this site. "
        "Lists play 4 Edward Newgate, 4 Shiki, 4 Charlotte Linlin, 4 Gloriosa, 4 Miss Buckingham Stussy, 4 Rocks D. Xebec, the Rocks Pirates stage, and There's No Authority. "
        "Kaido, Streusen, Don Marlon, and Captain John are the usual ratio fights."
    ),
    "OP17-058": (
        "Purple OP17 Kaido is All-Star midrange with a tight tournament core. "
        "King, Queen, Basil Hawkins, Yamato, the on-leader Kaido, Mamaragan, and We're Going to Claim the One Piece show up in every averaged list. "
        "Flex is Black Maria, Jack, Divine Departure, or the new OP17 events."
    ),
    "OP17-079": (
        "Black OP17 Monkey D. Luffy is the Elbaph blocker deck, not Imu. "
        "Usopp, Gerd, and Loki are 4-ofs; most lists also play Jaguar D. Saul, a Luffy beater, Zoro, Nico Robin, Rodo, Sanji, and Chopper. "
        "Flex is extra giants versus events like Gum-Gum Kong Gun, Tempest Kick, or Thousand Sunny."
    ),
    "OP17-099": (
        "Yellow OP17 Charlotte Linlin is a Big Mom swarm leader. "
        "Pudding, the on-color Linlin, and Cracker are in every averaged list; Katakuri, Oven, Sweet 3 Generals, Daifuku, and Zeus are close behind. "
        "Perospero, Smoothie, Streusen, Teach, and Brulee fill the rest."
    ),
    "OP13-001": (
        "RG Luffy is a Straw Hat value pile that still posts in current format. "
        "Lists average Sanji, Usopp, Nami, EB04 Zoro, Brook, Charlestone, starter Luffy, and Thousand Sunny. "
        "Laboon, Electrical Luna, and Bonney are common; the 10-cost Luffy and extra Zoro events are the usual cuts."
    ),
    "OP11-041": (
        "Blue/Yellow Nami draws when Life cards leave, then plays a Thriller Bark yellow package. "
        "Every averaged list has Kumacy, Gecko Moria, Nico Robin, Nami, Borsalino, and Perona; Hogback, Zeus, and a Newgate splash are close to required. "
        "Mr. 3, Marco, Kikunojo, and Gravity Blade are the next tier."
    ),
    "OP14-020": (
        "Green Mihawk is a rest/control pile. "
        "Limitless lists play Perona (both printings), Law & Bepo, Kin'emon, Kouzuki Oden, the Mihawk character, and Dead Man's Game. "
        "Otama, Kikunojo, You Can Be My Samurai, Coffin Boat, and the rush event show up in most lists; Smoker, Zoro, and the ten-cost Mihawk are flex."
    ),
    "OP16-001": (
        "Red OP16 Portgas D. Ace is Whitebeard rush — not the red/blue OP13 Ace. "
        "Lists lock 4 Monkey D. Luffy, 4 Edward Newgate, 4 Vista, and Moby Dick; Garp, Little Oars Jr., Curiel, Marco, and Thatch are close to required. "
        "The 10-cost Ace is usually a 3-of; Namule, Time for the Counterattack, Uta, and Izo are flex."
    ),
    "OP15-058": (
        "Purple OP15 Enel is Sky Island ramp: a 6-card DON!! deck that floods DON!! from turn two and rests the board. "
        "Averaged lists play Ohm, Shura, Enel, El Thor, Lightning Beast Kiten, Lightning Dragon, Mamaragan, Charlotte Pudding, and Vinsmoke Reiju. "
        "Gamma Knife, Varie, Senor Pink, and Divine Departure fill the rest. This is not yellow OP05 Enel."
    ),
    "OP11-062": (
        "Purple OP11 Charlotte Katakuri is the other Big Mom leader, separate from yellow OP17 Linlin. "
        "DON!! −1 on attack or on the opponent's attack to peek their deck and gain power. "
        "Core is Katakuri and Pudding in both printings plus ST34 Big Mom: Katakuri, Brulee, Linlin, and Cracker, with We're Going to Claim the One Piece, Mamaragan, and Divine Departure."
    ),
    "OP13-079": (
        "Black OP13 Imu is Mary Geoise / Five Elders, not OP17 Elbaph Luffy. "
        "No 2-cost or higher events, and the Empty Throne stage starts in play from deck. "
        "Lists play Saturn, Warcury, Nusjuro, Mars, Ju Peter, the 10-cost Five Elders, Saint Shalria, and The Five Elders Are at Your Service. Saint Charlos, Sabo, Never Existed, and Ground Death are flex."
    ),
    "OP13-002": (
        "OP13 Ace is red/blue Portgas D. Ace — 3 life, 6000 power — not the red OP16 Ace rush deck. "
        "Trash a card to give −2000, then draw when you take damage or a 6000-power body dies. "
        "Core is Monkey D. Garp, Otama, Izo, Marco, Yamato, OP13 Edward Newgate, and I Am Whitebeard; Uta, Jozu, Atmos, and Roger finish."
    ),
    "OP12-061": (
        "Purple/yellow OP12 Donquixote Rosinante is Corazon’s Law engine, not green/blue OP05-022 Rosinante. "
        "Spend a life to save Trafalgar Law from K.O., then DON!! −1 to play a 4-cost or higher Law for 2 less. "
        "Lists are Law, Dressrosa, and DON!! tricks; some recent copies splash OP17 cards."
    ),
    "OP13-004": (
        "Red/black OP13-004 Sabo is Dressrosa / Revolutionary Army, not ST13 Sabo. "
        "At 4+ life the leader is −1000; DON!! x1 plus an 8-cost character pumps the whole board. "
        "Recent lists have started packing OP17 cards on top of the 8-cost Revolutionary package."
    ),
    "OP14-080": (
        "Black/yellow OP14 Gecko Moria is Thriller Bark: K.O. your own Thriller Bark character to give the board +1000, then trash 3 to gain a life. "
        "Recent copies include OP17 cards in the 50-card list. This is not a Mihawk sideboard — Moria is the leader."
    ),
    "OP09-062": (
        "Purple/yellow OP09 Nico Robin is a banish leader that trashes a Trigger to rest a DON!!. "
        "Recent lists have picked up OP17 cards. This is the Straw Hat archaeologist leader, not a cameo in Black Luffy."
    ),
}

POPUP_JS = r"""
    (function(){
      var lines = document.querySelectorAll('.text-line');
      if (!lines.length) return;
      function resetPop(pop){
        pop.style.position = '';
        pop.style.left = '';
        pop.style.top = '';
        pop.style.right = '';
        pop.style.bottom = '';
        pop.classList.remove('flip-left', 'flip-down');
      }
      function place(line){
        var pop = line.querySelector('.card-pop');
        var title = line.querySelector('.card-title');
        if (!pop || !title) return;
        resetPop(pop);
        var tr = title.getBoundingClientRect();
        var width = pop.offsetWidth || 110;
        var height = pop.offsetHeight || 154;
        var left = tr.left;
        var top = tr.top - height - 10;
        if (left + width > window.innerWidth - 12) left = window.innerWidth - width - 12;
        if (left < 12) left = 12;
        if (top < 12) top = tr.bottom + 10;
        if (top + height > window.innerHeight - 12) top = Math.max(12, window.innerHeight - height - 12);
        pop.style.position = 'fixed';
        pop.style.left = left + 'px';
        pop.style.top = top + 'px';
        pop.style.bottom = 'auto';
        pop.style.right = 'auto';
      }
      lines.forEach(function(line){
        line.addEventListener('mouseenter', function(){ place(line); });
        line.addEventListener('focus', function(){ place(line); });
        line.addEventListener('click', function(e){
          if (window.matchMedia('(hover: hover)').matches) return;
          e.stopPropagation();
          lines.forEach(function(other){ if (other !== line) other.classList.remove('is-open'); });
          line.classList.toggle('is-open');
          place(line);
        });
      });
      document.addEventListener('click', function(e){
        if (!e.target.closest('.text-line')) {
          lines.forEach(function(line){ line.classList.remove('is-open'); });
        }
      });
    })();
"""


def parse_deck(path: Path, leader_id: str) -> dict[str, int] | None:
    text = path.read_text()
    cards: dict[str, int] = {}
    for n, cid in LINE_RE.findall(text):
        cid = cid.strip()
        if cid == leader_id:
            continue
        cards[cid] = cards.get(cid, 0) + int(n)
    if sum(cards.values()) < 40:
        return None
    return cards


def consensus_list(decks: list[dict[str, int]]) -> list[tuple[str, int, float]]:
    n = len(decks)
    play: dict[str, int] = defaultdict(int)
    copy_sum: dict[str, int] = defaultdict(int)
    for deck in decks:
        for cid, count in deck.items():
            play[cid] += 1
            copy_sum[cid] += count
    ranked = sorted(play, key=lambda cid: (-play[cid] / n, -copy_sum[cid] / play[cid], cid))
    picked: list[tuple[str, int, float]] = []
    total = 0
    for cid in ranked:
        rate = play[cid] / n
        if rate < 0.25 and total >= 46:
            continue
        copies = int(round(copy_sum[cid] / play[cid]))
        copies = max(1, min(4, copies))
        if total + copies > TARGET:
            copies = TARGET - total
        if copies <= 0:
            break
        picked.append((cid, copies, rate))
        total += copies
        if total >= TARGET:
            break
    if total < TARGET:
        have = {cid for cid, _c, _r in picked}
        for cid in ranked:
            if cid in have:
                continue
            need = TARGET - total
            copies = min(need, max(1, min(4, int(round(copy_sum[cid] / play[cid])))))
            picked.append((cid, copies, play[cid] / n))
            total += copies
            if total >= TARGET:
                break
    return picked


def grouped_from_picks(leader: dict, picks: list[tuple[str, int, float]], cache: dict) -> tuple[dict, dict]:
    grouped = {"Leader": [], "Characters": [], "Events": [], "Stages": []}
    totals = defaultdict(int)
    lid = leader["id"]
    grouped["Leader"].append(
        {
            "count": 1,
            "id": lid,
            "name": cache.get(lid, {}).get("name") or leader["name"],
            "group": "Leader",
        }
    )
    for cid, count, _rate in picks:
        meta = cache.get(cid) or {}
        cat = (meta.get("category") or "character").lower()
        if cat == "event":
            group = "Events"
        elif cat == "stage":
            group = "Stages"
        else:
            group = "Characters"
        grouped[group].append(
            {
                "count": count,
                "id": cid,
                "name": meta.get("name") or cid,
                "group": group,
            }
        )
        totals[group] += count

    def cost_key(item: dict) -> int:
        try:
            return int((cache.get(item["id"]) or {}).get("cost"))
        except (TypeError, ValueError):
            return 99

    for group in grouped:
        grouped[group].sort(
            key=lambda it: (
                cost_key(it),
                gen.display_name((cache.get(it["id"]) or {}).get("name") or it["name"]),
            )
        )
    return grouped, totals


def analysis_block(leader: dict, n: int, take: str, text_deck: str) -> str:
    text_deck = text_deck.replace("<h3>Text list</h3>", "<h3>Consensus list</h3>", 1)
    text_deck = text_deck.replace(
        '<p class="muted">Hover or tap a card name to see the picture.</p>',
        (
            f'<p class="muted">Averaged from {n} lists on this page, then filled to 50 cards. '
            "Hover or tap a name for the picture.</p>"
        ),
        1,
    )
    return f"""        <!-- LEADER_ANALYSIS -->
        <section class="leader-analysis" style="margin-top:22px">
          <div class="section-title">
            <h3>How it plays</h3>
            <div class="muted">Staples from lists on this page</div>
          </div>
          <p class="leader-take">{html.escape(take)}</p>
        </section>
        <!-- /LEADER_ANALYSIS -->
        <!-- CONSENSUS_LIST -->
{text_deck}
        <!-- /CONSENSUS_LIST -->
"""


def ensure_popup_js(page: str) -> str:
    if "querySelectorAll('.text-line')" in page:
        return page
    old = """  <script>
    document.getElementById('year').textContent = new Date().getFullYear();
  </script>"""
    new = f"""  <script>
    document.getElementById('year').textContent = new Date().getFullYear();{POPUP_JS}
  </script>"""
    if old not in page:
        return page
    return page.replace(old, new, 1)


def inject(page: str, block: str) -> str:
    page = BLOCK_RE.sub("", page)
    marker = "        <!-- COMMUNITY_DECKLISTS -->"
    if marker not in page:
        marker = "        <!-- TOURNAMENT_DECKLISTS -->"
    if marker not in page:
        raise SystemExit("no insert marker")
    return page.replace(marker, block + "\n" + marker, 1)


def main() -> None:
    cache = gen.load_card_cache()
    index = {}
    for leader in gen.LEADERS:
        lid = leader["id"]
        decks = []
        for path in sorted((ROOT / leader["dir"]).glob("*.html")):
            parsed = parse_deck(path, lid)
            if parsed:
                decks.append({"slug": path.stem, "cards": parsed})
        raw_decks = [d["cards"] for d in decks]
        if not raw_decks:
            print(lid, "no decks")
            continue
        picks = consensus_list(raw_decks)
        total = sum(c for _i, c, _r in picks)
        print(lid, "from", len(raw_decks), "lists", "cards", total)
        grouped, totals = grouped_from_picks(leader, picks, cache)
        text_deck = gen.render_text_deck(grouped, cache, ["Leader", "Characters", "Events", "Stages"], totals)
        take = TAKES[lid]
        block = analysis_block(leader, len(raw_decks), take, text_deck)
        page_path = ROOT / leader["page"]
        page = inject(page_path.read_text(), block)
        page = ensure_popup_js(page)
        page_path.write_text(page)
        index[lid] = {
            "lists": len(raw_decks),
            "cards": [{"id": cid, "count": count, "rate": round(rate, 3)} for cid, count, rate in picks],
        }
    (ROOT / "data/consensus-decks.json").write_text(json.dumps(index, indent=2) + "\n")
    print("done")


if __name__ == "__main__":
    main()
