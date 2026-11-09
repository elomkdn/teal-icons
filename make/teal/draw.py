#!/usr/bin/env python3
"""Draw Teal's own app icons into make/teal/apps (run it after changing a design).

They follow Adwair's grid, itself that of macOS icons: a 56 px tile with 13 px corners on a
64 px canvas, lit from above, its soft shadow below. The shadow is Adwair's own picture
(Plasma's QtSvg has no blur filter), taken from one of its icons. Every color is a
Catppuccin one: the theme builder copies these icons as they are, after the recoloring.

The rule that keeps them together: an app has a tile of its own color with a paper symbol;
a tool of the system with its own launcher has the Mocha tile with a silver symbol, and the
system's pages and hardware are free pastel shapes, without a tile, colored by family: the
icons stay light and the accent gives the theme its character (see ../RULES.md); the terminal, the system's state and the apps' own logos have that
tile too. Each
symbol is drawn on the 64 px grid, within about 16 to 48.

usage: draw.py
"""
import math
import sys
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent.parent / "src/apps/scalable"
sys.path.insert(0, str(HERE.parent / "generator"))
import catppuccin  # noqa: E402

LATTE = {"red": "#d20f39", "maroon": "#e64553", "peach": "#fe640b", "yellow": "#df8e1d",
         "green": "#40a02b", "teal": "#179299", "sky": "#04a5e5", "blue": "#1e66f5",
         "lavender": "#7287fd", "mauve": "#8839ef", "pink": "#ea76cb"}
MOCHA = {"red": "#f38ba8", "maroon": "#eba0ac", "peach": "#fab387", "yellow": "#f9e2af",
         "green": "#a6e3a1", "teal": "#94e2d5", "sky": "#89dceb", "blue": "#89b4fa",
         "lavender": "#b4befe", "mauve": "#cba6f7", "pink": "#f5c2e7"}
CRUST, BASE, SURFACE0, SURFACE1, SURFACE2, TEXT = "#11111b", "#1e1e2e", "#313244", "#45475a", "#585b70", "#cdd6f4"
PAPER, PAPER_SHADE, PAPER_EDGE = "#eff1f5", "#dce0e8", "#ccd0da"  # Latte base, crust, surface0
SILVER_TOP, SILVER_BOTTOM = "#e6e9ef", "#9399b2"  # Latte's mantle, Mocha's overlay 2
BOLD_LINE = 4.2  # a free shape has no thin lines next to the solid ones

TILE = 'x="4" y="3.969" width="56.002" height="56.002" rx="13.002"'


# kept beside the drawings, for the logos made on each computer, where Adwair's sources are not
SHADOW = HERE / "shadow.xml"


def shadow():
    """Adwair's tile shadow, the first picture of its icons."""
    if not (SRC / "discord.svg").is_file():
        return SHADOW.read_text()
    svg = (SRC / "discord.svg").read_text()
    return re.search(r"<image [^>]*/>", svg).group(0)


def icon(defs, body):
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'viewBox="0 0 64 64" width="64" height="64">'
            f"<defs>{defs}</defs>{shadow()}{body}</svg>\n")


def vertical(id, top, bottom, y1=3.969, y2=59.971):
    return (f'<linearGradient id="{id}" x1="0" x2="0" y1="{y1}" y2="{y2}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>')


# the dark tile, Mocha: the terminal, the system monitor, Haruna, micro, Elisa, the apps' logos
def mocha_tile():
    return vertical("tile", SURFACE0, BASE)


MOCHA_RIM = .18


def rim(opacity):
    """Light catching the tile's top edge."""
    return (f'<rect x="4.4" y="4.369" width="55.202" height="55.202" rx="12.6" fill="none" '
            f'stroke="{TEXT}" stroke-opacity="{opacity}" stroke-width=".8"/>')


def terminal():
    """The terminal: its prompt and underline cursor, in white, on the Mocha tile."""
    prompt = "M18.5 24 26.5 31.5 18.5 39"
    stroke = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    return icon(mocha_tile(),
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                # a faint glow, then the prompt and its cursor
                f'<path d="{prompt}M31 39H44" {stroke} stroke="{PAPER}" stroke-opacity=".10" stroke-width="8"/>'
                f'<path d="{prompt}" {stroke} stroke="{PAPER}" stroke-width="4.2"/>'
                f'<path d="M31 39H44" {stroke} stroke="{PAPER}" stroke-opacity=".85" stroke-width="4.2"/>')


def gear(cx, cy, outer, root, teeth, hole):
    """A gear outline with rounded-off teeth, and its hole (even-odd)."""
    pitch = 2 * math.pi / teeth
    points = []
    for i in range(teeth):
        a = i * pitch - math.pi / 2
        for angle, r in ((a - .30 * pitch, root), (a - .17 * pitch, outer), (a + .17 * pitch, outer),
                         (a + .30 * pitch, root)):
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    d = "M" + " ".join(f"{x:.3f} {y:.3f}" for x, y in points) + "Z"
    return d + (f"M{cx + hole:.3f} {cy}a{hole} {hole} 0 1 0 {-2 * hole} 0a{hole} {hole} 0 1 0 {2 * hole} 0Z")


def settings():
    """The settings: a silver gear, in Catppuccin's grays (Latte's mantle to Mocha's overlay 2)."""
    d = gear(32, 31.97, 19.5, 15.8, 12, 6.2)
    return icon(vertical("tile", SURFACE2, SURFACE0)
                + vertical("gear", SILVER_TOP, SILVER_BOTTOM, 12.5, 51.5),
                f'<rect {TILE} fill="url(#tile)"/>{rim(.3)}'
                f'<path d="{d}" transform="translate(0 .8)" fill="{CRUST}" fill-opacity=".35" fill-rule="evenodd"/>'
                f'<path d="{d}" fill="url(#gear)" fill-rule="evenodd"/>'
                # the hub: a ring a shade darker, lit on top
                f'<circle cx="32" cy="31.97" r="9.6" fill="none" stroke="#7f849c" stroke-width="2.4"/>'
                f'<circle cx="32" cy="31.97" r="10.9" fill="none" stroke="{PAPER}" stroke-opacity=".35" stroke-width=".6"/>')


def page(content, family):
    """A sheet of paper with a folded corner on a tile of the app's color."""
    sheet = "M22 12.5h15l8 8v29a2.5 2.5 0 0 1-2.5 2.5h-20.5a2.5 2.5 0 0 1-2.5-2.5v-34.5a2.5 2.5 0 0 1 2.5-2.5Z"
    fold = "M37 12.5l8 8h-5.5a2.5 2.5 0 0 1-2.5-2.5Z"
    return icon(vertical("tile", MOCHA[family], LATTE[family]),
                f'<rect {TILE} fill="url(#tile)"/>{rim(.25)}'
                f'<path d="{sheet}" transform="translate(0 1)" fill="{CRUST}" fill-opacity=".22"/>'
                f'<path d="{sheet}" fill="{PAPER}"/><path d="{fold}" fill="{PAPER_EDGE}"/>'
                + content(LATTE[family]))


def lines(color, widths, top=25.5):
    return "".join(f'<rect x="24" y="{top + 5 * i}" width="{w}" height="2.2" rx="1.1" fill="{color}"/>'
                   for i, w in enumerate(widths))


def writer(c):
    return f'<rect x="24" y="18" width="10" height="3" rx="1.5" fill="{c}"/>' + lines(c, (16, 16, 13, 16, 9))


def calc(c):
    cells = "".join(f'<rect x="{24 + 6 * col}" y="{24 + 5 * row}" width="4.6" height="3.6" rx=".9" fill="{c}" '
                    f'fill-opacity="{1 if row == 0 else .45}"/>'
                    for row in range(5) for col in range(3))
    return cells


def impress(c):
    return (f'<rect x="24" y="22" width="16" height="11" rx="1.6" fill="{c}"/>'
            f'<path d="M27 30.5l3.5-4 3 3 2-2 2.5 3Z" fill="{PAPER}"/>' + lines(c, (16, 11), 37.5))


def draw(c):
    return (f'<circle cx="29" cy="30" r="5.5" fill="{c}"/>'
            f'<path d="M30.5 44.5 37 33l6.5 11.5Z" fill="{c}" fill-opacity=".55"/>'
            f'<rect x="24" y="37" width="8" height="8" rx="1.6" fill="{c}" fill-opacity=".8"/>')


def base(c):
    disk = lambda y, o: (f'<path d="M24 {y}v3.6c0 1.6 3.6 2.9 8 2.9s8-1.3 8-2.9V{y}" fill="{c}" fill-opacity="{o}"/>')
    return (disk(30.5, .55) + disk(36.6, .8) + disk(42.7, 1)
            + f'<ellipse cx="32" cy="26.6" rx="8" ry="2.9" fill="{c}"/>'
            + f'<ellipse cx="32" cy="30.5" rx="8" ry="2.9" fill="{c}" fill-opacity=".55"/>')


def math_(c):
    return (f'<path d="M24.5 26.5h5l3.2 12 4.3-17H40" fill="none" stroke="{c}" stroke-width="2.4" '
            f'stroke-linecap="round" stroke-linejoin="round"/>' + lines(c, (16, 10), 41.5))



# --- symbols: glyph(c, a) draws with c, details in a (the tile's color shows through) -----

ROUND = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'


def on_color(glyph, family):
    return icon(vertical("tile", MOCHA[family], LATTE[family]),
                f'<rect {TILE} fill="url(#tile)"/>{rim(.25)}'
                f'<g opacity=".22" transform="translate(0 .9)">{glyph(CRUST, CRUST)}</g>'
                + glyph(PAPER, LATTE[family]))


def on_mocha(glyph, family=None):
    """The system's tools and pages: a silver symbol on the Mocha tile, or one in a family's
    color; its details in the tile's color."""
    top, bottom = (MOCHA[family], LATTE[family]) if family else (SILVER_TOP, SILVER_BOTTOM)
    return icon(mocha_tile() + vertical("glyph", top, bottom, 13, 51),
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                f'<g opacity=".35" transform="translate(0 .9)">{glyph(CRUST, CRUST)}</g>'
                + glyph("url(#glyph)", SURFACE0))


def mix(a, b, t):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


# What each color of a free shape means; a symbol missing here stops the build
FREE_FAMILIES = {glyph: family for family, glyphs in {
    "silver": "plain_gear two_gears info sliders autostart x_mark letter letter_down animations wallet sound_card "
              "music_note magnifier search_bar page_search",  # the system, text, motion, sound, search
    "mauve": "palette_brush app_window desktop_panel paint_roller icon_shapes color_circles "
             "splash_screen landscape sparkles",  # the look
    "pink": "media_frame",  # media
    "lavender": "keyboard mouse touchpad arrow_cursor key_combo drawing_tablet touch_screen swipe screen_edges "
                "virtual_keyboard gamepad hard_drive usb_stick disc phone plug chip display two_screens",  # the hardware
    "blue": "app_grid window_gear traffic_window desktops stacked_windows activities "
            "spelling page_check bubble bluetooth people",  # windows, apps, documents; Bluetooth; users
    "sky": "network wifi hotspot ethernet two_arrows relay cloud globe",  # connections and the world
    "yellow": "moon day_night bolt battery clock",  # light, energy and time
    "green": "shield shield_check padlock",  # security
    "peach": "person_frame accessibility leave bell",  # your session and what calls for you
}.items() for glyph in glyphs.split()}


