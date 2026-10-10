#!/usr/bin/env python3
"""Generate the profile README.md and its themed SVG assets.

Edit CONTENT below, then run:  python3 tools/build.py   (no dependencies)

Markdown can't color text, so two pieces are small SVGs drawn in GitHub's own
system font and theme colors (light + dark via <picture>):
  - section headings: GitHub's h2 with a lime underline fading out by mid-page
  - company names: GitHub's h3 with a grey underline fading out halfway through the name
  - role descriptions: GitHub's muted grey
Asset names include a content hash so GitHub's image cache never serves stale art.
"""
import hashlib, html, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

# ---- content ---------------------------------------------------------------
ABOUT = ("Computer Science & Software Engineering graduate from Auburn University with a Cyber "
         "Defense certificate. I build products with AI as a first-class layer, from semantic search "
         "to automated media pipelines, grounded in a cybersecurity background.")
# (org, [(title, dates, description or None)]), newest first
EXPERIENCE = [
    ("Praxis AI", [
        ("UI/UX Engineer", "Oct 2026 – Present",
         "Designing and building the platform's user experience, from user flows to production front-end."),
        ("Engineering Intern", "Jun 2026 – Oct 2026",
         "Led a full audit of the Pria platform, then began building a completely new interface for it."),
    ]),
    ("Maha Media", [
        ("Software Developer", "Feb 2026 – Present",
         "Backend web systems and platform infrastructure for media and content delivery."),
    ]),
    ("Proxima Aerospace", [
        ("Software Engineering Intern", "Jan 2026 – Mar 2026",
         "Python pipelines for retrieving and processing satellite and astrodynamics data."),
    ]),
]
EDUCATION = [
    ("Auburn University", [
        ("B.S. Computer Science & Software Engineering", "Dec 2025", None),
        ("Cyber Defense Certificate", "May 2026", None),
    ]),
]

# ---- style -----------------------------------------------------------------
W = 830  # README content width on a GitHub profile (desktop)
FONT = "-apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, &quot;Noto Sans&quot;, Helvetica, Arial, sans-serif"
THEMES = {  # GitHub Primer colors; accent = rydertetreault.dev lime
    "dark":  dict(fg="#f0f6fc", muted="#9198a1", rule="#3d444db3", accent="#a3e635"),
    "light": dict(fg="#1f2328", muted="#59636e", rule="#d1d9e0b3", accent="#4d7c0f"),
}
DESC_SIZE = 15

# Advance widths (em) of Arial/Liberation Sans Bold, a close stand-in for GitHub's bold
# system font; only used to size the company underline, so small error is invisible.
BOLD_EM = {
    ' ': 0.278, '!': 0.333, '"': 0.474, '#': 0.556, '$': 0.556, '%': 0.889, '&': 0.722, "'": 0.238, '(': 0.333, ')': 0.333, '*': 0.389, '+': 0.584,
    ',': 0.278, '-': 0.333, '.': 0.278, '/': 0.278, '0': 0.556, '1': 0.556, '2': 0.556, '3': 0.556, '4': 0.556, '5': 0.556, '6': 0.556, '7': 0.556,
    '8': 0.556, '9': 0.556, ':': 0.333, ';': 0.333, '<': 0.584, '=': 0.584, '>': 0.584, '?': 0.611, '@': 0.975, 'A': 0.722, 'B': 0.722, 'C': 0.722,
    'D': 0.722, 'E': 0.667, 'F': 0.611, 'G': 0.778, 'H': 0.722, 'I': 0.278, 'J': 0.556, 'K': 0.722, 'L': 0.611, 'M': 0.833, 'N': 0.722, 'O': 0.778,
    'P': 0.667, 'Q': 0.778, 'R': 0.722, 'S': 0.667, 'T': 0.611, 'U': 0.722, 'V': 0.667, 'W': 0.944, 'X': 0.667, 'Y': 0.667, 'Z': 0.611, '[': 0.333,
    '\\': 0.278, ']': 0.333, '^': 0.584, '_': 0.556, '`': 0.333, 'a': 0.556, 'b': 0.611, 'c': 0.556, 'd': 0.611, 'e': 0.556, 'f': 0.333, 'g': 0.611,
    'h': 0.611, 'i': 0.278, 'j': 0.278, 'k': 0.556, 'l': 0.278, 'm': 0.889, 'n': 0.611, 'o': 0.611, 'p': 0.611, 'q': 0.611, 'r': 0.389, 's': 0.556,
    't': 0.333, 'u': 0.611, 'v': 0.556, 'w': 0.778, 'x': 0.556, 'y': 0.556, 'z': 0.5, '{': 0.389, '|': 0.28, '}': 0.389, '~': 0.584,
}

