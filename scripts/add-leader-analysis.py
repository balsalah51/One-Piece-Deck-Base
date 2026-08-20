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
        "YouTube is carrying OP17 Edward Newgate while Limitless still has no posted standings for OP17-001. "
        "MarinefordTCG (also on X @MarinefordTCG) is selling the leader as an 8k-forever beatstick and asking whether the new Whitebeard is already better than Ace; "
        "NightingaleTCG (@BenSchumi7) is on the same page, treating Newgate as a big body that wins long games. "
        "The three public lists agree on the core: 4 Sanji, 4 Portgas D. Ace, 4 Izo, 4 ten-cost Edward Newgate, 4 Kouzuki Oden, Marco, Uta, and Moby Dick. "
        "Flex slots are where the videos diverge — Namule/Curiel search, Rakuyo/Ace beatdown, or an Ivankov/Zoro package — so the consensus below is the Whitebeard package everyone actually shares, not a made-up tournament winner."
    ),
    "OP17-020": (
        "Green Shanks is the loudest argument on YouTube and X, and the quietest deck on Limitless. "
        "StrawHatPecan (@StrawHatPecan) is teaching a freeze-the-board Red Hair list; MarinefordTCG (@MarinefordTCG) is asking if that rest package is already better than Mihawk; "
        "a first-impressions video is still titled as if the leader might be overhyped. "
        "Only a handful of ChinoizeCup lists have shown up, mostly mid-table, so the public take is: the leader effect is real, the deck is not yet proven as the green deck of the format. "
        "Every list still locks Benn Beckman, Yasopp, and the ten-cost Shanks. Most also play Limejuice, Lucky Roux, Crone Oli, and the rest events. "
        "The split is whether you stay in Red Hair or splash Perona, Smoker, and Law like a Mihawk list — the average stays Red Hair."
    ),
    "OP17-039": (
        "Rocks D. Xebec is the OP17 deck people actually registered. JohnnyTCG called it the most fun leader; a first-impressions video asked if blue Rocks was overhyped or legit; "
        "CAPIAMO and CardKaizoku posted testing lists and a builder link almost immediately. "
        "The X/YouTube hype matches the table: this is the densest Limitless pile on the site, and the list is close to solved. "
        "Every sampled deck plays 4 Edward Newgate, 4 Shiki, 4 Charlotte Linlin, 4 Gloriosa, 4 Miss Buckingham Stussy, 4 Rocks D. Xebec, the 4-cost Rocks Pirates stage, and There's No Authority. "
        "Kaido, Streusen, Don Marlon, and Captain John are the only real ratios people argue about. "
        "If you want one list that looks like what the room is playing, use the consensus below."
    ),
    "OP17-058": (
        "Purple Kaido's YouTube arc was 'people slept on this.' JohnnyTCG said the leader is hard to beat; another profile is literally titled that they were wrong about purple Kaido; "
        "a third calls it the new best purple deck; MarinefordTCG (@MarinefordTCG) told people not to sleep on the King of the Beasts. "
        "Limitless agrees more than it does for Shanks or Newgate: Kaido is a high-volume OP17 registration with a tight core. "
        "King, Queen, Basil Hawkins, Yamato, the on-leader Kaido, Mamaragan, and We're Going to Claim the One Piece are in every list we averaged. "
        "Charlotte Linlin from the starter, Slow-Slow Beam Sword, and the cheaper Kaido are close behind. "
        "Flex is Black Maria, Jack, Divine Departure, or the new OP17 events — not whether the All-Star package belongs."
    ),
    "OP17-079": (
        "Black OP17 Monkey D. Luffy is the Elbaph blocker deck on YouTube. StrawHatPecan (@StrawHatPecan) is selling infinite blockers; "
        "BlaisePlaysTCG says the leader is already strong; the early Elbaph profile lists are the same Straw Hat plus giants package you see on Limitless. "
        "Usopp, Gerd, and Loki are 4-ofs in every list. Most also play Jaguar D. Saul, a Luffy beater, Zoro, Nico Robin, Rodo, Sanji, and Chopper. "
        "The argument on X and in the comments is how much Straw Hat glue you keep versus extra giants and events like Gum-Gum Kong Gun, Tempest Kick, or Thousand Sunny. "
        "It is not a solved 4-of pile like Rocks, but the consensus is clearly Elbaph Luffy, not a leftover black midrange pile from an older set."
    ),
    "OP17-099": (
        "Yellow Charlotte Linlin came out of YouTube sounding like a problem. StrawHatPecan (@StrawHatPecan) called it the slop yellow deck and meant that as a compliment; "
        "another profile is titled that Linlin is a big problem. "
        "Limitless lists back that up: this is a real OP17 registration, not a flavor leader. "
        "Pudding, the on-color Linlin, and Cracker are in every averaged list. Katakuri, Oven, Sweet 3 Generals, Daifuku, and Zeus are in almost all of them. "
        "Perospero, Smoothie, and Streusen are the next tier. Teach and Brulee are the main splits. "
        "The community take is that yellow finally has an OP17 boss that just plays Big Mom cards and wins by generating too many bodies, not by a cute trigger gimmick."
    ),
    "OP13-001": (
        "RG Luffy is the current-format deck YouTube keeps returning to. JohnnyTCG asked if it just became meta again; "
        "ArtressTCG (@michaelartress) said they made it even harder to beat and posted the list on the EgmanEvents builder. "
        "Unlike the brand-new OP17 leaders, this one has a long Limitless sample, and the average is a Straw Hat value pile: Sanji, Usopp, Nami, EB04 Zoro, Brook, Charlestone, starter Luffy, and Thousand Sunny. "
        "Laboon, Electrical Luna, and Bonney are common; the 10-cost Luffy and extra Zoro events are the usual cuts. "
        "The X take matches the lists: RG Luffy did not leave when OP17 arrived, it just absorbed new green and red tools and kept winning local tables."
    ),
    "OP11-041": (
        "UY Nami's public conversation is older than OP17, and the lists show it. YouTube profiles from OP15/EB04, an 'ultimate' blue/yellow guide, and KebbieG's OP16 gameplay all point at the same engine: "
        "draw when Life cards leave, then a Thriller Bark yellow package. "
        "Every averaged list plays Kumacy, Gecko Moria, Nico Robin, Nami, Borsalino, and Perona. Hogback, Zeus, and a Newgate splash are close to required. "
        "Mr. 3, Marco, Kikunojo, and Gravity Blade are the next tier; Girl and Teach are the older vs newer split. "
        "On X and in those videos the knock is that Nami is linear; the praise is that the linear plan still puts up Limitless results next to the new emperors."
    ),
    "OP14-020": (
        "Green Mihawk's YouTube story is the starter-deck lottery. ArtressTCG (@michaelartress) said Mihawk won that lottery and posted a Law/Bepo plus ST32 list on EgmanEvents. "
        "Limitless is full of that same green pile: Perona (both printings), Law & Bepo, Kin'emon, Kouzuki Oden, the Mihawk character, and Dead Man's Game. "
        "Otama, Kikunojo, You Can Be My Samurai, Coffin Boat, and the rush event show up in most lists; Smoker, Zoro, and the ten-cost Mihawk are the flex. "
        "The community comparison on X is Mihawk versus the new OP17 Shanks rest deck — Mihawk has the tournament sample, Shanks has the new-set hype. "
        "The consensus below is the Mihawk list the room is actually submitting."
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
            f'<p class="muted">Averaged from {n} YouTube, web, and Limitless lists on this page. '
            "Copies are the typical count among lists that play the card, then filled to 50. "
            "Hover or tap a name for the picture.</p>"
        ),
        1,
    )
    return f"""        <!-- LEADER_ANALYSIS -->
        <section class="leader-analysis" style="margin-top:22px">
          <div class="section-title">
            <h3>Community take</h3>
            <div class="muted">YouTube and X</div>
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
