#!/usr/bin/env python3
"""Render the last year of GitHub contributions as an isometric skyline SVG.

Usage: GITHUB_TOKEN=... python3 scripts/render_skyline.py [user] [output.svg]
Only the standard library is used, so the GitHub Action needs no pip install.
"""
import json
import os
import sys
import urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else "erocha42"
OUT = sys.argv[2] if len(sys.argv) > 2 else "contrib-skyline.svg"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}"""

# GitHub dark palette: background, empty cell, then 4 activity levels
BG = "#0d1117"
TEXT = "#8b949e"
ACCENT = "#58a6ff"
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

# Isometric axes: one step along a week, one step along a weekday
UX, UY = 12.0, 4.6     # week  -> right / down
VX, VY = -6.0, 4.6     # day   -> left  / down
MAX_H = 70.0           # height of the tallest tower, in px
MIN_H = 2.0            # height of an empty cell


def fetch(user):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is required")
    body = json.dumps({"query": QUERY, "variables": {"login": user}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-skyline"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def shade(hex_color, factor):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, int(c * factor))) for c in (r, g, b)))


def level(count, top):
    if count == 0:
        return 0
    # quartiles of the max, like GitHub's own calendar
    return min(4, 1 + int(3 * count / max(top, 1)))


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def render(cal):
    weeks = cal["weeks"]
    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    top = max(counts) if counts else 0
    nweeks = len(weeks)

    # origin chosen so the whole drawing fits with margins
    ox = 40 + 7 * -VX
    oy = 90 + MAX_H
    width = int(ox + nweeks * UX + 40)
    height = int(oy + nweeks * UY + 7 * VY + 60)

    cells = []
    for w, week in enumerate(weeks):
        for day in week["contributionDays"]:
            cells.append((w, day["weekday"], day["contributionCount"]))
    # painter's algorithm: draw back (small w + d) to front
    cells.sort(key=lambda c: (c[0] + c[1], c[0]))

    out = []
    for w, d, count in cells:
        lvl = level(count, top)
        h = MIN_H if count == 0 else MIN_H + MAX_H * (count / top) ** 0.8
        x0 = ox + w * UX + d * VX
        y0 = oy + w * UY + d * VY
        p = (x0, y0)                          # back corner of the footprint
        pu = (x0 + UX, y0 + UY)
        pv = (x0 + VX, y0 + VY)
        puv = (x0 + UX + VX, y0 + UY + VY)
        up = lambda q: (q[0], q[1] - h)
        color = LEVELS[lvl]
        out.append(f'<polygon points="{pts([pv, puv, up(puv), up(pv)])}" fill="{shade(color, 0.62)}"/>')
        out.append(f'<polygon points="{pts([pu, puv, up(puv), up(pu)])}" fill="{shade(color, 0.80)}"/>')
        out.append(f'<polygon points="{pts([up(p), up(pu), up(puv), up(pv)])}" fill="{color}"/>')

    total = cal["totalContributions"]
    first = weeks[0]["contributionDays"][0]["date"]
    last = weeks[-1]["contributionDays"][-1]["date"]
    legend_x = width - 40 - 5 * 16
    legend = "".join(
        f'<rect x="{legend_x + i * 16}" y="{height - 34}" width="12" height="12" rx="2" fill="{c}"/>'
        for i, c in enumerate(LEVELS)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} contributions in the last year">
<rect width="100%" height="100%" rx="12" fill="{BG}"/>
<g font-family="'JetBrains Mono','Fira Code',Consolas,'DejaVu Sans Mono',monospace">
<text x="28" y="40" font-size="22" font-weight="700" fill="{ACCENT}">{total}</text>
<text x="28" y="62" font-size="13" fill="{TEXT}">contributions · {first} → {last}</text>
<text x="{legend_x - 8}" y="{height - 24}" font-size="11" fill="{TEXT}" text-anchor="end">less</text>
<text x="{legend_x + 5 * 16 + 4}" y="{height - 24}" font-size="11" fill="{TEXT}">more</text>
</g>
{legend}
{"".join(out)}
</svg>
"""


if __name__ == "__main__":
    svg = render(fetch(USER))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT}")
