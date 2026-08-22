#!/usr/bin/env python3
"""Scrape public X, YouTube, Limitless, and OnePieceDB pages for 50-card lists.

Only keeps complete NxSET-NNN lists. Does not invent cards from screenshots.
Does not wipe existing tournament pages.
"""

from __future__ import annotations

import importlib.util
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

spec = importlib.util.spec_from_file_location("genlists", "/workspace/scripts/generate-tournament-lists.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

cspec = importlib.util.spec_from_file_location("commlists", "/workspace/scripts/add-community-lists.py")
comm = importlib.util.module_from_spec(cspec)
cspec.loader.exec_module(comm)

mspec = importlib.util.spec_from_file_location("morelists", "/workspace/scripts/add-more-tournament-lists.py")
more = importlib.util.module_from_spec(mspec)
mspec.loader.exec_module(more)

ROOT = gen.ROOT
UA = "OnePieceDeckBase/1.0 (+https://onepiecedeckbase.com; public OPTCG list scrape)"
LINE_RE = comm.LINE_RE
TARGET_IDS = {
    "OP15-002": "lucy",
    "OP14-060": "doffy",
    "OP16-080": "blackbeard",
    "OP16-001": "portgas-d-ace",
    "OP16-022": "gb-luffy",
    "OP16-041": "buggy",
    "OP16-060": "sengoku",
    "OP16-079": "yamato",
}
OPDB_SLUGS = {
    "OP15-002": "lucy-op15-002",
    "OP14-060": "donquixote-doflamingo-op14-060",
    "OP16-080": "marshall-d-teach-op16-080",
    "OP16-001": "portgas-d-ace-op16-001",
    "OP16-022": "monkey-d-luffy-op16-022",
    "OP16-041": "buggy-op16-041",
    "OP16-060": "sengoku-op16-060",
    "OP16-079": "yamato-op16-079",
}
YOUTUBE_ID_RE = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{8,})", re.I)
DECK_HREF_RE = re.compile(r'href="(https?://onepiecedb\.io/[^"]+)"')


def log(*args) -> None:
    print(*args, flush=True)


def fetch(url: str, timeout: int = 16) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "text/html,application/json,*/*"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace") if exc.fp else ""
        return exc.code, body
    except Exception as exc:  # noqa: BLE001
        return 0, f"{type(exc).__name__}: {exc}"


def parse_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for n, cid in LINE_RE.findall(text or ""):
        cid = cid.upper()
        counts[cid] = counts.get(cid, 0) + int(n)
    return counts


def leader_of(counts: dict[str, int]) -> str | None:
    hits = [cid for cid in counts if cid in TARGET_IDS]
    if len(hits) == 1:
        return hits[0]
    for cid in hits:
        if counts[cid] == 1:
            return cid
    return None


def complete(counts: dict[str, int], leader_id: str) -> bool:
    if leader_id not in counts:
        return False
    total = sum(n for cid, n in counts.items() if cid != leader_id)
    if any(cid in gen.BANNED_CARDS for cid in counts):
        return False
    return 46 <= total <= 52


def slug_for(kind: str, player: str, title: str) -> str:
    return gen.slugify(f"{kind}-{player}-{title}")[:70]


def record(found: list[dict], item: dict, seen: set[str]) -> None:
    key = item["raw"]
    if key in seen:
        return
    seen.add(key)
    found.append(item)
    log("found", item["leader"], item["kind"], item["slug"], "cards", item["cards"])


def ddg(query: str) -> str:
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    status, body = fetch(url, timeout=12)
    log("ddg", status, query[:60])
    return body


