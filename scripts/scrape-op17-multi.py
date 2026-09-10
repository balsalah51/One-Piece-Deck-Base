#!/usr/bin/env python3
"""Host new complete OP17 50-card lists from several public sites.

Sources, in order: TCG PORTAL shop results, OPDeckGuide east/west, Egman
standalone lists, OnePieceDB, YouTube descriptions, then a small Limitless
supplement. Does not wipe existing pages. Does not invent cards from photos.
"""

from __future__ import annotations

import importlib.util
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path("/workspace")
UA = "OnePieceDeckBase/1.0 (+https://onepiecedeckbase.com; public OPTCG list scrape)"
PORTAL_API = "https://tcg-portal.jp/api/onepiece/tournament-results"
EGMAN_REST = "https://resgvirjzcpamfumrygh.supabase.co/rest/v1/standalone_decklists"
EGMAN_KEY = "sb_publishable_bdDgor6ifmOvryEuZKWniw_RBzb3vuh"
CARD_RE = re.compile(r"((?:OP|ST|EB|PRB)\d{2}-\d{3}|P-\d{3}):(\d+)")
PORTAL_ALT_RE = re.compile(r'alt="[^"]*\(((?:OP|ST|EB|PRB)\d{2}-\d{3})\)"')
PORTAL_HREF_RE = re.compile(r'href="/onepiece/cards/((?:OP|ST|EB|PRB)\d{2}-\d{3})"')
YT_RE = re.compile(r"(?:watch\?v=|/shorts/)([A-Za-z0-9_-]{11})")
DESC_RE = re.compile(
    r"(?:Deck List:|Decklist:|Deck Profile:)\\n((?:\\n?\d+x(?:OP|ST|EB|PRB)\d{2}-\d{3}|\\n?\d+xP-\d{3})+)",
    re.I,
)
PORTAL_SINCE = "2026-08-16"
PORTAL_PAGES = 12
LIMITLESS_CAP_PER_LEADER = 1


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def log(*args) -> None:
    print(*args, flush=True)


