#!/usr/bin/env python3
"""What Teal's own icons are drawn with: the palette, the tiles and the planes, and every shape.

They follow Teal's grid: a 56 px tile with 13 px corners on a 64 px canvas, lit
from above, its soft shadow below. The shadow is the base icons' own picture (Plasma's QtSvg
has no blur filter), taken from one of its icons. Every color is a Catppuccin one.

The rule that keeps them together: everything is an object built in planes. An app has a tile
of its own color with a paper object, a tool of the system the teal tile (some start on the
Mocha tile, which logos.tint_folder colors), and the system's pages and hardware are objects
without a tile: the
icons stay light and the accent gives the theme its character (see ../RULES.md). Each symbol
is drawn on the 64 px grid, within about 16 to 48.

draw.py says which icon gets which shape; logos.py puts an app's own logo on a tile.
"""
import math
import sys
import re
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

TILE = 'x="4" y="3.969" width="56.002" height="56.002" rx="13.002"'


# kept beside the drawings, for the logos made on each computer, where the base's sources are not
SHADOW = HERE / "shadow.xml"


def shadow():
    """The base's tile shadow, the first picture of its icons."""
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
    return diagonal("tile", SURFACE0, BASE)


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


# --- symbols: glyph(c, a) draws with c, details in a (the tile's color shows through) -----

ROUND = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'


def enlarged(glyph):
    """A symbol still drawn within 16 to 48 (mostly an app's own mark), brought to the free shapes' grid."""
    return lambda p: at(-23.52, -23.52, 1.735, glyph(p.main, p.deep))


def symbol(glyph, scale=.68):
    """An object on a tile: its soft shadow, then its planes."""
    t = round(32 * (1 - scale), 2)
    return at(t, t, scale, f'<g opacity=".13" transform="translate(0 3.4)">{glyph(Silhouette)}</g>'
                           f'<g opacity=".2" transform="translate(0 1.6)">{glyph(Silhouette)}</g>{glyph(Planes)}')


def paper_planes(family):
    """The planes of an object on a colored tile: paper, its tint, and the tile's color."""
    hue, strong, near = MOCHA[family], LATTE[family], LATTE[NEIGHBOR[family]]
    colors = (("main", PAPER, mix(hue, PAPER, .72)), ("mid", mix(hue, PAPER, .55), mix(hue, PAPER, .3)),
              ("deep", mix(strong, near, .4), mix(strong, SURFACE0, .3)), ("pale", strong, mix(strong, near, .5)),
              ("ink", mix(strong, CRUST, .62), mix(near, CRUST, .72)))
    return "".join(diagonal(*c) for c in colors)


def colored_tile(family):
    hue = MOCHA[family]
    return diagonal("tile", mix(hue, LATTE[family], .12), mix(hue, LATTE[NEIGHBOR[family]], .62))


def on_color(glyph, family):
    """An app: an object of paper on a tile of its color."""
    return icon(colored_tile(family) + paper_planes(family),
                f'<rect {TILE} fill="url(#tile)"/>{rim(.25)}' + symbol(glyph))


def on_mocha(glyph, family=None):
    """An object in silver, or in a family's color, on the Mocha tile; the tile then takes the
    color of its app (logos.tint_folder): teal for the system's tools, black for the terminal."""
    return icon(mocha_tile() + planes(family or "silver"),
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}' + symbol(glyph))


def on_latte(glyph, family="teal"):
    """An object in its color on the light Latte tile."""
    return icon(diagonal("tile", PAPER, PAPER_SHADE) + planes(family), f'<rect {TILE} fill="url(#tile)"/>' + symbol(glyph))


def mix(a, b, t):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


# Each page's or device's own color: the hue of Papirus's icon of the same name, in its closest
# Catppuccin color; silver where it was asked for. A name missing here takes its family below.
PAGE_COLORS = {
    "applications-all": "sky",
    "audio-card": "green",
    "audio-headphones": "mauve",
    "audio-headset": "mauve",
    "audio-speakers": "sky",
    "auth-sim": "yellow",
    "battery": "green",
    "bluetooth": "blue",
    "computer-laptop": "sky",
    "computer": "sky",
    "cpu": "green",
    "drive-harddisk": "lavender",
    "drive-removable-media": "peach",
    "input-gamepad": "yellow",
    "input-mouse": "silver",
    "monitor": "sky",
    "processor": "green",
    "soundcard": "green",
    "media-flash": "yellow",
    "memory": "green",
    "tablet": "blue",
    "video-television": "mauve",
    "emblem-music-symbolic": "silver",
    "input-keyboard-virtual": "lavender",
    "krunner": "yellow",
    "ktip": "blue",
    "kwalletmanager": "silver",
    "lighttable": "yellow",
    "media-optical": "yellow",
    "network-wired-symbolic": "sky",
    "network-wireless-hotspot": "sky",
    "network-wireless-symbolic": "sky",
    "phone": "blue",
    "plasma-search": "silver",
    "preferences-desktop": "silver",
    "preferences-desktop-accessibility": "lavender",
    "preferences-desktop-activities": "blue",
    "preferences-desktop-animations": "silver",
    "preferences-desktop-baloo": "blue",
    "preferences-desktop-color": "pink",
    "preferences-desktop-cursors": "silver",
    "preferences-desktop-default-applications": "green",
    "preferences-desktop-display": "sky",
    "preferences-desktop-display-randr": "sky",
    "preferences-desktop-effects": "yellow",
    "preferences-desktop-feedback": "green",
    "preferences-desktop-filetype-association": "blue",
    "preferences-desktop-font": "silver",
    "preferences-desktop-font-installer": "silver",
    "preferences-desktop-gaming": "yellow",
    "preferences-desktop-gestures-screenedges": "blue",
    "preferences-desktop-gestures-touch": "blue",
    "preferences-desktop-icons": "blue",
    "preferences-desktop-keyboard": "lavender",
    "preferences-desktop-keyboard-shortcut": "lavender",
    "preferences-desktop-locale": "blue",
    "preferences-desktop-mouse": "silver",
    "preferences-desktop-multimedia": "mauve",
    "preferences-desktop-notification-bell": "yellow",
    "preferences-desktop-peripherals": "peach",
    "preferences-desktop-plasma-theme": "sky",
    "preferences-desktop-search": "silver",
    "preferences-desktop-sound": "silver",
    "preferences-desktop-tablet": "green",
    "preferences-desktop-theme": "blue",
    "preferences-desktop-theme-applications": "mauve",
    "preferences-desktop-theme-global": "blue",
    "preferences-desktop-theme-windowdecorations": "lavender",
    "preferences-desktop-thunderbolt": "blue",
    "preferences-desktop-touchpad": "mauve",
    "preferences-desktop-touchscreen": "blue",
    "preferences-desktop-user": "peach",
    "preferences-desktop-user-password": "yellow",
    "preferences-desktop-virtual": "blue",
    "preferences-desktop-wallpaper": "sky",
    "preferences-devices-cpu": "green",
    "preferences-online-accounts": "sky",
    "preferences-security": "green",
    "preferences-security-firewall": "red",
    "preferences-system": "silver",
    "preferences-system-bluetooth": "blue",
    "preferences-system-disks": "lavender",
    "preferences-system-login": "green",
    "preferences-system-network": "sky",
    "preferences-system-network-connection": "mauve",
    "preferences-system-network-proxy": "lavender",
    "preferences-system-network-sharing": "sky",
    "preferences-system-privacy": "green",
    "preferences-system-power-management": "yellow",
    "preferences-system-session-services": "sky",
    "preferences-system-splash": "mauve",
    "preferences-system-tabbox": "blue",
    "preferences-system-time": "yellow",
    "preferences-system-users": "blue",
    "preferences-web-browser-shortcuts": "lavender",
    "redshift-status-on": "peach",
    "system-log-out": "green",
    "system-run": "silver",
    "tools-check-spelling": "blue",
    "video-display": "sky",
    "xorg": "silver",
}
_page = ""  # the icon being written (write_all)


# What each color of a free shape means; a symbol missing here stops the build
FREE_FAMILIES = {glyph: family for family, glyphs in {
    "silver": "plain_gear two_gears info sliders autostart x_mark letter letter_down animations wallet sound_card "
              "music_note magnifier search_bar page_search printer scanner",  # the system, text, motion, sound, search, paper
    "mauve": "palette_brush app_window desktop_panel paint_roller icon_shapes color_circles "
             "splash_screen landscape sparkles",  # the look
    "pink": "media_frame media_player",  # media
    "lavender": "keyboard mouse touchpad arrow_cursor key_combo drawing_tablet touch_screen swipe screen_edges "
                "virtual_keyboard gamepad hard_drive usb_stick disc phone plug chip display two_screens "
                "headphones headset speaker laptop tablet television optical_drive drives locked_drive "
                "memory sd_card sim_card",  # the hardware
    "blue": "app_grid window_gear traffic_window desktops stacked_windows activities "
            "spelling page_check bubble bluetooth people",  # windows, apps, documents; Bluetooth; users
    "sky": "network wifi hotspot ethernet two_arrows relay cloud globe router server share_nodes "
           "network_card",  # connections and the world
    "yellow": "moon day_night bolt battery clock",  # light, energy and time
    "green": "shield shield_check padlock camera video_camera webcam",  # security; what watches (the camera sign's green)
    "peach": "person_frame person accessibility leave bell microphone",  # your session, what calls for you, what listens
}.items() for glyph in glyphs.split()}


WARM = {"yellow", "peach"}  # toward gray, these turn to brown
# Each hue leans toward its neighbor: two colors, not one color lit from above.
NEIGHBOR = {"sky": "blue", "blue": "lavender", "lavender": "mauve", "mauve": "pink", "pink": "mauve", "teal": "green",
            "red": "maroon", "peach": "peach", "yellow": "peach", "green": "teal"}


def diagonal(id, start, end):
    return (f'<linearGradient id="{id}" x1="10" y1="4" x2="54" y2="60" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{start}"/><stop offset="1" stop-color="{end}"/></linearGradient>')


def planes(family):
    """The planes a free shape is built from, lightest last: ink, deep, mid, main, pale."""
    if family == "silver":
        colors = (("ink", SURFACE1, SURFACE0), ("deep", "#7f849c", SURFACE2), ("mid", "#a6adc8", "#7f849c"),
                  ("main", SILVER_TOP, "#a6adc8"), ("pale", PAPER, SILVER_TOP))
    else:
        hue, near = MOCHA[family], LATTE[NEIGHBOR[family]]
        colors = (("ink", mix(LATTE[family], SURFACE0, .72), mix(near, CRUST, .72)),
                  ("deep", mix(hue, LATTE[family], .62), mix(near, SURFACE0, .16 if family in WARM else .38)),
                  ("mid", mix(hue, LATTE[family], .3), mix(hue, near, .62)),
                  ("main", mix(hue, PAPER, .08), mix(hue, near, .35)),
                  ("pale", mix(hue, PAPER, .78), mix(hue, PAPER, .5)))
    return "".join(diagonal(*c) for c in colors)


class Planes:
    """What a free shape paints with: its planes and, for a thing's real colors, Mocha's."""
    ink, deep, mid, main, pale = "url(#ink)", "url(#deep)", "url(#mid)", "url(#main)", "url(#pale)"
    metal = "#bac2de"  # Mocha's subtext 1

    @staticmethod
    def real(name):
        return MOCHA[name]


class Silhouette:
    """The same glyph in one color, for its shadow."""
    ink = deep = mid = main = pale = metal = CRUST

    @staticmethod
    def real(name):
        return CRUST


class Symbol:
    """The same glyph in the text color, for Plasma's monochrome icons."""
    ink = deep = mid = main = pale = metal = "currentColor"

    @staticmethod
    def real(name):
        return "currentColor"