def scrape_youtube(found: list[dict], seen: set[str]) -> None:
    queries = [
        "OP16 Buggy OP16-041 decklist youtube",
        "OP16 Sengoku OP16-060 decklist youtube",
        "OP14 Doflamingo OP14-060 decklist youtube",
        "OP15 Lucy OP15-002 decklist youtube",
        "OP16 Blackbeard OP16-080 decklist youtube",
        "OP16 Ace OP16-001 decklist youtube",
        "OP16 Yamato OP16-079 decklist youtube",
        "OP16 GB Luffy OP16-022 decklist youtube",
    ]
    video_ids: list[str] = []
    for q in queries:
        body = ddg(q)
        for vid in YOUTUBE_ID_RE.findall(body):
            if vid not in video_ids:
                video_ids.append(vid)
        time.sleep(0.2)
    log("youtube ids", len(video_ids))
    for vid in video_ids[:24]:
        url = f"https://www.youtube.com/watch?v={vid}"
        status, body = fetch(f"https://r.jina.ai/{url}", timeout=20)
        counts = parse_counts(body)
        lid = leader_of(counts)
        log("yt", status, vid, "lines", len(counts), lid or "-")
        if not lid or not complete(counts, lid):
            time.sleep(0.15)
            continue
        title = f"{TARGET_IDS[lid].replace('-', ' ').title()} YouTube list"
        m = re.search(r"(?im)^Title:\s*(.+)$", body)
        if m:
            title = m.group(1).strip()[:90]
        raw = " ".join(f"{n}x{cid}" for cid, n in counts.items())
        record(
            found,
            {
                "leader": lid,
                "kind": "youtube",
                "player": "YouTube",
                "title": title,
                "subtitle": "YouTube deck profile scraped from a public description",
                "source_url": url,
                "slug": slug_for("yt", "youtube", f"{TARGET_IDS[lid]}-{vid}"),
                "raw": raw,
                "cards": sum(n for cid, n in counts.items() if cid != lid),
            },
            seen,
        )
        time.sleep(0.15)


def scrape_opdb(found: list[dict], seen: set[str]) -> None:
    for lid, slug in OPDB_SLUGS.items():
        page = f"https://onepiecedb.io/category/leader/{slug}"
        status, body = fetch(f"https://r.jina.ai/{page}", timeout=20)
        log("opdb category", status, slug, "chars", len(body))
        hrefs = []
        for href in DECK_HREF_RE.findall(body):
            if "/category/" in href or "/card/" in href:
                continue
            if href not in hrefs:
                hrefs.append(href)
        # also accept relative paths rewritten by jina as markdown links
        for href in re.findall(r"https://onepiecedb\.io/[A-Za-z0-9_/?#.-]+", body):
            if any(x in href for x in ("/category/", "/card/", "/tag/")):
                continue
            if href not in hrefs:
                hrefs.append(href)
        counts = parse_counts(body)
        if complete(counts, lid):
            raw = " ".join(f"{n}x{cid}" for cid, n in counts.items())
            record(
                found,
                {
                    "leader": lid,
                    "kind": "web",
                    "player": "OnePieceDB",
                    "title": f"{TARGET_IDS[lid].replace('-', ' ').title()} — OnePieceDB",
                    "subtitle": "Public OnePieceDB leader page",
                    "source_url": page,
                    "slug": slug_for("opdb", "onepiecedb", TARGET_IDS[lid]),
                    "raw": raw,
                    "cards": sum(n for cid, n in counts.items() if cid != lid),
                },
                seen,
            )
        for href in hrefs[:8]:
            st, deck_body = fetch(f"https://r.jina.ai/{href}", timeout=18)
            deck_counts = parse_counts(deck_body)
            log("opdb deck", st, href, "lines", len(deck_counts))
            if not complete(deck_counts, lid):
                time.sleep(0.1)
                continue
            raw = " ".join(f"{n}x{cid}" for cid, n in deck_counts.items())
            record(
                found,
                {
                    "leader": lid,
                    "kind": "web",
                    "player": "OnePieceDB",
                    "title": f"{TARGET_IDS[lid].replace('-', ' ').title()} — OnePieceDB list",
                    "subtitle": "Public OnePieceDB deck page",
                    "source_url": href,
                    "slug": slug_for("opdb", "onepiecedb", href),
                    "raw": raw,
                    "cards": sum(n for cid, n in deck_counts.items() if cid != lid),
                },
                seen,
            )
            time.sleep(0.12)
        time.sleep(0.15)


