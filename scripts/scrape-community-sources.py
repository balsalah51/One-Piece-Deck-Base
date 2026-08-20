#!/usr/bin/env python3
"""Pull public 50-card OPTCG lists from One Piece Top Decks, YouTube, and X.

Does not invent lists, log into anything, or run generate-tournament-lists.main().
Writes new pages, then rebuilds hub community/tournament blocks in place.
"""

from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import importlib.util

spec = importlib.util.spec_from_file_location("genlists", "/workspace/scripts/generate-tournament-lists.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

cspec = importlib.util.spec_from_file_location("commlists", "/workspace/scripts/add-community-lists.py")
comm = importlib.util.module_from_spec(cspec)
cspec.loader.exec_module(comm)

aspec = importlib.util.spec_from_file_location("morelists", "/workspace/scripts/add-more-tournament-lists.py")
more = importlib.util.module_from_spec(aspec)
aspec.loader.exec_module(more)

ROOT = gen.ROOT
UA = "OnePieceDeckBase/1.0 (+https://onepiecedeckbase.com; public OPTCG list scrape)"
BROWSER = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
LEADERS = {L["id"] for L in gen.LEADERS}
LEADER_BY_ID = {L["id"]: L for L in gen.LEADERS}
LINE_RE = re.compile(r"(?i)(\d+)\s*[x×]\s*((?:OP|ST|EB|PRB)\d{2}-\d{3}|P-\d{3})")
COMPACT_RE = re.compile(r"(\d+)n((?:OP|ST|EB|PRB)\d{2}-\d{3}|P-\d{3})a", re.I)
YT_ID_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|watch\?v=|\"videoId\":\")([A-Za-z0-9_-]{11})"
)
STATUS_RE = re.compile(r"(?:x\.com|twitter\.com)/([A-Za-z0-9_]+)/status/(\d+)", re.I)
OPTD_LIMIT = 40
YT_LIMIT = 8
X_LIMIT = 8

OPTD_PAGES = [
    "https://onepiecetopdecks.com/deck-list/english-op17-deck-list-the-worlds-strongest-warriors/",
    "https://onepiecetopdecks.com/deck-list/english-op16-deck-list-the-time-of-battle/",
    "https://onepiecetopdecks.com/deck-list/english-op15-eb04-deck-list-adventure-on-kamis-island/",
    "https://onepiecetopdecks.com/deck-list/english-op-14-eb-04-deck-list-the-azure-sea-seven/",
    "https://onepiecetopdecks.com/deck-list/english-op-13-deck-list-carrying-on-his-will/",
]

YT_CHANNELS = [
    "https://www.youtube.com/@MarinefordTCG",
    "https://www.youtube.com/@MarinefordTCG/videos",
    "https://www.youtube.com/@StrawHatPecan",
    "https://www.youtube.com/@StrawHatPecan/videos",
    "https://www.youtube.com/@CardKaizoku",
    "https://www.youtube.com/@CardKaizoku/videos",
    "https://www.youtube.com/@JohnnyTCG",
    "https://www.youtube.com/@JohnnyTCG/videos",
    "https://www.youtube.com/@BlaisePlaysTCG",
    "https://www.youtube.com/@BlaisePlaysTCG/videos",
    "https://www.youtube.com/@ArtressTCG",
    "https://www.youtube.com/@KebbieG",
    "https://www.youtube.com/@NightingaleTCG",
    "https://www.youtube.com/@TCG353",
    "https://www.youtube.com/@TheEgman",
    "https://www.youtube.com/@EgmanEvents",
    "https://www.youtube.com/@CAPIAMO",
    "https://www.youtube.com/@MabTCG",
]

