#!/usr/bin/env python3
"""Fetch public X posts for complete OPTCG 50-card ID lists.

Uses only public proxies (Jina reader, FxTwitter, DuckDuckGo HTML). Does not
log in, does not read DMs, and does not invent lists from screenshots.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path("/workspace")
UA = "OnePieceDeckBase/1.0 (+https://onepiecedeckbase.com; public OPTCG list scrape)"
LINE_RE = re.compile(r"(?i)(\d+)\s*[x×]\s*((?:OP|ST|EB|PRB)\d{2}-\d{3}|P-\d{3})")
STATUS_RE = re.compile(
    r"(?:x\.com|twitter\.com|nitter\.[^/\s]+)/([A-Za-z0-9_]+)/status/(\d+)",
    re.I,
)
LEADERS = {
    "OP17-001",
    "OP17-020",
    "OP17-039",
    "OP17-058",
    "OP17-079",
    "OP17-099",
    "OP13-001",
    "OP11-041",
    "OP14-020",
    "OP16-001",
    "OP15-058",
    "OP11-062",
    "OP13-079",
    "OP13-002",
    "OP16-022",
    "OP16-080",
    "OP12-061",
    "OP15-002",
    "OP16-079",
    "OP11-001",
    "OP14-060",
    "OP16-041",
    "OP16-060",
}

# Public creator accounts that actually post OPTCG content.
HANDLES = [
    "MarinefordTCG",
    "StrawHatPecan",
    "BenSchumi7",
    "CardKaizoku",
    "BlaisePlays",
    "BlaisePlaysTCG",
    "NightingaleTCG",
    "michaelartress",
    "ONEPIECE_tcg_EN",
    "Silvers_D_Foxy",
    "LimitlessTCG",
]
HANDLE_SET = {h.lower() for h in HANDLES}

# Tweet IDs already visible on public profile scrapes (plus a few replies).
SEED_TWEETS = {
    "2090197490913902734": "Silvers_D_Foxy",
    "2089448508684189741": "MarinefordTCG",
    "2088771006592663815": "MarinefordTCG",
    "2089597170316144997": "cardkaizoku",
    "2089491621176029306": "cardkaizoku",
    "2088505853402108192": "cardkaizoku",
    "2088365415928127503": "cardkaizoku",
    "2086926321696076196": "cardkaizoku",
}

SEARCHES = [
    'site:x.com "4xOP17"',
    'site:twitter.com "4xOP17-040"',
    'site:x.com "1xOP17-001" decklist',
    'site:x.com "1xOP16-001"',
    "site:x.com MarinefordTCG OP17 decklist",
    "site:x.com StrawHatPecan OP17 list",
    "site:x.com CardKaizoku Ace OP16-001",
    'site:x.com "1xOP14-060" decklist',
    'site:x.com "1xOP16-041" Buggy',
    'site:x.com "1xOP16-060" Sengoku',
    'site:x.com "1xOP15-002" Lucy',
    'site:x.com "1xOP16-080" Blackbeard',
    "site:x.com Doffy OP14-060 decklist",
]


def log(*args) -> None:
    print(*args, flush=True)


def fetch(url: str, timeout: int = 10) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/json,*/*",
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


def extract_status_ids(text: str) -> list[tuple[str, str]]:
    found = []
    seen: set[tuple[str, str]] = set()
    for handle, sid in STATUS_RE.findall(text or ""):
        key = (handle, sid)
        if key not in seen:
            seen.add(key)
            found.append((handle, sid))
    return found


def tweet_blob(data: dict) -> str:
    tweet = data.get("tweet") or data
    parts = [tweet.get("text") or "", json.dumps(tweet.get("raw_text") or "")]
    media = tweet.get("media") or {}
    if isinstance(media, dict):
        for photo in media.get("photos") or []:
            if isinstance(photo, dict):
                parts.append(photo.get("altText") or photo.get("alt") or "")
                parts.append(photo.get("url") or "")
        for item in media.get("all") or []:
            if isinstance(item, dict):
                parts.append(item.get("altText") or "")
    quote = tweet.get("quote") or {}
    if isinstance(quote, dict):
        parts.append(quote.get("text") or "")
    return "\n".join(str(p) for p in parts)


def main() -> None:
    out: dict = {
        "profiles": [],
        "searches": [],
        "tweets": [],
        "complete_lists": [],
        "partial_id_hits": [],
        "notes": [],
    }
    status_ids = dict(SEED_TWEETS)

    for handle in HANDLES:
        url = f"https://r.jina.ai/https://x.com/{handle}"
        status, body = fetch(url, timeout=18)
        ids = extract_status_ids(body)
        hits = card_hits(body)
        lists = complete_lists(hits)
        row = {
            "handle": handle,
            "url": url,
            "status": status,
            "chars": len(body),
            "tweet_ids": [f"{h}/{s}" for h, s in ids],
            "card_lines": len(hits),
            "complete_lists": len(lists),
            "note": body[:120] if status in (0, 401, 403, 503) else "",
        }
        kept = [(h, s) for h, s in ids if h.lower() in HANDLE_SET or h.lower() == handle.lower()]
        row["tweet_ids"] = [f"{h}/{s}" for h, s in kept]
        out["profiles"].append(row)
        log("profile", status, len(kept), "ids", handle)
        for h, sid in kept:
            status_ids.setdefault(sid, h)
        out["complete_lists"].extend({"source": url, **item} for item in lists)
        if hits and not lists:
            out["partial_id_hits"].append({"source": url, "hits": hits[:40]})

    for q in SEARCHES:
        url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": q})
        status, body = fetch(url, timeout=12)
        ids = extract_status_ids(body)
        hits = card_hits(body)
        lists = complete_lists(hits)
        row = {
            "query": q,
            "status": status,
            "chars": len(body),
            "tweet_ids": [f"{h}/{s}" for h, s in ids],
            "card_lines": len(hits),
            "complete_lists": len(lists),
        }
        out["searches"].append(row)
        log("search", status, len(ids), "ids", len(hits), "lines", q[:48])
        for h, sid in ids:
            if h.lower() in HANDLE_SET:
                status_ids.setdefault(sid, h)
        out["complete_lists"].extend({"source": q, **item} for item in lists)
        if hits:
            out["partial_id_hits"].append({"source": q, "hits": hits[:12]})

    log("unique tweet ids", len(status_ids))
    for sid, handle in status_ids.items():
        url = f"https://api.fxtwitter.com/{handle}/status/{sid}"
        status, body = fetch(url, timeout=12)
        data = {}
        try:
            data = json.loads(body) if body.lstrip().startswith("{") else {}
        except json.JSONDecodeError:
            data = {}
        blob = tweet_blob(data) if data else body
        hits = card_hits(blob)
        lists = complete_lists(hits)
        tweet = (data.get("tweet") or {}) if isinstance(data, dict) else {}
        row = {
            "handle": handle,
            "id": sid,
            "url": f"https://x.com/{handle}/status/{sid}",
            "http": status,
            "text": (tweet.get("text") or "")[:400],
            "card_lines": len(hits),
            "complete_lists": len(lists),
        }
        log("tweet", status, handle, sid, "lines", len(hits), (tweet.get("text") or "")[:72].replace("\n", " "))
        text_l = (tweet.get("text") or "").lower()
        if handle.lower() not in HANDLE_SET and not hits:
            continue
        if handle.lower() == "silvers_d_foxy" and "op17" not in text_l and "one piece" not in text_l and "optcg" not in text_l:
            continue
        out["tweets"].append(row)
        out["complete_lists"].extend({"source": row["url"], "handle": handle, **item} for item in lists)
        if hits and not lists:
            out["partial_id_hits"].append({"source": row["url"], "hits": hits})
        time.sleep(0.15)

    if not out["complete_lists"]:
        out["notes"].append(
            "Public X proxies (Jina reader, FxTwitter, DuckDuckGo site:x.com) returned "
            "no complete 50-card NxSET-NNN lists for tracked leaders. Recent creator tweets "
            "were memes, meta charts, product ads, and single-card photos. "
            "CardKaizoku's Ace/meta posts are win-rate graphics (staple names + matchups), "
            "not pasteable lists. Artress Lucy tweets attach playmat photos of OP04-002 Lucy, "
            "which is not a hub leader and has no readable NxSET-NNN lines. "
            "Creator 50-card lists on this site still come from YouTube descriptions, "
            "with X profile links."
        )

    path = ROOT / "data/x-search-log.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    log("complete X lists found", len(out["complete_lists"]))
    log("wrote", path)


if __name__ == "__main__":
    sys.exit(main() or 0)
