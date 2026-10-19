#!/usr/bin/env python3
"""Render self-contained pixel art and a public-data player card for GitHub."""

import argparse
import json
from datetime import date, timedelta
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INK = "#171c36"
PANEL = "#202641"
LINE = "#444b70"
WHITE = "#f5edda"
LILAC = "#c6b5f4"
PEACH = "#ffb89a"
MINT = "#9bdfcf"
MUTED = "#b0b4cd"

# Bitmap lettering stays identical in GitHub's image proxy, with no web fonts.
FONT = {
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "B": "11110/10001/10001/11110/10001/10001/11110",
    "C": "01111/10000/10000/10000/10000/10000/01111",
    "D": "11110/10001/10001/10001/10001/10001/11110",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "F": "11111/10000/10000/11110/10000/10000/10000",
    "G": "01111/10000/10000/10111/10001/10001/01111",
    "H": "10001/10001/10001/11111/10001/10001/10001",
    "I": "11111/00100/00100/00100/00100/00100/11111",
    "J": "00111/00010/00010/00010/10010/10010/01100",
    "K": "10001/10010/10100/11000/10100/10010/10001",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "M": "10001/11011/10101/10101/10001/10001/10001",
    "N": "10001/11001/10101/10011/10001/10001/10001",
    "O": "01110/10001/10001/10001/10001/10001/01110",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "Q": "01110/10001/10001/10001/10101/10010/01101",
    "R": "11110/10001/10001/11110/10100/10010/10001",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "U": "10001/10001/10001/10001/10001/10001/01110",
    "V": "10001/10001/10001/10001/10001/01010/00100",
    "W": "10001/10001/10001/10101/10101/11011/10001",
    "X": "10001/10001/01010/00100/01010/10001/10001",
    "Y": "10001/10001/01010/00100/00100/00100/00100",
    "Z": "11111/00001/00010/00100/01000/10000/11111",
    "0": "01110/10001/10011/10101/11001/10001/01110",
    "1": "00100/01100/00100/00100/00100/00100/01110",
    "2": "01110/10001/00001/00010/00100/01000/11111",
    "3": "11110/00001/00001/01110/00001/00001/11110",
    "4": "00010/00110/01010/10010/11111/00010/00010",
    "5": "11111/10000/10000/11110/00001/00001/11110",
    "6": "01110/10000/10000/11110/10001/10001/01110",
    "7": "11111/00001/00010/00100/01000/01000/01000",
    "8": "01110/10001/10001/01110/10001/10001/01110",
    "9": "01110/10001/10001/01111/00001/00001/01110",
    " ": "00000/00000/00000/00000/00000/00000/00000",
    "-": "00000/00000/00000/11111/00000/00000/00000",
    "+": "00000/00100/00100/11111/00100/00100/00000",
    ":": "00000/00100/00100/00000/00100/00100/00000",
    ".": "00000/00000/00000/00000/00000/00100/00100",
    "/": "00001/00010/00010/00100/01000/01000/10000",
    ">": "10000/01000/00100/00010/00100/01000/10000",
}


def rect(x, y, width, height, color, extra=""):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{color}" {extra}/>'


def pixel(text, x, y, size=3, color=WHITE):
    cells = []
    for index, char in enumerate(text):
        for row, bits in enumerate(FONT[char].split("/")):
            for col, bit in enumerate(bits):
                if bit == "1":
                    cells.append(f"M{x + (index * 6 + col) * size},{y + row * size}h{size}v{size}h-{size}z")
    return f'<path d="{"".join(cells)}" fill="{color}"/>'


def text(content, x, y, size=16, color=MUTED, extra=""):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" {extra}>{escape(str(content))}</text>'


def sparkle(x, y, color=LILAC, scale=1):
    return f'<path d="M{x},{y-5*scale}v{10*scale}M{x-5*scale},{y}h{10*scale}" stroke="{color}" stroke-width="{2*scale}"/>'


