#!/usr/bin/env python3
"""The apps' own logos, read from the system when the theme is made at home on a computer
(localize.py): in Catppuccin colors, on Teal's tile. The logos are not redistributed here."""
import subprocess
import threading

from shapes import *  # noqa: F401,F403


def logo_tile(path, box=40, disc=None, square=False):
    """An app's own logo (SVG, SVGZ or PNG, from the app's install), in Catppuccin colors, on
    a Mocha tile, where its colors stand out like in the dock; a round logo (disc, from
    ROUND_LOGOS) loses its disc, whose color becomes the tile; a square one (square, from
    SQUARE_LOGOS) is its own tile, cut to Teal's. Built on the user's machine: the logos are not
    redistributed here."""
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
    if square and path.suffix in (".svg", ".svgz"):
        svg = square_tile(catppuccin.recolor_svg(raw.decode("utf-8", "ignore"), everything=True))
    elif disc:
        svg = icon(vertical("tile", *disc["tile"]), f'<rect {TILE} fill="url(#tile)"/>{rim(disc["rim"])}{body}')
    else:
        svg = icon(mocha_tile(), f'<rect {TILE} fill="url(#tile)"/>{rim(MOCHA_RIM)}{body}')
    from xml.dom import minidom
    minidom.parseString(svg)  # raises on a logo we could not clean: our drawing stays
    return svg


def rainbow_letters(path):
    """Kvantum: the white letters of its logo, on its rainbow (shapes.rainbow_tile), across the
    tile. Its logo is a rectangle: cut to the tile, its letters would stretch."""
    import io
    from PIL import Image
    letters = " ".join(re.findall(r'<path\b[^>]*\bd="([^"]+)"', Path(path).read_text()))
    probe = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="480" height="480"><path d="{letters}"/></svg>'
    png = subprocess.run(["rsvg-convert"], input=probe.encode(), capture_output=True, check=True).stdout
    left, top, right, bottom = (v / 10 for v in Image.open(io.BytesIO(png)).getchannel("A").getbbox())
    scale = 38 / (right - left)
    x, y = 32 - (left + right) / 2 * scale, 32 - (top + bottom) / 2 * scale
    shade = f'<g transform="translate({x:.3f} {y + 1:.3f}) scale({scale:.4f})"><path d="{letters}" fill="{CRUST}" fill-opacity=".25"/></g>'
    white = f'<g transform="translate({x:.3f} {y:.3f}) scale({scale:.4f})"><path d="{letters}" fill="{PAPER}"/></g>'
    return icon(rainbow_tile(), f'<rect {TILE} fill="url(#tile)"/>{rim(.25)}{shade}{white}')


def square_tile(svg):
    """A logo that is already a square (its own background, its own corners): what it covers
    fills the tile, the color by each of its corners behind them where they are rounder than
    the tile's, cut to the tile's corners. A picture with the tile's shape in it: Plasma's QtSvg
    draws neither the logos' own clips nor ours."""
    import base64
    import io
    from PIL import Image, ImageDraw
    png = subprocess.run(["rsvg-convert", "-w", "256", "-h", "256", "-a"], input=svg.encode(), capture_output=True,
                         check=True).stdout
    logo = Image.open(io.BytesIO(png)).convert("RGBA")
    logo = logo.crop(logo.getchannel("A").getbbox())
    side, over = 256, 260  # the tile, and the logo a little over its edge
    corner = logo.getpixel((round(logo.width * .09), round(logo.height * .09)))
    tile = Image.new("RGBA", (side, side), corner[:3] + (255,))
    logo = logo.resize((over, over), Image.LANCZOS)
    tile.alpha_composite(logo, (-(over - side) // 2, -(over - side) // 2))
    mask = Image.new("L", (side * 4, side * 4), 0)  # drawn large, for smooth corners
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, side * 4 - 1, side * 4 - 1), radius=round(side * 4 * 13.002 / 56.002), fill=255)
    tile.putalpha(mask.resize((side, side), Image.LANCZOS))
    out = io.BytesIO()
    tile.save(out, "PNG")
    data = base64.b64encode(out.getvalue()).decode()
    return icon("", f'<image x="4" y="3.969" width="56.002" height="56.002" '
                    f'xlink:href="data:image/png;base64,{data}"/>{rim(.25)}')


