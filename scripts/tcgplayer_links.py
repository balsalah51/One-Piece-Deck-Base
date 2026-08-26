"""Build TCGplayer search, product, and mass-entry URLs.

Buy links wrap through the Impact partner URL in data/tcgplayer.json
(and js/tcgplayer-config.js as a fallback).
"""

from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path("/workspace")
CONFIG_PATH = ROOT / "data/tcgplayer.json"
IDS_PATH = ROOT / "data/tcgplayer-ids.json"
DEFAULT_PARTNER = "https://partner.tcgplayer.com/c/7670706/1780961/21018"
PRODUCT_LINE = "One Piece Card Game"
SEARCH_LINE = "one-piece-card-game"
SIM_CHUNK_RE = re.compile(
    r"(?i)(\d+)\s*[x×]\s*((?:OP|ST|EB|PRB)\d{2}-\d{3}|P-\d{3})"
)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"partnerLink": ""}
    return json.loads(CONFIG_PATH.read_text())


def load_ids() -> dict[str, int]:
    if not IDS_PATH.exists():
        return {}
    raw = json.loads(IDS_PATH.read_text())
    out: dict[str, int] = {}
    for cid, pid in raw.items():
        try:
            out[cid.upper()] = int(pid)
        except (TypeError, ValueError):
            continue
    return out


def affiliate_url(dest: str, partner_link: str | None = None) -> str:
    if partner_link is None:
        partner_link = str(load_config().get("partnerLink") or "")
    partner_link = (partner_link or DEFAULT_PARTNER).strip() or DEFAULT_PARTNER
    if "partner.tcgplayer.com" in dest:
        return dest
    sep = "&" if "?" in partner_link else "?"
    return partner_link + sep + "u=" + urllib.parse.quote(dest, safe="")


def card_url(cid: str, product_id: int | None = None) -> str:
    if product_id:
        return f"https://www.tcgplayer.com/product/{int(product_id)}"
    q = urllib.parse.urlencode({"q": cid, "productLineName": SEARCH_LINE})
    return f"https://www.tcgplayer.com/search/{SEARCH_LINE}/product?{q}"


def mass_entry_url(cards: list[tuple[int, str]]) -> str:
    parts = []
    for qty, cid in cards:
        if qty <= 0 or not cid:
            continue
        parts.append(f"{int(qty)} {cid}")
    c = "||".join(parts)
    q = urllib.parse.urlencode({"productline": PRODUCT_LINE, "c": c})
    return f"https://www.tcgplayer.com/massentry?{q}"


def parse_sim_text(text: str) -> list[tuple[int, str]]:
    cards: list[tuple[int, str]] = []
    seen: set[str] = set()
    for qty, cid in SIM_CHUNK_RE.findall(text or ""):
        cid = cid.upper()
        if cid in seen:
            continue
        seen.add(cid)
        cards.append((int(qty), cid))
    return cards
