#!/usr/bin/env python3
"""Build the themed SVG components for the profile README.

Run:  uv run --with fonttools --with brotli tools/build.py
Edit CONTENT below, re-run, commit the assets. Fonts: Geist / Geist Mono
(OFL-1.1), subset + embedded so the SVGs use rydertetreault.dev's type.
"""
import base64, html, io, os
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS, OUT = os.path.join(ROOT, "tools", "fonts"), os.path.join(ROOT, "assets")
W = 830  # GitHub profile README content width on desktop

THEMES = {  # GitHub canvas colors + rydertetreault.dev accent (used sparingly)
    "dark":  dict(fg="#e6edf3", body="#c9d1d9", muted="#8b949e", rule="#30363d", accent="#a3e635"),
    "light": dict(fg="#1f2328", body="#32383f", muted="#59636e", rule="#d1d9e0", accent="#4d7c0f"),
}

# ---- content ---------------------------------------------------------------
ABOUT = ("Computer Science & Software Engineering graduate from Auburn University with a Cyber "
         "Defense certificate. I build products with AI as a first-class layer, from semantic search "
         "to automated media pipelines, grounded in a cybersecurity background.")

# (org, [(title, dates, description or None)]) newest first; >1 role = promotion
EXPERIENCE = [
    ("Praxis AI", [
        ("UI/UX Engineer", "OCT 2026 – PRESENT",
         "Designing and building the platform's user experience, from user flows to production front-end."),
        ("Engineering Intern", "JUN 2026 – OCT 2026",
         "Security audits, PraxisShield™ red-teaming, and Forward Deployed Engineering on AI agents."),
    ]),
    ("Maha Media", [
        ("Software Developer", "FEB 2026 – PRESENT",
         "Backend web systems and platform infrastructure for media and content delivery."),
    ]),
    ("Proxima Aerospace", [
        ("Software Engineering Intern", "JAN 2026 – MAR 2026",
         "Python pipelines for retrieving and processing satellite and astrodynamics data."),
    ]),
]
EDUCATION = [
    ("Auburn University", [
        ("B.S. Computer Science & Software Engineering", "DEC 2025", None),
        ("Cyber Defense Certificate", "MAY 2026", None),
    ]),
]
SECTIONS = [("01", "ABOUT", ABOUT), ("02", "EXPERIENCE", EXPERIENCE), ("03", "EDUCATION", EDUCATION)]

# ---- layout ----------------------------------------------------------------
HEADER_H = 28      # section header row (label + hairline)
ORG_GAP = 44       # header / previous block -> org name baseline
ORG_TO_ROLE = 28   # org baseline -> first role baseline
DESC_LEAD = 21     # role baseline -> description baseline
DESC_LINE = 20     # description line height
ROLE_GAP = 30      # last line of a role -> next role baseline
ABOUT_SIZE, ABOUT_LINE = 15, 25
BOTTOM = 12
TL_X, TEXT_X = 5, 24  # timeline node x, role text x

GS_STACK = "GS, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"
GM_STACK = "GM, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

def all_text():
    sans, mono = ABOUT, "".join(n + l for n, l, _ in SECTIONS)
    for orgs in (EXPERIENCE, EDUCATION):
        for org, roles in orgs:
            sans += org + "".join(t + (d or "") for t, _, d in roles)
            mono += "".join(dt for _, dt, _ in roles)
    return sans, mono

def build_fonts():
    sans_t, mono_t = all_text()
    css, metrics = "", None
    for name, src, text in (("GS", "geist-latin.woff2", sans_t), ("GM", "geist-mono-latin.woff2", mono_t)):
        f = TTFont(os.path.join(FONTS, src))
        if name == "GS":
            cmap, hm, upem = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
            metrics = {ch: hm[cmap[ord(ch)]][0] / upem for ch in set(text)}  # default (400) instance
        o = subset.Options(); o.flavor = "woff2"; o.hinting = False; o.layout_features = ["kern"]
        s = subset.Subsetter(o); s.populate(text=text); s.subset(f)
        b = io.BytesIO(); f.flavor = "woff2"; f.save(b)
        css += (f'@font-face{{font-family:"{name}";src:url(data:font/woff2;base64,'
                f'{base64.b64encode(b.getvalue()).decode()}) format("woff2");font-weight:100 900}}')
    return css, metrics

