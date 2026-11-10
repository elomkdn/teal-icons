#!/usr/bin/env python3
"""The apps' own logos, read from the system when the theme is made at home on a computer
(localize.py): in Catppuccin colors, on Teal's tile. The logos are not redistributed here."""
from shapes import *  # noqa: F401,F403


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