def free_form(glyph):
    """The system's pages and hardware: a pastel shape without a tile, filling the grid, in the
    color of its family (FREE_FAMILIES). Its details are real holes (a mask: QtSvg draws them
    since Qt 6.7), so it reads on any background; a faint dark edge keeps it apart from a
    selection or a light background."""
    family = FREE_FAMILIES[glyph.__name__]
    top, bottom = (TEXT, "#bac2de") if family == "silver" else (MOCHA[family], mix(MOCHA[family], LATTE[family], .3))
    def bold(m):
        width = float(m.group(1))
        return m.group(0) if width < 2 or width >= BOLD_LINE else f'stroke="#fff" stroke-width="{BOLD_LINE}"'

    drawing = re.sub(r'stroke="#fff" stroke-width="([\d.]+)"', bold, glyph("#fff", "#000"))
    scaled = f'<g transform="translate(32 32) scale(1.42) translate(-32 -32)">{drawing}</g>'
    shape = ('<mask id="shape" maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">'
             f'<rect width="64" height="64" fill="#000"/>{scaled}</mask>')
    full = '<rect width="64" height="64" fill="{fill}" mask="url(#shape)" {more}/>'
    edge = "".join(full.format(fill=CRUST, more=f'opacity="{o}" transform="translate({x} {y})"')
                   for x, y, o in ((0, 1.1, .3), (.7, 0, .16), (-.7, 0, .16), (0, -.7, .1)))
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
            f'<defs>{vertical("tint", top, bottom, 6, 58)}{shape}</defs>'
            f'{edge}{full.format(fill="url(#tint)", more="")}</svg>\n')


def paper_on_mocha(glyph):
    """A sheet of paper on the Mocha tile; its details in the tile's color."""
    return icon(mocha_tile(),
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                f'<g opacity=".35" transform="translate(0 .9)">{glyph(CRUST, CRUST)}</g>'
                + glyph(PAPER, SURFACE0))


def on_latte(glyph, family="teal"):
    """A symbol in its color on the light Latte tile."""
    return icon(vertical("tile", PAPER, PAPER_SHADE) + vertical("glyph", MOCHA[family], LATTE[family], 13, 51),
                f'<rect {TILE} fill="url(#tile)"/>'
                f'<g opacity=".14" transform="translate(0 .9)">{glyph(CRUST, CRUST)}</g>'
                + glyph("url(#glyph)", PAPER))


def on_dark(glyph):
    """A glowing line drawing, like the terminal's prompt."""
    return icon(mocha_tile(),
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                f'<g opacity=".16">{glyph(SILVER_TOP, 8)}</g>{glyph(SILVER_TOP, 4)}')


def calculator(c, a):
    keys = "".join(f'<rect x="{24.5 + 5.75 * col}" y="{29 + 5.5 * row}" width="3.5" height="3.5" rx="1" '
                   f'fill="{a}" fill-opacity="{1 if col == 2 else .5}"/>' for row in range(4) for col in range(3))
    return (f'<rect x="21" y="14" width="22" height="36" rx="4.5" fill="{c}"/>'
            f'<rect x="24" y="17.5" width="16" height="7.5" rx="1.8" fill="{a}"/>' + keys)


def archive(c, a):
    zipper = "".join(f'<rect x="30.75" y="{y}" width="2.5" height="2" rx=".6" fill="{a}"/>'
                     for y in (18, 21.5, 27.5, 31))
    return (f'<rect x="15" y="15.5" width="34" height="9" rx="2.8" fill="{c}"/>'
            f'<path d="M17 26.5h30v18a3 3 0 0 1-3 3H20a3 3 0 0 1-3-3Z" fill="{c}"/>' + zipper
            + f'<rect x="27" y="35" width="10" height="6.5" rx="1.8" fill="{a}"/>')


def package(c, a):
    return (f'<path d="M32 14 48 22v20L32 50 16 42V22Z" fill="{c}"/>'
            f'<path d="M32 14 48 22 32 30 16 22Z" fill="{a}" fill-opacity=".35"/>'
            f'<path d="M32 30 48 22v20L32 50Z" fill="{CRUST}" fill-opacity=".14"/>'
            # the tape across the lid and down the front
            f'<path d="M24 18 40 26v6" {ROUND} stroke="{a}" stroke-opacity=".7" stroke-width="3"/>')


def printer(c, a):
    return (f'<rect x="21" y="14" width="22" height="12" rx="2" fill="{c}" fill-opacity=".6"/>'
            f'<rect x="14" y="24" width="36" height="17" rx="4.5" fill="{c}"/>'
            f'<circle cx="44" cy="29.5" r="1.8" fill="{a}"/>'
            f'<rect x="18.5" y="35.5" width="27" height="2.4" rx="1.2" fill="{a}" fill-opacity=".6"/>'
            f'<path d="M21 37h22v10a2 2 0 0 1-2 2H23a2 2 0 0 1-2-2Z" fill="{c}"/>'
            f'<path d="M25 42h14M25 45.5h9" {ROUND} stroke="{a}" stroke-opacity=".5" stroke-width="1.6"/>')


def webcam(c, a):
    return (f'<rect x="30.4" y="40" width="3.2" height="6" fill="{c}"/>'
            f'<rect x="23" y="45" width="18" height="4" rx="2" fill="{c}"/>'
            f'<circle cx="32" cy="28" r="13" fill="{c}"/><circle cx="32" cy="28" r="6.5" fill="{a}"/>'
            f'<circle cx="32" cy="28" r="3" fill="{c}" fill-opacity=".7"/><circle cx="34" cy="25.8" r="1.1" fill="{c}"/>')


def rings(c, a):
    def arc(r, start, end, width, opacity=1):
        x1, y1 = 32 + r * math.cos(math.radians(start)), 32 + r * math.sin(math.radians(start))
        x2, y2 = 32 + r * math.cos(math.radians(end)), 32 + r * math.sin(math.radians(end))
        large = 1 if (end - start) % 360 > 180 else 0
        return (f'<path d="M{x1:.2f} {y1:.2f}A{r} {r} 0 {large} 1 {x2:.2f} {y2:.2f}" fill="none" '
                f'stroke="{c}" stroke-opacity="{opacity}" stroke-width="{width}"/>')
    return (f'<circle cx="32" cy="32" r="6.5" fill="{c}"/>'
            + arc(11.5, -90, 110, 5) + arc(11.5, 116, 200, 5, .7) + arc(11.5, 206, 264, 5, .45)
            + arc(17.5, -90, 40, 4.4, .8) + arc(17.5, 46, 100, 4.4, .55) + arc(17.5, 120, 180, 4.4, .8))


def magnifier(c, a):
    return (f'<circle cx="28.5" cy="28.5" r="11.5" fill="{c}"/>'
            f'<circle cx="28.5" cy="28.5" r="7.6" fill="{a}"/>'
            f'<path d="M37 37 46.5 46.5" {ROUND} stroke="{c}" stroke-width="6"/>'
            f'<circle cx="28.5" cy="24.6" r="1.6" fill="{c}"/><rect x="27.1" y="27.6" width="2.8" height="7" rx="1.4" fill="{c}"/>')


def pencil_on_lines(c):
    return (lines(c, (16, 16, 12), 19)
            + f'<path d="M27 46.5l1.2-5.2 12.6-12.6 4 4-12.6 12.6Z" fill="{c}"/>'
            f'<path d="M40.8 28.7l1.7-1.7a1.4 1.4 0 0 1 2 0l2 2a1.4 1.4 0 0 1 0 2l-1.7 1.7Z" fill="{c}" fill-opacity=".6"/>')


def traffic_window(c, a):
    """Klassy: a white window, its red, yellow and green buttons, like the decoration's."""
    shadow = c == CRUST
    dots = ("red", "yellow", "green")
    return (f'<rect x="13" y="16" width="38" height="32" rx="5" fill="{CRUST if shadow else PAPER}"/>'
            + "".join(f'<circle cx="{19.5 + 6 * i}" cy="22" r="2.2" fill="{CRUST if shadow else MOCHA[f]}"/>' for i, f in enumerate(dots))
            + ("" if shadow else f'<rect x="17" y="27" width="30" height="17" rx="2.5" fill="{PAPER_EDGE}"/>'))


def menu_list_pencil(c, a):
    """The menu editor: its list, and an orange pencil on it, in Mocha peach."""
    return (menu_list(c, a)
            + f'<path d="M33 49.5l1.4-5.6 11.6-11.6 4.2 4.2-11.6 11.6Z" fill="{MOCHA["peach"] if c != CRUST else CRUST}" '
            f'stroke="{SURFACE0 if c != CRUST else CRUST}" stroke-width="1.2" stroke-linejoin="round"/>')


def menu_list(c, a):
    rows = "".join(f'<rect x="19.5" y="{y}" width="4" height="4" rx="1.2" fill="{a}"/>'
                   f'<rect x="26.5" y="{y + .8}" width="{w}" height="2.4" rx="1.2" fill="{a}" fill-opacity=".75"/>'
                   for y, w in ((20, 16), (27, 12), (34, 15), (41, 10)))
    return (f'<rect x="15" y="15" width="34" height="34" rx="5" fill="{c}"/>'
            f'<rect x="18" y="25.5" width="28" height="7" rx="2" fill="{a}" fill-opacity=".3"/>' + rows)


def partitions(c, a):
    """The partition manager: its disk as a pie of colored partitions."""
    return "".join(f'<path d="{d}" fill="{MOCHA[f] if c != CRUST else CRUST}"/>' for d, f in PARTITIONS) + \
        f'<circle cx="32" cy="32" r="5" fill="{SURFACE0 if c != CRUST else CRUST}"/>'


PARTITIONS = [('M32 32L32.00 15.00A17 17 0 0 1 42.93 45.02Z', 'blue'), ('M32 32L42.47 45.40A17 17 0 0 1 18.98 42.93Z', 'green'), ('M32 32L18.60 42.47A17 17 0 0 1 17.28 23.50Z', 'yellow'), ('M32 32L17.58 22.99A17 17 0 0 1 31.41 15.01Z', 'red')]


def pie(c, a):
    return (f'<circle cx="32" cy="32" r="17" fill="{c}" fill-opacity=".45"/>'
            f'<path d="M32 32V15a17 17 0 1 1-16.2 11.8Z" fill="{c}"/>'
            f'<circle cx="32" cy="32" r="4.5" fill="{a}"/>')


def smiley(c, a):
    return (f'<circle cx="32" cy="32" r="17" fill="{c}"/>'
            f'<ellipse cx="26" cy="28" rx="2.3" ry="3.2" fill="{a}"/><ellipse cx="38" cy="28" rx="2.3" ry="3.2" fill="{a}"/>'
            f'<path d="M24.5 36c4 5.5 11 5.5 15 0" {ROUND} stroke="{a}" stroke-width="3"/>')


def zap_bubble(c, a):
    """ZapFast: the speech bubble of its logo, its tail down on the left, and a zap in it."""
    return (f'<path d="M25 45.8A16.65 16.65 0 1 0 17.8 38.6L15 48.8Z" fill="{c}" stroke="{c}" '
            f'stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M35.8 20.5 25.6 33h6.2l-2.6 9.5L39.8 29.5h-6.2Z" fill="{a}" stroke="{a}" '
            f'stroke-width="1" stroke-linejoin="round"/>')


def viewfinder(c, a):
    return (f'<path d="M16.5 25v-5a3.5 3.5 0 0 1 3.5-3.5h5M39 16.5h5a3.5 3.5 0 0 1 3.5 3.5v5'
            f'M47.5 39v5a3.5 3.5 0 0 1-3.5 3.5h-5M25 47.5h-5a3.5 3.5 0 0 1-3.5-3.5v-5" {ROUND} stroke="{c}" stroke-width="4.2"/>'
            f'<circle cx="32" cy="32" r="7" fill="{c}"/><circle cx="32" cy="32" r="2.8" fill="{a}"/>')


