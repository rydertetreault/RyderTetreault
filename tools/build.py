#!/usr/bin/env python3
"""Build the themed SVG components for the profile README.

Run:  uv run --with fonttools --with brotli tools/build.py
Edit CONTENT below, re-run, commit README assets. Fonts: Geist / Geist Mono
(OFL-1.1), subset + embedded so the SVGs use rydertetreault.dev's type.
"""
import base64, html, io, os
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS, OUT = os.path.join(ROOT, "tools", "fonts"), os.path.join(ROOT, "assets")
W = 830  # GitHub profile README content width on desktop

THEMES = {  # GitHub canvas colors + rydertetreault.dev accents
    "dark":  dict(fg="#e6edf3", muted="#8b949e", rule="#30363d", accent="#a3e635"),
    "light": dict(fg="#1f2328", muted="#59636e", rule="#d1d9e0", accent="#4d7c0f"),
}

# ---- content ---------------------------------------------------------------
HERO = dict(
    eyebrow="SOFTWARE ENGINEER · AI · CYBER DEFENSE",
    lines=["AI-native software,", "security-minded engineering."],
)
SECTIONS = [
    ("01", "EXPERIENCE", [  # (org, [(title, dates)]) newest first; >1 role = promotion
        ("Praxis AI", [("UI/UX Engineer", "OCT 2026 – PRESENT"),
                       ("Engineering Intern", "JUN 2026 – OCT 2026")]),
        ("Maha Media", [("Software Developer", "FEB 2026 – PRESENT")]),
        ("Proxima Aerospace", [("Software Engineering Intern", "JAN 2026 – MAR 2026")]),
    ]),
    ("02", "EDUCATION", [
        ("Auburn University", [("B.S. Computer Science & Software Engineering", "DEC 2025"),
                               ("Cyber Defense Certificate", "MAY 2026")]),
    ]),
]

# ---- layout ----------------------------------------------------------------
HEADER_H = 28      # section header row
ORG_GAP = 46       # previous block -> next org name (> ORG_TO_ROLE so orgs group)
ORG_TO_ROLE = 28   # org baseline -> first role baseline
ROLE_STEP = 26     # role baseline -> next role baseline
BOTTOM = 14
TL_X, TEXT_X = 5, 24  # timeline node x, role text x

def fonts():
    sans_t, mono_t = "".join(HERO["lines"]), HERO["eyebrow"] + "/"
    for num, label, orgs in SECTIONS:
        mono_t += num + label
        for org, roles in orgs:
            sans_t += org + "".join(t for t, _ in roles)
            mono_t += "".join(d for _, d in roles)
    out = []
    for name, src, text in (("GS", "geist-latin.woff2", sans_t), ("GM", "geist-mono-latin.woff2", mono_t)):
        f = TTFont(os.path.join(FONTS, src))
        o = subset.Options(); o.flavor = "woff2"; o.hinting = False; o.layout_features = ["kern"]
        s = subset.Subsetter(o); s.populate(text=text); s.subset(f)
        b = io.BytesIO(); f.flavor = "woff2"; f.save(b)
        out.append(f'@font-face{{font-family:"{name}";src:url(data:font/woff2;base64,{base64.b64encode(b.getvalue()).decode()}) format("woff2");font-weight:100 900}}')
    return "".join(out)

CSS = fonts()
e = html.escape

def svg(h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{e(label)}">'
            f'<style>{CSS}</style>{body}</svg>\n')

def mono(x, y, s, fill, anchor="start", size=12, track=0.25, weight=500):
    return (f'<text x="{x}" y="{y}" font-family="GM, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{track*size:.2f}" text-anchor="{anchor}" fill="{fill}">{e(s)}</text>')

def sans(x, y, s, fill, size, weight, track=0):
    return (f'<text x="{x}" y="{y}" font-family="GS, -apple-system, Segoe UI, Helvetica, Arial, sans-serif" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{track}" fill="{fill}">{e(s)}</text>')

def hero(c):
    h = 132
    body = mono(0, 22, HERO["eyebrow"], c["accent"], track=0.2)
    for i, line in enumerate(HERO["lines"]):
        body += sans(-1, 66 + 38 * i, line, c["fg"] if i == 0 else c["muted"], 32, 600, -0.6)
    body += f'<rect x="0" y="{h-1}" width="{W}" height="1" fill="{c["rule"]}"/>'
    body += f'<rect x="0" y="{h-2}" width="40" height="2" fill="{c["accent"]}"/>'
    return svg(h, body, HERO["eyebrow"] + ". " + " ".join(HERO["lines"]))

def section(c, num, label, orgs):
    # Header: lime index, tracked muted label, hairline to the edge (site's Section style).
    body = mono(0, 24, num, c["accent"])
    body += mono(30, 24, label, c["muted"], track=0.3)
    x_rule = 30 + len(label) * 12 * (0.6 + 0.3) + 14  # Geist Mono advance = 0.6em
    body += f'<rect x="{x_rule:.0f}" y="19" width="{W - x_rule:.0f}" height="1" fill="{c["rule"]}"/>'
    y, alt = HEADER_H, [label.title()]
    for org, roles in orgs:
        y += ORG_GAP
        body += sans(0, y, org, c["fg"], 18, 600, -0.2)
        ys = [y + ORG_TO_ROLE + ROLE_STEP * i for i in range(len(roles))]
        if len(roles) > 1:  # promotion: one accent line joining the roles
            body += f'<rect x="{TL_X - 0.75}" y="{ys[0]-5}" width="1.5" height="{ys[-1]-ys[0]}" fill="{c["accent"]}" opacity="0.45"/>'
        for i, ((title, dates), ry) in enumerate(zip(roles, ys)):
            cy = ry - 4.25  # optical centre of the x-height, not the ink box
            if i == 0:
                body += f'<circle cx="{TL_X}" cy="{cy}" r="4" fill="{c["accent"]}"/>'
            else:
                body += f'<circle cx="{TL_X}" cy="{cy}" r="3.25" fill="none" stroke="{c["accent"]}" stroke-width="1.5"/>'
            body += sans(TEXT_X, ry, title, c["accent"], 15, 500)
            body += mono(W, ry, dates, c["muted"], anchor="end", size=11.5, track=0.15, weight=400)
            alt.append(f"{title}, {org}, {dates.title()}")
        y = ys[-1]
    return svg(y + BOTTOM, body, ". ".join(alt))

os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".svg"): os.remove(os.path.join(OUT, f))
for theme, c in THEMES.items():
    open(os.path.join(OUT, f"hero-{theme}.svg"), "w").write(hero(c))
    for num, label, orgs in SECTIONS:
        open(os.path.join(OUT, f"{label.lower()}-{theme}.svg"), "w").write(section(c, num, label, orgs))
print("built", sorted(os.listdir(OUT)))