YT_SEARCHES = [
    'site:youtube.com "1xOP17-001"',
    'site:youtube.com "1xOP17-020" decklist',
    'site:youtube.com "1xOP17-039" Rocks decklist',
    'site:youtube.com "1xOP17-058" Kaido decklist',
    'site:youtube.com "1xOP17-079" Luffy decklist',
    'site:youtube.com "1xOP17-099" Linlin decklist',
    'site:youtube.com "1xOP13-001" RG Luffy decklist',
    'site:youtube.com "1xOP11-041" Nami decklist',
    'site:youtube.com "1xOP14-020" Mihawk decklist',
    'site:youtube.com "1xOP16-001" Ace decklist',
    'site:youtube.com "1xOP15-058" Enel decklist',
    'site:youtube.com "1xOP13-079" Imu decklist',
    'site:youtube.com OP17 Newgate deck profile',
    'site:youtube.com OP17 Shanks deck profile',
]

X_HANDLES = [
    "MarinefordTCG",
    "StrawHatPecan",
    "BenSchumi7",
    "CardKaizoku",
    "BlaisePlaysTCG",
    "NightingaleTCG",
    "michaelartress",
    "ArtressTCG",
    "JohnnyTCG",
    "TheEgman",
    "KebbieG",
    "TCG353",
    "ONEPIECE_tcg_EN",
    "LimitlessTCG",
    "optcg",
]
X_SEARCHES = [
    'site:x.com "1xOP17-001"',
    'site:x.com "1xOP17-020"',
    'site:x.com "1xOP17-039"',
    'site:x.com "1xOP17-058"',
    'site:x.com "4xOP17-040"',
    'site:x.com "1xOP16-001" decklist',
    'site:x.com "1xOP13-079" Imu',
    "site:x.com MarinefordTCG OP17 decklist",
    "site:x.com CardKaizoku OP17",
    "site:x.com StrawHatPecan OP17 list",
]


def log(*args) -> None:
    print(*args, flush=True)


def fetch(url: str, timeout: int = 20, browser: bool = False) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": BROWSER if browser else UA,
            "Accept": "text/html,application/json,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace") if exc.fp else ""
        return exc.code, body
    except Exception as exc:  # noqa: BLE001
        return 0, f"{type(exc).__name__}: {exc}"


def card_hits(text: str) -> list[tuple[int, str]]:
    return [(int(n), cid.upper()) for n, cid in LINE_RE.findall(text or "")]


def complete_lists(hits: list[tuple[int, str]]) -> list[dict]:
    if not hits:
        return []
    chunks: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for count, cid in hits:
        if count == 1 and cid in LEADERS and current:
            chunks.append(current)
            current = []
        current.append((count, cid))
    if current:
        chunks.append(current)
    out = []
    for chunk in chunks:
        leader = chunk[0][1] if chunk[0][1] in LEADERS else None
        main = chunk[1:] if leader else chunk
        total = sum(c for c, _ in main)
        if leader and 46 <= total <= 52:
            out.append(
                {
                    "leader": leader,
                    "cards": total,
                    "raw": " ".join(f"{c}x{i}" for c, i in chunk),
                }
            )
    return out


def parse_compact(blob: str) -> tuple[str | None, str, int]:
    cards = [(int(n), cid.upper()) for n, cid in COMPACT_RE.findall(blob or "")]
    if not cards:
        return None, "", 0
    leader = cards[0][1] if cards[0][0] == 1 and cards[0][1] in LEADERS else None
    if leader is None:
        return None, "", 0
    total = sum(n for n, cid in cards if cid != leader)
    raw = " ".join(f"{n}x{cid}" for n, cid in cards)
    return leader, raw, total


def parse_mdy(text: str) -> str:
    text = (text or "").strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def parse_placing(text: str) -> int | None:
    m = re.match(r"\s*(\d+)(?:st|nd|rd|th)\b", text or "", re.I)
    if m:
        return int(m.group(1))
    return None