def symbolic(glyph):
    """A free shape as a symbol, for Plasma's popups (in Teal-Shell): one color, the text's,
    which Plasma gives through the color scheme's class. Its planes merge, as in Papirus's."""
    body = re.sub(r"<(\w+)(?=[^>]*currentColor)", r'<\1 class="ColorScheme-Text"', glyph(Symbol))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="16" height="16">'
            '<defs><style id="current-color-scheme" type="text/css">'
            f'.ColorScheme-Text {{ color:{TEXT}; }}</style></defs>{body}</svg>\n')


def free_form(glyph):
    """The system's pages and hardware: an object without a tile, filling the grid, built in
    planes of its color (PAGE_COLORS, FREE_FAMILIES). A shadow one pixel below keeps it apart
    from a selection or a light background."""
    family = PAGE_COLORS.get(_page) or FREE_FAMILIES[glyph.__name__]
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
            f'<defs>{planes(family)}</defs>'
            f'<g opacity=".28" transform="translate(0 1)">{glyph(Silhouette)}</g>{glyph(Planes)}</svg>\n')


@enlarged
def zap_bubble(c, a):
    """ZapFast: the speech bubble of its logo, its tail down on the left, and a zap in it."""
    return (f'<path d="M25 45.8A16.65 16.65 0 1 0 17.8 38.6L15 48.8Z" fill="{c}" stroke="{c}" '
            f'stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M35.8 20.5 25.6 33h6.2l-2.6 9.5L39.8 29.5h-6.2Z" fill="{a}" stroke="{a}" '
            f'stroke-width="1" stroke-linejoin="round"/>')


@enlarged
def mu(c, a):
    """Micro, where it is not installed: its letter."""
    return f'<path d="M24 20v26M24 34c0 5 3 8 7.5 8s7.5-3 7.5-8V20M39 36c0 4 1.5 6 4.5 6" {ROUND} stroke="{c}" stroke-width="4.4"/>'


def haruna():
    """Haruna's logo, a film strip shaped like an H, on its dark tile (the base's version
    clips it with CSS, which Plasma ignores)."""
    holes = "".join(f"M{x} {y}h4v4h-4Z" for x in (18.5, 41.5) for y in (19, 30, 41))
    h = f"M16 15h10v12.5h12V15h10v34H38V36.5H26V49H16Z{holes}"
    return icon(mocha_tile(),
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                f'<path d="{h}" transform="translate(0 .9)" fill="{CRUST}" fill-opacity=".4" fill-rule="evenodd"/>'
                f'<path d="{h}" fill="{PAPER}" fill-rule="evenodd"/>')


def cachyos_hello():
    """The base's CachyOS logo, in Catppuccin colors, on the Mocha tile, which becomes the
    system's teal (logos.tint_folder)."""
    svg = catppuccin.recolor_svg((SRC / "org.cachyos.hello.svg").read_text(), everything=True)
    tile = re.search(r'<linearGradient id="d".*?</linearGradient>', svg).group(0)
    svg = svg.replace(tile, vertical("d", SURFACE0, BASE))
    # the light on its top edge, after its tile, like the other Mocha tiles
    at = svg.index(">", svg.index('fill="url(#d)"')) + 1
    return svg[:at] + rim(MOCHA_RIM) + svg[at:]


# --- the apps' own logos, redrawn in the island's grammar --------------------------------

def qt_badge(letters):
    """Qt's tools: Qt's badge, its corners cut, with the tool's letter."""
    def glyph(c, a):
        return (f'<path d="M23 16H48V41L41 48H16V23Z" fill="{c}"/>'
                f'<path d="{letters}" {ROUND} stroke="{a}" stroke-width="3.4"/>')
    return enlarged(glyph)


QT_A = "M26 40 32 24 38 40M28.4 35h7.2"
QT_D = "M27 24v16h3.5a8 8 0 0 0 0-16Z"
QT_L = "M28 24v16h9"
QT_DV = "M21.5 26v12h2.5a6 6 0 0 0 0-12ZM32.5 26l4.5 12 4.5-12"


@enlarged
def kernel(c, a):
    """CachyOS Kernel Manager: its K, and the dot beside it."""
    return (f'<path d="M22 17v30M22 34 34 17M27 28.5 35.5 47" {ROUND} stroke="{c}" stroke-width="5"/>'
            f'<circle cx="43.5" cy="32" r="4" fill="{c}"/>')


def quarter_gear(p):
    """SchedExt: the gear of its logo, its upper right quarter squared off by two arms, the hole
    squared toward them: the gear in paper on the system's teal, the arms in the mauve its
    logo ends in."""
    cx, cy, r = 31, 33, 17
    teeth = "".join(f'<rect x="{cx - 6}" y="{cy - r - 9}" width="12" height="14" rx="2" fill="{p.main}" '
                    f'transform="rotate({a} {cx} {cy})"/>' for a in (90, 135, 180, 225, 270, 315))
    body = f"M{cx} {cy}V{cy - r}A{r} {r} 0 1 0 {cx + r} {cy}Z"  # three quarters, from the top round the left
    arms = (f"M{cx - 6} {cy}V{cy - r - 7}a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2V{cy - 6}H{cx + r + 7}"
            f"a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H{cx}Z")
    hole = f"M{cx + 1} {cy - 6.5}H{cx + 7.5}V{cy}A6.5 6.5 0 1 1 {cx + 1} {cy - 6.5}Z"
    return (teeth + f'<path d="{body}" fill="{p.main}"/><path d="{arms}" fill="{p.real("mauve")}"/>'
            f'<path d="{hole}" fill="{p.deep}"/>')


def rainbow_tile():
    """Kvantum's tile: its rainbow, from the top left corner, in Catppuccin colors."""
    hues = ("red", "peach", "yellow", "green", "sky", "blue", "mauve")
    stops = "".join(f'<stop offset="{i / (len(hues) - 1):.3f}" stop-color="{mix(MOCHA[f], LATTE[f], .45)}"/>'
                    for i, f in enumerate(hues))
    return f'<radialGradient id="tile" cx="4" cy="4" r="78" gradientUnits="userSpaceOnUse">{stops}</radialGradient>'


def kvantum_logo():
    """Kvantum, where it is not installed: its Kv in white on its rainbow (on each computer,
    logos.rainbow_letters puts the logo's own letters there)."""
    letters = "M19 19v26M19 33.5 31 19M24 28.5 32.5 45M36 29l5 16 5-16"
    return icon(rainbow_tile(),
                f'<rect {TILE} fill="url(#tile)"/>{rim(.25)}'
                f'<path d="{letters}" transform="translate(0 1)" {ROUND} stroke="{CRUST}" stroke-opacity=".25" stroke-width="5.5"/>'
                f'<path d="{letters}" {ROUND} stroke="{PAPER}" stroke-width="5.5"/>')


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


def hypnotix():
    """Hypnotix: the spiral of its logo, blades turning around the play button, in its blues
    on paper."""
    r0, r1, width, twist, steps = 9, 24.5, 21, 62, 14

    def edge(start):
        return [(32 + r * math.cos(math.radians(start + twist * (r - r0) / (r1 - r0))),
                 32 + r * math.sin(math.radians(start + twist * (r - r0) / (r1 - r0))))
                for r in (r0 + (r1 - r0) * k / steps for k in range(steps + 1))]
    blades = ""
    for i in range(10):
        a, b = edge(i * 36 + 8), edge(i * 36 + 8 + width)
        d = ("M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in a) + f"A{r1} {r1} 0 0 1 {b[-1][0]:.2f} {b[-1][1]:.2f}"
             + "".join(f"L{x:.2f} {y:.2f}" for x, y in reversed(b[:-1])) + "Z")
        blades += f'<path d="{d}" fill="url(#{"main" if i % 2 else "deep"})"/>'
    return icon(diagonal("tile", PAPER, PAPER_SHADE) + planes("sky"),
                f'<rect {TILE} fill="url(#tile)"/>{blades}'
                f'<circle cx="32" cy="32" r="12.8" fill="{CRUST}" fill-opacity=".12"/>'
                f'<circle cx="32" cy="32" r="11.3" fill="{PAPER}"/>'
                f'<path d="M28.4 25.6v12.8l10.6-6.4Z" fill="url(#deep)" stroke="url(#deep)" stroke-width="3" '
                f'stroke-linejoin="round"/>')


def facets(corners, center, t=.28):
    """A triangle with rounded corners, cut into one plane per side, the planes meeting at center."""
    def half(p0, p1, p2):  # a quadratic curve cut at its middle
        m01, m12 = [(a + b) / 2 for a, b in zip(p0, p1)], [(a + b) / 2 for a, b in zip(p1, p2)]
        mid = [(a + b) / 2 for a, b in zip(m01, m12)]
        return (p0, m01, mid), (mid, m12, p2)

    def xy(q):
        return f"{q[0]:.2f} {q[1]:.2f}"
    rounded = []
    for i, v in enumerate(corners):
        before, after = corners[i - 1], corners[(i + 1) % 3]
        rounded.append(half([v[k] + (before[k] - v[k]) * t for k in (0, 1)], v,
                            [v[k] + (after[k] - v[k]) * t for k in (0, 1)]))
    return [f"M{xy(center)}L{xy(rounded[i][1][0])}Q{xy(rounded[i][1][1])} {xy(rounded[i][1][2])}"
            f"L{xy(rounded[(i + 1) % 3][0][0])}Q{xy(rounded[(i + 1) % 3][0][1])} {xy(rounded[(i + 1) % 3][0][2])}Z"
            for i in range(3)]


def nuvio():
    """Nuvio: its play button folded in planes, sky, pink and blue, the dark screen in it and its
    own play button, on the Mocha tile, which takes its color (logos.tint_folder)."""
    top, right, left = facets([(13, 9), (55, 32), (13, 55)], (27, 30))
    return icon(mocha_tile() + diagonal("top", MOCHA["sky"], mix(MOCHA["sky"], MOCHA["blue"], .5))
                + diagonal("right", MOCHA["pink"], MOCHA["mauve"]) + diagonal("left", LATTE["blue"], LATTE["lavender"]),
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                + at(4.48, 4.48, .86,
                     f'<path d="{top}" fill="url(#top)"/><path d="{right}" fill="url(#right)"/>'
                     f'<path d="{left}" fill="url(#left)"/>'
                     f'<rect x="20.5" y="23" width="18" height="18" rx="5" transform="rotate(-8 29.5 32)" fill="{CRUST}"/>'
                     f'<path d="M26.6 27.6v8.8l7.2-4.4Z" fill="{PAPER}" stroke="{PAPER}" stroke-width="2.4" '
                     f'stroke-linejoin="round"/>'))


@enlarged
def lens(c, a):
    """Gwenview: its eye, a picture in the iris."""
    return (f'<path d="M13 32c5.2-8.7 11.4-13 19-13s13.8 4.3 19 13c-5.2 8.7-11.4 13-19 13S18.2 40.7 13 32Z" fill="{c}"/>'
            f'<circle cx="32" cy="32" r="9" fill="{a}"/>'
            f'<path d="M25.6 36.4 29.8 31l3.2 3.4 2.4-2.6 4.1 4.6Z" fill="{c}"/>'
            f'<circle cx="35.2" cy="27.8" r="1.7" fill="{c}"/>')


@enlarged
def bird(c, a):
    """Kate: its bird, in flight."""
    return (f'<path d="M14 37.5c6.5-.3 11.2-3 15-7.6 3.6-4.4 7.4-9.4 14.2-10.4-1.6 1.6-2.6 3.4-2.8 5.4 '
            f'3.4-1.2 6.8-.6 9.6 1.4-3.4.4-6.2 1.6-8.4 3.8-4.4 5.6-9.4 11-18 12.2-3.8.5-7.6-1-9.6-4.8Z" fill="{c}"/>'
            f'<path d="M30.5 29.5c-1.4-4.6-4.4-8-9-10.5 6.4.2 11.2 2.8 14.2 7.4Z" fill="{c}" fill-opacity=".7"/>'
            f'<circle cx="42" cy="24.6" r="1.3" fill="{a}"/>')