def scrape_x(found: list[dict], seen: set[str]) -> None:
    xspec = importlib.util.spec_from_file_location("xlists", "/workspace/scripts/scrape-x-lists.py")
    xmod = importlib.util.module_from_spec(xspec)
    xspec.loader.exec_module(xmod)
    xmod.LEADERS = set(TARGET_IDS)
    xmod.main()
    log_path = ROOT / "data/x-search-log.json"
    if not log_path.exists():
        return
    data = json.loads(log_path.read_text())
    for item in data.get("complete_lists") or []:
        raw = item.get("raw") or ""
        counts = parse_counts(raw)
        lid = item.get("leader") or leader_of(counts)
        if lid not in TARGET_IDS or not complete(counts, lid):
            continue
        url = item.get("source") or item.get("url") or "https://x.com/"
        handle = item.get("handle") or "x"
        record(
            found,
            {
                "leader": lid,
                "kind": "x",
                "player": handle,
                "title": f"{TARGET_IDS[lid].replace('-', ' ').title()} — @{handle}",
                "subtitle": "List copied from a public X/Twitter post",
                "source_url": url if url.startswith("http") else f"https://x.com/{handle}",
                "slug": slug_for("x", handle, TARGET_IDS[lid] + raw[-12:]),
                "raw": " ".join(f"{n}x{cid}" for cid, n in counts.items()),
                "cards": sum(n for cid, n in counts.items() if cid != lid),
            },
            seen,
        )


def write_lists(found: list[dict]) -> set[str]:
    if not found:
        return set()
    needed = set()
    parsed = []
    for item in found:
        counts = comm.parse_raw(item["raw"])
        needed.update(counts)
        parsed.append((item, counts))
    cache = gen.ensure_cards(needed, gen.load_card_cache())
    index = more.load_index()
    community = {}
    comm_path = ROOT / "data/community-decks.json"
    if comm_path.exists():
        community = json.loads(comm_path.read_text())
    touched = set()
    by_id = {L["id"]: L for L in gen.LEADERS}
    for item, counts in parsed:
        leader = by_id.get(item["leader"])
        if not leader:
            continue
        out_dir = ROOT / leader["dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{item['slug']}.html"
        if path.exists():
            log("exists", path)
            continue
        dl = comm.counts_to_decklist(counts, cache, leader["id"])
        entry = {
            "player": item["player"],
            "tournament_name": item["title"],
            "placing": None,
            "record": {},
            "date": "",
            "decklist": dl,
            "source_url": item["source_url"],
            "kind": item["kind"],
            "title_override": item["title"],
            "subtitle": item["subtitle"],
            "forced_slug": item["slug"],
            "slug": item["slug"],
            "href": f"/{leader['dir']}/{item['slug']}.html",
        }
        page = gen.render_deck_page(leader, entry, cache)
        path.write_text(page)
        rows = community.setdefault(leader["id"], [])
        if not any(row.get("slug") == item["slug"] for row in rows):
            rows.append(
                {
                    "slug": item["slug"],
                    "href": entry["href"],
                    "title": item["title"],
                    "subtitle": item.get("subtitle") or "",
                    "source_url": item["source_url"],
                    "kind": item["kind"],
                }
            )
        touched.add(leader["id"])
        log("wrote", path)
    more.save_index(index)
    comm_path.write_text(json.dumps(community, indent=2, ensure_ascii=False) + "\n")
    if touched:
        more.rebuild_hubs(index, only_ids=touched)
    return touched


def main() -> None:
    found: list[dict] = []
    seen: set[str] = set()
    scrape_opdb(found, seen)
    scrape_youtube(found, seen)
    scrape_x(found, seen)
    (ROOT / "data/community-scrape-log.json").write_text(
        json.dumps({"found": found}, indent=2, ensure_ascii=False) + "\n"
    )
    log("complete community lists", len(found))
    write_lists(found)
    print("done")


if __name__ == "__main__":
    main()
