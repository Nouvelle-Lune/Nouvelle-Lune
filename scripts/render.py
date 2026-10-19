#!/usr/bin/env python3
"""Render Lune Native Blue profile artwork from a public GitHub snapshot."""

import argparse
import json
import re
from datetime import date, timedelta
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PALETTE = json.loads((ROOT / "scripts/palette.json").read_text())
COLORS = PALETTE["dark"]
MONO = "Menlo,Consolas,monospace"
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

# Keep the exact ten-row crescent used by Lune's five-line terminal header.
MOON = [
    "   1111   ", " 1111     ", " 2222     ", "2222      ", "3333      ",
    "3333      ", "4444      ", " 4444     ", " 5555     ", "   5555   ",
]


def box(x, y, width, height, fill, stroke="none", radius=0):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def line(x1, y1, x2, y2, color):
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}"/>'


def text(content, x, y, size=16, color=COLORS["muted"], weight=400, extra=""):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{MONO}" font-size="{size}" font-weight="{weight}" {extra}>{escape(str(content))}</text>'


def document(width, height, title, body, description):
    return f'''<svg xmlns="{SVG_NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
{body}
</svg>\n'''


def crescent(x, y, size):
    pixels = []
    for row, bits in enumerate(MOON):
        for col, shade in enumerate(bits):
            if shade != " ":
                pixels.append(box(x + col*size, y + row*size, size, size, COLORS[f"moon{shade}"]))
    pixels += [text("·", x + 9*size, y + size, size*2, COLORS["moon4"]),
               text("*", x + 7*size, y + 4*size, size*1.8, COLORS["moon2"]),
               text("·", x + 8*size, y + 8*size, size*2, COLORS["moon5"])]
    return '<g shape-rendering="crispEdges">' + "".join(pixels) + "</g>"


def header(mobile):
    width, height = (560, 244) if mobile else (900, 224)
    parts = [box(0, 0, width, height, COLORS["bg"], COLORS["borderMuted"], 4)]
    if mobile:
        parts += [crescent(22, 53, 6),
                  text("L U N E", 124, 35, 14, COLORS["muted"], 700, 'letter-spacing="2"'),
                  text("Nouvelle Lune", 124, 80, 29, COLORS["text"], 700),
                  text("Light tools. Deeper work.", 125, 112, 15, COLORS["moon2"]),
                  text("Agents / terminal UIs / devtools", 125, 144, 12),
                  line(24, 180, 536, 180, COLORS["borderMuted"]),
                  text("~/nouvelle-lune", 24, 210, 11, COLORS["dim"]),
                  text("tools for thoughtful work", 536, 210, 10, COLORS["accentBright"], extra='text-anchor="end"')]
    else:
        parts += [crescent(32, 51, 8),
                  text("L U N E", 164, 43, 15, COLORS["muted"], 700, 'letter-spacing="2"'),
                  text("Nouvelle Lune", 164, 89, 34, COLORS["text"], 700),
                  text("Light tools. Deeper work.", 165, 124, 18, COLORS["moon2"]),
                  text("Coding agents / terminal interfaces / developer tools", 165, 153, 13),
                  line(32, 183, 868, 183, COLORS["borderMuted"]),
                  text("~/nouvelle-lune", 32, 207, 12, COLORS["dim"]),
                  text("tools for thoughtful work", 868, 207, 12, COLORS["accentBright"], extra='text-anchor="end"')]
    return document(width, height, "Nouvelle Lune — Native Blue", "".join(parts),
                    "The Lune ice-blue crescent beside Nouvelle Lune. Light tools. Deeper work. Coding agents, terminal interfaces and developer tools.")