@enlarged
def qb(c, a):
    """qBittorrent: its two letters, the q's stem down and the b's up."""
    return (f'<circle cx="22.8" cy="33" r="6.6" {ROUND} stroke="{c}" stroke-width="3.6"/>'
            f'<path d="M29.4 26.4V47" {ROUND} stroke="{c}" stroke-width="3.6"/>'
            f'<circle cx="41.2" cy="33" r="6.6" {ROUND} stroke="{c}" stroke-width="3.6"/>'
            f'<path d="M34.6 19V39.6" {ROUND} stroke="{c}" stroke-width="3.6"/>')


@enlarged
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


# --- a four-pointed star, for the effects and the sparkles -------------------------------------

def star(cx, cy, r):
    k = .22 * r
    return (f"M{cx} {cy - r}L{cx + k} {cy - k}L{cx + r} {cy}L{cx + k} {cy + k}L{cx} {cy + r}"
            f"L{cx - k} {cy + k}L{cx - r} {cy}L{cx - k} {cy - k}Z")


# --- the free shapes: an object in planes, each glyph takes the planes it paints with --------

def at(x, y, s, body):
    return f'<g transform="translate({x} {y}) scale({s})">{body}</g>'


def sheen(d, p, opacity=.28):
    """Light across a screen or a surface, always on top of another plane."""
    return f'<path d="{d}" fill="{p.pale}" fill-opacity="{opacity}"/>'


def sector(cx, cy, r, start, end):
    a, b = math.radians(start), math.radians(end)
    return (f'M{cx} {cy}L{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}'
            f'A{r} {r} 0 0 1 {cx + r * math.cos(b):.2f} {cy + r * math.sin(b):.2f}Z')


def display(p):
    """A monitor: its screen lit, on its foot."""
    return (f'<path d="M26 46h12l1.8 7.5H24.2Z" fill="{p.deep}"/>'
            f'<rect x="17" y="51.5" width="30" height="5.5" rx="2.75" fill="{p.deep}"/>'
            f'<rect x="5" y="8" width="54" height="40" rx="7.5" fill="{p.ink}"/>'
            f'<rect x="8.5" y="11.5" width="47" height="33" rx="4.5" fill="{p.main}"/>'
            + sheen("M13 11.5h24L18 44.5h-5A4.5 4.5 0 0 1 8.5 40V16A4.5 4.5 0 0 1 13 11.5Z", p))


def two_screens(p):
    """The screens' layout: one behind the other."""
    return (f'<rect x="4" y="7" width="40" height="30" rx="6.5" fill="{p.deep}"/>'
            f'<rect x="31" y="53" width="19" height="4.5" rx="2.25" fill="{p.deep}"/>'
            f'<rect x="19" y="21" width="41" height="32" rx="6.5" fill="{p.ink}"/>'
            f'<rect x="22.5" y="24.5" width="34" height="25" rx="3.5" fill="{p.main}"/>'
            + sheen("M26 24.5h17L30 49.5h-4a3.500 3.5 0 0 1-3.5-3.5V28a3.500 3.5 0 0 1 3.5-3.5Z", p))


def chip(p):
    """The processor: a die in its package, the pins around it."""
    pins = "".join(f'<path d="M{x} 6v9M{x} 49v9M6 {x}h9M49 {x}h9" {ROUND} stroke="{p.deep}" stroke-width="4.4"/>'
                   for x in (22, 32, 42))
    return (pins + f'<rect x="13" y="13" width="38" height="38" rx="8" fill="{p.main}"/>'
            f'<rect x="22" y="22" width="20" height="20" rx="4.5" fill="{p.ink}"/>'
            f'<circle cx="19" cy="19" r="2" fill="{p.pale}"/>')


def hard_drive(p):
    """A disk drive: its lid catches the light, its front has a slot and a light."""
    return (f'<rect x="5" y="13" width="54" height="38" rx="9" fill="{p.main}"/>'
            f'<path d="M5 35h54v7a9 9 0 0 1-9 9H14a9 9 0 0 1-9-9Z" fill="{p.deep}"/>'
            f'<rect x="12.5" y="41" width="20" height="3.8" rx="1.9" fill="{p.pale}" fill-opacity=".75"/>'
            f'<circle cx="49.5" cy="43" r="3" fill="{p.pale}"/>'
            + sheen("M14 13h26L28 35H5V22a9 9 0 0 1 9-9Z", p, .22))


def usb_stick(p):
    """A USB stick: its metal plug, its body and its light."""
    return (f'<rect x="21" y="4" width="22" height="19" rx="3" fill="{p.metal}"/>'
            f'<rect x="26" y="9" width="4.5" height="4.5" rx="1" fill="{p.ink}"/>'
            f'<rect x="33.5" y="9" width="4.5" height="4.5" rx="1" fill="{p.ink}"/>'
            f'<rect x="14" y="19" width="36" height="41" rx="9" fill="{p.main}"/>'
            f'<path d="M14 42h36v9a9 9 0 0 1-9 9H23a9 9 0 0 1-9-9Z" fill="{p.deep}"/>'
            f'<circle cx="32" cy="31" r="3.8" fill="{p.pale}"/>')


def disc(p):
    """A disc: the light in its grooves, its hub."""
    return (f'<circle cx="32" cy="32" r="27.5" fill="{p.main}"/>'
            f'<path d="{sector(32, 32, 27.5, 200, 262)}{sector(32, 32, 27.5, 20, 82)}" fill="{p.pale}" fill-opacity=".55"/>'
            f'<circle cx="32" cy="32" r="11" fill="{p.deep}"/><circle cx="32" cy="32" r="4.2" fill="{p.ink}"/>')


def phone(p):
    """A phone: its frame, its lit screen."""
    return (f'<rect x="15.5" y="4" width="33" height="56" rx="8.5" fill="{p.ink}"/>'
            f'<rect x="18.5" y="7" width="27" height="50" rx="5.8" fill="{p.main}"/>'
            + sheen("M24.3 7H40L18.5 45V12.8A5.800 5.8 0 0 1 24.3 7Z", p) +
            f'<rect x="27" y="10" width="10" height="3.2" rx="1.6" fill="{p.ink}"/>')


def keys(p, top):
    """Two rows of keys and the space bar, on a keyboard whose body starts at top."""
    caps = "".join(f'<rect x="{10 + 9.2 * i:.1f}" y="{top + dy}" width="7.2" height="6.8" rx="1.8" fill="{p.main}"/>'
                   for dy in (6.5, 15.5) for i in range(5))
    return caps + f'<rect x="19.2" y="{top + 24.5}" width="25.6" height="6" rx="2" fill="{p.pale}"/>'


def keyboard(p):
    """A keyboard, its keys raised from the body."""
    return f'<rect x="4" y="14" width="56" height="36" rx="8" fill="{p.deep}"/>' + keys(p, 14)


def virtual_keyboard(p):
    """The on-screen keyboard: a keyboard that goes away."""
    return (f'<rect x="4" y="5" width="56" height="36" rx="8" fill="{p.deep}"/>' + keys(p, 5) +
            f'<path d="M22.5 48.5 32 57l9.5-8.5" {ROUND} stroke="{p.main}" stroke-width="6"/>')


def mouse(p):
    """A mouse: its buttons in the shade, its wheel."""
    return (f'<rect x="16" y="4.5" width="32" height="55" rx="16" fill="{p.main}"/>'
            f'<path d="M16 26v-5.5a16 16 0 0 1 32 0V26Z" fill="{p.deep}"/>'
            f'<rect x="29" y="11.5" width="6" height="12.5" rx="3" fill="{p.pale}"/>')


def sound_card(p):
    """The sound: a speaker, its box and its cone, and the waves."""
    return (f'<path d="M15 22h4.5L33 11a2.500 2.5 0 0 1 4 1.9v38.200a2.500 2.5 0 0 1-4 1.9L19.5 42H15Z" fill="{p.main}"/>'
            f'<path d="M9 22h10v20H9a4 4 0 0 1-4-4V26a4 4 0 0 1 4-4Z" fill="{p.deep}"/>'
            f'<path d="M44.5 24.5a11 11 0 0 1 0 15" {ROUND} stroke="{p.main}" stroke-width="5"/>'
            f'<path d="M51.5 16a22 22 0 0 1 0 32" {ROUND} stroke="{p.deep}" stroke-width="5"/>')


def palette_brush(p):
    """The look of the desktop: a painter's palette and its paints."""
    paints = (("red", 21, 26), ("yellow", 33, 17), ("green", 45, 25), ("sky", 16, 40))
    return (f'<path d="M32 5a27 27 0 1 0 0 54c4.800 0 6.3-3.6 4.5-6.6-2.1-3.5-.2-8.4 4.5-8.4h7.500A10.500 10.5 0 0 0 59 33.5C59 17.7 46.9 5 32 5Z" fill="{p.deep}"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="5.5" fill="{p.real(name)}"/>' for name, x, y in paints))


def landscape(p):
    """The wallpaper: the sun over mountains."""
    return (f'<rect x="5" y="9" width="54" height="46" rx="10" fill="{p.main}"/>'
            f'<circle cx="44.5" cy="23" r="6" fill="{p.pale}"/>'
            f'<path d="M5 45 21 28l13 15 6-5.5 19 15.5a10 10 0 0 1-9 2H15a10 10 0 0 1-10-10Z" fill="{p.deep}"/>')


def letter(p):
    """The fonts: a capital, its thick and thin strokes."""
    return (f'<path d="M28 9 11 55" {ROUND} stroke="{p.deep}" stroke-width="7.5"/>'
            f'<path d="M20 41h24" {ROUND} stroke="{p.deep}" stroke-width="6.5"/>'
            f'<path d="M33 9 52 55" {ROUND} stroke="{p.main}" stroke-width="11"/>')


def network(p):
    """The network: three machines, linked."""
    def machine(x, y, w, h):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5.5" fill="{p.main}"/>'
                f'<rect x="{x + 4.5}" y="{y + 4.5}" width="{w - 9}" height="3.8" rx="1.9" fill="{p.pale}" fill-opacity=".8"/>')
    return (f'<path d="M32 24v10M14 44v-9a1 1 0 0 1 1-1h34a1 1 0 0 1 1 1v9" {ROUND} stroke="{p.deep}" stroke-width="4.4"/>'
            + machine(20, 5, 24, 19) + machine(4, 42, 21, 17) + machine(39, 42, 21, 17))


def color_circles(p):
    """The colors: red, green and blue, mixing."""
    return (f'<circle cx="32" cy="22" r="17" fill="{p.real("red")}" fill-opacity=".92"/>'
            f'<circle cx="21" cy="41" r="17" fill="{p.real("green")}" fill-opacity=".86"/>'
            f'<circle cx="43" cy="41" r="17" fill="{p.real("blue")}" fill-opacity=".86"/>')


def globe(p):
    """The languages and regions: the Earth, not its grid."""
    return (f'<circle cx="32" cy="32" r="27.5" fill="{p.main}"/>'
            f'<path d="M21 9.5c6-2.5 14-1.8 17 2 1.8 2.6-1.6 4.8-2 7.5-.5 3.5 5 3.6 6 7 .8 3-2.6 5.5-6 5-3.5-.5-4 2.8-6 6-2.3 3.3-6.5 2-7.5-1.8-.8-3-4-4-6.5-6.7-3-3.2-5-7.8-3.2-12.3C14 13.5 17.5 11 21 9.5Z" fill="{p.deep}"/>'
            f'<path d="M46 34c3-1.5 7.5-1.8 11-.5-.8 7.2-4.2 13.5-9.5 18-2.7-1.8-3.8-5-3.5-8.5-3-1.5-2-7 2-9Z" fill="{p.deep}"/>'
            f'<path d="M26 48.5c3-1 6.5-.5 8 1.7 1.2 2-.3 4.5-2.5 6.3-2 .3-3.800.2-5.5-.2-2.8-2.5-3.2-6.8 0-7.8Z" fill="{p.deep}"/>')


