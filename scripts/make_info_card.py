#!/usr/bin/env python3
"""Render a neofetch-style info card as SVG. Edit INFO below, then run:

    python3 scripts/make_info_card.py
"""
from html import escape

OUT = "info-card.svg"
TITLE = "enzo@42angouleme"

LOGO = [
    "        :::      ::::::::",
    "      :+:      :+:    :+:",
    "    +:+ +:+         +:+  ",
    "  +#+  +:+       +#+     ",
    "+#+#+#+#+#+   +#+        ",
    "     #+#    #+#          ",
    "    ###   ########.fr    ",
]

INFO = [
    ("Name", "Enzo Rocha--Fabing"),
    ("School", "42 Angoulême · Common Core"),
    ("Location", "Angoulême, France"),
    ("Languages", "C, C++98"),
    ("Focus", "UNIX systems, networking, low-level"),
    ("Projects", "minishell · cub3D · ft_irc · philo"),
    ("Currently", "ft_irc, an IRC server in C++98"),
    ("Shell", "zsh"),
    ("Contact", "erocha--@student.42angouleme.fr"),
]

BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
LOGO_COLOR = "#39d353"
BLOCKS = ["#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#f0f6fc"]

FONT = "'JetBrains Mono','Fira Code',Consolas,'DejaVu Sans Mono',monospace"
SIZE = 14
LINE = 22
WIDTH = 860
KEY_W = 92  # width of the key column
NBSP = " "  # keeps the logo's leading spaces in every SVG renderer


def main():
    logo_x, text_x, top = 36, 290, 46
    rows = len(INFO) + 3

    logo_y = top + ((rows - 1) * LINE - len(LOGO) * LINE) // 2 + 4
    logo = "".join(
        f'<text x="{logo_x}" y="{logo_y + i * LINE}" fill="{LOGO_COLOR}">{escape(l).replace(" ", NBSP)}</text>'
        for i, l in enumerate(LOGO)
    )

    lines = [
        f'<text x="{text_x}" y="{top}" fill="{ACCENT}" font-weight="700">{escape(TITLE)}</text>',
        f'<text x="{text_x}" y="{top + LINE}" fill="{MUTED}">{"-" * len(TITLE)}</text>',
    ]
    for i, (key, value) in enumerate(INFO):
        y = top + (i + 2) * LINE
        lines.append(f'<text x="{text_x}" y="{y}" fill="{ACCENT}" font-weight="700">{escape(key)}</text>')
        lines.append(f'<text x="{text_x + KEY_W}" y="{y}" fill="{MUTED}">:</text>')
        lines.append(f'<text x="{text_x + KEY_W + 16}" y="{y}" fill="{TEXT}">{escape(value)}</text>')
    by = top + (len(INFO) + 2) * LINE - 12
    height = by + 16 + 28
    blocks = "".join(
        f'<rect x="{text_x + i * 26}" y="{by}" width="24" height="16" fill="{c}"/>' for i, c in enumerate(BLOCKS)
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Enzo Rocha--Fabing, student at 42 Angoulême: C, C++, UNIX systems and networking">
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
<g font-family="{FONT}" font-size="{SIZE}">
{logo}
{"".join(lines)}
</g>
{blocks}
</svg>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