def parse_record(text: str) -> dict:
    m = re.search(r"(\d+)\s*-\s*(\d+)(?:\s*-\s*(\d+))?", text or "")
    if not m:
        return {}
    rec = {"wins": int(m.group(1)), "losses": int(m.group(2))}
    if m.group(3) is not None:
        rec["ties"] = int(m.group(3))
    return rec


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def existing_source_urls() -> set[str]:
    urls: set[str] = set()
    for items in comm.COMMUNITY.values():
        for item in items:
            if item.get("source_url"):
                urls.add(item["source_url"])
    index = more.load_index()
    for items in index.values():
        for item in items or []:
            if item.get("source_url"):
                urls.add(item["source_url"])
    return urls


def existing_player_keys(index: dict) -> set[tuple[str, str, str]]:
    keys = set()
    for lid, items in index.items():
        for item in items or []:
            keys.add((lid, norm(item.get("player") or ""), parse_mdy(item.get("date") or "") or (item.get("date") or "")))
            keys.add((lid, norm(item.get("player") or ""), norm(item.get("tournament") or item.get("tournament_name") or "")))
    return keys


def existing_video_ids() -> set[str]:
    ids = set()
    for url in existing_source_urls():
        m = YT_ID_RE.search(url)
        if m:
            ids.add(m.group(1))
    return ids


def scrape_optd() -> list[dict]:
    found = []
    for url in OPTD_PAGES:
        status, body = fetch(url, timeout=40)
        log("optd", status, url.split("/")[-2], "chars", len(body))
        for href in re.findall(r"href=['\"](deckgen\?[^'\"]+)['\"]", body):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(href.replace("&amp;", "&")).query)
            blob = (qs.get("dg") or [""])[0]
            leader, raw, total = parse_compact(blob)
            if not leader or not (46 <= total <= 52):
                continue
            player = (qs.get("au") or [""])[0].strip() or "Unknown"
            host = (qs.get("hs") or [""])[0].strip()
            tname = (qs.get("tn") or [""])[0].strip()
            event = " · ".join(p for p in (host, tname) if p) or "One Piece Top Decks"
            place_text = (qs.get("pl") or [""])[0].strip()
            deck_name = (qs.get("dn") or [""])[0].strip()
            date = parse_mdy((qs.get("date") or [""])[0])
            found.append(
                {
                    "leader": leader,
                    "raw": raw,
                    "player": player,
                    "tournament_name": event,
                    "placing": parse_placing(place_text),
                    "record": parse_record(place_text),
                    "date": date,
                    "kind": "topdecks",
                    "title": f"{player} — {deck_name or LEADER_BY_ID[leader]['name']}",
                    "subtitle": " · ".join(p for p in (event, place_text, date, "One Piece Top Decks") if p),
                    "source_url": url,
                    "source_page": url,
                }
            )
        time.sleep(0.2)
    log("optd complete lists", len(found))
    return found


def ddg_ids(query: str) -> list[str]:
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    status, body = fetch(url, timeout=18, browser=True)
    text = urllib.parse.unquote(body.replace("&amp;", "&"))
    ids = list(dict.fromkeys(YT_ID_RE.findall(text)))
    log("ddg yt", status, len(ids), query[:48])
    return ids


def extract_yt_desc(html_text: str) -> tuple[str, str, str]:
    title = ""
    m = re.search(r'<meta property="og:title" content="([^"]+)"', html_text)
    if m:
        title = html.unescape(m.group(1))
    author = ""
    m = re.search(r'"ownerChannelName":"([^"]+)"', html_text)
    if m:
        author = html.unescape(m.group(1))
    desc = ""
    key = '"attributedDescriptionBodyText":{"content":'
    i = html_text.find(key)
    if i >= 0:
        try:
            desc, _ = json.JSONDecoder().raw_decode(html_text[i + len(key) :])
        except json.JSONDecodeError:
            desc = ""
    return title, author, desc or ""