def people(p):
    """The users: two people, one behind the other."""
    return (f'<circle cx="44" cy="20" r="9" fill="{p.deep}"/>'
            f'<path d="M37 33.5c10-3 22 2 22 15 0 2-1.5 3.5-3.5 3.5H47C47 44 43 37.5 37 33.5Z" fill="{p.deep}"/>'
            f'<circle cx="24" cy="20" r="12.5" fill="{p.main}"/>'
            f'<path d="M4.500 53c0-12.5 8.5-19.5 19.5-19.5S43.500 40.5 43.5 53c0 2.5-1.8 4-4 4h-31c-2.2 0-4-1.5-4-4Z" fill="{p.main}"/>')


def sliders(p):
    """Quick settings: three sliders."""
    return "".join(f'<path d="M8 {y}H56" {ROUND} stroke="{p.deep}" stroke-width="7"/>'
                   f'<circle cx="{x}" cy="{y}" r="9.5" fill="{p.main}"/><circle cx="{x}" cy="{y}" r="3.6" fill="{p.pale}"/>'
                   for y, x in ((15, 42), (32, 21), (49, 36)))


def spelling(p):
    """The spell checker: a letter, checked."""
    return (f'<path d="M7 41 19.5 9 32 41M12.500 31h14" {ROUND} stroke="{p.deep}" stroke-width="6.5"/>'
            f'<path d="M28 44l10 10 20-25" {ROUND} stroke="{p.main}" stroke-width="8"/>')


def day_night(p):
    """The day-night cycle: the sun, and the moon after it."""
    rays = "".join(f'M{23 + 16 * math.cos(math.radians(t)):.2f} {23 + 16 * math.sin(math.radians(t)):.2f}'
                   f'L{23 + 20 * math.cos(math.radians(t)):.2f} {23 + 20 * math.sin(math.radians(t)):.2f}'
                   for t in (0, 90, 135, 180, 225, 270, 315))
    return (f'<circle cx="23" cy="23" r="10.5" fill="{p.main}"/><path d="{rays}" {ROUND} stroke="{p.main}" stroke-width="4.6"/>'
            f'<path d="M46 29a15.500 15.5 0 1 0 14 22.5A13.500 13.5 0 0 1 46 29Z" fill="{p.real("lavender")}"/>')


def autostart(p):
    """What starts by itself: a play button."""
    return (f'<circle cx="32" cy="32" r="27.5" fill="{p.main}"/>'
            f'<path d="M26 19.5v25L46 32Z" fill="{p.pale}" stroke="{p.pale}" stroke-width="4.5" stroke-linejoin="round"/>')


def moon(p):
    """The night light: a crescent and its stars."""
    return (f'<path d="M34 5.5a27 27 0 1 0 22.5 41.5A23.500 23.5 0 0 1 34 5.5Z" fill="{p.main}"/>'
            f'<path d="{star(49, 16, 9.5)}" fill="{p.main}" stroke="{p.main}" stroke-width="1.4" stroke-linejoin="round"/>'
            f'<path d="{star(38, 29, 5)}" fill="{p.deep}"/>')


def hotspot(p):
    """The hotspot: waves going out on both sides."""
    return (f'<path d="M14 9a33 33 0 0 0 0 46M50 9a33 33 0 0 1 0 46" {ROUND} stroke="{p.deep}" stroke-width="5.8"/>'
            f'<path d="M22.5 18a20 20 0 0 0 0 28M41.5 18a20 20 0 0 1 0 28" {ROUND} stroke="{p.main}" stroke-width="5.8"/>'
            f'<circle cx="32" cy="32" r="7" fill="{p.main}"/>')


def key_combo(p):
    """The shortcuts: two keys, pressed together."""
    return (f'<rect x="5" y="6" width="32" height="32" rx="8.5" fill="{p.deep}"/>'
            f'<rect x="8.5" y="8.5" width="25" height="22" rx="6" fill="{p.mid}"/>'
            f'<rect x="24" y="24" width="35" height="35" rx="9.5" fill="{p.ink}"/>'
            f'<rect x="27.5" y="26.5" width="28" height="25.5" rx="7" fill="{p.main}"/>'
            f'<path d="M41.5 33v12.500M35.200 39.2h12.600" {ROUND} stroke="{p.pale}" stroke-width="4.8"/>')


def ethernet(p):
    """The wired network: its plug and cable."""
    pins = "".join(f'<rect x="{20.5 + 5.2 * i:.1f}" y="10" width="3.2" height="11" rx="1" fill="{p.pale}"/>' for i in range(5))
    return (f'<rect x="28.5" y="42" width="7" height="18" rx="3.5" fill="{p.deep}"/>'
            f'<path d="M23 35h18v8a3 3 0 0 1-3 3H26a3 3 0 0 1-3-3Z" fill="{p.deep}"/>'
            f'<rect x="14" y="5" width="36" height="33" rx="7" fill="{p.main}"/>{pins}')


def wifi(p):
    """The Wi-Fi: its arcs, the far one fading."""
    return (f'<path d="M7 22a36 36 0 0 1 50 0" {ROUND} stroke="{p.deep}" stroke-width="7"/>'
            f'<path d="M16 32a23 23 0 0 1 32 0M24.5 42a11 11 0 0 1 15 0" {ROUND} stroke="{p.main}" stroke-width="7"/>'
            f'<circle cx="32" cy="52.5" r="5.5" fill="{p.main}"/>')


def music_note(p):
    """The system's sounds: a pair of notes, their beam."""
    return (f'<path d="M23.500 47V16M54.500 40V9" {ROUND} stroke="{p.main}" stroke-width="5.4"/>'
            f'<path d="M21 14 57 6v11l-36 8Z" fill="{p.deep}" stroke="{p.deep}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<ellipse cx="15" cy="47" rx="11" ry="9" fill="{p.main}"/><ellipse cx="46" cy="40" rx="11" ry="9" fill="{p.main}"/>')


def bell(p):
    """The notifications: a bell, something waiting."""
    return (f'<path d="M23 50a9.500 9.5 0 0 0 18 0Z" fill="{p.deep}"/>'
            f'<path d="M32 5C20 5 13 14 13 25v11L7.500 45.2A2.500 2.5 0 0 0 9.7 49h44.600a2.500 2.5 0 0 0 2.2-3.8L51 36V25C51 14 44 5 32 5Z" fill="{p.main}"/>'
            f'<circle cx="49" cy="13" r="8" fill="{p.real("red")}"/>')


def leave(p):
    """The desktop's session: a door ajar, and the way out."""
    return (f'<path d="M9 5h22a4 4 0 0 1 4 4v46a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4V9a4 4 0 0 1 4-4Z" fill="{p.deep}"/>'
            f'<path d="M10 7.5 25 14a2.500 2.5 0 0 1 1.5 2.3V60L10 56.5A2 2 0 0 1 8.5 54V9a1.500 1.5 0 0 1 1.5-1.5Z" fill="{p.main}"/>'
            f'<circle cx="21" cy="34" r="2.4" fill="{p.ink}"/>'
            f'<path d="M34 32h24M49.500 23l9 9-9 9" {ROUND} stroke="{p.main}" stroke-width="5.8"/>')


def accessibility(p):
    """Accessibility: the figure with open arms, in its disc."""
    return (f'<circle cx="32" cy="32" r="27.5" fill="{p.main}"/><circle cx="32" cy="15.5" r="5" fill="{p.pale}"/>'
            f'<path d="M15.5 24.5c5.500 2 11 3 16.5 3s11-1 16.5-3M32 27.5V38l-7.5 12.5M32 38l7.500 12.5" {ROUND} stroke="{p.pale}" stroke-width="5"/>')


def activities(p):
    """The activities: three sets of work, stacked."""
    cast = 'fill="{}" fill-opacity=".45"'.format(p.ink)
    return (f'<rect x="16" y="5" width="32" height="20" rx="6.5" fill="{p.deep}"/>'
            f'<rect x="10" y="12.5" width="44" height="22" rx="7.5" {cast}/>'
            f'<rect x="10" y="15" width="44" height="22" rx="7.5" fill="{p.mid}"/>'
            f'<rect x="4" y="25.5" width="56" height="31" rx="9.5" {cast}/>'
            f'<rect x="4" y="28" width="56" height="31" rx="9.5" fill="{p.main}"/>')


def animations(p):
    """The animations: something moving, its trail behind it."""
    return (f'<circle cx="11" cy="32" r="5.5" fill="{p.deep}"/><circle cx="25" cy="32" r="9" fill="{p.mid}"/>'
            f'<circle cx="45" cy="32" r="15" fill="{p.main}"/><circle cx="40" cy="26" r="4" fill="{p.pale}" fill-opacity=".85"/>')


def app_grid(p):
    """The apps: a grid of them."""
    return "".join(f'<rect x="{x}" y="{y}" width="25" height="25" rx="7.5" fill="{fill}"/>'
                   for x, y, fill in ((6, 6, p.main), (33, 6, p.mid), (6, 33, p.deep), (33, 33, p.main)))


PAGE = "M16 4h24l16 16v34a6 6 0 0 1-6 6H16a6 6 0 0 1-6-6V10a6 6 0 0 1 6-6Z"


def page_check(p):
    """Default apps: a page, approved."""
    return (f'<path d="{PAGE}" fill="{p.main}"/><path d="M40 4l16 16H44a4 4 0 0 1-4-4Z" fill="{p.deep}"/>'
            f'<path d="M21 39l8 8 15-18" {ROUND} stroke="{p.pale}" stroke-width="6"/>')


def page_search(p):
    """File search: a page under the lens."""
    return (f'<path d="M14 4h22l14 14v36a6 6 0 0 1-6 6H14a6 6 0 0 1-6-6V10a6 6 0 0 1 6-6Z" fill="{p.deep}"/>'
            f'<rect x="15" y="17" width="17" height="3.8" rx="1.9" fill="{p.mid}"/><rect x="15" y="26" width="11" height="3.8" rx="1.9" fill="{p.mid}"/>'
            f'<circle cx="38" cy="39" r="12" fill="{p.pale}" stroke="{p.main}" stroke-width="6"/>'
            f'<path d="M47.500 48.5 57.5 58.5" {ROUND} stroke="{p.main}" stroke-width="7"/>')


def bluetooth(p):
    """Bluetooth: its rune."""
    return (f'<rect x="12" y="4" width="40" height="56" rx="20" fill="{p.main}"/>'
            f'<path d="M21.500 22.5 42.5 41.5 32 52V12l10.500 10.5-21 19" {ROUND} stroke="{p.pale}" stroke-width="5"/>')


def desktops(p):
    """The virtual desktops: four, one of them yours."""
    others = "".join(f'<rect x="{x}" y="{y}" width="26" height="26" rx="7" fill="{p.deep}"/>' for x, y in ((33, 5), (5, 33), (33, 33)))
    return (others + f'<rect x="5" y="5" width="26" height="26" rx="7" fill="{p.main}"/>'
            f'<rect x="10" y="10" width="16" height="11" rx="2.5" fill="{p.pale}"/>')


CLOUD = "M21.500 47a10.500 10.5 0 0 1-1.7-20.9A13.500 13.5 0 0 1 45.6 27 10 10 0 0 1 44 47Z"


