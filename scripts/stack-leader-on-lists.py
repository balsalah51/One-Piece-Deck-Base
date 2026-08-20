#!/usr/bin/env python3
"""Move the Leader picture block above the text list on every decklist page."""

from __future__ import annotations

from pathlib import Path

ROOT = Path("/workspace/decklists")
OLD_CSS = 'href="/css/site.css?v=stack1"'
NEW_CSS = 'href="/css/site.css?v=stack2"'

LEADER_OPEN = '<section style="margin-top:22px">'
LEADER_HEAD = "<h3>Leader</h3>"


def find_matching_section(html: str, start: int) -> tuple[int, int] | None:
    if not html.startswith("<section", start):
        return None
    depth = 0
    i = start
    while i < len(html):
        if html.startswith("<section", i):
            depth += 1
            i = html.find(">", i) + 1
            continue
        if html.startswith("</section>", i):
            depth -= 1
            i += len("</section>")
            if depth == 0:
                return start, i
            continue
        i += 1
    return None


def patch(html: str) -> str:
    html = html.replace(OLD_CSS, NEW_CSS)
    if "class=\"leader-block\"" in html or "class='leader-block'" in html:
        return html
    pic = html.find('<section class="picture-summary">')
    text = html.find('<section class="text-deck">')
    if pic < 0 or text < 0:
        return html
    search_from = pic
    while True:
        sec = html.find(LEADER_OPEN, search_from)
        if sec < 0 or sec < pic:
            return html
        span = find_matching_section(html, sec)
        if not span:
            return html
        a, b = span
        chunk = html[a:b]
        if LEADER_HEAD in chunk:
            leader = chunk.replace(
                LEADER_OPEN,
                '<section class="leader-block" style="margin-top:22px">',
                1,
            )
            html = html[:a] + html[b:]
            if html[a : a + 1] == "\n":
                html = html[:a] + html[a + 1 :]
            html = html[:text] + leader + "\n" + html[text:]
            return html
        search_from = b
    return html


def main() -> None:
    n = 0
    skipped = 0
    for path in ROOT.rglob("*.html"):
        original = path.read_text()
        updated = patch(original)
        if updated == original:
            skipped += 1
            continue
        path.write_text(updated)
        n += 1
    print(f"patched {n} files, unchanged {skipped}")


if __name__ == "__main__":
    main()
