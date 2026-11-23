#!/usr/bin/env python3
"""Inject a clean 'boot-up' reveal animation into a gh-ascii card SVG.

GitHub strips <script> from READMEs but DOES run CSS animations inside an SVG
loaded as an <img>. Effect: the whole card is wiped in top-to-bottom via an
animated clip-path (content stays fully sharp — no ghosty opacity fade), with a
thin accent scan-line sweeping down the reveal edge like a printer head.

Idempotent (marker id 'ghascii-anim'). The daily refresh downloads a FRESH
un-animated card, so the workflow must run this after the download.

Usage: python scripts/animate_svg.py dark_mode.svg
"""
import re
import sys

MARKER = "ghascii-anim"
DUR = 1.3          # seconds for the full wipe
ACCENT = "#7aa2f7"  # scan-line colour (matches the card's blue)


def animate(path: str) -> None:
    svg = open(path, encoding="utf-8").read()
    if MARKER in svg:
        print(f"{path}: already animated, skipping")
        return

    m = re.search(r"<svg\b[^>]*>", svg)
    svg_tag = m.group(0)
    w = float(re.search(r'width="([\d.]+)"', svg_tag).group(1))
    h = float(re.search(r'height="([\d.]+)"', svg_tag).group(1))

    style = (
        f'<style id="{MARKER}">'
        "@keyframes ghwipe{from{clip-path:inset(0 0 100% 0)}to{clip-path:inset(0 0 0 0)}}"
        f"@keyframes ghscan{{0%{{transform:translateY(0);opacity:0}}"
        f"10%{{opacity:.9}}90%{{opacity:.9}}100%{{transform:translateY({h:.1f}px);opacity:0}}}}"
        f"#ghwrap{{clip-path:inset(0 0 100% 0);animation:ghwipe {DUR}s cubic-bezier(.4,0,.2,1) forwards}}"
        f"#ghscan{{opacity:0;animation:ghscan {DUR}s cubic-bezier(.4,0,.2,1) forwards}}"
        "@media(prefers-reduced-motion:reduce){#ghwrap{animation:none;clip-path:none}#ghscan{display:none}}"
        "</style>"
    )

    # wrap all card content so the clip-path reveals it as one crisp unit
    svg = svg.replace(svg_tag, svg_tag + "\n  " + style + '\n  <g id="ghwrap">', 1)
    scan = (
        f'  <rect id="ghscan" x="0" y="0" width="{w:.1f}" height="2.5" '
        f'fill="{ACCENT}" opacity="0"/>\n'
    )
    svg = svg.replace("</svg>", "  </g>\n" + scan + "</svg>", 1)

    open(path, "w", encoding="utf-8").write(svg)
    print(f"{path}: wiped reveal ~{DUR}s over {w:.0f}x{h:.0f}")


if __name__ == "__main__":
    for p in sys.argv[1:] or ["dark_mode.svg"]:
        animate(p)