def cloud(p):
    """The online accounts: two clouds."""
    return at(15.6, -4.4, .8, f'<path d="{CLOUD}" fill="{p.deep}"/>') + at(-7, 4.7, 1.18, f'<path d="{CLOUD}" fill="{p.main}"/>')


def search_bar(p):
    """KRunner: a search bar."""
    return (f'<rect x="4" y="16" width="56" height="32" rx="16" fill="{p.main}"/>'
            f'<circle cx="20.5" cy="30.5" r="6.5" fill="none" stroke="{p.deep}" stroke-width="3.8"/>'
            f'<path d="M25.500 35.5 30 40M37 32h14" {ROUND} stroke="{p.deep}" stroke-width="3.8"/>')


def gamepad(p):
    """The game controllers: a controller and its buttons."""
    body = 'M21 21h22c6 0 10 5 10.6 11l1.100 9c.6 5.3-5.8 8.3-9.3 4.3L40.500 39h-17l-5.9 6.3c-3.5 4-9.9 1-9.3-4.3l1.100-9C10 26 15 21 21 21Z'
    return at(-5.6, -10, 1.2,
              f'<path d="{body}" fill="{p.main}"/><path d="M20 26.5v9M15.500 31h9" {ROUND} stroke="{p.deep}" stroke-width="3.2"/>'
              f'<circle cx="41.5" cy="28.5" r="2.7" fill="{p.real("red")}"/><circle cx="46.5" cy="34" r="2.7" fill="{p.real("blue")}"/>')


def clock(p):
    """The date and time: a clock."""
    return (f'<circle cx="32" cy="32" r="27.5" fill="{p.deep}"/><circle cx="32" cy="32" r="22" fill="{p.pale}"/>'
            f'<path d="M32 17.5V32l9.500 6" {ROUND} stroke="{p.ink}" stroke-width="4.8"/>')


def glint(cx, cy, r, fill):
    return f'<path d="{star(cx, cy, r)}" fill="{fill}" stroke="{fill}" stroke-width="1.6" stroke-linejoin="round"/>'


def sparkles(p):
    """The desktop effects: three glints."""
    return glint(27, 35, 22.5, p.main) + glint(49, 16, 11.5, p.mid) + glint(51, 49, 7.5, p.deep)


def letter_down(p):
    """Installing a font: a letter, and the arrow down."""
    return (f'<path d="M6 43 19 9l13 34M11 31.5h16" {ROUND} stroke="{p.main}" stroke-width="6.5"/>'
            f'<path d="M46 12v38M35 40l11 11 11-11" {ROUND} stroke="{p.deep}" stroke-width="6.5"/>')


def icon_shapes(p):
    """The icons: four shapes."""
    return (f'<circle cx="18.5" cy="18.5" r="13" fill="{p.main}"/><rect x="35.5" y="6.5" width="23" height="23" rx="5.5" fill="{p.deep}"/>'
            f'<path d="M18.500 36.5 31 58H6Z" fill="{p.mid}" stroke="{p.mid}" stroke-width="2.4" stroke-linejoin="round"/>'
            + glint(46.5, 46.5, 13, p.main))


SHIELD = "M32 4.5 56 13.5v17c0 14-9.5 25-24 29.5C17.500 55.5 8 44.5 8 30.5v-17Z"
SHIELD_SHADE = "M32 4.5 56 13.5v17c0 14-9.5 25-24 29.5Z"


def shield(p):
    """The security: a shield, half in the shade."""
    return f'<path d="{SHIELD}" fill="{p.main}"/><path d="{SHIELD_SHADE}" fill="{p.deep}"/>'


def shield_check(p):
    """The firewall: a shield that holds."""
    return shield(p) + f'<path d="M21 32l8 8 14.5-17" {ROUND} stroke="{p.pale}" stroke-width="6"/>'


def touchpad(p):
    """The touchpad: its surface and its two buttons."""
    return (f'<rect x="5" y="7" width="54" height="50" rx="10" fill="{p.deep}"/>'
            f'<rect x="9" y="11" width="46" height="27" rx="6" fill="{p.main}"/>'
            f'<path d="M9 41h21.500v12H15a6 6 0 0 1-6-6Z" fill="{p.mid}"/><path d="M33.500 41H55v6a6 6 0 0 1-6 6H33.500Z" fill="{p.mid}"/>')


def arrow_cursor(p):
    """The cursors: an arrow, its tail in the shade."""
    tip = "M19 12v35l9.500-8.9 6.5 14 6.2-2.8-6.5-13.6 13.4-1.2Z"
    tail = "M28.500 38.1 35 52.1 41.2 49.3 34.7 35.7Z"
    return at(-9, -11, 1.2, f'<path d="{tip}" fill="{p.main}" stroke="{p.main}" stroke-width="1.8" stroke-linejoin="round"/>'
                            f'<path d="{tail}" fill="{p.deep}" stroke="{p.deep}" stroke-width="1.8" stroke-linejoin="round"/>')


def x_mark(p):
    """X.Org: its X."""
    return (f'<path d="M11 9 53 55" {ROUND} stroke="{p.deep}" stroke-width="10"/>'
            f'<path d="M53 9 11 55" {ROUND} stroke="{p.main}" stroke-width="10"/>')


def two_arrows(p):
    """The connections: one way and the other."""
    return (f'<path d="M58 44H10M20 33 9 44l11 11" {ROUND} stroke="{p.deep}" stroke-width="6.5"/>'
            f'<path d="M6 20h48M44 9l11 11-11 11" {ROUND} stroke="{p.main}" stroke-width="6.5"/>')


def bubble(p):
    """The feedback: a word, and its answer."""
    dots = "".join(f'<circle cx="{x}" cy="33.5" r="3.4" fill="{p.pale}"/>' for x in (18, 29, 40))
    return (f'<rect x="20" y="5" width="39" height="30" rx="8" fill="{p.deep}"/>'
            f'<path d="M12 16h34a7 7 0 0 1 7 7v21a7 7 0 0 1-7 7H28l-11 9v-9h-5a7 7 0 0 1-7-7V23a7 7 0 0 1 7-7Z" fill="{p.main}"/>{dots}')


def relay(p):
    """The proxy: what stands between two machines."""
    return (f'<rect x="4" y="18" width="19" height="28" rx="6" fill="{p.deep}"/><rect x="41" y="18" width="19" height="28" rx="6" fill="{p.deep}"/>'
            f'<path d="M22 32h20" {ROUND} stroke="{p.mid}" stroke-width="4.4"/>'
            f'<circle cx="32" cy="32" r="9" fill="{p.main}"/><circle cx="32" cy="32" r="3.4" fill="{p.pale}"/>')


def plain_gear(p):
    """The settings: a gear and its hub."""
    return (f'<path d="{gear(32, 32, 28.5, 22.5, 12, 1)}" fill="{p.main}" stroke="{p.main}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<circle cx="32" cy="32" r="14.5" fill="{p.deep}"/><circle cx="32" cy="32" r="7" fill="{p.pale}"/>')


def two_gears(p):
    """The background services: two gears."""
    return (f'<path d="{gear(46, 46, 14.5, 11.2, 9, 1)}" fill="{p.deep}" stroke="{p.deep}" stroke-width="1.8" stroke-linejoin="round"/>'
            f'<circle cx="46" cy="46" r="4.6" fill="{p.pale}"/>'
            f'<path d="{gear(24, 24, 20.5, 16, 10, 1)}" fill="{p.main}" stroke="{p.main}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="24" cy="24" r="10" fill="{p.deep}"/><circle cx="24" cy="24" r="4.8" fill="{p.pale}"/>')


TITLE_BAR = "M14 8h36a9 9 0 0 1 9 9v5H5v-5a9 9 0 0 1 9-9Z"


def app_window(p):
    """The apps' style: a window."""
    return (f'<rect x="5" y="8" width="54" height="48" rx="9" fill="{p.main}"/><path d="{TITLE_BAR}" fill="{p.deep}"/>'
            f'<circle cx="13.5" cy="15" r="2.6" fill="{p.pale}"/><circle cx="21.5" cy="15" r="2.6" fill="{p.pale}"/>'
            f'<rect x="11" y="28" width="42" height="22" rx="4.5" fill="{p.pale}" fill-opacity=".38"/>')


def traffic_window(p):
    """Klassy: a window and its red, yellow and green buttons, like the decoration's."""
    return (f'<rect x="5" y="8" width="54" height="48" rx="9" fill="{p.pale}"/><path d="{TITLE_BAR}" fill="{p.deep}"/>'
            + "".join(f'<circle cx="{13.5 + 8 * i}" cy="15" r="3" fill="{p.real(name)}"/>' for i, name in enumerate(("red", "yellow", "green"))) +
            f'<rect x="11" y="28" width="42" height="22" rx="4.5" fill="{p.main}"/>')


def window_gear(p):
    """Window behavior, rules and scripts: a window, a gear on it."""
    return (f'<rect x="4" y="6" width="50" height="44" rx="9" fill="{p.main}"/>'
            f'<path d="M13 6h32a9 9 0 0 1 9 9v4H4v-4a9 9 0 0 1 9-9Z" fill="{p.deep}"/>'
            f'<circle cx="44" cy="44" r="16.5" fill="{p.ink}"/>'
            f'<path d="{gear(44, 44, 13, 10, 8, 1)}" fill="{p.pale}" stroke="{p.pale}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<circle cx="44" cy="44" r="4.4" fill="{p.ink}"/>')


def desktop_panel(p):
    """The Plasma style: a desktop and its panel."""
    return (f'<rect x="5" y="7" width="54" height="50" rx="9" fill="{p.main}"/>'
            + sheen("M14 7h28L16 43H5V16a9 9 0 0 1 9-9Z", p, .24) +
            f'<rect x="10.5" y="42.5" width="43" height="9.5" rx="4.75" fill="{p.deep}"/>'
            f'<circle cx="17" cy="47.25" r="2.4" fill="{p.pale}"/><circle cx="24.5" cy="47.25" r="2.4" fill="{p.pale}"/>')


def stacked_windows(p):
    """The task switcher: a window in front of another."""
    return (f'<rect x="20" y="6" width="39" height="32" rx="8" fill="{p.deep}"/>'
            f'<rect x="5" y="22" width="44" height="36" rx="8" fill="{p.main}"/>'
            f'<path d="M13 22h28a8 8 0 0 1 8 8v3H5v-3a8 8 0 0 1 8-8Z" fill="{p.mid}"/>')


def drawing_tablet(p):
    """The drawing tablet: its surface and pen."""
    return (f'<rect x="6" y="10" width="52" height="44" rx="8" fill="{p.deep}"/>'
            f'<rect x="11" y="15" width="42" height="34" rx="4.5" fill="{p.main}"/>'
            f'<path d="M46.500 20 27 39.5" {ROUND} stroke="{p.pale}" stroke-width="5.5"/>'
            f'<path d="M27 39.5 22.5 44" {ROUND} stroke="{p.ink}" stroke-width="4.2"/>')


def bolt(p):
    """Thunderbolt: its bolt, folded."""
    whole = "M36.500 12 18 36.5h12.500L26.500 52 46.5 27H34Z"
    fold = "M30.500 36.5 26.5 52 46.5 27H34Z"
    return at(-12, -12.5, 1.38, f'<path d="{whole}" fill="{p.main}" stroke="{p.main}" stroke-width="1.6" stroke-linejoin="round"/>'
                                f'<path d="{fold}" fill="{p.deep}" stroke="{p.deep}" stroke-width="1.6" stroke-linejoin="round"/>')