def activity(user, today, mobile):
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    values = [calendar["totalContributions"], sum(day["contributionCount"] > 0 for day in days),
              user["repositories"]["totalCount"]]
    width, height = (560, 216) if mobile else (900, 186)
    parts = [box(0, 0, width, height, COLORS["panel"], COLORS["borderMuted"], 4),
             text("ACTIVITY", 26, 29, 12 if mobile else 11, COLORS["accentBright"], 700, 'letter-spacing="2"'),
             text("LAST 12 MONTHS", width-26, 29, 11, COLORS["dim"], extra='text-anchor="end"')]
    for index, (value, label) in enumerate(zip(values, ["contributions", "active days", "original repos"])):
        x = (24 if mobile else 26) + index * (184 if mobile else 300)
        if index:
            parts.append(line(x-18 if mobile else x-26, 50, x-18 if mobile else x-26, 122 if mobile else 116, COLORS["borderMuted"]))
        parts += [text(value, x, 92 if mobile else 89, 40 if mobile else 37, COLORS["text"], 500),
                  text(label, x, 122 if mobile else 114, 14 if mobile else 13)]
    parts += [line(26, 142 if mobile else 136, width-26, 142 if mobile else 136, COLORS["borderMuted"]),
              text("7D ACTIVITY", 26, 172 if mobile else 165, 11, COLORS["dim"]),
              text(f"UPDATED {today.isoformat()}", width-26, 199 if mobile else 165, 11, COLORS["dim"], extra='text-anchor="end"')]
    # Use complete UTC dates; the current day's partial count is not a comparable bar.
    counts = {day["date"]: day["contributionCount"] for day in days}
    recent = [counts[(today-timedelta(days=offset)).isoformat()] for offset in range(7, 0, -1)]
    peak = max(max(recent), 1)
    for index, count in enumerate(recent):
        x = (144 if mobile else 165) + index * (48 if mobile else 58)
        y, bar_width = (156, 32) if mobile else (149, 42)
        parts.append(box(x, y, bar_width, 20, COLORS["surface"], radius=1))
        if count:
            bar_height = max(2, round(count/peak*20))
            parts.append(box(x, y+20-bar_height, bar_width, bar_height, COLORS["accent"], radius=1))
    description = f"{values[0]} contributions and {values[1]} active days in the last 12 months; {values[2]} public original repositories. Updated {today.isoformat()} UTC. Bars show the seven complete UTC days before the update date."
    return document(width, height, "Nouvelle-Lune activity", "".join(parts), description)


def contribution_trail(path, colors):
    snake = ET.parse(path).getroot()
    # Nested SVG renderers disagree on :root custom-property inheritance.
    # Resolve colors explicitly while keeping the upstream animation keyframes.
    style = snake.find(f"{{{SVG_NS}}}style")
    css = re.sub(r":root\{[^}]+\}", "", style.text)
    variables = {"cb": colors["borderMuted"], "cs": colors["accentBright"],
                 "ce": colors["surface"], "c0": colors["surface"], "c1": colors["border"],
                 "c2": colors["phase1"], "c3": colors["phase2"], "c4": colors["phase3"]}
    for name, value in variables.items():
        css = css.replace(f"var(--{name})", value)
    style.text = css
    # Reuse the upstream animation inside a Lune panel; its -32px top padding
    # leaves room for the moving head, and the bottom progress bar stays visible.
    snake.set("x", "10")
    snake.set("y", "-14")
    snake.set("width", "880")
    snake.set("height", "192")
    panel = box(.5, .5, 899, 150, colors["bg"], colors["borderMuted"], 4)
    body = panel + ET.tostring(snake, encoding="unicode")
    return document(900, 151, "Nouvelle-Lune contribution trail", body,
                    "An ice-blue snake follows Nouvelle-Lune's real GitHub contribution calendar. Animation generated with Platane/snk.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True, help="GitHub GraphQL response")
    parser.add_argument("--date", type=date.fromisoformat, required=True, help="Snapshot date in UTC")
    parser.add_argument("--snakes", type=Path, required=True, help="Directory containing raw snake.svg and snake-dark.svg")
    parser.add_argument("--output", type=Path, default=ROOT / "assets")
    args = parser.parse_args()
    payload = json.loads(args.data.read_text())
    if payload.get("errors"):
        raise ValueError(payload["errors"])
    user = payload["data"]["user"]
    if user["login"] != "Nouvelle-Lune":
        raise ValueError("The response does not belong to Nouvelle-Lune")
    outputs = {}
    for mobile in (False, True):
        suffix = "-mobile" if mobile else ""
        outputs[f"lune-header{suffix}.svg"] = header(mobile)
        outputs[f"activity{suffix}.svg"] = activity(user, args.date, mobile)
    outputs["contributions.svg"] = contribution_trail(args.snakes / "snake.svg", PALETTE["light"])
    outputs["contributions-dark.svg"] = contribution_trail(args.snakes / "snake-dark.svg", PALETTE["dark"])
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, content in outputs.items():
        (args.output / filename).write_text(content)
    print(f"Rendered six Lune Native Blue assets for {args.date}")


if __name__ == "__main__":
    main()
