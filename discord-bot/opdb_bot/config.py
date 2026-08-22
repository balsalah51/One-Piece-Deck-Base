"""Server layout, leaders, and copy for the OPDB Discord bot."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

SITE_URL = "https://onepiecedeckbase.com"
INVITE_URL = "https://discord.gg/adZ2WUQ3D"
REPO_ROOT = Path(__file__).resolve().parents[2]
BOT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = BOT_ROOT / "assets" / "emojis"
STATE_PATH = BOT_ROOT / "state.json"

# Discord: 5 rows × 5 buttons. One slot is reserved for Clear flair.
MAX_FLAIR_LEADERS = 24

# Discord channel names: lowercase, digits, hyphen.
# Discord emoji names: 2-32 chars, alphanumeric + underscore.

COLOR_HEX = {
    "color-red": 0xC62828,
    "color-green": 0x2E7D32,
    "color-blue": 0x1565C0,
    "color-purple": 0x6A1B9A,
    "color-black": 0x212121,
    "color-yellow": 0xF9A825,
    "color-red-green": 0x558B2F,
    "color-blue-yellow": 0x0288D1,
    "color-red-blue": 0xC2185B,
    "color-green-blue": 0x00838F,
    "color-black-yellow": 0xF9A825,
    "color-purple-yellow": 0x7B1FA2,
    "color-red-black": 0xB71C1C,
}

COLOR_UNICODE = {
    "color-red": "🔴",
    "color-green": "🟢",
    "color-blue": "🔵",
    "color-purple": "🟣",
    "color-black": "⚫",
    "color-yellow": "🟡",
    "color-red-green": "🟢",
    "color-blue-yellow": "🔵",
    "color-red-blue": "🔴",
    "color-green-blue": "🟢",
    "color-black-yellow": "🟡",
    "color-purple-yellow": "🟣",
    "color-red-black": "🔴",
}

COLOR_FROM_CACHE = {
    "red": "color-red",
    "green": "color-green",
    "blue": "color-blue",
    "purple": "color-purple",
    "black": "color-black",
    "yellow": "color-yellow",
    "red/green": "color-red-green",
    "green/red": "color-red-green",
    "blue/yellow": "color-blue-yellow",
    "yellow/blue": "color-blue-yellow",
    "red/blue": "color-red-blue",
    "blue/red": "color-red-blue",
    "green/blue": "color-green-blue",
    "blue/green": "color-green-blue",
    "black/yellow": "color-black-yellow",
    "yellow/black": "color-black-yellow",
    "purple/yellow": "color-purple-yellow",
    "yellow/purple": "color-purple-yellow",
    "red/black": "color-red-black",
    "black/red": "color-red-black",
}

# Discord-only fields. id / key / name / color / page come from the site list.
LEADER_COPY: dict[str, dict] = {
    "OP17-001": {
        "short": "Newgate",
        "search": ["whitebeard", "newgate", "edwardnewgate"],
        "take": (
            "Red OP17 Edward Newgate is a Whitebeard beatstick that keeps 8000-power bodies on the board. "
            "Core lists play Sanji, Portgas D. Ace, Izo, ten-cost Edward Newgate, Kouzuki Oden, Marco, Uta, and Moby Dick."
        ),
    },
    "OP17-020": {
        "short": "Shanks",
        "search": ["shanks", "redhair"],
        "take": (
            "Green OP17 Shanks rests the board and plays Red Hair Pirates. "
            "Every list locks Benn Beckman, Yasopp, and the ten-cost Shanks."
        ),
    },
    "OP17-039": {
        "short": "Xebec",
        "search": ["xebec", "rocks"],
        "take": (
            "Blue OP17 Rocks D. Xebec is a dense Rocks Pirates pile: Newgate, Shiki, Linlin, Gloriosa, "
            "Stussy, Rocks, the stage, and There's No Authority."
        ),
    },
    "OP17-058": {
        "short": "Kaido",
        "search": ["kaido"],
        "take": (
            "Purple OP17 Kaido is All-Star midrange. King, Queen, Basil Hawkins, Yamato, "
            "on-leader Kaido, Mamaragan, and We're Going to Claim the One Piece are the core."
        ),
    },
    "OP17-079": {
        "short": "OP17 Luffy",
        "search": ["luffy", "strawhat", "elbaph"],
        "take": (
            "Black OP17 Monkey D. Luffy is the Elbaph blocker deck, not Imu. "
            "Usopp, Gerd, and Loki are 4-ofs; most lists also play Saul, a Luffy beater, Zoro, and Robin."
        ),
    },
    "OP17-099": {
        "short": "Linlin",
        "search": ["linlin", "bigmom", "big-mom"],
        "take": (
            "Yellow OP17 Charlotte Linlin is a Big Mom swarm leader. "
            "Pudding, on-color Linlin, and Cracker are in every averaged list."
        ),
    },
    "OP13-001": {
        "short": "RG Luffy",
        "search": ["luffy"],
        "take": (
            "RG Luffy is a Straw Hat value pile still posting in current format. "
            "Lists average Sanji, Usopp, Nami, EB04 Zoro, Brook, Charlestone, starter Luffy, and Thousand Sunny."
        ),
    },
    "OP11-041": {
        "short": "Nami",
        "search": ["nami"],
        "take": (
            "Blue/Yellow Nami draws when Life cards leave, then plays a Thriller Bark yellow package. "
            "Kumacy, Gecko Moria, Nico Robin, Nami, Borsalino, and Perona are the average core."
        ),
    },
    "OP14-020": {
        "short": "Mihawk",
        "search": ["mihawk"],
        "take": (
            "Green Mihawk is a rest/control pile. Limitless lists play Perona (both printings), "
            "Law & Bepo, Kin'emon, Kouzuki Oden, the Mihawk character, and Dead Man's Game."
        ),
    },
    "OP16-001": {
        "short": "OP16 Ace",
        "search": ["ace", "portgas"],
        "take": (
            "Red OP16 Portgas D. Ace is Whitebeard rush — not the red/blue OP13 Ace. "
            "Lists lock Monkey D. Luffy, Edward Newgate, Vista, and Moby Dick."
        ),
    },
    "OP13-002": {
        "short": "OP13 Ace",
        "search": ["ace", "portgas"],
        "take": (
            "OP13 Ace is red/blue Portgas D. Ace — 3 life, 6000 power — not the red OP16 Ace rush deck. "
            "Trash a card to give −2000, then draw when you take damage or a 6000-power body dies."
        ),
    },
    "OP13-079": {
        "short": "Imu",
        "search": ["imu"],
        "take": (
            "Black OP13 Imu is Mary Geoise / Five Elders, not OP17 Elbaph Luffy. "
            "No 2-cost or higher events, and the Empty Throne stage starts in play from deck."
        ),
    },
    "OP15-058": {
        "short": "Enel",
        "search": ["enel", "eneru"],
        "take": (
            "Purple OP15 Enel is Sky Island ramp: a 6-card DON!! deck that floods DON!! from turn two "
            "and rests the board. This is not yellow OP05 Enel."
        ),
    },
    "OP11-062": {
        "short": "Katakuri",
        "search": ["katakuri"],
        "take": (
            "Purple OP11 Charlotte Katakuri is the other Big Mom leader, separate from yellow OP17 Linlin. "
            "DON!! −1 on attack or on the opponent's attack to peek their deck and gain power."
        ),
    },
    "OP16-022": {
        "short": "GB Luffy",
        "search": ["impeldown"],
        "take": (
            "Green/Blue OP16 Luffy is Impel Down, not RG OP13 Luffy and not black OP17 Elbaph Luffy. "
            "If the only characters on your field are Impel Down, set up to 2 DON!! active."
        ),
    },
    "OP16-080": {
        "short": "Blackbeard",
        "search": ["blackbeard", "teach", "marshall"],
        "take": (
            "Black/Yellow OP16 Marshall D. Teach is Blackbeard. Opponent's turn, your characters cost +1. "
            "Trash a Trigger from hand to change an attack target."
        ),
    },
    "OP12-061": {
        "short": "Rosinante",
        "search": ["rosinante", "corazon"],
        "take": (
            "Purple/Yellow OP12 Rosinante is Law's partner — not purple OP14 Doffy. "
            "Once per turn, spend a Life to keep Trafalgar Law from being K.O.'d."
        ),
    },
    "OP15-002": {
        "short": "Lucy",
        "search": ["lucy", "dressrosa"],
        "take": (
            "Red/Blue OP15 Lucy is Dressrosa, not red/blue OP13 Ace. "
            "Trash events or stages from hand to gain power on attack or when you are attacked."
        ),
    },
    "OP16-079": {
        "short": "Yamato",
        "search": ["yamato"],
        "take": (
            "Black OP16 Yamato is the Wano leader, not a Kaido character. "
            "Land of Wano characters played from trash gain Rush that turn."
        ),
    },
    "OP11-001": {
        "short": "Koby",
        "search": ["koby", "sword"],
        "take": (
            "Red/Black OP11 Koby is Navy / SWORD. "
            "SWORD characters can attack the turn they are played."
        ),
    },
    "OP14-060": {
        "short": "Doffy",
        "search": ["doflamingo", "doffy"],
        "take": (
            "Purple OP14 Donquixote Doflamingo is Doffy — not blue OP01 Doffy and not purple Katakuri. "
            "DON!! −1 on the opponent's attack to redirect it onto this leader or a Donquixote Pirate."
        ),
    },
    "OP16-041": {
        "short": "Buggy",
        "search": ["buggy"],
        "take": (
            "Blue OP16 Buggy is Impel Down / Cross Guild. "
            "When an Impel Down character leaves the field, play a Prisoner of Impel Down from trash."
        ),
    },
    "OP16-060": {
        "short": "Sengoku",
        "search": ["sengoku"],
        "take": (
            "Purple OP16 Sengoku is the Navy admiral leader. "
            "Return 8 active DON!! to play up to 3 differently named Admiral characters from hand."
        ),
    },
}

LEADERS: list[dict] = []


def card_image(cid: str) -> str:
    set_code = cid.split("-")[0]
    return f"https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/one-piece/{set_code}/{cid}_EN.webp"


def load_site_generator_leaders() -> list[dict]:
    path = REPO_ROOT / "scripts" / "generate-tournament-lists.py"
    if not path.exists():
        return []
    spec = importlib.util.spec_from_file_location("opdb_site_leaders", path)
    if spec is None or spec.loader is None:
        return []
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    leaders = getattr(module, "LEADERS", None) or []
    return [dict(item) for item in leaders if isinstance(item, dict) and item.get("id") and item.get("key")]


def _pretty_name(raw: str) -> str:
    if not raw:
        return ""
    text = re.sub(r"\.D\.", " D. ", raw)
    text = re.sub(r"(?<!D)\.", " ", text)
    return " ".join(text.split())


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:90]


def _page_path(page: str) -> str:
    page = (page or "").strip()
    if not page:
        return "/"
    if not page.startswith("/"):
        page = "/" + page
    return page


def _color_from_cache(raw: str) -> str:
    key = re.sub(r"\s+", "", (raw or "").lower())
    return COLOR_FROM_CACHE.get(key, "color-black")


def _card_meta(cid: str) -> dict:
    cache_path = REPO_ROOT / "data" / "card-cache.json"
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        if isinstance(cache, dict) and cid in cache:
            return cache.get(cid) or {}
    other = REPO_ROOT / "data" / "other-leaders.json"
    if other.exists():
        payload = json.loads(other.read_text(encoding="utf-8"))
        leaders = payload.get("leaders") if isinstance(payload, dict) else {}
        if isinstance(leaders, dict) and cid in leaders:
            return leaders.get(cid) or {}
    return {}


def _consensus_ids() -> list[str]:
    path = REPO_ROOT / "data" / "consensus-decks.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return []
    return [key for key in data if isinstance(key, str)]


def discord_leader_from_site(site: dict) -> dict:
    cid = str(site["id"])
    copy = LEADER_COPY.get(cid, {})
    name = site.get("name") or copy.get("name") or cid
    key = site.get("key") or copy.get("key") or _slug(name) or cid.lower()
    page = site.get("page") or f"decklists/{key}.html"
    return {
        "id": cid,
        "key": key,
        "name": name,
        "short": copy.get("short") or str(name).split()[-1],
        "color": site.get("color") or copy.get("color") or "color-black",
        "meta": "op17" if site.get("nav_op17") else "format",
        "page": _page_path(page),
        "image": copy.get("image") or card_image(cid),
        "search": list(copy.get("search") or [key.replace("-", "")]),
        "take": copy.get("take")
        or f"{name} (`{cid}`) is a site leader. The pinned consensus list updates after `/opdb-consensus`.",
    }


def discord_leader_from_id(cid: str) -> dict:
    copy = LEADER_COPY.get(cid, {})
    meta = _card_meta(cid)
    name = copy.get("name") or _pretty_name(str(meta.get("name") or cid))
    key = copy.get("key") or _slug(name) or cid.lower()
    color = copy.get("color") or _color_from_cache(str(meta.get("color") or ""))
    return discord_leader_from_site(
        {
            "id": cid,
            "key": key,
            "name": name,
            "color": color,
            "page": f"decklists/{key}.html",
            "nav_op17": False,
        }
    )


def refresh_leaders() -> list[dict]:
    """Rebuild LEADERS from the site list, then any extra consensus IDs."""
    by_id: dict[str, dict] = {}
    order: list[str] = []
    for site in load_site_generator_leaders():
        cid = str(site["id"])
        if cid in by_id:
            continue
        by_id[cid] = discord_leader_from_site(site)
        order.append(cid)
    for cid in _consensus_ids():
        if cid in by_id:
            continue
        by_id[cid] = discord_leader_from_id(cid)
        order.append(cid)
    LEADERS.clear()
    LEADERS.extend(by_id[cid] for cid in order)
    return LEADERS


refresh_leaders()

METAS: list[dict] = [
    {
        "key": "op17",
        "name": "OP17",
        "category": "OP17 · World's Strongest Warriors",
        "discussion": "op17-meta",
        "topic": "Current English meta. Discuss OP17 as a format here; leader rooms are for that deck.",
    },
    {
        "key": "format",
        "name": "Format staples",
        "category": "Format staples",
        "discussion": "format-talk",
        "topic": "Site leaders still posting in OP17 that are not OP17-set leaders.",
    },
]

GENERIC_CATEGORIES: list[dict] = [
    {
        "key": "information",
        "name": "Information",
        "channels": [
            {
                "key": "welcome",
                "name": "welcome",
                "kind": "text",
                "readonly": True,
                "topic": "Start here. What this server is and where to go next.",
            },
            {
                "key": "rules",
                "name": "rules",
                "kind": "text",
                "readonly": True,
                "topic": "How we play in this room.",
            },
            {
                "key": "announcements",
                "name": "announcements",
                "kind": "news",
                "readonly": True,
                "topic": "Site updates, meta snapshots, and shop notes.",
            },
            {
                "key": "flair",
                "name": "flair",
                "kind": "text",
                "readonly": True,
                "topic": "Pick your favorite OPTCG leader. One flair at a time.",
            },
        ],
    },
    {
        "key": "general",
        "name": "GENERAL",
        "channels": [
            {
                "key": "general",
                "name": "general",
                "kind": "text",
                "readonly": False,
                "topic": "Hang out. Anything that is not a leader-room list.",
            },
        ],
    },
    {
        "key": "community",
        "name": "Community",
        "channels": [
            {
                "key": "deck-help",
                "name": "deck-help",
                "kind": "text",
                "readonly": False,
                "topic": "Paste a 50-card list. Ask for cuts, tech, and matchup advice.",
            },
            {
                "key": "tournament-talk",
                "name": "tournament-talk",
                "kind": "text",
                "readonly": False,
                "topic": "Results, pairings, and what actually tabled.",
            },
            {
                "key": "shop-orders",
                "name": "shop-orders",
                "kind": "text",
                "readonly": False,
                "topic": "Playmats, dice, sleeves, custom leaders. Product + city + quantity.",
            },
            {
                "key": "off-topic",
                "name": "off-topic",
                "kind": "text",
                "readonly": False,
                "topic": "One Piece, other games, anything that is not a decklist.",
            },
        ],
    },
]


def emoji_name(leader: dict) -> str:
    return leader["key"].replace("-", "_")[:32]


def role_name(leader: dict) -> str:
    return f"Leader · {leader['name']}"


def channel_name(leader: dict) -> str:
    return leader["key"]


def site_url(leader: dict) -> str:
    return SITE_URL + leader["page"]


def color_hex(leader: dict) -> int:
    return COLOR_HEX.get(leader.get("color") or "", 0xB71C1C)


def leaders_for_meta(meta_key: str) -> list[dict]:
    return [leader for leader in LEADERS if leader["meta"] == meta_key]


def flair_leaders() -> list[dict]:
    return list(LEADERS[:MAX_FLAIR_LEADERS])


def leader_by_key(key: str) -> dict | None:
    for leader in LEADERS:
        if leader["key"] == key:
            return leader
    return None


def planned_channel_names() -> list[str]:
    names: list[str] = []
    for cat in GENERIC_CATEGORIES:
        for ch in cat["channels"]:
            names.append(ch["name"])
    for meta in METAS:
        names.append(meta["discussion"])
        for leader in leaders_for_meta(meta["key"]):
            names.append(channel_name(leader))
    return names


WELCOME_BODY = """**One Piece Deck Base**