def scrape_youtube() -> list[dict]:
    video_ids: list[str] = []
    seen = existing_video_ids()
    for channel in YT_CHANNELS:
        status, body = fetch(channel, timeout=25, browser=True)
        ids = list(dict.fromkeys(YT_ID_RE.findall(body)))
        log("yt channel", status, len(ids), channel.split("/")[-2])
        for vid in ids[:10]:
            if vid not in seen:
                video_ids.append(vid)
                seen.add(vid)
        time.sleep(0.15)
    for query in YT_SEARCHES:
        for vid in ddg_ids(query):
            if vid not in seen:
                video_ids.append(vid)
                seen.add(vid)
        time.sleep(0.2)
    found = []
    per_leader: dict[str, int] = defaultdict(int)
    for vid in video_ids:
        if all(per_leader[lid] >= YT_LIMIT for lid in LEADERS) and found:
            break
        url = f"https://www.youtube.com/watch?v={vid}"
        status, body = fetch(url, timeout=25, browser=True)
        title, author, desc = extract_yt_desc(body)
        lists = complete_lists(card_hits(desc))
        log("yt video", status, vid, "lists", len(lists), (title or "")[:60])
        player = author or "YouTube"
        for item in lists:
            lid = item["leader"]
            if per_leader[lid] >= YT_LIMIT:
                continue
            found.append(
                {
                    **item,
                    "player": player,
                    "kind": "youtube",
                    "title": (title.split("|")[0].split("-")[0].strip() or f"{player} decklist") + f" — {player}",
                    "subtitle": f"YouTube deck profile · {player}",
                    "source_url": url,
                }
            )
            per_leader[lid] += 1
        time.sleep(0.2)
    log("youtube complete lists", len(found))
    return found


def scrape_x() -> list[dict]:
    status_ids: dict[str, str] = {}
    found: list[dict] = []
    handle_set = {h.lower() for h in X_HANDLES}
    for handle in X_HANDLES:
        url = f"https://r.jina.ai/https://x.com/{handle}"
        status, body = fetch(url, timeout=18)
        ids = STATUS_RE.findall(body)
        lists = complete_lists(card_hits(body))
        log("x profile", status, handle, "ids", len(ids), "lists", len(lists))
        for item in lists:
            found.append(
                {
                    **item,
                    "player": handle,
                    "kind": "x",
                    "title": f"{handle} list — {LEADER_BY_ID[item['leader']]['name']}",
                    "subtitle": f"Public X post · @{handle}",
                    "source_url": f"https://x.com/{handle}",
                }
            )
        for h, sid in ids:
            if h.lower() in handle_set or h.lower() == handle.lower():
                status_ids.setdefault(sid, h)
        time.sleep(0.2)
    for query in X_SEARCHES:
        url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
        status, body = fetch(url, timeout=15, browser=True)
        ids = STATUS_RE.findall(urllib.parse.unquote(body.replace("&amp;", "&")))
        log("x search", status, len(ids), query[:48])
        for h, sid in ids:
            status_ids.setdefault(sid, h)
        found.extend(
            {
                **item,
                "player": "X",
                "kind": "x",
                "title": f"X list — {LEADER_BY_ID[item['leader']]['name']}",
                "subtitle": "Public X post",
                "source_url": query,
            }
            for item in complete_lists(card_hits(body))
        )
        time.sleep(0.2)
    per_leader: dict[str, int] = defaultdict(int)
    kept = []
    for sid, handle in list(status_ids.items())[:80]:
        url = f"https://api.fxtwitter.com/{handle}/status/{sid}"
        status, body = fetch(url, timeout=12)
        data = {}
        try:
            data = json.loads(body) if body.lstrip().startswith("{") else {}
        except json.JSONDecodeError:
            data = {}
        tweet = (data.get("tweet") or {}) if isinstance(data, dict) else {}
        blob = (tweet.get("text") or "") + "\n" + body
        lists = complete_lists(card_hits(blob))
        log("x tweet", status, handle, sid, "lists", len(lists))
        source = f"https://x.com/{handle}/status/{sid}"
        for item in lists:
            lid = item["leader"]
            if per_leader[lid] >= X_LIMIT:
                continue
            kept.append(
                {
                    **item,
                    "player": handle,
                    "kind": "x",
                    "title": f"{handle} — {LEADER_BY_ID[lid]['name']}",
                    "subtitle": f"Public X post · @{handle}",
                    "source_url": source,
                }
            )
            per_leader[lid] += 1
        time.sleep(0.15)
    found.extend(kept)
    log("x complete lists", len(found))
    return found