def pulse(color, width):
    return (f'<path d="M14.5 34h7l4-11 6 19 5-14 3 6h10" {ROUND} stroke="{color}" stroke-width="{width}"/>')


def mu(c, a):
    """Micro, where it is not installed: its letter."""
    return f'<path d="M24 20v26M24 34c0 5 3 8 7.5 8s7.5-3 7.5-8V20M39 36c0 4 1.5 6 4.5 6" {ROUND} stroke="{c}" stroke-width="4.4"/>'


def media_library(c, a):
    return (f'<rect x="21" y="14.5" width="22" height="5" rx="2" fill="{c}" fill-opacity=".45"/>'
            f'<rect x="18" y="18" width="28" height="5" rx="2" fill="{c}" fill-opacity=".7"/>'
            f'<rect x="15" y="22" width="34" height="26" rx="4.5" fill="{c}"/>'
            f'<path d="M28.5 29.6c0-1.2 1.3-1.9 2.3-1.3l8.4 5.4c.9.6.9 2 0 2.6l-8.4 5.4c-1 .6-2.3-.1-2.3-1.3Z" fill="{a}"/>')


def haruna():
    """Haruna's logo, a film strip shaped like an H, on its dark tile (Adwair's version
    clips it with CSS, which Plasma ignores)."""
    holes = "".join(f"M{x} {y}h4v4h-4Z" for x in (18.5, 41.5) for y in (19, 30, 41))
    h = f"M16 15h10v12.5h12V15h10v34H38V36.5H26V49H16Z{holes}"
    return icon(mocha_tile(),
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                f'<path d="{h}" transform="translate(0 .9)" fill="{CRUST}" fill-opacity=".4" fill-rule="evenodd"/>'
                f'<path d="{h}" fill="{PAPER}" fill-rule="evenodd"/>')


def cachyos_hello():
    """Adwair's CachyOS logo, in Catppuccin colors, on the Mocha tile of the system's tools."""
    svg = catppuccin.recolor_svg((SRC / "org.cachyos.hello.svg").read_text(), everything=True)
    tile = re.search(r'<linearGradient id="d".*?</linearGradient>', svg).group(0)
    svg = svg.replace(tile, vertical("d", SURFACE0, BASE))
    # the light on its top edge, after its tile, like the other Mocha tiles
    at = svg.index(">", svg.index('fill="url(#d)"')) + 1
    return svg[:at] + rim(MOCHA_RIM) + svg[at:]


def folder(c, a):
    return (f'<path d="M14 20a4 4 0 0 1 4-4h9.4a3.4 3.4 0 0 1 2.6 1.2l2.3 2.8H46a4 4 0 0 1 4 4V27H14Z" '
            f'fill="{c}" fill-opacity=".6"/>'
            f'<rect x="14" y="23.5" width="36" height="25" rx="4" fill="{c}"/>'
            f'<rect x="25.5" y="29.5" width="13" height="2.8" rx="1.4" fill="{a}" fill-opacity=".8"/>')


# --- the apps' own logos, redrawn in the island's grammar --------------------------------

def qt_badge(letters):
    """Qt's tools: Qt's badge, its corners cut, with the tool's letter."""
    def glyph(c, a):
        return (f'<path d="M23 16H48V41L41 48H16V23Z" fill="{c}"/>'
                f'<path d="{letters}" {ROUND} stroke="{a}" stroke-width="3.4"/>')
    return glyph


QT_A = "M26 40 32 24 38 40M28.4 35h7.2"
QT_D = "M27 24v16h3.5a8 8 0 0 0 0-16Z"
QT_L = "M28 24v16h9"
QT_DV = "M21.5 26v12h2.5a6 6 0 0 0 0-12ZM32.5 26l4.5 12 4.5-12"


def gear_sector(cx, cy, outer, root, teeth, start, end):
    """The part of a gear between two angles (degrees, clockwise from the top), to its center."""
    pitch = 360 / teeth
    points = [(cx, cy)]
    a = start
    while a <= end + 0.01:
        phase = ((a % pitch) + pitch) % pitch / pitch
        r = outer if 0.2 <= phase <= 0.55 else root
        rad = math.radians(a - 90)
        points.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        a += pitch / 20
    return "M" + " ".join(f"{x:.2f} {y:.2f}" for x, y in points) + "Z"


def btrfs(c, a):
    """btrfs-assistant: a gear around a tree of snapshots."""
    return (f'<path d="{gear(32, 32, 19, 15.6, 10, 10.5)}" fill="{c}" fill-rule="evenodd"/>'
            f'<path d="M32 26v12M32 30.5h-5v6M32 30.5h5v6" {ROUND} stroke="{c}" stroke-width="2.2"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="2.1" fill="{c}"/>' for x, y in ((32, 25.5), (27, 37), (37, 37), (32, 38.5))))


def refresh(c, a):
    """Cachy-Update: its cycle of two arrows."""
    return (f'<path d="M45.2 27.5A14 14 0 0 0 20.5 22.6M18.8 36.5a14 14 0 0 0 24.7 4.9" {ROUND} stroke="{c}" stroke-width="4.5"/>'
            f'<path d="M47 16.5v11.8H35.2Z" fill="{c}" stroke="{c}" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<path d="M17 47.5V35.7h11.8Z" fill="{c}" stroke="{c}" stroke-width="1.5" stroke-linejoin="round"/>')


def kernel(c, a):
    """CachyOS Kernel Manager: its K, and the dot beside it."""
    return (f'<path d="M22 17v30M22 34 34 17M27 28.5 35.5 47" {ROUND} stroke="{c}" stroke-width="5"/>'
            f'<circle cx="43.5" cy="32" r="4" fill="{c}"/>')


def scx_gear(c, a):
    """scx-manager: its gear of four colored pieces, in Mocha colors."""
    colors = [LATTE[f] for f in ("mauve", "blue", "pink", "peach")] if c != CRUST else [CRUST] * 4
    return ("".join(f'<path d="{gear_sector(32, 32, 19, 15.2, 12, 90 * i + 2, 90 * i + 88)}" fill="{col}"/>'
                    for i, col in enumerate(colors))
            + f'<circle cx="32" cy="32" r="6.5" fill="{PAPER if c != CRUST else CRUST}"/>')


def circuit(c, a):
    """Limine Snapper: its circuit, a ring and three wires."""
    return (f'<circle cx="21" cy="32" r="6.2" fill="none" stroke="{c}" stroke-width="3.6"/>'
            f'<path d="M27.2 32H44M25.5 27.5 29 23.5h15M25.5 36.5 29 40.5h15" {ROUND} stroke="{c}" stroke-width="2.8"/>'
            + "".join(f'<circle cx="46" cy="{y}" r="2.8" fill="{c}"/>' for y in (23.5, 32, 40.5)))


def kvantum_logo():
    """Kvantum: its Kv, in the Catppuccin rainbow, on the Mocha tile of the system's tools."""
    stops = "".join(f'<stop offset="{i / 4:g}" stop-color="{MOCHA[f]}"/>'
                    for i, f in enumerate(("red", "peach", "green", "blue", "mauve")))
    letters = "M19 19v26M19 33.5 31 19M24 28.5 32.5 45M36 29l5 16 5-16"
    return icon(mocha_tile()
                + f'<linearGradient id="rainbow" x1="17" x2="48" y1="0" y2="0" gradientUnits="userSpaceOnUse">{stops}</linearGradient>',
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                f'<path d="{letters}" transform="translate(0 .9)" {ROUND} stroke="{CRUST}" stroke-opacity=".35" stroke-width="5"/>'
                f'<path d="{letters}" {ROUND} stroke="url(#rainbow)" stroke-width="5"/>')


def elisa():
    """Elisa: its cassette, the tile being its black case: the label from green to blue,
    the window and its reels. Catppuccin's closest colors to the logo's own."""
    tape = "#6e3c27"  # Latte peach far into crust: the brown tape
    return icon(mocha_tile()
                + vertical("label", MOCHA["green"], "#209fb5", 11, 42),  # Latte sapphire
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                f'<rect x="10" y="11" width="44" height="31" rx="4" fill="url(#label)"/>'
                f'<rect x="17" y="22" width="30" height="9" rx="4.5" fill="{CRUST}"/>'
                f'<rect x="26.5" y="24" width="11" height="5" fill="{PAPER}" fill-opacity=".9"/>'
                f'<rect x="26.5" y="24" width="4" height="5" fill="{tape}"/>'
                + "".join(f'<circle cx="{x}" cy="26.5" r="3.3" fill="{PAPER}"/>' for x in (21.6, 42.4))
                + f'<path d="M17 56 20.5 47h23L47 56Z" fill="{SURFACE1}"/>'
                + "".join(f'<circle cx="{x}" cy="51.6" r="2" fill="{CRUST}"/>' for x in (25.5, 38.5)))


def striped_shield(c, a):
    """Gufw: its shield crossed by a band."""
    return (f'<path d="M32 14 47 19.5v11.3c0 9.2-6.4 16-15 19.2-8.6-3.2-15-10-15-19.2V19.5Z" fill="{c}"/>'
            f'<path d="M37.6 16 47 19.5v5.2L22.4 46c-1.8-1.6-3.3-3.4-4.4-5.4Z" fill="{a}"/>')


def lens(c, a):
    """Gwenview: its eye, a picture in the iris."""
    return (f'<path d="M13 32c5.2-8.7 11.4-13 19-13s13.8 4.3 19 13c-5.2 8.7-11.4 13-19 13S18.2 40.7 13 32Z" fill="{c}"/>'
            f'<circle cx="32" cy="32" r="9" fill="{a}"/>'
            f'<path d="M25.6 36.4 29.8 31l3.2 3.4 2.4-2.6 4.1 4.6Z" fill="{c}"/>'
            f'<circle cx="35.2" cy="27.8" r="1.7" fill="{c}"/>')


def bird(c, a):
    """Kate: its bird, in flight."""
    return (f'<path d="M14 37.5c6.5-.3 11.2-3 15-7.6 3.6-4.4 7.4-9.4 14.2-10.4-1.6 1.6-2.6 3.4-2.8 5.4 '
            f'3.4-1.2 6.8-.6 9.6 1.4-3.4.4-6.2 1.6-8.4 3.8-4.4 5.6-9.4 11-18 12.2-3.8.5-7.6-1-9.6-4.8Z" fill="{c}"/>'
            f'<path d="M30.5 29.5c-1.4-4.6-4.4-8-9-10.5 6.4.2 11.2 2.8 14.2 7.4Z" fill="{c}" fill-opacity=".7"/>'
            f'<circle cx="42" cy="24.6" r="1.3" fill="{a}"/>')


def qb(c, a):
    """qBittorrent: its two letters, the q's stem down and the b's up."""
    return (f'<circle cx="22.8" cy="33" r="6.6" {ROUND} stroke="{c}" stroke-width="3.6"/>'
            f'<path d="M29.4 26.4V47" {ROUND} stroke="{c}" stroke-width="3.6"/>'
            f'<circle cx="41.2" cy="33" r="6.6" {ROUND} stroke="{c}" stroke-width="3.6"/>'
            f'<path d="M34.6 19V39.6" {ROUND} stroke="{c}" stroke-width="3.6"/>')


def kde_phone(c, a):
    """KDE Connect: its phone, KDE's gear on the screen."""
    return (f'<rect x="21" y="13" width="22" height="38" rx="4.5" fill="{c}"/>'
            f'<rect x="24" y="18" width="16" height="26" rx="1.6" fill="{a}"/>'
            f'<path d="{gear(32, 31, 6.4, 5.1, 8, 2.4)}" fill="{c}" fill-rule="evenodd"/>'
            f'<rect x="29" y="46.5" width="6" height="1.8" rx=".9" fill="{a}"/>')