def text_width(text, size):
    return sum(BOLD_EM.get(ch, 0.6) for ch in text) * size

# ---- svg pieces --------------------------------------------------------------
def svg(w, h, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'preserveAspectRatio="xMinYMid meet" role="img" aria-label="{html.escape(label)}">{body}</svg>\n')

def heading_svg(c, text, h=46):
    return svg(W, h, text,
        f'<defs><linearGradient id="fade"><stop offset="0" stop-color="{c["accent"]}"/>'
        f'<stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/></linearGradient></defs>'
        f'<text x="0" y="30" font-family="{FONT}" font-size="24" font-weight="600" fill="{c["fg"]}">{html.escape(text)}</text>'
        f'<rect x="0" y="{h-2}" width="{W // 2}" height="2" fill="url(#fade)"/>')

def org_svg(c, text, h=44, size=20):
    # GitHub's h3 (1.25em/600) with a grey underline that fades out halfway through
    # the name. 8px of top space keeps h3's separation from the previous company.
    line = round(text_width(text, size) / 2)
    return svg(W, h, text,
        f'<defs><linearGradient id="fade"><stop offset="0" stop-color="{c["muted"]}"/>'
        f'<stop offset="1" stop-color="{c["muted"]}" stop-opacity="0"/></linearGradient></defs>'
        f'<text x="0" y="31" font-family="{FONT}" font-size="{size}" font-weight="600" fill="{c["fg"]}">{html.escape(text)}</text>'
        f'<rect x="0" y="{h-2}" width="{line}" height="2" fill="url(#fade)"/>')

def desc_svg(c, text, h=22):
    return svg(W, h, text,
        f'<text x="0" y="16" font-family="{FONT}" font-size="{DESC_SIZE}" fill="{c["muted"]}">{html.escape(text)}</text>')

written = set()
def picture(kind, text, make, attrs):
    key = hashlib.sha1((kind + text + repr(THEMES) + make.__code__.co_code.hex()).encode()).hexdigest()[:8]
    names = {}
    for theme, c in THEMES.items():
        names[theme] = f"{kind}-{key}-{theme}.svg"
        with open(os.path.join(ASSETS, names[theme]), "w") as f:
            f.write(make(c, text))
        written.add(names[theme])
    alt = html.escape(text)
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{names["dark"]}">'
            f'<source media="(prefers-color-scheme: light)" srcset="assets/{names["light"]}">'
            f'<img alt="{alt}" src="assets/{names["light"]}" {attrs}></picture>')

# ---- readme ------------------------------------------------------------------
def section(title):
    return picture("heading", title, heading_svg, 'width="100%"') + "\n"

def entries(orgs):
    out = []
    for org, roles in orgs:
        out.append(picture("org", org, org_svg, 'width="100%"') + "\n")
        for title, dates, desc in roles:
            line = f"**{title}** · {dates}"
            if desc:
                line += "<br>\n" + picture("desc", desc, desc_svg, f'width="{W}"')
            out.append(line + "\n")
    return "\n".join(out)

os.makedirs(ASSETS, exist_ok=True)
readme = "\n".join([
    section("About"),
    ABOUT + "\n",
    "<br>\n",
    section("Experience"),
    entries(EXPERIENCE),
    "<br>\n",
    section("Education"),
    entries(EDUCATION),
])
with open(os.path.join(ROOT, "README.md"), "w") as f:
    f.write(readme)
for name in os.listdir(ASSETS):  # drop assets no longer referenced
    if name.endswith(".svg") and name not in written:
        os.remove(os.path.join(ASSETS, name))
print(f"README.md + {len(written)} assets")