def pick_optd(rows: list[dict], index: dict) -> list[dict]:
    known = existing_player_keys(index)
    have = {L["id"]: more.existing_stems(L) for L in gen.LEADERS}
    picked: dict[str, list] = defaultdict(list)
    def quality(row: dict) -> tuple:
        placing = row.get("placing")
        placing_n = int(placing) if placing is not None else 10_000
        date = row.get("date") or ""
        return (placing_n, date)
    for row in sorted(rows, key=quality):
        lid = row["leader"]
        if lid not in LEADERS or len(picked[lid]) >= OPTD_LIMIT:
            continue
        player_n = norm(row["player"])
        date = row.get("date") or ""
        event_n = norm(row.get("tournament_name") or "")
        if (lid, player_n, date) in known or (lid, player_n, event_n) in known:
            continue
        leader = LEADER_BY_ID[lid]
        entry = {
            "player": row["player"],
            "tournament_name": row["tournament_name"],
            "placing": row.get("placing"),
            "record": row.get("record") or {},
            "date": date,
            "kind": "topdecks",
            "source_url": row["source_url"],
            "subtitle": row.get("subtitle"),
        }
        slug = gen.unique_slug(
            {
                **entry,
                "forced_slug": None,
                "player": f"optd-{row['player']}",
                "tournament_name": row["tournament_name"],
            },
            have[lid],
        )
        # unique_slug uses player in the slug; prefix already added via player rewrite above
        entry["slug"] = slug
        entry["href"] = f"/{leader['dir']}/{slug}.html"
        entry["raw"] = row["raw"]
        entry["leader"] = lid
        picked[lid].append(entry)
        known.add((lid, player_n, date))
        known.add((lid, player_n, event_n))
    out = []
    for lid, items in picked.items():
        log("optd keep", lid, len(items))
        out.extend(items)
    return out


def pick_community(rows: list[dict], kind: str, limit: int) -> dict[str, list]:
    have = {L["id"]: more.existing_stems(L) for L in gen.LEADERS}
    seen_raw: set[str] = set()
    for items in comm.COMMUNITY.values():
        for item in items:
            seen_raw.add(re.sub(r"\s+", " ", item.get("raw") or "").strip())
    known_urls = existing_source_urls()
    out: dict[str, list] = defaultdict(list)
    for row in rows:
        lid = row["leader"]
        if lid not in LEADERS or len(out[lid]) >= limit:
            continue
        raw = re.sub(r"\s+", " ", row["raw"]).strip()
        if raw in seen_raw:
            continue
        if row.get("source_url") in known_urls:
            continue
        leader = LEADER_BY_ID[lid]
        player = row.get("player") or kind
        title = row.get("title") or f"{player} — {leader['name']}"
        base = gen.slugify(f"{kind}-{player}-{leader['key']}")
        slug = base
        n = 2
        while slug in have[lid]:
            slug = f"{base}-{n}"
            n += 1
        have[lid].add(slug)
        seen_raw.add(raw)
        known_urls.add(row.get("source_url") or "")
        out[lid].append(
            {
                "slug": slug,
                "href": f"/{leader['dir']}/{slug}.html",
                "player": player,
                "title": title,
                "subtitle": row.get("subtitle") or f"Public {kind} list",
                "kind": kind,
                "source_url": row["source_url"],
                "raw": raw,
            }
        )
    return out