def wallet(c, a):
    """KWallet: its wallet."""
    return (f'<rect x="18" y="15" width="24" height="9" rx="2" fill="{c}" fill-opacity=".55"/>'
            f'<rect x="14" y="20" width="36" height="27" rx="5" fill="{c}"/>'
            f'<rect x="35" y="28" width="15" height="11" rx="3" fill="{a}" fill-opacity=".3"/>'
            f'<circle cx="40.5" cy="33.5" r="2.3" fill="{a}"/>')


def knob(c, a):
    """pavucontrol: its volume knob."""
    def arc(start, sweep):
        r = 17
        x1, y1 = 32 + r * math.cos(math.radians(start)), 33 + r * math.sin(math.radians(start))
        x2, y2 = 32 + r * math.cos(math.radians(start + sweep)), 33 + r * math.sin(math.radians(start + sweep))
        return f"M{x1:.2f} {y1:.2f}A{r} {r} 0 {1 if sweep > 180 else 0} 1 {x2:.2f} {y2:.2f}"
    return (f'<path d="{arc(135, 270)}" {ROUND} stroke="{c}" stroke-opacity=".4" stroke-width="3"/>'
            f'<path d="{arc(135, 185)}" {ROUND} stroke="{c}" stroke-width="3"/>'
            f'<circle cx="32" cy="33" r="11.5" fill="{c}"/>'
            f'<path d="M32 33 38.4 27.6" {ROUND} stroke="{a}" stroke-width="3"/>')


def penguin(c, a):
    """Faugus: its penguin, and the gamepad it holds."""
    return (f'<path d="M32 13c-7.6 0-12.5 5.8-12.5 12.6 0 3.6 1.3 6.4 3.2 8.4h18.6c1.9-2 3.2-4.8 3.2-8.4 0-6.8-4.9-12.6-12.5-12.6Z" fill="{c}"/>'
            f'<circle cx="27.6" cy="24.5" r="2.2" fill="{a}"/><circle cx="36.4" cy="24.5" r="2.2" fill="{a}"/>'
            f'<path d="M29.5 28.6h5L32 31.6Z" fill="{a}"/>'
            f'<path d="M22.5 34.5h19c4 0 6.2 2.8 6.9 7l.6 3.6c.4 2.6-1.4 4.2-3.4 4.2-1.5 0-2.4-.8-3.2-2.1l-1.4-2.5H23'
            f'l-1.4 2.5c-.8 1.3-1.7 2.1-3.2 2.1-2 0-3.8-1.6-3.4-4.2l.6-3.6c.7-4.2 2.9-7 6.9-7Z" fill="{c}" stroke="{a}" stroke-width="1.2"/>'
            f'<path d="M22.5 40h5M25 37.5v5" {ROUND} stroke="{a}" stroke-width="1.8"/>'
            f'<circle cx="38.5" cy="38.6" r="1.4" fill="{a}"/><circle cx="41.6" cy="41.4" r="1.4" fill="{a}"/>')


def okular():
    """Okular: the wave and the reading glasses of its logo, on the light Latte tile."""
    wave = ("M42 11.5c-9.6 2.2-17.4 12-18.6 23.2-.9 8.6 3.9 14.6 10.9 14.6 6 0 11-4 13.9-9.8-3.2 2.8-6.8 4.3-10.1 4.3"
            "-5.1 0-7.8-4-7.1-10 .8-8.2 4.9-16 11-22.3Z")
    lens = f'y="30" width="16" height="11" rx="5" fill="{MOCHA["sky"]}" fill-opacity=".75" stroke="{SURFACE0}" stroke-width="2.4"'
    return icon(vertical("tile", PAPER, PAPER_SHADE) + vertical("wave", MOCHA["sky"], LATTE["blue"], 11, 50),
                f'<rect {TILE} fill="url(#tile)"/><path d="{wave}" fill="url(#wave)"/>'
                f'<g transform="rotate(-13 32 34)"><rect x="13.5" {lens}/><rect x="34.5" {lens}/>'
                f'<path d="M29.5 34c1.6-1.2 3.4-1.2 5 0M13.5 33.5 8.5 32M50.5 33.5 55.5 32" {ROUND} '
                f'stroke="{SURFACE0}" stroke-width="2.4"/></g>')


# --- settings: the system's tools have the Mocha tile, whatever Adwair draws for them ------------

def window_gear(c, a):
    """Window behavior, rules and scripts: a window, a gear on it."""
    return (f'<rect x="14" y="16" width="36" height="32" rx="6" fill="{c}"/>'
            f'<path d="M14 22a6 6 0 0 1 6-6h24a6 6 0 0 1 6 6v2H14Z" fill="{a}" fill-opacity=".3"/>'
            f'<path d="{gear(32, 36.5, 9, 7, 8, 2.8)}" fill="{a}" fill-rule="evenodd"/>')


def chip(c, a):
    """The processor: a chip and its pins."""
    pins = "".join(f'<path d="M{x} 13v6M{x} 45v6M13 {x}h6M45 {x}h6" {ROUND} stroke="{c}" stroke-width="2.6"/>'
                   for x in (25, 32, 39))
    return (pins + f'<rect x="18" y="18" width="28" height="28" rx="5" fill="{c}"/>'
            f'<rect x="25" y="25" width="14" height="14" rx="2.5" fill="{a}"/>')


def display(c, a):
    """A screen on its foot."""
    return (f'<rect x="13.5" y="15.5" width="37" height="25" rx="4" fill="{c}"/>'
            f'<rect x="17" y="19" width="30" height="18" rx="1.5" fill="{a}"/>'
            f'<path d="M32 41v6.5M24.5 48.5h15" {ROUND} stroke="{c}" stroke-width="3.2"/>')


def sound_card(c, a):
    """The sound: a speaker and its waves."""
    return (f'<path d="M16 26.5h6.5L32 18.5v27l-9.5-8H16a1.5 1.5 0 0 1-1.5-1.5v-8a1.5 1.5 0 0 1 1.5-1.5Z" fill="{c}"/>'
            f'<path d="M38 26a8 8 0 0 1 0 12M42.5 21a15 15 0 0 1 0 22" {ROUND} stroke="{c}" stroke-width="3.2"/>')


def hard_drive(c, a):
    """A disk drive and its light."""
    return (f'<rect x="13.5" y="18" width="37" height="28" rx="6" fill="{c}"/>'
            f'<path d="M14 33.5h36" stroke="{a}" stroke-opacity=".5" stroke-width="2"/>'
            f'<rect x="19" y="38" width="12" height="3" rx="1.5" fill="{a}"/><circle cx="43.5" cy="39.5" r="2.2" fill="{a}"/>')


def usb_stick(c, a):
    """A USB stick."""
    return (f'<path d="M25.5 13.5h13v12h-13Z" fill="{c}" fill-opacity=".6"/>'
            f'<rect x="28.5" y="17" width="2.6" height="2.6" fill="{a}"/><rect x="33" y="17" width="2.6" height="2.6" fill="{a}"/>'
            f'<rect x="20.5" y="24" width="23" height="27" rx="5" fill="{c}"/>'
            f'<rect x="27" y="32" width="10" height="10" rx="5" fill="{a}"/>')


def disc(c, a):
    """A disc: its label, its hole."""
    return (f'<circle cx="32" cy="32" r="19" fill="{c}"/>'
            f'<circle cx="32" cy="32" r="9" fill="none" stroke="{a}" stroke-opacity=".5" stroke-width="2"/>'
            f'<circle cx="32" cy="32" r="4.2" fill="{a}"/>')


def phone(c, a):
    """A phone."""
    return (f'<rect x="21" y="13" width="22" height="38" rx="4.5" fill="{c}"/>'
            f'<rect x="24" y="17.5" width="16" height="27" rx="1.6" fill="{a}"/>'
            f'<rect x="29" y="46.8" width="6" height="1.8" rx=".9" fill="{a}"/>')


def keyboard(c, a):
    """A keyboard: three rows of keys and the space bar."""
    keys = "".join(f'<rect x="{x}" y="{y}" width="3.2" height="3.2" rx=".8" fill="{a}"/>'
                   for y in (26.5, 32) for x in (18.5, 24.2, 29.9, 35.6, 41.3))
    return (f'<rect x="12.5" y="21" width="39" height="23" rx="5" fill="{c}"/>{keys}'
            f'<rect x="23" y="38" width="18" height="2.8" rx="1.4" fill="{a}"/>')


def mouse(c, a):
    """A mouse and its wheel."""
    return (f'<rect x="21" y="13.5" width="22" height="37" rx="11" fill="{c}"/>'
            f'<rect x="30.4" y="20" width="3.2" height="8.5" rx="1.6" fill="{a}"/>')


def palette_brush(c, a):
    """The look of the desktop: a painter's palette."""
    return (f'<path d="M32 14a18 18 0 1 0 0 36c3.2 0 4.2-2.4 3-4.4-1.4-2.3-.1-5.6 3-5.6h5a7 7 0 0 0 7-7c0-10.5-8.1-19-18-19Z" fill="{c}"/>'
            f'<circle cx="24" cy="26" r="3.2" fill="{a}"/><circle cx="33" cy="22" r="3.2" fill="{a}"/>'
            f'<circle cx="41.5" cy="27" r="3.2" fill="{a}"/><circle cx="21.5" cy="36" r="3.2" fill="{a}"/>')


def landscape(c, a):
    """The wallpaper: a picture of mountains under the sun."""
    return (f'<rect x="13" y="17" width="38" height="30" rx="5" fill="{c}"/>'
            f'<circle cx="41" cy="25.5" r="3.6" fill="{a}"/>'
            f'<path d="M17 43.5 27 28l7 10 4-5 8.5 10.5Z" fill="{a}"/>')


def letter(c, a):
    """The fonts: a capital A."""
    return (f'<path d="M18.5 49 32 15l13.5 34M23.5 38h17" {ROUND} stroke="{c}" stroke-width="5.2"/>')


def network(c, a):
    """The network: three linked computers."""
    return (f'<path d="M32 26v7.5M19.5 41v-7.5h25V41" {ROUND} stroke="{c}" stroke-width="3"/>'
            f'<rect x="24" y="14" width="16" height="12.5" rx="3" fill="{c}"/>'
            f'<rect x="12" y="40" width="15" height="11" rx="3" fill="{c}"/><rect x="37" y="40" width="15" height="11" rx="3" fill="{c}"/>')


def color_circles(c, a):
    """The colors: three overlapping discs."""
    return (f'<circle cx="32" cy="24.5" r="11.5" fill="{c}"/><circle cx="24" cy="38.5" r="11.5" fill="{c}" fill-opacity=".72"/>'
            f'<circle cx="40" cy="38.5" r="11.5" fill="{c}" fill-opacity=".48"/>')


def globe(c, a):
    """The languages and regions: a globe."""
    return (f'<circle cx="32" cy="32" r="18.5" fill="none" stroke="{c}" stroke-width="3.4"/>'
            f'<ellipse cx="32" cy="32" rx="8" ry="18.5" fill="none" stroke="{c}" stroke-width="3"/>'
            f'<path d="M14 26h36M14 38h36" stroke="{c}" stroke-width="3"/>')