def paint_roller(p):
    """The window decorations' colors: a paint roller."""
    return (f'<path d="M51 14h7v18H32v10" {ROUND} stroke="{p.deep}" stroke-width="5"/>'
            f'<rect x="5" y="5" width="46" height="19" rx="6.5" fill="{p.main}"/>'
            f'<rect x="11" y="9" width="22" height="3.8" rx="1.9" fill="{p.pale}" fill-opacity=".7"/>'
            f'<rect x="26.5" y="40" width="11" height="20" rx="4" fill="{p.main}"/>')


def padlock(p):
    """The lock: its shackle, its body, its keyhole."""
    return (f'<path d="M19 28V18a13 13 0 0 1 26 0v10" {ROUND} stroke="{p.metal}" stroke-width="7"/>'
            f'<rect x="8" y="26" width="48" height="34" rx="9" fill="{p.main}"/>'
            f'<circle cx="32" cy="40" r="4.6" fill="{p.deep}"/><rect x="29.6" y="41" width="4.8" height="10" rx="2.4" fill="{p.deep}"/>')


def info(p):
    """The information: an i in its disc."""
    return (f'<circle cx="32" cy="32" r="27.5" fill="{p.main}"/><circle cx="32" cy="18.5" r="4.4" fill="{p.pale}"/>'
            f'<rect x="28.5" y="28" width="7" height="21" rx="3.5" fill="{p.pale}"/>')


def person_frame(p):
    """The login screen: someone on a card."""
    return (f'<rect x="5" y="5" width="54" height="54" rx="13" fill="{p.deep}"/><circle cx="32" cy="24" r="10" fill="{p.main}"/>'
            f'<path d="M14 52c0-11 8.5-16.5 18-16.5S50 41 50 52c0 1.2-.8 2-2 2H16c-1.2 0-2-.8-2-2Z" fill="{p.main}"/>')


def splash_screen(p):
    """The splash screen: a logo, and the bar that fills."""
    return (f'<rect x="5" y="8" width="54" height="48" rx="9" fill="{p.deep}"/><circle cx="32" cy="27" r="9.5" fill="{p.main}"/>'
            f'<rect x="15" y="43" width="34" height="5.5" rx="2.75" fill="{p.ink}"/><rect x="15" y="43" width="19" height="5.5" rx="2.75" fill="{p.pale}"/>')


def touch_screen(p):
    """The touchscreen: a finger on it."""
    return (f'<rect x="9" y="4" width="46" height="56" rx="9" fill="{p.deep}"/><rect x="13" y="8" width="38" height="48" rx="5.5" fill="{p.main}"/>'
            f'<circle cx="32" cy="32" r="12" fill="{p.pale}" fill-opacity=".45"/><circle cx="32" cy="32" r="5.8" fill="{p.pale}"/>')


def battery(p):
    """The energy: a battery, charging."""
    return (f'<rect x="4" y="15" width="50" height="34" rx="9" fill="{p.deep}"/><rect x="56" y="25" width="5" height="14" rx="2.5" fill="{p.deep}"/>'
            f'<rect x="8.5" y="19.5" width="41" height="25" rx="5.5" fill="{p.main}"/>'
            f'<path d="M31 22.5 22 34h7l-2 8 10-12h-7Z" fill="{p.pale}" stroke="{p.pale}" stroke-width="1.4" stroke-linejoin="round"/>')


def plug(p):
    """The peripherals: a plug."""
    return (f'<path d="M22 6v15M42 6v15M32 50v9" {ROUND} stroke="{p.deep}" stroke-width="7"/>'
            f'<path d="M11 19h42v11a21 21 0 0 1-42 0Z" fill="{p.main}" stroke="{p.main}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="32" cy="30" r="3.8" fill="{p.pale}"/>')


def media_frame(p):
    """The media: a player and its button."""
    return (f'<rect x="5" y="10" width="54" height="44" rx="11" fill="{p.main}"/>'
            f'<path d="M26.500 21v22L45 32Z" fill="{p.pale}" stroke="{p.pale}" stroke-width="4" stroke-linejoin="round"/>')


def screen_edges(p):
    """The screen edges: a corner that reacts."""
    return (f'<rect x="6" y="10" width="52" height="44" rx="9" fill="{p.main}"/>'
            f'<path d="M15 10h17v5a17 17 0 0 1-17 17H6V19a9 9 0 0 1 9-9Z" fill="{p.deep}"/><circle cx="16" cy="20" r="4" fill="{p.pale}"/>')


def swipe(p):
    """The gestures: a finger going across."""
    return (f'<path d="M32 32h26M47.500 21 58.5 32 47.5 43" {ROUND} stroke="{p.deep}" stroke-width="6.5"/>'
            f'<circle cx="17" cy="32" r="13" fill="{p.main}"/><circle cx="17" cy="32" r="5" fill="{p.pale}"/>')


def magnifier(p):
    """The search: a lens, its glass catching the light."""
    return (f'<path d="M41 41 56.5 56.5" {ROUND} stroke="{p.deep}" stroke-width="9"/>'
            f'<circle cx="27" cy="27" r="18" fill="{p.pale}" stroke="{p.main}" stroke-width="7"/>'
            f'<path d="M17 27a10 10 0 0 1 10-10" {ROUND} stroke="{p.mid}" stroke-width="3.6"/>')


def wallet(p):
    """KWallet: its wallet and its clasp."""
    return (f'<path d="M12 7h32a6 6 0 0 1 6 6v4H7v-5a5 5 0 0 1 5-5Z" fill="{p.deep}"/>'
            f'<rect x="5" y="14" width="54" height="42" rx="10" fill="{p.main}"/>'
            f'<rect x="40" y="28" width="19" height="14" rx="5" fill="{p.deep}"/><circle cx="48" cy="35" r="3.2" fill="{p.pale}"/>')


# --- more hardware: what the volume, Bluetooth, battery and disk applets, the Places panel and
# the Info Center show ---------------------------------------------------------------------

def headphones(p):
    """Headphones: their band, their two cups and the pads inside."""
    return (f'<path d="M13 37V29a19 19 0 0 1 38 0v8" {ROUND} stroke="{p.deep}" stroke-width="6.5"/>'
            f'<rect x="5" y="31" width="16" height="27" rx="8" fill="{p.main}"/>'
            f'<rect x="43" y="31" width="16" height="27" rx="8" fill="{p.main}"/>'
            f'<rect x="16.5" y="36" width="4.5" height="17" rx="2.25" fill="{p.deep}"/>'
            f'<rect x="43" y="36" width="4.5" height="17" rx="2.25" fill="{p.deep}"/>')


def headset(p):
    """A headset: headphones, and the microphone on its boom."""
    return (f'<path d="M13 31V26a19 19 0 0 1 38 0v5" {ROUND} stroke="{p.deep}" stroke-width="6.5"/>'
            f'<path d="M13 48v4a5.500 5.5 0 0 0 5.5 5.500h9" {ROUND} stroke="{p.deep}" stroke-width="4.2"/>'
            f'<rect x="5" y="26" width="16" height="25" rx="8" fill="{p.main}"/>'
            f'<rect x="43" y="26" width="16" height="25" rx="8" fill="{p.main}"/>'
            f'<rect x="16.5" y="31" width="4.5" height="15" rx="2.25" fill="{p.deep}"/>'
            f'<rect x="43" y="31" width="4.5" height="15" rx="2.25" fill="{p.deep}"/>'
            f'<rect x="25.500" y="53.5" width="13" height="7" rx="3.5" fill="{p.main}"/>')


def microphone(p):
    """A microphone: its capsule in its cradle, on its stand."""
    return (f'<path d="M13 28v2a19 19 0 0 0 38 0v-2M32 49v7" {ROUND} stroke="{p.deep}" stroke-width="5.5"/>'
            f'<rect x="20" y="54.5" width="24" height="5.5" rx="2.75" fill="{p.deep}"/>'
            f'<rect x="21" y="4" width="22" height="35" rx="11" fill="{p.main}"/>'
            f'<rect x="26" y="9.500" width="5" height="15" rx="2.5" fill="{p.pale}" fill-opacity=".7"/>')


def speaker(p):
    """A loudspeaker: its box, its woofer and its tweeter."""
    return (f'<rect x="12" y="4" width="40" height="56" rx="9" fill="{p.main}"/>'
            f'<circle cx="32" cy="40" r="13" fill="{p.deep}"/><circle cx="32" cy="40" r="7.500" fill="{p.ink}"/>'
            f'<circle cx="32" cy="40" r="2.6" fill="{p.pale}"/>'
            f'<circle cx="32" cy="16.500" r="6" fill="{p.deep}"/><circle cx="32" cy="16.500" r="2.2" fill="{p.pale}"/>')


def laptop(p):
    """A laptop: its screen lit, open over its base."""
    return (f'<rect x="9" y="8" width="46" height="35" rx="6.5" fill="{p.ink}"/>'
            f'<rect x="12.500" y="11.500" width="39" height="27" rx="3.5" fill="{p.main}"/>'
            + sheen("M16 11.500h17.500L18.500 38.500H16a3.500 3.5 0 0 1-3.500-3.500V15a3.500 3.5 0 0 1 3.500-3.500Z", p) +
            f'<path d="M3 45h58v3a8 8 0 0 1-8 8H11a8 8 0 0 1-8-8Z" fill="{p.deep}"/>'
            f'<rect x="25" y="45" width="14" height="3.6" rx="1.8" fill="{p.ink}"/>')


def tablet(p):
    """A tablet: its frame, its wide lit screen."""
    return (f'<rect x="8" y="4" width="48" height="56" rx="9" fill="{p.ink}"/>'
            f'<rect x="11.500" y="7.500" width="41" height="49" rx="5.8" fill="{p.main}"/>'
            + sheen("M17.300 7.500H38L11.500 50V13.300A5.800 5.800 0 0 1 17.300 7.500Z", p))


def camera(p):
    """A camera: its body and grip, its lens, its flash."""
    return (f'<path d="M21 17l3.200-6.400A3 3 0 0 1 26.900 9h10.200a3 3 0 0 1 2.700 1.600L43 17Z" fill="{p.deep}"/>'
            f'<rect x="4" y="15" width="56" height="41" rx="9.5" fill="{p.main}"/>'
            f'<path d="M4 43h56v3.500a9.500 9.500 0 0 1-9.500 9.500h-37A9.500 9.500 0 0 1 4 46.500Z" fill="{p.deep}"/>'
            f'<rect x="46.500" y="20.500" width="8" height="5" rx="2.5" fill="{p.pale}"/>'
            f'<circle cx="32" cy="36" r="14.500" fill="{p.ink}"/><circle cx="32" cy="36" r="8.500" fill="{p.deep}"/>'
            f'<circle cx="36" cy="32" r="2.8" fill="{p.pale}"/>')


def video_camera(p):
    """A video camera: its body, its lens hood, the light that says it records."""
    return (f'<rect x="10" y="8" width="21" height="8" rx="4" fill="{p.deep}"/>'
            f'<path d="M41 28 56.500 19.600A2.500 2.500 0 0 1 60 21.800v22.400a2.500 2.500 0 0 1-3.500 2.200L41 38Z" fill="{p.deep}"/>'
            f'<rect x="4" y="14" width="40" height="38" rx="9" fill="{p.main}"/>'
            f'<circle cx="14" cy="24" r="3.4" fill="{p.real("red")}"/>'
            f'<rect x="11" y="40" width="18" height="3.8" rx="1.9" fill="{p.pale}" fill-opacity=".7"/>')


def scanner(p):
    """A scanner: the sheet under its lid, the light that reads it."""
    return (f'<rect x="17" y="4" width="30" height="24" rx="3.5" fill="{p.main}"/>'
            f'<rect x="22" y="9.500" width="20" height="3.2" rx="1.6" fill="{p.mid}"/><rect x="22" y="15.500" width="13" height="3.2" rx="1.6" fill="{p.mid}"/>'
            f'<rect x="6" y="21" width="52" height="15" rx="5.5" fill="{p.mid}"/>'
            f'<rect x="4" y="31" width="56" height="25" rx="8.500" fill="{p.deep}"/>'
            f'<rect x="11" y="41.500" width="30" height="4" rx="2" fill="{p.pale}"/><circle cx="50" cy="43.500" r="3" fill="{p.main}"/>')