def write_raw_page(leader: dict, item: dict, cache: dict, extra: dict | None = None) -> None:
    counts = comm.parse_raw(item["raw"])
    dl = comm.counts_to_decklist(counts, cache, leader["id"])
    entry = extra or {
        "player": item["player"],
        "tournament_name": item.get("title") or item.get("tournament_name") or item["player"],
        "placing": item.get("placing"),
        "record": item.get("record") or {},
        "date": item.get("date") or "",
        "decklist": dl,
        "source_url": item["source_url"],
        "kind": item["kind"],
        "title_override": item.get("title"),
        "subtitle": item.get("subtitle") or "",
        "forced_slug": item["slug"],
        "slug": item["slug"],
        "href": item["href"],
    }
    if "decklist" not in entry:
        entry["decklist"] = dl
    page = gen.render_deck_page(leader, entry, cache)
    out = ROOT / leader["dir"] / f"{item['slug']}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)


def main() -> None:
    index = more.load_index()
    optd_rows = [] if "--skip-optd" in sys.argv else scrape_optd()
    yt_rows = scrape_youtube()
    x_rows = scrape_x()

    optd_keep = pick_optd(optd_rows, index)
    yt_keep = pick_community(yt_rows, "youtube", YT_LIMIT)
    x_keep = pick_community(x_rows, "x", X_LIMIT)

    needed = set()
    for item in optd_keep:
        needed.update(comm.parse_raw(item["raw"]))
    for group in (yt_keep, x_keep):
        for items in group.values():
            for item in items:
                needed.update(comm.parse_raw(item["raw"]))
    cache = gen.ensure_cards(needed, gen.load_card_cache()) if needed else gen.load_card_cache()

    added_optd = 0
    for item in optd_keep:
        lid = item.get("leader")
        if not lid:
            continue
        leader = LEADER_BY_ID[lid]
        counts = comm.parse_raw(item["raw"])
        dl = comm.counts_to_decklist(counts, cache, lid)
        entry = {
            "player": item["player"],
            "tournament_name": item["tournament_name"],
            "placing": item.get("placing"),
            "record": item.get("record") or {},
            "date": item.get("date") or "",
            "decklist": dl,
            "source_url": item["source_url"],
            "kind": "topdecks",
            "subtitle": item.get("subtitle") or "",
            "slug": item["slug"],
            "href": item["href"],
        }
        page = gen.render_deck_page(leader, entry, cache)
        (ROOT / leader["dir"] / f"{item['slug']}.html").write_text(page)
        index.setdefault(lid, []).append(more.index_row(entry))
        added_optd += 1

    scraped = json.loads((ROOT / "data/scraped-community.json").read_text()) if (ROOT / "data/scraped-community.json").exists() else {}
    added_yt = added_x = 0
    for lid, items in yt_keep.items():
        leader = LEADER_BY_ID[lid]
        scraped.setdefault(lid, [])
        for item in items:
            write_raw_page(leader, item, cache)
            scraped[lid].append(
                {
                    "slug": item["slug"],
                    "href": item["href"],
                    "player": item["player"],
                    "title": item["title"],
                    "subtitle": item["subtitle"],
                    "kind": item["kind"],
                    "source_url": item["source_url"],
                    "raw": item["raw"],
                }
            )
            added_yt += 1
    for lid, items in x_keep.items():
        leader = LEADER_BY_ID[lid]
        scraped.setdefault(lid, [])
        for item in items:
            write_raw_page(leader, item, cache)
            scraped[lid].append(
                {
                    "slug": item["slug"],
                    "href": item["href"],
                    "player": item["player"],
                    "title": item["title"],
                    "subtitle": item["subtitle"],
                    "kind": item["kind"],
                    "source_url": item["source_url"],
                    "raw": item["raw"],
                }
            )
            added_x += 1

    more.save_index(index)
    (ROOT / "data/scraped-community.json").write_text(json.dumps(scraped, indent=2, ensure_ascii=False) + "\n")
    more.rebuild_hubs(index)
    more.rewrite_sitemap()
    log("added optd", added_optd, "youtube", added_yt, "x", added_x)
    log("done")


if __name__ == "__main__":
    main()