def people(c, a):
    """The users: two people."""
    return (f'<circle cx="42" cy="26" r="6.2" fill="{c}" fill-opacity=".6"/>'
            f'<path d="M37 36.5c7.8-1.8 15 2.6 15 10.5h-9.5c0-4.2-2.2-7.7-5.5-10.5Z" fill="{c}" fill-opacity=".6"/>'
            f'<circle cx="26" cy="25" r="8.2" fill="{c}"/>'
            f'<path d="M12 48c0-9 6-14.5 14-14.5S40 39 40 48c0 .8-.6 1.4-1.4 1.4H13.4C12.6 49.4 12 48.8 12 48Z" fill="{c}"/>')


def sliders(c, a):
    """Quick settings: three sliders."""
    rows = ((21.5, 40), (32, 23.5), (42.5, 36))
    return ("".join(f'<path d="M15 {y}H49" {ROUND} stroke="{c}" stroke-opacity=".5" stroke-width="3.4"/>'
                    f'<circle cx="{x}" cy="{y}" r="5.8" fill="{c}"/>' for y, x in rows))


def spelling(c, a):
    """The spell checker: a letter, checked."""
    return (f'<path d="M15.5 38.5 25.5 14l10 24.5M19.5 30.5h12" {ROUND} stroke="{c}" stroke-width="4.4"/>'
            f'<path d="M29.5 44 36.5 50.5 49.5 33" {ROUND} stroke="{c}" stroke-width="5"/>')


def day_night(c, a):
    """The day-night cycle: a disc, half night, the rays of the day on the other side."""
    rays = "".join(f'M{32 + 20.5 * math.cos(math.radians(t)):.2f} {32 + 20.5 * math.sin(math.radians(t)):.2f}'
                   f'L{32 + 25.5 * math.cos(math.radians(t)):.2f} {32 + 25.5 * math.sin(math.radians(t)):.2f}'
                   for t in (110, 145, 180, 215, 250))
    return (f'<circle cx="32" cy="32" r="14.5" fill="none" stroke="{c}" stroke-width="3.4"/>'
            f'<path d="M32 17.5a14.5 14.5 0 0 1 0 29Z" fill="{c}"/>'
            f'<path d="{rays}" {ROUND} stroke="{c}" stroke-width="3.4"/>')


def autostart(c, a):
    """What starts by itself: a play button."""
    return (f'<circle cx="32" cy="32" r="19" fill="{c}"/>'
            f'<path d="M27.5 23v18L42 32Z" fill="{a}" stroke="{a}" stroke-width="2.4" stroke-linejoin="round"/>')


def moon(c, a):
    """The night light: a crescent and a star."""
    return (f'<path d="M36.5 14.5a18.5 18.5 0 1 0 13.5 29 15.5 15.5 0 0 1-13.5-29Z" fill="{c}"/>'
            f'<path d="M45 15.5l1.4 3.6 3.6 1.4-3.6 1.4-1.4 3.6-1.4-3.6-3.6-1.4 3.6-1.4Z" fill="{c}"/>')


def hotspot(c, a):
    """The hotspot: waves going out on both sides."""
    return (f'<circle cx="32" cy="32" r="4.8" fill="{c}"/>'
            f'<path d="M22.5 21.5a14.5 14.5 0 0 0 0 21M41.5 21.5a14.5 14.5 0 0 1 0 21'
            f'M15.5 15a24 24 0 0 0 0 34M48.5 15a24 24 0 0 1 0 34" {ROUND} stroke="{c}" stroke-width="3.6"/>')


def key_combo(c, a):
    """The shortcuts: two keys, pressed together."""
    return (f'<rect x="11" y="21" width="18" height="22" rx="5" fill="{c}"/><rect x="35" y="21" width="18" height="22" rx="5" fill="{c}"/>'
            f'<rect x="15.5" y="35.5" width="9" height="2.6" rx="1.3" fill="{a}"/><rect x="39.5" y="35.5" width="9" height="2.6" rx="1.3" fill="{a}"/>'
            f'<path d="M32 29v6M29 32h6" {ROUND} stroke="{c}" stroke-width="2.6"/>')


def ethernet(c, a):
    """The wired network: its plug and cable."""
    pins = "".join(f'<rect x="{x}" y="17" width="2.2" height="6" fill="{a}"/>' for x in (24.5, 28.5, 32.5, 36.5))
    return (f'<path d="M20.5 16a2.5 2.5 0 0 1 2.5-2.5h18a2.5 2.5 0 0 1 2.5 2.5v15a3 3 0 0 1-3 3H38v8H26v-8h-2.5a3 3 0 0 1-3-3Z" fill="{c}"/>'
            f'{pins}<rect x="29" y="41" width="6" height="10" fill="{c}"/>')


def wifi(c, a):
    """The Wi-Fi: its three arcs."""
    return (f'<path d="M13.5 28.5a26 26 0 0 1 37 0M20.5 35.5a16 16 0 0 1 23 0M27 42a7 7 0 0 1 10 0" {ROUND} stroke="{c}" stroke-width="4.2"/>'
            f'<circle cx="32" cy="48" r="3.4" fill="{c}"/>')


def music_note(c, a):
    """The system's sounds: a pair of notes."""
    return (f'<path d="M25.5 45V20.5l21.5-5V40" {ROUND} stroke="{c}" stroke-width="3.6"/>'
            f'<ellipse cx="20" cy="45" rx="6.8" ry="5.4" fill="{c}"/><ellipse cx="41.5" cy="40" rx="6.8" ry="5.4" fill="{c}"/>')


def virtual_keyboard(c, a):
    """The on-screen keyboard: a keyboard that goes away."""
    keys = "".join(f'<rect x="{x}" y="{y}" width="3.2" height="3.2" rx=".8" fill="{a}"/>'
                   for y in (20, 25.5) for x in (18.5, 24.2, 29.9, 35.6, 41.3))
    return (f'<rect x="12.5" y="14.5" width="39" height="23" rx="5" fill="{c}"/>{keys}'
            f'<rect x="23" y="31.5" width="18" height="2.8" rx="1.4" fill="{a}"/>'
            f'<path d="M25.5 43.5 32 49l6.5-5.5" {ROUND} stroke="{c}" stroke-width="3.6"/>')


def two_screens(c, a):
    """The screens' layout: two screens side by side."""
    return (f'<rect x="12" y="15" width="26" height="19" rx="4" fill="{c}" fill-opacity=".55"/>'
            f'<rect x="26" y="29" width="26" height="19" rx="4" fill="{a}"/>'
            f'<rect x="28" y="31" width="22" height="15" rx="2.6" fill="{c}"/>')


def bell(c, a):
    """The notifications: a bell."""
    return (f'<path d="M32 13c-8 0-13.5 6-13.5 13.5v8L14 41a2 2 0 0 0 1.7 3h32.6a2 2 0 0 0 1.7-3l-4.5-6.5v-8C45.5 19 40 13 32 13Z" fill="{c}"/>'
            f'<path d="M26.5 47.5a6 6 0 0 0 11 0Z" fill="{c}"/>')


def leave(c, a):
    """The desktop's session: a door, and the arrow leaving it."""
    return (f'<rect x="14" y="13" width="23" height="38" rx="4.5" fill="{c}"/><circle cx="31.5" cy="32" r="2" fill="{a}"/>'
            f'<path d="M41 32h12.5M47 25l7 7-7 7" {ROUND} stroke="{c}" stroke-width="4"/>')


def shopping_bag(c, a):
    """The software center: a bag."""
    return (f'<path d="M17 24h30l2.6 22.5a4 4 0 0 1-4 4.5H18.4a4 4 0 0 1-4-4.5Z" fill="{c}"/>'
            f'<path d="M24.5 30v-9a7.5 7.5 0 0 1 15 0v9" {ROUND} stroke="{a}" stroke-width="3.2"/>'
            f'<path d="M24.5 24v-3a7.5 7.5 0 0 1 15 0v3" {ROUND} stroke="{c}" stroke-width="3.2"/>')


def star(cx, cy, r):
    k = .22 * r
    return (f"M{cx} {cy - r}L{cx + k} {cy - k}L{cx + r} {cy}L{cx + k} {cy + k}L{cx} {cy + r}"
            f"L{cx - k} {cy + k}L{cx - r} {cy}L{cx - k} {cy - k}Z")


def accessibility(c, a):
    return (f'<circle cx="32" cy="17.5" r="5" fill="{c}"/>'
            f'<path d="M15.5 26c5.5 2 10.8 3 16.5 3s11-1 16.5-3M32 29v9l-7 13M32 38l7 13" {ROUND} stroke="{c}" stroke-width="4.2"/>')


def activities(c, a):
    return (f'<rect x="19" y="14" width="26" height="9" rx="4" fill="{c}" fill-opacity=".45"/>'
            f'<rect x="15.5" y="26" width="33" height="10" rx="4.5" fill="{c}" fill-opacity=".72"/>'
            f'<rect x="12" y="39" width="40" height="11" rx="5" fill="{c}"/>')


def animations(c, a):
    return (f'<circle cx="41.5" cy="32" r="10.5" fill="{c}"/><circle cx="25" cy="32" r="6" fill="{c}" fill-opacity=".55"/>'
            f'<circle cx="14.5" cy="32" r="3.2" fill="{c}" fill-opacity=".3"/>')


def app_grid(c, a):
    return "".join(f'<rect x="{x}" y="{y}" width="16" height="16" rx="4.5" fill="{c}"/>' for x in (14, 34) for y in (14, 34))


def page_check(c, a):
    return (f'<path d="M18.5 13h17L46 23.5V47a4 4 0 0 1-4 4H18.5a4 4 0 0 1-4-4V17a4 4 0 0 1 4-4Z" fill="{c}"/>'
            f'<path d="M23 35l6 6 11-13" {ROUND} stroke="{a}" stroke-width="3.6"/>')


def bluetooth(c, a):
    return f'<path d="M21.5 22 42.5 41 32 51V13l10.5 10-21 19" {ROUND} stroke="{c}" stroke-width="4.2"/>'


def desktops(c, a):
    outlines = "".join(f'<rect x="{x}" y="{y}" width="16" height="16" rx="4" fill="none" stroke="{c}" stroke-width="3"/>'
                       for x, y in ((35, 15), (15, 35), (35, 35)))
    return f'<rect x="13.5" y="13.5" width="19" height="19" rx="5" fill="{c}"/>{outlines}'


def cloud(c, a):
    return f'<path d="M21.5 47a10.5 10.5 0 0 1-1.7-20.9A13.5 13.5 0 0 1 45.6 27 10 10 0 0 1 44 47Z" fill="{c}"/>'


def search_bar(c, a):
    return (f'<rect x="12" y="22.5" width="40" height="19" rx="9.5" fill="{c}"/>'
            f'<circle cx="23" cy="31" r="4.1" fill="none" stroke="{a}" stroke-width="2.6"/>'
            f'<path d="M26 34.2 29 37.4M34 32h11" {ROUND} stroke="{a}" stroke-width="2.6"/>')


def gamepad(c, a):
    dots = f'<circle cx="41.5" cy="28.5" r="2.4" fill="{a}"/><circle cx="46" cy="34" r="2.4" fill="{a}"/>'
    return (f'<path d="M21 21h22c6 0 10 5 10.6 11l1.1 9c.6 5.3-5.8 8.3-9.3 4.3L40.5 39h-17l-5.9 6.3c-3.5 4-9.9 1-9.3-4.3l1.1-9C10 26 15 21 21 21Z" fill="{c}"/>'
            f'<path d="M20 26.5v9M15.5 31h9" {ROUND} stroke="{a}" stroke-width="3"/>{dots}')


def clock(c, a):
    return f'<circle cx="32" cy="32" r="19" fill="{c}"/><path d="M32 20.5V32l8 5" {ROUND} stroke="{a}" stroke-width="3.6"/>'


