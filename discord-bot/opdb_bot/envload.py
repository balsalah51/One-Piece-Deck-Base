"""Load DISCORD_TOKEN from Windows-friendly files without printing the secret."""

from __future__ import annotations

import os
import re
from pathlib import Path

PLACEHOLDERS = {
    "",
    "paste-bot-token-here",
    "your-real-token",
    "your-token-here",
}


def clean_token(raw: str) -> str:
    token = (raw or "").strip().strip('"').strip("'")
    token = token.replace("\ufeff", "").replace("\x00", "")
    if token.lower().startswith("discord_token="):
        token = token.split("=", 1)[1].strip().strip('"').strip("'")
    if token in PLACEHOLDERS or token.lower() in PLACEHOLDERS:
        return ""
    return token


def decode_env_bytes(raw: bytes) -> str:
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    if b"\x00" in raw[:80]:
        return raw.decode("utf-16")
    return raw.decode("utf-8", errors="replace")


def parse_env_text(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip().replace("\ufeff", "")
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def token_files(bot_dir: Path) -> list[Path]:
    return [
        bot_dir / ".env",
        bot_dir / ".env.txt",
        bot_dir / "env.txt",
        bot_dir / "token.txt",
    ]


def load_token(bot_dir: Path) -> tuple[str, str]:
    """Return (token, source). Source is 'environment' or a file name."""
    env_token = clean_token(os.environ.get("DISCORD_TOKEN", ""))
    if env_token:
        return env_token, "environment"

    for path in token_files(bot_dir):
        if not path.exists() or not path.is_file():
            continue
        text = decode_env_bytes(path.read_bytes())
        if path.name.lower() == "token.txt":
            token = clean_token(text)
        else:
            values = parse_env_text(text)
            token = clean_token(values.get("DISCORD_TOKEN", ""))
            if not token:
                # Notepad users sometimes put the token on the guild line.
                other = clean_token(values.get("DISCORD_GUILD_ID", ""))
                if other and not re.fullmatch(r"\d{15,25}", other):
                    token = other
        if token:
            return token, path.name
    return "", ""


def load_guild_id(bot_dir: Path) -> str:
    raw = (os.environ.get("DISCORD_GUILD_ID") or "").strip()
    if raw and re.fullmatch(r"\d{15,25}", raw):
        return raw
    for path in token_files(bot_dir):
        if not path.exists() or path.name.lower() == "token.txt":
            continue
        values = parse_env_text(decode_env_bytes(path.read_bytes()))
        value = (values.get("DISCORD_GUILD_ID") or "").strip()
        if value and re.fullmatch(r"\d{15,25}", value):
            return value
    return ""


def describe_token_search(bot_dir: Path) -> str:
    lines = [f"Looking in {bot_dir}"]
    for path in token_files(bot_dir):
        lines.append(f"  {path.name}: {'found' if path.exists() else 'missing'}")
    return "\n".join(lines)