# --- the tiles' colors ------------------------------------------------------------------------
# A logo on the Mocha tile gets a tile whose color says what the app is:
# - a terminal stays black, on the Mocha tile;
# - a tool of the system (its menu's categories) is teal, the system's color;
# - another app has its own color: that of its installed icon, else of Papirus's icon of the
#   same name, else of the logo; a white logo with none of them, the color of its menu's category,
#   in the families of the free shapes; an app nothing is known of keeps the Mocha tile.
# The logo's hue goes on a pastel tile where it stays clear; a white logo, or one that would not
# stand out, on the vivid tile of that hue, then on its deep shade.

MOCHA_STOPS = re.compile(r'(<linearGradient\b[^>]*>)<stop offset="0" stop-color="#313244"/>'
                         r'<stop offset="1" stop-color="#1e1e2e"/>(</linearGradient>)', re.I)
APP_HUES = [f for f in MOCHA if f not in ("teal", "maroon")]  # teal is the system's; maroon goes with red
KEYS = ("#ff00ff", "#00ff00")  # the tile while the logo is measured: what changes with it is not the logo
PAPIRUS_APPS = Path("/usr/share/icons/Papirus/64x64/apps")
TERMINAL = {"TerminalEmulator"}
SYSTEM = {"System", "Settings", "DesktopSettings", "HardwareSettings", "Monitor", "Filesystem", "Printing"}
# a white logo's color, by its menu's first category found here
CATEGORIES = [("Game", "red"), ("AudioVideo", "pink"), ("Audio", "pink"), ("Video", "pink"),
              ("Graphics", "mauve"), ("Development", "blue"), ("Office", "blue"), ("Network", "sky"),
              ("Education", "lavender"), ("Science", "lavender"), ("Utility", "peach")]
# where the menu's categories say otherwise
TILE_HUES = {"cachy-update-blue": "teal"}  # the system's updates, filed under Utility
MENUS = [Path("/usr/share/applications"), Path.home() / ".local/share/applications",
         Path("/var/lib/flatpak/exports/share/applications"), Path.home() / ".local/share/flatpak/exports/share/applications"]
_menu = None
_menu_lock = threading.Lock()  # the theme's tiles are tinted in parallel


def categories(names):
    """The menu's categories of the apps that use one of these icon names."""
    global _menu
    with _menu_lock:
        if _menu is None:
            menu = {}
            for folder in MENUS:
                for f in folder.glob("*.desktop") if folder.is_dir() else ():
                    text = f.read_text(errors="ignore")
                    icon, found = re.search(r"^Icon=(.+)$", text, re.M), re.search(r"^Categories=(.+)$", text, re.M)
                    if icon and found:
                        menu.setdefault(icon.group(1).strip(), set()).update(c for c in found.group(1).split(";") if c)
            _menu = menu
    return set().union(*(_menu.get(n, set()) for n in names))


def tile_shades(family):
    near = NEIGHBOR[family]
    return [(mix(MOCHA[family], PAPER, .72), mix(MOCHA[family], PAPER, .38)),  # pastel
            (mix(MOCHA[family], LATTE[family], .12), mix(MOCHA[family], LATTE[near], .62)),  # vivid
            (mix(LATTE[family], CRUST, .42), mix(LATTE[near], CRUST, .62))]  # deep


def _render(svg, size=48):
    """The picture's pixels inside the tile, as RGBA."""
    import io
    from PIL import Image
    png = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size)], input=svg.encode(),
                         capture_output=True, check=True).stdout
    image = Image.open(io.BytesIO(png)).convert("RGBA")
    inside = range(round(size * 6 / 64), round(size * 58 / 64))
    return [image.getpixel((x, y)) for y in inside for x in inside]


def _lab(pixel):
    return catppuccin.oklab("#%02x%02x%02x" % pixel[:3])


def _pixels(svg):
    """A picture's opaque pixels, in OKLab."""
    return [_lab(p) for p in _render(svg) if p[3] > 200]


def _logo(svg):
    """The pixels of the logo alone: the picture drawn on two tiles of different colors, the
    pixels that stay the same (not the tile, nor the edges and the light blending into it)."""
    first, second = (_render(MOCHA_STOPS.sub(rf'\1<stop offset="0" stop-color="{k}"/><stop offset="1" stop-color="{k}"/>\2', svg))
                     for k in KEYS)
    return [_lab(p) for p, q in zip(first, second) if p[3] > 200 and max(abs(x - y) for x, y in zip(p[:3], q[:3])) < 8]