This is the Discord for [onepiecedeckbase.com]({site}) — OPTCG decklists, consensus 50-card lists, and fan gear.

**Where to go**
- {rules} — how we talk in here
- {announcements} — site and meta updates
- {flair} — pick your favorite leader (one face, one role)
- Leader rooms under **OP17** and **Format staples** — each site leader has a channel with the current consensus list pinned
- {shop} — playmats, dice, sleeves, custom leaders

Not affiliated with Bandai or Shueisha. Fan site.
"""

RULES_BODY = """**Rules**

1. Be civil. Argue the list, not the person.
2. English constructed, current format, unless a channel says otherwise.
3. Paste real 50-card lists when you ask for help. Card IDs (`OP17-003`) beat nicknames.
4. Leader rooms are for that leader. Cross-meta talk goes in {meta} or {general}.
5. Spoilers for anime/manga get a spoiler tag. Card spoilers for unreleased English product get a warning in the first line.
6. No scalping spam, fake listings, or unofficial proxies passed off as English product.
7. Shop orders stay in {shop}. Include product, color, quantity, and shipping city.
8. Mods can move or delete posts that miss the room. Repeat problems lose chat.

Site: {site}
"""

ANNOUNCEMENTS_BODY = """**Welcome to the OPDB Discord**

The bot laid out this server from the site:

- Generic rooms: welcome, rules, announcements, flair, general, deck help, tournaments, shop, off-topic
- **OP17** — one channel per OP17 leader, plus an OP17 meta room
- **Format staples** — every other leader page on the site, including Katakuri, GB Luffy, Blackbeard, Rosinante, Lucy, Yamato, Koby, Doffy, Buggy, and Sengoku

Each leader channel has a **pinned consensus list** averaged from the lists on that page. Use `/opdb-setup` when new leaders land on the site, then `/opdb-consensus` after a list refresh.

Grab a leader flair in {flair}.
"""

FLAIR_BODY = """**Leader flair**

Pick the OPTCG leader you actually play — or the one you like looking at. One favorite at a time.

Buttons use a little One Piece face cropped from that leader's card (the same Limitless art as the site). Click again on another leader to swap. Clear flair drops the role.
"""