def document(width, height, title, body, description=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description or title)}</desc>
<style>
  .twinkle {{ animation: twinkle 4s steps(2, end) infinite; }}
  .prompt {{ animation: prompt 3s steps(2, end) infinite; }}
  @keyframes twinkle {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
  @keyframes prompt {{ 0%,70%,100% {{ opacity: 1; }} 85% {{ opacity: .45; }} }}
  @media (prefers-reduced-motion: reduce) {{ .twinkle,.prompt {{ animation: none; }} }}
</style>
{rect(0, 0, width, height, INK)}
<path d="M10 1H{width-10}V9H{width-1}V{height-9}H{width-10}V{height-1}H10V{height-9}H1V9H10Z" fill="none" stroke="{LINE}" stroke-width="2"/>
{body}
</svg>\n'''


def hero(mobile=False):
    width, height = (560, 390) if mobile else (900, 350)
    parts = [rect(11, 11, width-22, 35, PANEL), text("PLAYER 01", 26, 34, 13, LILAC),
             text("OPEN SOURCE ARCADE", width-202, 34, 13, MUTED)]
    stars = [(37, 65), (260, 60), (width-30, 95), (width-46, 215), (width-270, 260), (width-190, 67)]
    for index, (sx, sy) in enumerate(stars):
        parts.append(f'<g class="twinkle" style="animation-delay:-{index}s">{sparkle(sx, sy, MINT if index % 2 else LILAC, .65)}</g>')
    if mobile:
        parts += [pixel("NOUVELLE", 30, 95, 5), pixel("LUNE", 30, 154, 8, LILAC),
                  text("Small tools. Better quests.", 30, 251, 20, WHITE),
                  text("Agents / terminal UIs / devtools", 30, 280, 15)]
        ground, prompt_y = 311, 350
    else:
        parts += [pixel("NOUVELLE", 40, 86, 7), pixel("LUNE", 40, 155, 10, LILAC),
                  text("Small tools. Better quests.", 41, 258, 20, WHITE),
                  text("Agents / terminal UIs / developer tools", 41, 286, 15)]
        ground, prompt_y = 306, 328
    parts += [rect(12, ground, width-24, 3, LINE)]
    for gx in range(18, width-20, 28):
        parts.append(rect(gx, ground+5, 10, 3, "#303855"))
    parts += [f'<g class="prompt">{pixel("> SELECT A QUEST", 30 if mobile else 41, prompt_y, 2, PEACH)}</g>',
              text("1P", width-62, prompt_y+13, 15, MINT)]
    return document(width, height, "Nouvelle Lune — open source arcade", "".join(parts),
                    "Nouvelle Lune. Small tools. Better quests. Agents, terminal UIs and developer tools.")


def player_card(user, today, mobile=False):
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    active = sum(day["contributionCount"] > 0 for day in days)
    total = calendar["totalContributions"]
    repos = user["repositories"]["totalCount"]
    width, height = (560, 252) if mobile else (900, 200)
    parts = [pixel("PLAYER STATS", 26, 24, 2, LILAC), text("LAST 12 MONTHS", width-176, 38, 12)]
    columns = [26, 213, 400] if mobile else [28, 325, 622]
    for x, value, label in zip(columns, [total, active, repos], ["CONTRIBUTIONS", "ACTIVE DAYS", "ORIGINAL REPOS"]):
        parts.extend([pixel(str(value), x, 66, 5, WHITE), text(label, x, 123, 13, MINT)])
    bar_y = 165 if mobile else 153
    parts += [text("7D ACTIVITY", 26, bar_y+9, 12), text("UTC", width-51, height-18, 11)]
    counts = {day["date"]: day["contributionCount"] for day in days}
    recent = [counts[(today-timedelta(days=offset)).isoformat()] for offset in range(7, 0, -1)]
    peak = max(max(recent), 1)
    for index, count in enumerate(recent):
        x = 155+index*(48 if mobile else 82)
        for level in range(5):
            color = PEACH if count > 0 and level < (count*5+peak-1)//peak else LINE
            parts.append(rect(x, bar_y+12-level*5, 28 if mobile else 56, 3, color))
    stamp_y = 231 if mobile else 188
    parts.append(text(f"SAVED {today.isoformat()} / PUBLIC GITHUB DATA", 26, stamp_y, 11))
    desc = f"{total} contributions and {active} active days in the last 12 months; {repos} public original repositories. Updated {today.isoformat()} UTC. Activity bars show the last seven complete UTC days."
    return document(width, height, "Nouvelle-Lune player stats", "".join(parts), desc)


def secret_room(mobile=False):
    width, height = (560, 196) if mobile else (900, 196)
    body = [pixel("SECRET ROOM", 28, 30, 3, PEACH),
            text("Achievement unlocked: curiosity.", 28, 85, 17, WHITE),
            text("No boss fight here. Just one more idea.", 28, 113, 14),
            text("Take a side quest. Leave a useful tool behind.", 28, 141, 14, MINT)]
    body.append(pixel("+1 CURIOSITY", 28, height-33, 2, LILAC))
    return document(width, height, "Secret room: curiosity unlocked", "".join(body))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True, help="GitHub GraphQL response")
    parser.add_argument("--date", type=date.fromisoformat, required=True, help="Snapshot date in UTC")
    parser.add_argument("--output", type=Path, default=ROOT / "assets")
    args = parser.parse_args()
    payload = json.loads(args.data.read_text())
    if payload.get("errors"):
        raise ValueError(payload["errors"])
    user = payload["data"]["user"]
    if user["login"] != "Nouvelle-Lune":
        raise ValueError("The response does not belong to Nouvelle-Lune")
    args.output.mkdir(parents=True, exist_ok=True)
    for mobile in (False, True):
        suffix = "-mobile" if mobile else ""
        for name, svg in [("title-screen", hero(mobile)), ("player-stats", player_card(user, args.date, mobile)),
                          ("hidden-room", secret_room(mobile))]:
            (args.output / f"{name}{suffix}.svg").write_text(svg)
    print(f"Rendered six arcade assets for {args.date}")


if __name__ == "__main__":
    main()