CSS, ADV = build_fonts()
e = html.escape

def wrap(text, size, width):
    lines, cur = [], ""
    for word in text.split():
        cand = f"{cur} {word}".strip()
        if cur and sum(ADV[c] for c in cand) * size > width:
            lines.append(cur); cur = word
        else:
            cur = cand
    return lines + [cur]

def svg(h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
            f'role="img" aria-label="{e(label)}"><style>{CSS}</style>{body}</svg>\n')

def mono(x, y, s, fill, anchor="start", size=12, track=0.25, weight=500):
    return (f'<text x="{x}" y="{y}" font-family="{GM_STACK}" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{track*size:.2f}" text-anchor="{anchor}" fill="{fill}">{e(s)}</text>')

def sans(x, y, s, fill, size, weight, track=0):
    return (f'<text x="{x}" y="{y}" font-family="{GS_STACK}" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{track}" fill="{fill}">{e(s)}</text>')

def header(c, num, label):
    # Site's Section style: tracked muted label + hairline; the number is the one lime accent.
    x_rule = 30 + len(label) * 12 * (0.6 + 0.3) + 14  # Geist Mono advance = 0.6em
    return (mono(0, 24, num, c["accent"]) + mono(30, 24, label, c["muted"], track=0.3) +
            f'<rect x="{x_rule:.0f}" y="19" width="{W - x_rule:.0f}" height="1" fill="{c["rule"]}"/>')

def about(c, num, label, text):
    body, y = header(c, num, label), HEADER_H + 8
    for line in wrap(text, ABOUT_SIZE, W - 40):
        y += ABOUT_LINE
        body += sans(0, y, line, c["body"], ABOUT_SIZE, 400)
    return svg(y + BOTTOM, body, f"{label.title()}. {text}")

def timeline(c, num, label, orgs):
    body, y, alt = header(c, num, label), HEADER_H, [label.title()]
    for org, roles in orgs:
        y += ORG_GAP
        body += sans(0, y, org, c["fg"], 18, 600, -0.2)
        ry, nodes = y + ORG_TO_ROLE, []
        for title, dates, desc in roles:
            nodes.append(ry - 4.25)  # optical centre of the x-height
            body += sans(TEXT_X, ry, title, c["fg"], 15, 500)
            body += mono(W, ry, dates, c["muted"], anchor="end", size=11.5, track=0.15, weight=400)
            last = ry
            if desc:
                for i, line in enumerate(wrap(desc, 13.5, W - TEXT_X)):
                    last = ry + DESC_LEAD + DESC_LINE * i
                    body += sans(TEXT_X, last, line, c["muted"], 13.5, 400)
            alt.append(f"{title}, {org}, {dates.title()}" + (f": {desc}" if desc else ""))
            y, ry = last, last + ROLE_GAP
        if len(nodes) > 1:  # promotion: hairline joining the roles
            body += f'<rect x="{TL_X - 0.5}" y="{nodes[0]}" width="1" height="{nodes[-1] - nodes[0]}" fill="{c["rule"]}"/>'
        for cy in nodes:
            body += f'<circle cx="{TL_X}" cy="{cy}" r="3.5" fill="{c["accent"]}"/>'
    return svg(y + BOTTOM, body, ". ".join(alt))

os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".svg"): os.remove(os.path.join(OUT, f))
for theme, c in THEMES.items():
    for num, label, data in SECTIONS:
        fn = about if isinstance(data, str) else timeline
        open(os.path.join(OUT, f"{label.lower()}-{theme}.svg"), "w").write(fn(c, num, label, data))
print("built", sorted(os.listdir(OUT)))
