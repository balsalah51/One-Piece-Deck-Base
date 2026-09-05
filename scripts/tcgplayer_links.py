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


TCG_SET_OVERRIDES = {
    "P": "OP-PR",
    "OP15": "OP15-EB04",
    "EB04": "OP15-EB04",
    "EB03": "EB-03-04",
}


def tcg_set_code(cid: str) -> str:
    """TCGPlayer Mass Entry set abbreviation for a Bandai card id."""
    cid = (cid or "").strip().upper()
    prefix = cid.split("-", 1)[0] if "-" in cid else cid
    if prefix in TCG_SET_OVERRIDES:
        return TCG_SET_OVERRIDES[prefix]
    if re.fullmatch(r"OP\d+", prefix):
        return prefix
    m = re.fullmatch(r"([A-Z]+)(\d+)", prefix)
    return f"{m.group(1)}-{m.group(2)}" if m else prefix


def collector_number(cid: str) -> str:
    cid = (cid or "").strip().upper()
    return cid.split("-", 1)[1] if "-" in cid else cid


def catalog_name(name: str, cid: str) -> str:
    name = (name or "").strip()
    if name and "." in name and "(" not in name:
        return f"{name} ({collector_number(cid)})"
    return name


def mass_entry_line(qty: int, cid: str, name: str = "", product_id: int | None = None) -> str:
    """One Mass Entry line for this card.

    Prefers TCGPlayer's product-id form (`4-708209`) when we have an id.
    Otherwise uses the documented text form:
      Quantity → Card Name → [Set Code] → Card Number
    e.g. 4 Charlotte Cracker [OP17] OP17-104
    """
    cid = (cid or "").strip().upper()
    if product_id:
        return f"{int(qty)}-{int(product_id)}"
    name = catalog_name(name, cid)
    set_code = tcg_set_code(cid)
    if name and set_code:
        return f"{int(qty)} {name} [{set_code}] {cid}"
    if name:
        return f"{int(qty)} {name}"
    return f"{int(qty)} {cid}"


def mass_entry_text(cards: list[tuple]) -> str:
    """Newline Mass Entry list for the paste box."""
    parts = []
    seen: set[str] = set()
    for row in cards:
        qty = int(row[0])
        cid = str(row[1] or "").strip().upper()
        name = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if qty <= 0 or not cid or cid in seen:
            continue
        seen.add(cid)
        parts.append(mass_entry_line(qty, cid, name))
    return "\n".join(parts)


def mass_entry_url(cards: list[tuple], product_ids: dict[str, int] | None = None) -> str:
    """Build a TCGplayer Mass Entry URL.

    Each card is (qty, card_id) or (qty, card_id, name).
    product_ids defaults to data/tcgplayer-ids.json. Pass {} to force text lines.
    """
    if product_ids is None:
        product_ids = load_ids()
    parts = []
    for row in cards:
        qty = int(row[0])
        cid = str(row[1] or "").strip().upper()
        name = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if qty <= 0 or not cid:
            continue
        pid = product_ids.get(cid)
        parts.append(mass_entry_line(qty, cid, name, pid))
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