def sparkles(c, a):
    return (f'<path d="{star(27, 34, 16)}" fill="{c}"/><path d="{star(44, 21, 8)}" fill="{c}"/>'
            f'<path d="{star(46, 44, 5)}" fill="{c}" fill-opacity=".7"/>')


def letter_down(c, a):
    return (f'<path d="M12.5 39 22.5 14l10 25M16.5 31h12" {ROUND} stroke="{c}" stroke-width="4.4"/>'
            f'<path d="M43.5 17v28M35.5 37l8 8 8-8" {ROUND} stroke="{c}" stroke-width="4.4"/>')


def icon_shapes(c, a):
    return (f'<circle cx="22.5" cy="22.5" r="8.5" fill="{c}"/><rect x="34.5" y="14.5" width="16" height="16" rx="3.5" fill="{c}"/>'
            f'<path d="M22.5 34.5l8.8 15.5H13.7Z" fill="{c}" stroke="{c}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="{star(42.5, 42.5, 9.5)}" fill="{c}"/>')


def shield_check(c, a):
    return (f'<path d="M32 12.5 49.5 19v12.5c0 10-7 17.5-17.5 21-10.5-3.5-17.5-11-17.5-21V19Z" fill="{c}"/>'
            f'<path d="M24 32l6 6 11-13" {ROUND} stroke="{a}" stroke-width="3.8"/>')


def touchpad(c, a):
    return (f'<rect x="13" y="15" width="38" height="34" rx="6" fill="{c}"/>'
            f'<path d="M13 40h38M32 40v9" stroke="{a}" stroke-width="2.4"/>')


def arrow_cursor(c, a):
    return f'<path d="M19 12v35l9.5-8.9 6.5 14 6.2-2.8-6.5-13.6 13.4-1.200Z" fill="{c}" stroke="{c}" stroke-width="1.6" stroke-linejoin="round"/>'


def x_mark(c, a):
    return f'<path d="M17 16 47 48M47 16 17 48" {ROUND} stroke="{c}" stroke-width="5.6"/>'


def two_arrows(c, a):
    return f'<path d="M14 24.500h34M40 16.500l8 8-8 8M50 39.500H16M24 31.500l-8 8 8 8" {ROUND} stroke="{c}" stroke-width="4.2"/>'


def page_search(c, a):
    return (f'<path d="M17 13h15l9 9v8.500a12 12 0 0 0-14 20H17a4 4 0 0 1-4-4V17a4 4 0 0 1 4-4Z" fill="{c}" fill-opacity=".65"/>'
            f'<circle cx="37.5" cy="38.5" r="8" fill="none" stroke="{c}" stroke-width="3.8"/>'
            f'<path d="M43.5 44.5 50 51" {ROUND} stroke="{c}" stroke-width="4.2"/>')


def bubble(c, a):
    dots = "".join(f'<circle cx="{x}" cy="28.5" r="2.6" fill="{a}"/>' for x in (23, 32, 41))
    return (f'<path d="M17 13.500h30a5 5 0 0 1 5 5V38.500a5 5 0 0 1-5 5H31l-11 8.500v-8.500h-3a5 5 0 0 1-5-5V18.500a5 5 0 0 1 5-5Z" fill="{c}"/>{dots}')


def relay(c, a):
    return (f'<path d="M26 32h12" {ROUND} stroke="{c}" stroke-width="3.4"/>'
            f'<rect x="12" y="22.5" width="15" height="19" rx="4" fill="{c}"/><rect x="37" y="22.5" width="15" height="19" rx="4" fill="{c}"/>'
            f'<circle cx="32" cy="32" r="4.4" fill="{c}"/>')


def two_gears(c, a):
    return (f'<path d="{gear(25, 25, 13, 10.2, 9, 4.2)}" fill="{c}" fill-rule="evenodd"/>'
            f'<path d="{gear(43.5, 42.5, 9.8, 7.6, 8, 3)}" fill="{c}" fill-opacity=".72" fill-rule="evenodd"/>')


def app_window(c, a):
    return (f'<rect x="13" y="15.5" width="38" height="33" rx="6.5" fill="{c}"/>'
            f'<circle cx="19.5" cy="22" r="2" fill="{a}"/><circle cx="26" cy="22" r="2" fill="{a}"/>'
            f'<rect x="18" y="28" width="28" height="15" rx="2.5" fill="{a}"/>')


def desktop_panel(c, a):
    return (f'<rect x="13" y="14.5" width="38" height="35" rx="6.5" fill="{c}"/>'
            f'<rect x="18" y="41" width="28" height="4.5" rx="2.25" fill="{a}"/>')


def stacked_windows(c, a):
    return (f'<rect x="23" y="14" width="29" height="24" rx="5.5" fill="{c}" fill-opacity=".5"/>'
            f'<rect x="12" y="24" width="31" height="26" rx="5.5" fill="{c}"/>')


def drawing_tablet(c, a):
    return (f'<rect x="14.5" y="14" width="35" height="36" rx="6" fill="{c}"/>'
            f'<path d="M38.5 22.5 26 39" {ROUND} stroke="{a}" stroke-width="3.4"/>')


def bolt(c, a):
    return f'<path d="M36.5 12 18 36.500h12.500L26.5 52 46.5 27H34Z" fill="{c}" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>'


def paint_roller(c, a):
    return (f'<rect x="13.5" y="14" width="32" height="13" rx="4.5" fill="{c}"/>'
            f'<path d="M45.5 20.500h5v12.500H32v6" {ROUND} stroke="{c}" stroke-width="3.4"/>'
            f'<rect x="27.5" y="38.5" width="9" height="13" rx="2.8" fill="{c}"/>')


def padlock(c, a):
    return (f'<path d="M22 29v-7a10 10 0 0 1 20 0v7" {ROUND} stroke="{c}" stroke-width="4.2"/>'
            f'<rect x="14.5" y="28" width="35" height="24" rx="5.5" fill="{c}"/>'
            f'<circle cx="32" cy="37.5" r="3.1" fill="{a}"/><rect x="30.5" y="38.5" width="3" height="7.5" rx="1.5" fill="{a}"/>')


def info(c, a):
    return (f'<circle cx="32" cy="32" r="19" fill="{c}"/><circle cx="32" cy="22.5" r="2.8" fill="{a}"/>'
            f'<rect x="29.5" y="28.5" width="5" height="14" rx="2.5" fill="{a}"/>')


def person_frame(c, a):
    return (f'<rect x="13" y="13" width="38" height="38" rx="9" fill="{c}"/>'
            f'<circle cx="32" cy="26" r="6.2" fill="{a}"/><path d="M20.5 45.500c.8-7.5 5.5-11.5 11.5-11.500s10.7 4 11.5 11.500Z" fill="{a}"/>')


def splash_screen(c, a):
    return (f'<rect x="13" y="15.5" width="38" height="33" rx="6.5" fill="{c}"/>'
            f'<circle cx="32" cy="27" r="4.6" fill="{a}"/><rect x="21" y="37" width="22" height="3.6" rx="1.8" fill="{a}"/>')


def touch_screen(c, a):
    return (f'<rect x="15.5" y="13" width="33" height="38" rx="6" fill="{c}"/>'
            f'<circle cx="32" cy="32" r="8" fill="none" stroke="{a}" stroke-width="2.6"/><circle cx="32" cy="32" r="3" fill="{a}"/>')


def battery(c, a):
    return (f'<rect x="11.5" y="21.5" width="37" height="21" rx="5.5" fill="{c}"/><rect x="49.5" y="27.5" width="3.8" height="9" rx="1.6" fill="{c}"/>'
            f'<path d="M32 24.500l-7.5 9h5.500l-2 6.5 8-9.200h-5.500Z" fill="{a}"/>')


def shield(c, a):
    return f'<path d="M32 12.5 49.5 19v12.5c0 10-7 17.5-17.5 21-10.5-3.5-17.5-11-17.5-21V19Z" fill="{c}"/>'


def plug(c, a):
    return (f'<path d="M24 13v11M40 13v11M32 44v8" {ROUND} stroke="{c}" stroke-width="4.2"/>'
            f'<path d="M17.5 23h29v7.5a14.5 14.5 0 0 1-29 0Z" fill="{c}" stroke="{c}" stroke-width="1.6" stroke-linejoin="round"/>')


def media_frame(c, a):
    return (f'<rect x="13" y="16.5" width="38" height="31" rx="6.5" fill="{c}"/>'
            f'<path d="M27.5 24.5v15L41 32Z" fill="{a}" stroke="{a}" stroke-width="2.4" stroke-linejoin="round"/>')


def plain_gear(c, a):
    return f'<path d="{gear(32, 31.97, 19.5, 15.8, 12, 6.2)}" fill="{c}" fill-rule="evenodd"/>'


def screen_edges(c, a):
    return (f'<rect x="14.5" y="16.5" width="35" height="31" rx="5" fill="none" stroke="{c}" stroke-width="3.2"/>'
            f'<rect x="13" y="15" width="14" height="14" rx="5" fill="{c}"/>')


def swipe(c, a):
    return (f'<circle cx="19" cy="32" r="8" fill="{c}"/>'
            f'<path d="M32 32h18.5M43.5 25l7 7-7 7" {ROUND} stroke="{c}" stroke-width="4.2"/>')


# --- tray icons, in the text color like the system's beside them -----------------------------

def spotify_tray():
    """Spotify's disc, its three waves cut out of it; asked for by name, unlike most apps'."""
    disc = "M11 3a8 8 0 1 0 0 16a8 8 0 0 0 0-16Z"
    waves = ("M5.9 7.9c3.5-1 7.3-.7 10.4 1 .7.4.1 1.5-.6 1.1-2.7-1.5-6.1-1.8-9.4-.8-.8.2-1.2-1-.4-1.3Z"
             "M6.8 10.9c2.8-.8 5.8-.5 8.2.8.6.3.1 1.2-.5.9-2.1-1.1-4.8-1.4-7.4-.7-.7.2-1-.8-.3-1Z"
             "M7.6 13.6c2.1-.6 4.3-.4 6.1.6.5.3.1 1-.4.7-1.5-.8-3.5-1-5.4-.5-.6.2-.9-.6-.3-.8Z")
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 22" width="22" height="22">'
            f'<path d="{disc}{waves}" fill="{TEXT}" fill-rule="evenodd"/></svg>\n')


# --- the apps' own logos, read from the system when the theme is built ------------------