def _hue(pixels, share=.15):
    """The family of the colored pixels, if enough of them are colored: the hue whose stretch of
    the wheel, with its two neighbors, holds the most of them (Firefox's yellow, peach and red
    make it peach), the hue itself breaking a tie."""
    targets = {f: math.atan2(catppuccin.oklab(MOCHA[f])[2], catppuccin.oklab(MOCHA[f])[1]) for f in APP_HUES}
    wheel = sorted(targets, key=targets.get)
    count = dict.fromkeys(wheel, 0)
    for _, a, b in pixels:
        if math.hypot(a, b) > .06:
            h = math.atan2(b, a)
            count[min(targets, key=lambda f: abs(math.remainder(h - targets[f], math.tau)))] += 1
    if not pixels or sum(count.values()) / len(pixels) < share:
        return None

    def stretch(i):
        return count[wheel[i - 1]] + count[wheel[i]] + count[wheel[(i + 1) % len(wheel)]], count[wheel[i]]
    return wheel[max(range(len(wheel)), key=stretch)]


def _file_hue(path, share=.25):
    """The family of a picture file's colors, SVG or PNG."""
    if path.suffix == ".png":
        from PIL import Image
        image = Image.open(path).convert("RGBA").resize((48, 48))
        return _hue([_lab(p) for p in image.getdata() if p[3] > 200], share)
    if path.suffix == ".svg":
        return _hue(_pixels(path.read_text()), share)
    return None


def tile_family(logo, names):
    """The tile's family for this logo and these icon names (see above); None: the Mocha tile."""
    for name in names:
        if name in TILE_HUES:
            return TILE_HUES[name]
    menu = categories(names)
    if menu & TERMINAL:
        return None
    if menu & SYSTEM and "Game" not in menu:
        return "teal"
    sources = [find_logo(names)] + [PAPIRUS_APPS / f"{n}.svg" for n in names]
    for source in sources:
        if source and source.is_file() and (family := _file_hue(source)):
            return family
    if family := _hue(logo):
        return family
    return next((family for category, family in CATEGORIES if category in menu), None)


def tinted(svg, names=()):
    """The picture with its Mocha tile in the color of its app (see above), or as it was."""
    if not MOCHA_STOPS.search(svg):
        return svg
    try:
        logo = _logo(svg)
        family = tile_family(logo, list(names)) if logo else None
    except (ImportError, OSError, ValueError, subprocess.CalledProcessError):  # no Pillow or rsvg-convert: Mocha
        return svg
    if not family:
        return svg
    shades = tile_shades(family)[0 if _hue(logo) else 1:]  # a white logo would vanish on pastel
    if family in WARM:
        shades = shades[:-1]  # their deep shade is brown, no Catppuccin color: Mocha rather
    best, score = None, -1
    for start, end in shades:
        middle = catppuccin.oklab(mix(start, end, .5))
        clear = sum(1 for p in logo if math.dist(p, middle) > .12) / len(logo)
        if clear > score:
            best, score = (start, end), clear
        if clear >= .7:
            break
    if score < .7 and family in WARM:
        return svg
    return MOCHA_STOPS.sub(rf'\1<stop offset="0" stop-color="{best[0]}"/><stop offset="1" stop-color="{best[1]}"/>\2', svg)


# our icon -> the names its app's logo may have, in hicolor or Breeze. A gray, generic logo
# (KDE Connect's phone, pavucontrol's knob, Gufw's shield) would only dull its tile, and a small
# picture (SchedExt's gradient, Limine Snapper's thin circuit) would blur on it: our drawing stays.
LOGOS = {
    "assistant.svg": ["assistant", "qtassistant"], "designer.svg": ["designer", "qtdesigner"],
    "linguist.svg": ["linguist", "qtlinguistic"], "qdbusviewer.svg": ["qdbusviewer"],
    "btrfs-assistant.svg": ["btrfs-assistant"], "org.cachyos.KernelManager.svg": ["org.cachyos.KernelManager"],
    "gwenview.svg": ["gwenview", "org.kde.gwenview"], "kate.svg": ["kate", "org.kde.kate"],
    "kwalletmanager.svg": ["kwalletmanager", "kwalletmanager2"],
    "io.github.Faugus.faugus-launcher.svg": ["io.github.Faugus.faugus-launcher", "faugus-launcher"],
    "micro.svg": ["micro"],
    "firefox.svg": ["firefox"],
    "hypnotix.svg": ["hypnotix"], "utilities-system-monitor.svg": ["utilities-system-monitor"],
    "kvantum.svg": ["kvantum"],
}


# the logos that are already a square: their own background becomes the tile
SQUARE_LOGOS = {"hypnotix.svg", "utilities-system-monitor.svg"}
# the logos rebuilt from their parts: how
REBUILT_LOGOS = {"kvantum.svg": rainbow_letters}


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