def memory(p):
    """The memory: a module, its chips and its contacts."""
    chips = "".join(f'<rect x="{9.5 + 11.6 * i:.1f}" y="21" width="8.500" height="12" rx="2" fill="{p.ink}"/>' for i in range(4))
    pins = "".join(f'<rect x="{7.2 + 5.1 * i:.1f}" y="43.500" width="2.8" height="5" rx="1" fill="{p.pale}"/>' for i in range(10))
    return (f'<rect x="4" y="14" width="56" height="29" rx="5" fill="{p.main}"/>'
            f'<rect x="5" y="40" width="54" height="10" rx="2.500" fill="{p.deep}"/>{chips}{pins}')


def network_card(p):
    """A network card: its bracket, its socket, its chip, the edge that plugs in."""
    pins = "".join(f'<rect x="{23 + 4.6 * i:.1f}" y="46.500" width="2.6" height="5" rx="1" fill="{p.pale}"/>' for i in range(6))
    return (f'<rect x="20" y="42" width="32" height="11" rx="2.500" fill="{p.deep}"/>{pins}'
            f'<rect x="9" y="11" width="51" height="34" rx="6" fill="{p.main}"/>'
            f'<rect x="4" y="5" width="8" height="54" rx="3.5" fill="{p.metal}"/>'
            f'<rect x="12" y="19" width="16" height="17" rx="3.5" fill="{p.ink}"/>'
            f'<rect x="16" y="23" width="8" height="5" rx="1.5" fill="{p.pale}" fill-opacity=".8"/>'
            f'<rect x="37" y="19" width="16" height="16" rx="4" fill="{p.deep}"/>')


def sd_card(p):
    """A memory card: its cut corner, its contacts, its label."""
    pins = "".join(f'<rect x="{17 + 5.6 * i:.1f}" y="9" width="3.4" height="10" rx="1.2" fill="{p.pale}"/>' for i in range(4))
    return (f'<path d="M17 4h23l13 13v37a6 6 0 0 1-6 6H17a6 6 0 0 1-6-6V10a6 6 0 0 1 6-6Z" fill="{p.main}"/>{pins}'
            f'<rect x="17" y="30" width="30" height="23" rx="4.500" fill="{p.deep}"/>'
            f'<rect x="22" y="36" width="16" height="3.6" rx="1.8" fill="{p.pale}" fill-opacity=".8"/>')


def sim_card(p):
    """A SIM card: its cut corner and its chip."""
    return (f'<path d="M17 4h21l15 15v35a6 6 0 0 1-6 6H17a6 6 0 0 1-6-6V10a6 6 0 0 1 6-6Z" fill="{p.main}"/>'
            f'<rect x="18.500" y="27" width="27" height="23" rx="5" fill="{p.pale}"/>'
            f'<path d="M18.500 38.500h27M28 27v23M36 38.500V50" {ROUND} stroke="{p.deep}" stroke-width="2.6"/>')


def optical_drive(p):
    """An optical drive: the disc going in, its slot, its button."""
    return (f'<path d="M14 26a18 18 0 0 1 36 0Z" fill="{p.mid}"/><path d="M26 26a6 6 0 0 1 12 0Z" fill="{p.ink}"/>'
            f'<rect x="4" y="24" width="56" height="26" rx="8.500" fill="{p.main}"/>'
            f'<path d="M4 37h56v4.500a8.500 8.500 0 0 1-8.500 8.500h-39A8.500 8.500 0 0 1 4 41.500Z" fill="{p.deep}"/>'
            f'<rect x="11" y="41.500" width="29" height="3.6" rx="1.8" fill="{p.pale}" fill-opacity=".75"/>'
            f'<circle cx="50" cy="43.300" r="2.8" fill="{p.pale}"/>')


def drives(p):
    """Several disks: two drives, stacked."""
    return (f'<rect x="5" y="5" width="54" height="25" rx="8" fill="{p.mid}"/>'
            f'<path d="M5 19h54v3a8 8 0 0 1-8 8H13a8 8 0 0 1-8-8Z" fill="{p.deep}"/>'
            f'<circle cx="50" cy="24.500" r="2.6" fill="{p.pale}"/>'
            f'<rect x="5" y="33" width="54" height="26" rx="8" fill="{p.main}"/>'
            f'<path d="M5 47h54v4a8 8 0 0 1-8 8H13a8 8 0 0 1-8-8Z" fill="{p.deep}"/>'
            f'<rect x="12" y="51.200" width="20" height="3.6" rx="1.8" fill="{p.pale}" fill-opacity=".75"/>'
            f'<circle cx="50" cy="53" r="2.6" fill="{p.pale}"/>')


def locked_drive(p):
    """An encrypted disk: a drive, and its padlock."""
    return (hard_drive(p) + f'<circle cx="46" cy="44" r="15.500" fill="{p.ink}"/>'
            f'<path d="M40.500 43v-4a5.500 5.5 0 0 1 11 0v4" {ROUND} stroke="{p.metal}" stroke-width="3.6"/>'
            f'<rect x="37.500" y="41.500" width="17" height="12.500" rx="3.6" fill="{p.real("yellow")}"/>')


def television(p):
    """A television: its wide screen, on its two feet."""
    return (f'<path d="M18 46l-4.500 10M46 46l4.500 10" {ROUND} stroke="{p.deep}" stroke-width="5.5"/>'
            f'<rect x="3" y="8" width="58" height="40" rx="7.500" fill="{p.ink}"/>'
            f'<rect x="6.500" y="11.500" width="51" height="33" rx="4.500" fill="{p.main}"/>'
            + sheen("M11 11.500h25L17 44.500h-6A4.500 4.500 0 0 1 6.500 40V16A4.500 4.500 0 0 1 11 11.500Z", p))


def media_player(p):
    """A music player: its screen and its wheel."""
    return (f'<rect x="14" y="4" width="36" height="56" rx="9" fill="{p.main}"/>'
            f'<rect x="19.500" y="9.500" width="25" height="19" rx="4" fill="{p.ink}"/>'
            f'<circle cx="32" cy="43.500" r="11" fill="{p.deep}"/><circle cx="32" cy="43.500" r="4.200" fill="{p.main}"/>')


def router(p):
    """A modem or a router: its antennas, its lights."""
    lights = "".join(f'<circle cx="{14 + 8.5 * i}" cy="46" r="2.6" fill="{p.pale}"/>' for i in range(3))
    return (f'<path d="M13 36V11M51 36V11" {ROUND} stroke="{p.deep}" stroke-width="5.5"/>'
            f'<path d="M24.500 22.500a10.500 10.500 0 0 1 15 0" {ROUND} stroke="{p.mid}" stroke-width="4.6"/>'
            f'<circle cx="32" cy="28.500" r="3.2" fill="{p.mid}"/>'
            f'<rect x="4" y="35" width="56" height="22" rx="8.500" fill="{p.main}"/>{lights}'
            f'<rect x="40" y="44.200" width="13" height="3.6" rx="1.8" fill="{p.deep}"/>')


def server(p):
    """A server: three units in their rack, each with its slot and its light."""
    return "".join(f'<rect x="5" y="{y}" width="54" height="16.500" rx="5.5" fill="{fill}"/>'
                   f'<rect x="12" y="{y + 6.4}" width="22" height="3.6" rx="1.8" fill="{p.pale}" fill-opacity=".75"/>'
                   f'<circle cx="50" cy="{y + 8.2}" r="2.6" fill="{p.pale}"/>'
                   for y, fill in ((4.5, p.main), (23.7, p.mid), (43, p.deep)))


def share_nodes(p):
    """The sharing: one thing, reaching two others."""
    return (f'<path d="M17 32 45 14.500M17 32 45 49.500" {ROUND} stroke="{p.deep}" stroke-width="5.8"/>'
            f'<circle cx="17" cy="32" r="11.500" fill="{p.main}"/>'
            f'<circle cx="46" cy="14" r="9.500" fill="{p.main}"/><circle cx="46" cy="50" r="9.500" fill="{p.main}"/>')


def person(p):
    """What is yours: someone, in their disc."""
    return (f'<circle cx="32" cy="32" r="27.5" fill="{p.main}"/><circle cx="32" cy="24" r="9.500" fill="{p.pale}"/>'
            f'<path d="M13.200 52c2.200-9.200 9.600-14.500 18.800-14.500S48.600 42.800 50.800 52a27.500 27.500 0 0 1-37.600 0Z" fill="{p.pale}"/>')


# --- the apps' symbols: objects in planes, on the same 64 px grid as the free shapes ----------
# On a colored tile, main is the paper, mid its tint, deep and pale the tile's color.