def logo_tile(path, box=40, disc=None):
    """An app's own logo (SVG, SVGZ or PNG, from the app's install), in Catppuccin colors, on
    a Mocha tile, where its colors stand out like in the dock; a round logo (disc, from
    ROUND_LOGOS) loses its disc, whose color becomes the tile. Built on the user's machine:
    the logos are not redistributed here."""
    import base64
    import gzip
    import io
    path = Path(path)
    if path.suffix in (".svg", ".svgz"):
        raw = gzip.decompress(path.read_bytes()) if path.suffix == ".svgz" else path.read_bytes()
        svg = catppuccin.recolor_svg(raw.decode("utf-8", "ignore"), everything=True)
        root = re.search(r"<svg\b[^>]*>", svg).group(0)
        viewbox = re.search(r'viewBox="([^"]+)"', root)
        if viewbox:
            x, y, w, h = (float(v) for v in re.split(r"[ ,]+", viewbox.group(1).strip()))
        else:
            x = y = 0
            w, h = (float(re.sub(r"[^0-9.]", "", re.search(r'%s="([^"]+)"' % k, root).group(1))) for k in ("width", "height"))
        inner = svg[svg.index(root) + len(root):svg.rindex("</svg>")]
        if disc:
            box = disc["box"]
            for shape in disc["shapes"]:
                inner, found = re.subn(shape, "", inner)
                if not found:  # the logo changed: our drawing stays
                    raise ValueError(f"no disc in {path}")
        # what editors leave in (Inkscape's sodipodi:, inkscape:, the metadata) has no
        # namespace once inside ours: the file would not be valid, and Plasma shows nothing
        inner = re.sub(r"<metadata\b.*?</metadata>", "", inner, flags=re.S)
        inner = re.sub(r"<(\w+):[\w-]+\b[^>]*/>", "", inner)
        inner = re.sub(r"<(\w+):([\w-]+)\b[^>]*>.*?</\1:\2>", "", inner, flags=re.S)
        inner = re.sub(r'\s(?!xlink:)\w+:[\w-]+="[^"]*"', "", inner)
        # its ids beside ours
        inner = re.sub(r'id="([^"]+)"', r'id="logo-\1"', inner)
        inner = re.sub(r"url\(#([^)]+)\)", r"url(#logo-\1)", inner)
        inner = re.sub(r'href="#([^"]+)"', r'href="#logo-\1"', inner)
        scale = box / max(w, h)
        dx, dy = 32 - (x + w / 2) * scale, 32 - (y + h / 2) * scale
        body = f'<g transform="translate({dx:.3f} {dy:.3f}) scale({scale:.5f})">{inner}</g>'
    else:
        from PIL import Image
        image = Image.open(path).convert("RGBA")
        image.thumbnail((256, 256))
        pixels, cache = image.load(), {}
        for py in range(image.height):
            for px in range(image.width):
                r, g, b, a = pixels[px, py]
                if a:
                    key = (r, g, b)
                    if key not in cache:
                        cache[key] = catppuccin.rgb(catppuccin.recolor("#%02x%02x%02x" % key, everything=True))
                    pixels[px, py] = tuple(round(v * 255) for v in cache[key]) + (a,)
        out = io.BytesIO()
        image.save(out, "PNG")
        w, h = image.size
        scale = box / max(w, h)
        data = base64.b64encode(out.getvalue()).decode()
        body = (f'<image x="{32 - w * scale / 2:.3f}" y="{32 - h * scale / 2:.3f}" width="{w * scale:.3f}" '
                f'height="{h * scale:.3f}" xlink:href="data:image/png;base64,{data}"/>')
    if disc:
        svg = icon(vertical("tile", *disc["tile"]), f'<rect {TILE} fill="url(#tile)"/>{rim(disc["rim"])}{body}')
    else:
        svg = icon(mocha_tile(), f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}{body}')
    from xml.dom import minidom
    minidom.parseString(svg)  # raises on a logo we could not clean: our drawing stays
    return svg


# our icon -> the names its app's logo may have, in hicolor or Breeze
LOGOS = {
    "assistant.svg": ["assistant", "qtassistant"], "designer.svg": ["designer", "qtdesigner"],
    "linguist.svg": ["linguist", "qtlinguistic"], "qdbusviewer.svg": ["qdbusviewer"],
    "btrfs-assistant.svg": ["btrfs-assistant"], "org.cachyos.KernelManager.svg": ["org.cachyos.KernelManager"],
    "org.cachyos.scx-manager.svg": ["org.cachyos.scx-manager"],
    "gwenview.svg": ["gwenview", "org.kde.gwenview"], "kate.svg": ["kate", "org.kde.kate"],
    "kdeconnect.svg": ["kdeconnect", "org.kde.kdeconnect"],
    "kwalletmanager.svg": ["kwalletmanager", "kwalletmanager2"], "gufw.svg": ["gufw"],
    "multimedia-volume-control.svg": ["org.pulseaudio.pavucontrol", "pavucontrol"],
    "LimineSnapperSync.svg": ["LimineSnapperSync"],
    "io.github.Faugus.faugus-launcher.svg": ["io.github.Faugus.faugus-launcher", "faugus-launcher"],
    "micro.svg": ["micro"],
}


# the logos that are a symbol on a disc: the shapes of the disc, the tile that replaces it, and
# how large the logo's canvas is drawn (the symbol then takes the room the disc left)
ROUND_LOGOS = {
    "kate.svg": {"shapes": [r'<circle\b[^>]*url\(#m\)[^>]*/>', r'<ellipse\b[^>]*url\(#l\)[^>]*/>',
                            r'<path\b[^>]*url\(#b\)[^>]*/>'],
                 "tile": (MOCHA["blue"], LATTE["blue"]), "rim": .25, "box": 56},
    "io.github.Faugus.faugus-launcher.svg": {"shapes": [r'<circle\b[^>]*\br="435"[^>]*/>'],
                                             "tile": (PAPER, PAPER_SHADE), "rim": 0, "box": 48},
    "micro.svg": {"shapes": [r'<path\b[^>]*\bid="path3"[^>]*/>'],
                  "tile": (LATTE["lavender"], LATTE["blue"]), "rim": .25, "box": 68},
}


def find_logo(names):
    """The app's own icon: a vector one first, else the largest picture."""
    for name in names:
        for folder in ("/usr/share/icons/hicolor/scalable/apps", "/usr/share/icons/breeze/apps/48"):
            for ext in (".svg", ".svgz"):
                if Path(folder, name + ext).is_file():
                    return Path(folder, name + ext)
    pictures = [p for name in names for p in Path("/usr/share/icons/hicolor").glob(f"*/apps/{name}.png")]
    return max(pictures, key=lambda p: p.stat().st_size, default=None)


def kde(*names):
    """An app's names: its own, and KDE's org.kde ones."""
    return [n for name in names for n in (name, f"org.kde.{name}")]


DESIGNS = {
    "terminal.svg": terminal,
    # the system's main app: the strongest tile, teal; Adwair's is a bare folder, like those it shows
    # the folders it shows, teal, on the light Latte tile
    "system-file-manager.svg": (lambda: on_latte(folder),
                                ["dolphin", "file-manager", "org.gnome.Nautilus", "nautilus", "org.gnome.Files"]),
    "preferences-system.svg": settings,
    "libreoffice-writer.svg": lambda: page(writer, "blue"),
    "libreoffice-calc.svg": lambda: page(calc, "green"),
    "libreoffice-impress.svg": lambda: page(impress, "peach"),
    "libreoffice-draw.svg": lambda: page(draw, "yellow"),
    "libreoffice-base.svg": lambda: page(base, "mauve"),
    "libreoffice-math.svg": lambda: page(math_, "red"),
}


# name: design, or (design, other names linked to it)
DESIGNS.update({
    "accessories-calculator.svg": (lambda: on_color(calculator, "peach"),
                                   kde("kcalc") + ["org.gnome.Calculator", "galculator"]),
    "ark.svg": (lambda: on_color(archive, "yellow"),
                ["org.kde.ark", "file-roller", "org.gnome.FileRoller", "xarchiver", "engrampa"]),
    "assistant.svg": (lambda: on_color(qt_badge(QT_A), "green"), ["qtassistant", "assistant-qt6", "assistant6"]),
    "designer.svg": (lambda: on_color(qt_badge(QT_D), "green"), ["qtdesigner", "designer-qt6", "designer6"]),
    "linguist.svg": (lambda: on_color(qt_badge(QT_L), "green"), ["qtlinguistic", "linguist-qt6", "linguist6"]),
    "qdbusviewer.svg": (lambda: on_color(qt_badge(QT_DV), "green"), ["qtdbusviewer", "qdbusviewer-qt6", "qdbusviewer6"]),
    "btrfs-assistant.svg": lambda: on_color(btrfs, "peach"),
    "org.cachyos.hello.svg": (cachyos_hello, ["cachyos-hello"]),
    "org.cachyos.KernelManager.svg": (lambda: on_mocha(kernel), ["cachyos-kernel-manager"]),
    "org.cachyos.scx-manager.svg": (lambda: on_mocha(scx_gear), ["scx-manager"]),
    "cachy-update-blue.svg": (lambda: on_mocha(refresh, "teal"), ["cachy-update", "arch-update"]),
    "cachyos-pi.svg": (lambda: on_mocha(package, "teal"), ["cachyos-package-installer"]),
    "printer.svg": (lambda: on_color(printer, "lavender"),
                    ["cups", "system-config-printer", "preferences-devices-printer", "printer-settings"]),
    "elisa.svg": (elisa, kde("elisa")[1:]),
    "haruna.svg": (haruna, kde("haruna")[1:]),
    "qv4l2.svg": (lambda: on_color(webcam, "sky"), ["qvidcap", "kamoso", "org.kde.kamoso", "cheese", "org.gnome.Cheese"]),
    "gwenview.svg": (lambda: on_color(lens, "pink"), kde("gwenview")[1:]),
    "filelight.svg": (lambda: on_color(rings, "blue"), kde("filelight")[1:] + ["baobab", "org.gnome.baobab"]),
    "hwinfo.svg": (lambda: on_color(magnifier, "lavender"), ["hwloc", "hardinfo", "hardinfo2"]),
    "kate.svg": (lambda: on_color(bird, "blue"), kde("kate")[1:]),
    "kwrite.svg": (lambda: page(pencil_on_lines, "sky"), kde("kwrite")[1:]),
    "kdeconnect.svg": (lambda: on_color(kde_phone, "sky"), kde("kdeconnect")[1:] + ["kdeconnect-app"]),
    "klassy-settings.svg": lambda: on_mocha(traffic_window),
    "preferences-desktop-theme-windowdecorations.svg": lambda: free_form(traffic_window),
    "preferences-system-windows.svg": (lambda: free_form(window_gear), ["preferences-system-windows-actions"]),
    "preferences-devices-cpu.svg": lambda: free_form(chip),
    # Adwair links it here too, and the apps' folder comes first
    "video-display.svg": lambda: free_form(display),
    "kmenuedit.svg": (lambda: paper_on_mocha(menu_list_pencil), kde("kmenuedit")[1:]),
    "kvantum.svg": (kvantum_logo, ["kvantummanager"]),
    "kwalletmanager.svg": (lambda: on_color(wallet, "peach"), ["kwalletmanager2", "org.kde.kwalletmanager5",
                                                            "org.kde.kwalletmanager", "kwallet"]),
    "okular.svg": (okular, kde("okular")[1:]),
    "qbittorrent.svg": lambda: on_color(qb, "blue"),
    "multimedia-volume-control.svg": (lambda: on_color(knob, "lavender"),
                                      ["org.pulseaudio.pavucontrol", "pavucontrol", "pavucontrol-qt"]),
    "partitionmanager.svg": (lambda: on_mocha(partitions), kde("partitionmanager")[1:] + ["gparted", "gnome-disks",
                                                                                     "org.gnome.DiskUtility"]),
    "preferences-desktop-emoticons.svg": (lambda: on_color(smiley, "yellow"), ["org.kde.plasma.emojier"]),
    "spectacle.svg": (lambda: on_color(viewfinder, "sky"), kde("spectacle")[1:] + ["accessories-screenshot",
                                                                                  "org.gnome.Screenshot"]),
    "utilities-system-monitor.svg": (lambda: on_dark(pulse),
                                     kde("plasma-systemmonitor") + ["ksysguard", "gnome-system-monitor",
                                                                    "org.gnome.SystemMonitor"]),
    "gufw.svg": (lambda: on_color(striped_shield, "blue"), ["gufw_menu"]),
    "LimineSnapperSync.svg": (lambda: on_mocha(circuit), ["limine-snapper-restore", "limine-snapper-sync"]),
    "micro.svg": lambda: on_color(mu, "lavender"),
    "io.github.Faugus.faugus-launcher.svg": (lambda: on_color(penguin, "mauve"), ["faugus-launcher"]),
    "spotify-linux-32.svg": (spotify_tray, [f"spotify-linux-{size}" for size in (16, 22, 24, 48, 64, 128, 256, 512)]),
    # its .desktop file names a picture, not an icon: install.sh adds a local copy naming this one
    "nuvio.svg": lambda: on_color(media_library, "pink"),
    "zapfast.svg": lambda: on_color(zap_bubble, "green"),
})


