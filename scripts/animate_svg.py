#!/usr/bin/env python3
"""Inject a terminal-style line-by-line reveal animation into a gh-ascii card SVG.

GitHub strips <script> from READMEs but DOES run CSS animations inside an SVG
loaded as an <img>. We give every <text> line opacity:0 and a staggered
animation-delay so the card "prints" from top to bottom on load.

Idempotent: re-running on an already-animated file is a no-op. The daily
refresh workflow downloads a fresh (un-animated) card, then runs this to
re-apply the effect, so animation AND live stats both survive.

Usage: python scripts/animate_svg.py dark_mode.svg
"""
import re
import sys

MARKER = "ghascii-anim"
STEP = 0.035   # seconds between consecutive lines
DUR = 0.32     # per-line fade duration


def animate(path: str) -> None:
    svg = open(path, encoding="utf-8").read()
    if MARKER in svg:
        print(f"{path}: already animated, skipping")
        return

    style = (
        f'<style id="{MARKER}">'
        "@keyframes ghrv{from{opacity:0}to{opacity:1}}"
        f".ghl{{opacity:0;animation:ghrv {DUR}s ease-out forwards}}"
        "@media(prefers-reduced-motion:reduce){.ghl{animation:none;opacity:1}}"
        "</style>"
    )
    # insert the <style> right after the opening <svg ...> tag
    svg = re.sub(r"(<svg\b[^>]*>)", r"\1\n  " + style, svg, count=1)

    # tag each <text> with the reveal class + an increasing delay
    counter = {"i": 0}

    def tag(m):
        d = counter["i"] * STEP
        counter["i"] += 1
        return f'<text class="ghl" style="animation-delay:{d:.3f}s"'

    svg = re.sub(r"<text\b", tag, svg)

    open(path, "w", encoding="utf-8").write(svg)
    total = (counter["i"] - 1) * STEP + DUR
    print(f"{path}: animated {counter['i']} lines, ~{total:.1f}s reveal")


if __name__ == "__main__":
    for p in sys.argv[1:] or ["dark_mode.svg"]:
        animate(p)