def fetch(url: str, timeout: int = 25, headers: dict | None = None) -> str:
    hdrs = {"User-Agent": UA, "Accept": "text/html,application/json,*/*"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def get_json(url: str, headers: dict | None = None, timeout: int = 30):
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def existing_raws(gen, comm, ana) -> set[str]:
    seen: set[str] = set()
    for path in ROOT.glob("decklists/**/*.html"):
        text = path.read_text(errors="ignore")
        counts: dict[str, int] = {}
        for n, cid in ana.LINE_RE.findall(text):
            cid = cid.strip().upper()
            counts[cid] = counts.get(cid, 0) + int(n)
        if counts:
            seen.add(" ".join(f"{n}x{cid}" for cid, n in sorted(counts.items())))
    return seen


def existing_source_urls() -> set[str]:
    urls: set[str] = set()
    for name in ("community-decks.json", "tournament-decks.json", "tcgportal-log.json", "opdeckguide-log.json"):
        path = ROOT / "data" / name
        if not path.exists():
            continue
        blob = json.loads(path.read_text())
        rows = []
        if isinstance(blob, dict):
            if "hosted" in blob:
                rows.extend(blob.get("hosted") or [])
            else:
                for val in blob.values():
                    if isinstance(val, list):
                        rows.extend(val)
        for row in rows:
            url = (row.get("source_url") or "").strip()
            if url:
                urls.add(url)
    return urls


def counts_from_portal_html(html: str) -> dict[str, int]:
    hits = PORTAL_ALT_RE.findall(html)
    if len(set(hits)) < 6:
        hits = PORTAL_HREF_RE.findall(html)
    counts: dict[str, int] = {}
    for cid in hits:
        counts[cid] = counts.get(cid, 0) + 1
    return counts


def item_ok(item: dict, comm, gen, hosted: set[str], seen_raw: set[str]) -> bool:
    counts = comm.parse_raw(item["raw"])
    lid = item.get("leader")
    if lid not in hosted:
        return False
    if counts.get(lid) != 1:
        return False
    if any(cid in gen.BANNED_CARDS for cid in counts):
        return False
    if not any(cid.startswith("OP17-") for cid in counts):
        return False
    main_n = sum(n for cid, n in counts.items() if cid != lid)
    if not (46 <= main_n <= 52):
        return False
    raw = " ".join(f"{n}x{cid}" for cid, n in sorted(counts.items()))
    if raw in seen_raw:
        return False
    item["raw"] = raw
    item["cards"] = main_n
    return True


def scrape_portal(found, seen, commsrc, comm, gen, hosted, seen_raw, have_urls) -> None:
    log("=== TCG PORTAL ===")
    rows = []
    page = 1
    while page <= PORTAL_PAGES:
        data = get_json(f"{PORTAL_API}?page={page}&limit=50")
        batch = data.get("tournamentDecks") or []
        if not batch:
            break
        stop = False
        for row in batch:
            day = (row.get("date") or "")[:10]
            if day and day < PORTAL_SINCE:
                stop = True
                break
            rows.append(row)
        log("portal page", page, "kept", len(rows), "stop", stop)
        if stop:
            break
        page += 1
        time.sleep(0.08)
    log("portal rows", len(rows))
    for row in rows:
        pid = row.get("id")
        if not pid:
            continue
        url = f"https://tcg-portal.jp/onepiece/tournament-results/{pid}"
        if url in have_urls:
            continue
        try:
            html = fetch(url)
        except Exception as exc:  # noqa: BLE001
            log("portal fail", pid, exc)
            continue
        counts = counts_from_portal_html(html)
        lids = [cid for cid, n in counts.items() if cid in hosted and n == 1]
        lid = lids[0] if len(lids) == 1 else None
        if not lid:
            ones = [cid for cid, n in counts.items() if n == 1]
            lid = ones[0] if ones else None
        shop = (row.get("shop") or {}).get("name") or row.get("location") or "TCG PORTAL"
        event = row.get("tournamentName") or "Shop battle"
        guide = (row.get("deckGuide") or {}).get("name") or (lid or "list")
        day = (row.get("date") or "")[:10]
        item = {
            "leader": lid,
            "kind": "web",
            "player": shop,
            "title": f"{guide} {event} winner — {shop}",
            "subtitle": f"Public TCG PORTAL list · {day}",
            "source_url": url,
            "slug": gen.slugify(f"tcgportal-{day}-{shop}-{pid[-6:]}")[:70],
            "raw": " ".join(f"{n}x{cid}" for cid, n in counts.items()),
            "cards": sum(n for cid, n in counts.items() if cid != lid) if lid else 0,
            "date": day,
        }
        if item_ok(item, comm, gen, hosted, seen_raw):
            commsrc.record(found, item, seen)
            seen_raw.add(item["raw"])
            have_urls.add(url)
        time.sleep(0.1)


def scrape_opdeck(found, seen, commsrc, comm, gen, hosted, seen_raw, have_urls) -> None:
    log("=== OPDeckGuide ===")
    opdeck = load("opdeck", "/workspace/scripts/add-opdeckguide-lists.py")
    paths = opdeck.collect_paths()
    log("opdeck paths", len(paths))
    for path in paths:
        url = "https://opdeckguide.com" + path
        if url in have_urls:
            continue
        item = opdeck.parse_page(path, comm, gen)
        time.sleep(0.1)
        if not item:
            continue
        if item_ok(item, comm, gen, hosted, seen_raw):
            commsrc.record(found, item, seen)
            seen_raw.add(item["raw"])
            have_urls.add(url)


def scrape_egman(found, seen, commsrc, comm, gen, hosted, seen_raw, have_urls) -> None:
    log("=== Egman standalone ===")
    headers = {
        "apikey": EGMAN_KEY,
        "Authorization": f"Bearer {EGMAN_KEY}",
        "Range-Unit": "items",
        "Range": "0-999",
    }
    try:
        rows = get_json(
            EGMAN_REST + "?select=id,player_name,source,date,deck_list_url,set_group,deck_type&set_group=eq.OP17&order=date.desc",
            headers=headers,
        )
    except Exception as exc:  # noqa: BLE001
        log("egman fail", exc)
        return
    log("egman rows", len(rows) if isinstance(rows, list) else 0)
    for row in rows or []:
        urls = row.get("deck_list_url") or []
        if isinstance(urls, str):
            urls = [urls]
        href = urls[0] if urls else ""
        if not href:
            continue
        cards = CARD_RE.findall(urllib.parse.unquote(href))
        if not cards:
            continue
        counts: dict[str, int] = {}
        for cid, n in cards:
            cid = cid.upper()
            counts[cid] = counts.get(cid, 0) + int(n)
        lids = [cid for cid, n in counts.items() if cid in hosted and n == 1]
        lid = lids[0] if len(lids) == 1 else (lids[0] if lids else None)
        if not lid:
            continue
        day = (row.get("date") or "")[:10]
        player = row.get("player_name") or "Egman"
        source = row.get("source") or "Egman list"
        source_url = href if href.startswith("http") else f"https://deckbuilder.egmanevents.com/?deck={href}"
        if source_url in have_urls:
            continue
        item = {
            "leader": lid,
            "kind": "web",
            "player": player,
            "title": f"{gen.display_name(hosted_name(gen, lid))} — {source} ({player})",
            "subtitle": f"Public Egman deckbuilder list · {day}",
            "source_url": source_url,
            "slug": gen.slugify(f"egman-{day}-{player}-{row.get('id','')[:8]}")[:70],
            "raw": " ".join(f"{n}x{cid}" for cid, n in counts.items()),
            "cards": sum(n for cid, n in counts.items() if cid != lid),
            "date": day,
        }
        if item_ok(item, comm, gen, hosted, seen_raw):
            commsrc.record(found, item, seen)
            seen_raw.add(item["raw"])
            have_urls.add(source_url)


def hosted_name(gen, lid: str) -> str:
    for leader in gen.LEADERS:
        if leader["id"] == lid:
            return leader["name"]
    return lid


def scrape_youtube(found, seen, commsrc, comm, gen, hosted, seen_raw, have_urls) -> None:
    log("=== YouTube descriptions ===")
    ids: list[str] = []
    queries = (
        "OP17+decklist+2026",
        "OP17+Rocks+Xebec+decklist",
        "OP17+Kaido+decklist",
        "OP17+black+Luffy+decklist",
        "OP17+Shanks+decklist",
        "OP17+Linlin+decklist",
        "OP17+Newgate+decklist",
        "OP17+Mihawk+decklist+September",
        "OP17+Ace+decklist+September",
        "OP17+Sabo+decklist",
    )
    for q in queries:
        try:
            html = fetch("https://www.youtube.com/results?search_query=" + q)
        except Exception as exc:  # noqa: BLE001
            log("yt search fail", q, exc)
            continue
        for vid in YT_RE.findall(html):
            if vid not in ids:
                ids.append(vid)
        log("yt search", q, "ids", len(ids))
        time.sleep(0.15)
    for vid in ids[:70]:
        url = f"https://www.youtube.com/watch?v={vid}"
        if url in have_urls:
            continue
        try:
            html = fetch(url)
        except Exception as exc:  # noqa: BLE001
            log("yt fail", vid, exc)
            continue
        text = html.replace("\\u0026", "&").replace("\\/", "/").replace("\\n", "\n")
        counts = comm.parse_raw(text)
        lid = None
        hits = [cid for cid in counts if cid in hosted]
        if len(hits) == 1:
            lid = hits[0]
        else:
            ones = [cid for cid in hits if counts[cid] == 1]
            lid = ones[0] if ones else None
        title_m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
        title = re.sub(r"\s+", " ", title_m.group(1)).replace(" - YouTube", "").strip()[:90] if title_m else "YouTube list"
        item = {
            "leader": lid,
            "kind": "youtube",
            "player": "YouTube",
            "title": title,
            "subtitle": "YouTube deck profile from a public description",
            "source_url": url,
            "slug": commsrc.slug_for("yt", "youtube", f"{lid or 'list'}-{vid}"),
            "raw": " ".join(f"{n}x{cid}" for cid, n in counts.items()),
            "cards": sum(n for cid, n in counts.items() if cid != lid) if lid else 0,
        }
        if item_ok(item, comm, gen, hosted, seen_raw):
            commsrc.record(found, item, seen)
            seen_raw.add(item["raw"])
            have_urls.add(url)
        time.sleep(0.12)


def scrape_opdb(found, seen, commsrc, hosted, seen_raw) -> None:
    log("=== OnePieceDB ===")
    before = len(found)
    commsrc.scrape_opdb(found, seen)
    # drop anything that slipped in without OP17 / already hosted raw
    kept = found[:before]
    for item in found[before:]:
        raw = " ".join(f"{n}x{cid}" for cid, n in sorted(commsrc.parse_counts(item["raw"]).items()))
        if raw in seen_raw:
            continue
        if item.get("leader") not in hosted:
            continue
        if "OP17-" not in item["raw"]:
            continue
        item["raw"] = raw
        kept.append(item)
        seen_raw.add(raw)
    found[:] = kept


def main() -> None:
    gen = load("genlists", "/workspace/scripts/generate-tournament-lists.py")
    comm = load("commlists", "/workspace/scripts/add-community-lists.py")
    commsrc = load("commsrc", "/workspace/scripts/scrape-community-sources.py")
    more = load("morelists", "/workspace/scripts/add-more-tournament-lists.py")
    ana = load("analysis", "/workspace/scripts/add-leader-analysis.py")

    hosted = {L["id"] for L in gen.LEADERS}
    log("scanning hosted raw lists")
    seen_raw = existing_raws(gen, comm, ana)
    have_urls = existing_source_urls()
    log("existing fingerprints", len(seen_raw), "source urls", len(have_urls))

    found: list[dict] = []
    seen: set[str] = set()
    scrape_portal(found, seen, commsrc, comm, gen, hosted, seen_raw, have_urls)
    log("after portal", len(found))
    scrape_opdeck(found, seen, commsrc, comm, gen, hosted, seen_raw, have_urls)
    log("after opdeck", len(found))
    scrape_egman(found, seen, commsrc, comm, gen, hosted, seen_raw, have_urls)
    log("after egman", len(found))
    scrape_youtube(found, seen, commsrc, comm, gen, hosted, seen_raw, have_urls)
    log("after youtube", len(found))
    scrape_opdb(found, seen, commsrc, hosted, seen_raw)
    log("after opdb", len(found))

    (ROOT / "data/op17-multi-log.json").write_text(
        json.dumps({"found": found}, indent=2, ensure_ascii=False) + "\n"
    )
    log("ready to write", len(found))
    touched = commsrc.write_lists(found)
    log("wrote leaders", sorted(touched), "new pages", len(found))

    if len(found) < 400:
        log("=== Limitless supplement, cap", LIMITLESS_CAP_PER_LEADER, "per leader ===")
        index = more.load_index()
        index = more.fetch_more(
            index,
            pages=8,
            extra_limit=LIMITLESS_CAP_PER_LEADER,
            per_event=1,
            since="2026-08-28",
            require_op17=True,
        )
        more.save_index(index)
        more.rebuild_hubs(index)
    else:
        index = more.load_index()
        more.rebuild_hubs(index, only_ids=touched or None)
    more.rewrite_sitemap()
    log("scrape-op17-multi done", "found", len(found))


if __name__ == "__main__":
    main()