# --- places: the Desktop folder, with a symbol like the others, and the trash, in teal ----------

FOLDER_BACK, FOLDER_FRONT = "#80cec1", "#94e2d5"  # the mocha-teal folders' colors


def desktop_folder():
    """The folder the others are made from, with a screen on it."""
    svg = (HERE.parent / "generator/colors/mocha-teal/folder-documents.svg").read_text()
    screen = (f'<g fill="none" stroke="{SURFACE0}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
              '<rect x="22.8" y="27.8" width="18.4" height="12.4" rx="2.4"/><path d="M32 40.2v4.4M27.4 45.6h9.2"/></g>')
    return re.sub(r'<g transform="translate\(22[^>]*>.*?</g>', screen, svg, flags=re.S)


# the folders' soft shadow (generator/colors.py): stacked copies of the outline
SHADOW_LAYERS = ((5.0, 0.06), (3.6, 0.09), (2.4, 0.12), (1.2, 0.16))
TRASH_OUTLINE = ('<path d="M14.5 20h35l-2.7 33.1a5 5 0 0 1-5 4.6H22.2a5 5 0 0 1-5-4.6Z" {style}/>'
                 '<rect x="11.5" y="15.5" width="41" height="7" rx="3.2" {style}/>')


def soft_shadow(outline):
    layers = "".join(outline.replace("{style}", f'fill-opacity="{o}" stroke-opacity="{o}" stroke-width="{w}"')
                     for w, o in SHADOW_LAYERS)
    return f'<g fill="#11111b" stroke="#11111b" stroke-linejoin="round" transform="translate(0 1)">{layers}</g>'


def trash(full=False):
    """A can in the folders' colors; full, sheets of paper stick out from under its rim."""
    ribs = "".join(f'<path d="M{x} 29l{d} 18" stroke="{SURFACE0}" stroke-opacity=".75" stroke-width="2.6" '
                   'stroke-linecap="round"/>' for x, d in ((24.6, .9), (32, 0), (39.4, -.9)))
    can = ('<path d="M14.5 20h35l-2.7 33.1a5 5 0 0 1-5 4.6H22.2a5 5 0 0 1-5-4.6Z" fill="url(#can)"/>'
           f'<rect x="11.5" y="15.5" width="41" height="7" rx="3.2" fill="{FOLDER_BACK}"/>')
    paper = ""
    if full:
        paper = (f'<rect x="34" y="4.5" width="13" height="17" rx="2" fill="{PAPER_SHADE}" transform="rotate(14 40.5 13)"/>'
                 f'<rect x="28" y="2.5" width="9" height="15" rx="2" fill="{MOCHA["peach"]}" transform="rotate(3 32.5 10)"/>'
                 f'<rect x="17.5" y="4.5" width="14" height="17" rx="2" fill="{PAPER}" transform="rotate(-12 24.5 13)"/>')
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="128" height="128">'
            f'<defs>{vertical("can", FOLDER_FRONT, FOLDER_BACK, 20, 57.7)}</defs>{paper}{soft_shadow(TRASH_OUTLINE)}{can}{ribs}</svg>\n')


PLACES = {
    "user-desktop.svg": (desktop_folder, ["folder-desktop"]),
    "user-trash.svg": (trash, ["user-trash-dark"]),
    "user-trash-full.svg": (lambda: trash(full=True), ["user-trash-full-dark"]),
}


DRIVE_NAMES = ["drive-harddisk-ieee1394", "drive-harddisk-root", "drive-harddisk-scsi", "drive-harddisk-solidstate",
               "drive-harddisk-system", "drive-harddisk-usb", "drive-partition", "harddrive"]
# the hardware in the Info Center and in the Places panel, among the devices
DEVICES = {
    "cpu.svg": lambda: free_form(chip),
    "video-display.svg": lambda: free_form(display),
    "audio-card.svg": lambda: free_form(sound_card),
    "computer.svg": (lambda: free_form(display), ["gnome-dev-computer", "computer-desktop"]),
    "drive-harddisk.svg": (lambda: free_form(hard_drive), DRIVE_NAMES),
    "drive-removable-media.svg": (lambda: free_form(usb_stick), ["drive-removable-media-usb", "drive-removable-media-usb-pendrive",
                                                                "drive-removable-usb", "media-removable"]),
    "media-optical.svg": (lambda: free_form(disc), ["media-optical-audio", "media-optical-blu-ray", "media-optical-cd",
                                                   "media-optical-cd-r", "media-optical-dvd", "media-cdrom"]),
    "phone.svg": (lambda: free_form(phone), ["smartphone", "stock_cell-phone"]),
    "preferences-desktop-keyboard.svg": lambda: free_form(keyboard),
    "preferences-desktop-mouse.svg": lambda: free_form(mouse),
}


# System Settings' pages: the system's teal, like its tools
SETTINGS_PAGES = {
    "preferences-desktop-theme.svg": (lambda: free_form(palette_brush), ["theme-config"]),
    "preferences-desktop-wallpaper.svg": lambda: free_form(landscape),
    "preferences-desktop-font.svg": (lambda: free_form(letter), ["fonts"]),
    "preferences-desktop-display.svg": lambda: free_form(display),
    "preferences-desktop-sound.svg": lambda: free_form(sound_card),
    "preferences-system-network.svg": (lambda: free_form(network), ["network-workgroup"]),
    "preferences-desktop-color.svg": (lambda: free_form(color_circles), ["preferences-color"]),
    "preferences-desktop-locale.svg": lambda: free_form(globe),
    "preferences-system-users.svg": (lambda: free_form(people), ["cs-user"]),
    "preferences-desktop.svg": lambda: free_form(sliders),
    "tools-check-spelling.svg": lambda: free_form(spelling),
    "lighttable.svg": lambda: free_form(day_night),
    "system-run.svg": lambda: free_form(autostart),
    "redshift-status-on.svg": lambda: free_form(moon),
    "network-wireless-hotspot.svg": lambda: free_form(hotspot),
    "preferences-web-browser-shortcuts.svg": lambda: free_form(magnifier),
    "preferences-desktop-keyboard-shortcut.svg": lambda: free_form(key_combo),
    "network-wired-symbolic.svg": lambda: free_form(ethernet),
    "network-wireless-symbolic.svg": lambda: free_form(wifi),
    "emblem-music-symbolic.svg": lambda: free_form(music_note),
    "preferences-desktop-accessibility.svg": lambda: free_form(accessibility),
    "preferences-desktop-activities.svg": lambda: free_form(activities),
    "preferences-desktop-animations.svg": lambda: free_form(animations),
    "preferences-desktop-default-applications.svg": lambda: free_form(app_grid),
    "preferences-desktop-filetype-association.svg": lambda: free_form(page_check),
    "preferences-system-bluetooth.svg": lambda: free_form(bluetooth),
    "preferences-desktop-virtual.svg": lambda: free_form(desktops),
    "preferences-online-accounts.svg": lambda: free_form(cloud),
    "krunner.svg": lambda: free_form(search_bar),
    "preferences-desktop-gaming.svg": lambda: free_form(gamepad),
    "preferences-system-time.svg": lambda: free_form(clock),
    "preferences-desktop-effects.svg": lambda: free_form(sparkles),
    "preferences-desktop-font-installer.svg": lambda: free_form(letter_down),
    "preferences-desktop-icons.svg": lambda: free_form(icon_shapes),
    "preferences-security-firewall.svg": lambda: free_form(shield_check),
    "preferences-desktop-touchpad.svg": lambda: free_form(touchpad),
    "preferences-desktop-cursors.svg": lambda: free_form(arrow_cursor),
    "xorg.svg": lambda: free_form(x_mark),
    "preferences-system-network-connection.svg": lambda: free_form(two_arrows),
    "preferences-desktop-baloo.svg": lambda: free_form(page_search),
    "plasma-search.svg": lambda: free_form(magnifier),
    "preferences-desktop-feedback.svg": lambda: free_form(bubble),
    "preferences-system-network-proxy.svg": lambda: free_form(relay),
    "preferences-system-session-services.svg": lambda: free_form(two_gears),
    "preferences-desktop-theme-applications.svg": lambda: free_form(app_window),
    "preferences-desktop-plasma-theme.svg": lambda: free_form(desktop_panel),
    "preferences-system-tabbox.svg": lambda: free_form(stacked_windows),
    "preferences-desktop-tablet.svg": lambda: free_form(drawing_tablet),
    "preferences-desktop-thunderbolt.svg": lambda: free_form(bolt),
    "preferences-desktop-theme-global.svg": lambda: free_form(paint_roller),
    "preferences-desktop-user-password.svg": lambda: free_form(padlock),
    "ktip.svg": lambda: free_form(info),
    "preferences-system-login.svg": lambda: free_form(person_frame),
    "preferences-system-splash.svg": lambda: free_form(splash_screen),
    "preferences-desktop-touchscreen.svg": lambda: free_form(touch_screen),
    "preferences-system-power-management.svg": lambda: free_form(battery),
}
DESIGNS.update(SETTINGS_PAGES)
# Pages whose icon names the tray, the logout and the lock screens use too: their tiles live in a
# theme of their own, Teal-Settings, that only System Settings uses (systemsettingsrc).
SETTINGS_ONLY = {
    "input-keyboard-virtual.svg": lambda: free_form(virtual_keyboard),
    "preferences-desktop-display-randr.svg": lambda: free_form(two_screens),
    "preferences-desktop-notification-bell.svg": lambda: free_form(bell),
    "system-log-out.svg": lambda: free_form(leave),
    # the sidebar's categories, and the pages named like an app or the launcher's menu
    "applications-all.svg": lambda: free_form(app_grid),
    "kwalletmanager.svg": lambda: free_form(wallet),
    "preferences-desktop-gestures-screenedges.svg": lambda: free_form(screen_edges),
    "preferences-desktop-gestures-touch.svg": lambda: free_form(swipe),
    "preferences-desktop-multimedia.svg": lambda: free_form(media_frame),
    "preferences-desktop-peripherals.svg": lambda: free_form(plug),
    "preferences-desktop-search.svg": lambda: free_form(magnifier),
    "preferences-security.svg": lambda: free_form(shield),
    "preferences-system.svg": lambda: free_form(plain_gear),
    "preferences-system-disks.svg": lambda: free_form(hard_drive),
}
DESIGNS["softwarecenter.svg"] = (lambda: on_mocha(shopping_bag), ["plasmadiscover", "software-properties"])


def write_all(designs, out):
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir()
    for name, design in designs.items():
        design, aliases = design if isinstance(design, tuple) else (design, [])
        (out / name).write_text(design())
        for alias in aliases:
            (out / f"{alias}.svg").symlink_to(name)


def main():
    SHADOW.write_text(shadow())
    write_all(DESIGNS, HERE / "apps")
    write_all(PLACES, HERE / "places")
    write_all(DEVICES, HERE / "devices")
    write_all(SETTINGS_ONLY, HERE / "settings")
    print(f"{len(DESIGNS)} icons in {HERE / 'apps'}, {len(PLACES)} in {HERE / 'places'}")


if __name__ == "__main__":
    main()