def btrfs(p):
    """btrfs-assistant: a gear around a tree of snapshots."""
    nodes = "".join(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{p.main}"/>' for x, y in ((32, 21.5), (23.5, 42), (40.5, 42)))
    return (f'<path d="{gear(32, 32, 28.5, 23, 10, 1)}" fill="{p.main}" stroke="{p.main}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<circle cx="32" cy="32" r="18" fill="{p.deep}"/>'
            f'<path d="M32 22v9M23.500 41v-10h17v10" {ROUND} stroke="{p.main}" stroke-width="3.4"/>{nodes}')


def printer(p):
    """A printer: the sheet going in, the page coming out printed with its three inks."""
    inks = "".join(f'<rect x="{x}" y="45.5" width="7" height="7" rx="1.8" fill="{p.real(ink)}"/>'
                   for x, ink in ((21, "sky"), (28.5, "pink"), (36, "yellow")))
    return (f'<path d="M20 22V8a3 3 0 0 1 3-3h13l8 8v9Z" fill="{p.pale}"/>'
            f'<path d="M36 5v5a3 3 0 0 0 3 3h5Z" fill="{p.mid}"/>'
            f'<rect x="5" y="18" width="54" height="29" rx="8" fill="{p.main}"/>'
            f'<path d="M5 34h54v5a8 8 0 0 1-8 8H13a8 8 0 0 1-8-8Z" fill="{p.deep}"/>'
            f'<rect x="43" y="24" width="9" height="3.6" rx="1.8" fill="{p.mid}"/>'
            f'<circle cx="13" cy="25.8" r="2.2" fill="{p.real("green")}"/>'
            f'<rect x="12" y="36.5" width="40" height="4.5" rx="2.25" fill="{p.ink}"/>'
            f'<path d="M16 39h32v18a3 3 0 0 1-3 3H19a3 3 0 0 1-3-3Z" fill="{p.pale}"/>' + inks)


def webcam(p):
    """A webcam: its lens, its stand."""
    return (f'<rect x="28.5" y="44" width="7" height="11" fill="{p.mid}"/>'
            f'<rect x="16" y="53.5" width="32" height="6.5" rx="3.25" fill="{p.main}"/>'
            f'<circle cx="32" cy="26" r="22" fill="{p.main}"/><circle cx="32" cy="26" r="13" fill="{p.ink}"/>'
            f'<circle cx="32" cy="26" r="7" fill="{p.deep}"/><circle cx="36.5" cy="21.5" r="2.6" fill="{p.main}"/>')


def rings(p):
    """Filelight: the disk as rings of what fills it."""
    def arc(r, width, start, end, fill):
        x1, y1 = 32 + r * math.cos(math.radians(start)), 32 + r * math.sin(math.radians(start))
        x2, y2 = 32 + r * math.cos(math.radians(end)), 32 + r * math.sin(math.radians(end))
        large = 1 if (end - start) % 360 > 180 else 0
        return f'<path d="M{x1:.2f} {y1:.2f}A{r} {r} 0 {large} 1 {x2:.2f} {y2:.2f}" fill="none" stroke="{fill}" stroke-width="{width}"/>'
    return (f'<circle cx="32" cy="32" r="9.5" fill="{p.main}"/>'
            + arc(17.5, 7.5, -90, 110, p.main) + arc(17.5, 7.5, 116, 200, p.mid) + arc(17.5, 7.5, 206, 264, p.ink)
            + arc(26.5, 7, -90, 40, p.ink) + arc(26.5, 7, 46, 104, p.main) + arc(26.5, 7, 110, 200, p.mid) + arc(26.5, 7, 206, 264, p.main))


def smiley(p):
    """The emoji picker: a face."""
    return (f'<circle cx="32" cy="32" r="27" fill="{p.main}"/>'
            f'<circle cx="15.5" cy="37" r="4.6" fill="{p.pale}" fill-opacity=".35"/><circle cx="48.5" cy="37" r="4.6" fill="{p.pale}" fill-opacity=".35"/>'
            f'<ellipse cx="23" cy="25.5" rx="3.8" ry="5.2" fill="{p.ink}"/><ellipse cx="41" cy="25.5" rx="3.8" ry="5.2" fill="{p.ink}"/>'
            f'<path d="M20 38c6.500 9.5 17.5 9.5 24 0" {ROUND} stroke="{p.ink}" stroke-width="5"/>')


def refresh(p):
    """Cachy-Update: its cycle of two arrows."""
    return at(-24, -24, 1.75,
              f'<path d="M45.2 27.5A14 14 0 0 0 20.5 22.6" {ROUND} stroke="{p.main}" stroke-width="4.5"/>'
              f'<path d="M47 16.5v11.8H35.2Z" fill="{p.main}" stroke="{p.main}" stroke-width="1.5" stroke-linejoin="round"/>'
              f'<path d="M18.8 36.5a14 14 0 0 0 24.7 4.9" {ROUND} stroke="{p.deep}" stroke-width="4.5"/>'
              f'<path d="M17 47.5V35.7h11.8Z" fill="{p.deep}" stroke="{p.deep}" stroke-width="1.5" stroke-linejoin="round"/>')


def shell(p):
    """Shelly: its own logo, redrawn: a scallop rising out of an open cardboard box, outlined in
    planes, each outlined in a deep shade of its own color rather than the logo's black. Seven
    lobes fan out from a hinge at the box's mouth, the middle one tallest, with two ears lying
    flat at the hinge: the further out, the darker. The box is seen from above
    its front corner, its four flaps open: the back two behind the shell, the front two folded out
    and down. Drawn on the logo's own 256 px canvas, a touch wider, then brought onto the grid. In
    Catppuccin colors: the shell lavender, from white lavender at the top to blue violet at the
    hinge, the box peach, its left side lit, its back flaps in shade, its inside dark."""
    color = p is Planes
    s = 56 / 239  # the logo's drawing, 239 px tall from its top at 4, onto the grid's 56
    hx, hy = 122, 128  # the hinge
    L, B, R, F = (64, 137), (122, 113), (181, 137), (122, 161)  # the box's mouth
    Lb, Fb, Rb = (64, 207), (122, 236), (181, 207)  # its floor's corners
    if color:
        lavender = mix(MOCHA["lavender"], LATTE["lavender"], .55)
        peach, shade = mix(MOCHA["peach"], PAPER, .08), mix(MOCHA["peach"], mix(LATTE["peach"], LATTE["red"], .5), .3)
        rims = {"shell": mix(LATTE["lavender"], CRUST, .4), "box": mix(LATTE["peach"], CRUST, .55)}
        paint = {"lobe": "url(#shelly-lobe)", "ear": MOCHA["lavender"], "flap": mix(peach, PAPER, .25),
                 "back": mix(peach, shade, .55),
                 "lit": "url(#shelly-lit)", "shade": "url(#shelly-shade)",
                 "inside-l": mix(LATTE["peach"], CRUST, .5), "inside-r": mix(LATTE["peach"], CRUST, .64)}

        def vertical(id, y1, y2, stops):  # on the logo's canvas; without y1, along each shape, top to bottom
            units = f'gradientUnits="userSpaceOnUse" x1="0" y1="{y1}" x2="0" y2="{y2}"' if y1 is not None else 'x1="0" y1="0" x2="0" y2="1"'
            return (f'<linearGradient id="{id}" {units}>'
                    + "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + "</linearGradient>")
        defs = ("<defs>"
                + vertical("shelly-lobe", None, None, ((0, mix(MOCHA["lavender"], PAPER, .5)), (.45, lavender),
                                                   (.8, mix(MOCHA["lavender"], LATTE["lavender"], .3)), (1, MOCHA["lavender"])))
                + vertical("shelly-lit", 161, 236, ((0, peach), (1, mix(peach, shade, .45))))
                + vertical("shelly-shade", 137, 236, ((0, mix(shade, peach, .25)), (1, mix(shade, CRUST, .08))))
                + "</defs>")
    else:
        defs = ""
        rims = {"shell": p.ink, "box": p.ink}
        paint = dict.fromkeys(("lobe", "ear", "flap", "back", "lit", "shade", "inside-l", "inside-r"), p.main)

    def poly(kind, *pts):
        return (f'<path d="M{"L".join(f"{x:g} {y:g}" for x, y in pts)}Z" fill="{paint[kind]}" '
                f'stroke="{rims["box"]}" stroke-width="5" stroke-linejoin="round"/>')

    def shift(pt, dx, dy):
        return pt[0] + dx, pt[1] + dy

    def lobe(angle, length, w, kind="lobe", dim=0):
        # pointed at the hinge, widest high up, then a round top
        top = length - w
        d = (f"M0 0C{-w * .4:.2f} {-length * .2:.2f} {-w:.2f} {-length * .42:.2f} {-w:.2f} {-top:.2f}"
             f"A{w} {w} 0 0 1 {w:.2f} {-top:.2f}C{w:.2f} {-length * .42:.2f} {w * .4:.2f} {-length * .2:.2f} 0 0Z")
        out = f'<g transform="translate({hx} {hy}) rotate({angle})"><path d="{d}" fill="{paint[kind]}"/>'
        if color and dim:  # further out, darker
            out += f'<path d="{d}" fill="{LATTE["lavender"]}" fill-opacity="{dim}"/>'
        return out + f'<path d="{d}" fill="none" stroke="{rims["shell"]}" stroke-width="5" stroke-linejoin="round"/></g>'
    back = (poly("back", L, B, shift(B, -19, -21), shift(L, -19, -21))
            + poly("back", R, B, shift(B, 19, -21), shift(R, 19, -21))
            # the mouth: the far walls inside, the left one in the light, and their corner
            + poly("inside-l", L, B, F) + poly("inside-r", B, R, F)
            + f'<path d="M{B[0]} {B[1]}V{F[1]}" stroke="{rims["box"]}" stroke-width="3.6"/>')
    # the outer lobes first, each one further in over the last; the ears over their feet
    scallop = "".join(lobe(side * angle, length, w, dim=dim)
                      for angle, length, w, dim in ((48, 97, 16.5, .3), (31, 109, 17.5, .2), (15, 118, 18, .1))
                      for side in (-1, 1))
    scallop += lobe(0, 122, 19) + lobe(-93, 38, 9.5, "ear", .15) + lobe(93, 38, 9.5, "ear", .15)
    front = (poly("lit", L, F, Fb, Lb) + poly("shade", F, R, Rb, Fb)
             + poly("flap", L, F, shift(F, -18, 23), shift(L, -19, 19))
             + poly("flap", F, R, shift(R, 19, 19), shift(F, 18, 23)))
    stretch = 1.1
    return (f'{defs}<g transform="translate({32 - hx * s * stretch:.3f} {4 - 4 * s:.3f}) scale({s * stretch:.5f} {s:.5f})">'
            f"{back}{scallop}{front}</g>")


def snapshot_back(p):
    """Limine Snapper Restore: a snapshot, the shutter's blades, and the arrow turning back round
    it, to the system as it was."""
    cx, cy, r = 32, 32, 13.5
    blades = "".join(f'<path d="M{cx + r * math.cos(math.radians(a)):.2f} {cy + r * math.sin(math.radians(a)):.2f}'
                     f'L{cx + 5 * math.cos(math.radians(a + 60) + .9):.2f} {cy + 5 * math.sin(math.radians(a + 60) + .9):.2f}" '
                     f'stroke="{p.mid}" stroke-width="2.6" stroke-linecap="round"/>' for a in range(0, 360, 60))
    R, start, end = 22.5, -150, 150  # from the top left, round by the right, to the bottom left
    sx, sy = cx + R * math.cos(math.radians(start)), cy + R * math.sin(math.radians(start))
    ex, ey = cx + R * math.cos(math.radians(end)), cy + R * math.sin(math.radians(end))

    def on(radius, angle):
        return f"{cx + radius * math.cos(math.radians(angle)):.2f} {cy + radius * math.sin(math.radians(angle)):.2f}"
    # the head: its base across the arc where it starts, its tip further back on the circle
    head = f"M{on(R + 6, start)}L{on(R, start - 22)}L{on(R - 6, start)}Z"
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{p.main}"/>{blades}'
            f'<circle cx="{cx}" cy="{cy}" r="4.6" fill="{p.deep}"/>'
            f'<path d="M{sx:.2f} {sy:.2f}A{R} {R} 0 1 1 {ex:.2f} {ey:.2f}" {ROUND} stroke="{p.main}" stroke-width="5.5"/>'
            f'<path d="{head}" fill="{p.main}" stroke="{p.main}" stroke-width="2.4" stroke-linejoin="round"/>')


def pulse():
    """The system monitor: the system's pulse, in green on the dark tile, as on a monitor's screen."""
    line = "M11 34H20.5L24 28L29 45L35 15.5L40 40L42.5 34H53"
    stroke = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    return icon(mocha_tile(),
                f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}'
                # a faint glow, then the line
                f'<path d="{line}" {stroke} stroke="{MOCHA["green"]}" stroke-opacity=".14" stroke-width="9"/>'
                f'<path d="{line}" {stroke} stroke="{MOCHA["green"]}" stroke-width="4.4"/>')


def folder(p):
    """Dolphin: the folders it shows."""
    return (f'<path d="M6 16a7 7 0 0 1 7-7h13.500a6 6 0 0 1 4.5 2l4 4.5h16a7 7 0 0 1 7 7V30H6Z" fill="{p.deep}"/>'
            f'<rect x="6" y="21" width="52" height="35" rx="7" fill="{p.mid}"/>'
            f'<rect x="23" y="31" width="18" height="4.2" rx="2.1" fill="{p.pale}"/>')


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


# --- places: the Desktop folder, with a symbol like the others, and the trash, in teal ----------

FOLDER_BACK, FOLDER_FRONT = "#80cec1", "#94e2d5"  # the mocha-teal folders' colors


def desktop_folder():
    """The folder the others are made from, with a screen on it."""
    svg = (HERE.parent / "generator/colors/mocha-teal/folder-documents.svg").read_text()
    screen = (f'<g fill="none" stroke="{SURFACE0}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
              '<rect x="22.8" y="27.8" width="18.4" height="12.4" rx="2.4"/><path d="M32 40.2v4.4M27.4 45.6h9.2"/></g>')
    return re.sub(r'<g transform="translate\(22[^>]*>.*?</g>', screen, svg, flags=re.S)


# the folders' soft shadow (generator/colors.py): stacked copies of the outline
SHADOW_LAYERS = ((5.0, 0.06), (3.6, 0.09), (2.4, 0.12), (1.4, 0.18), (0.7, 0.3))
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
