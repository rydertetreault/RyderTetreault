#!/usr/bin/env python3
"""Section headers for the profile README: GitHub's own h2 (system font, 1.5em/600,
hairline divider) with a short lime lead-in on the divider. Themed light/dark.
Run: python3 tools/build.py   (no dependencies)"""
import os
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
W, H = 830, 46
SECTIONS = ["About", "Experience", "Education"]
THEMES = {
    "dark":  dict(fg="#f0f6fc", rule="#3d444db3", accent="#a3e635"),
    "light": dict(fg="#1f2328", rule="#d1d9e0b3", accent="#4d7c0f"),
}
FONT = "-apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, &quot;Noto Sans&quot;, Helvetica, Arial, sans-serif"
os.makedirs(OUT, exist_ok=True)
for name in SECTIONS:
    for theme, c in THEMES.items():
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{name}">'
               f'<text x="0" y="30" font-family="{FONT}" font-size="24" font-weight="600" fill="{c["fg"]}">{name}</text>'
               f'<rect x="0" y="{H-1}" width="{W}" height="1" fill="{c["rule"]}"/>'
               f'<rect x="0" y="{H-2}" width="32" height="2" fill="{c["accent"]}"/></svg>\n')
        open(os.path.join(OUT, f"{name.lower()}-{theme}.svg"), "w").write(svg)
print("built", sorted(os.listdir(OUT)))
