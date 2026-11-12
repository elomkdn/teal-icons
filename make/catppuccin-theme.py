#!/usr/bin/env python3
"""Build the Teal icon theme from its base icons (install-base.sh -c mocha-teal -a):

- full-color icons (apps, file types, devices, categories): the base's, recolored with
  Catppuccin by generator/catppuccin.py, brands included. Teal is kept for what belongs to
  the system (folders, file manager, settings, software center), so the accent still means
  something; other apps take their own Catppuccin hue, leaning to the saturated Latte shades
  so they stay easy to tell apart in a dock;
- the base's dark tiles (two grays, lighter than Mocha's) become the Mocha tile, with its lit
  rim; then every tile takes the color of its app (teal/logos.py, tint_folder): teal for the
  system's tools, black for a terminal, the app's own color for the others;
- code and text files are sheets of paper, their mark in the language's color, where the base
  colors the whole page: the icons stay light, like the everyday file types;
- icons drawn for Teal (teal/draw.py) where the base's are missing, wrong or not clean: the
  terminal, Dolphin, the KDE, Qt and CachyOS tools the base gives a generic or borrowed icon (on each computer,
  localize.py puts the apps' own logos in their place, where the app is installed);
- monochrome icons (actions, statuses, tray, symbolic icons): Papirus-Dark's system folders,
  copied with Catppuccin colors (Mocha text instead of Papirus's gray, teal instead of its
  blue, Catppuccin red, yellow and green for states). GTK apps show these colors as they are,
  KDE apps recolor them with the color scheme. The base's own monochrome icons are removed, and
  so are its full-color icons named like a Papirus system icon (edit-find, bluetooth-active…).
  The copies sit inside the theme, not only in an inherited one: icon lookups shorten an
  unknown name inside a theme before moving on to the next one (bluetooth-active ->
  bluetooth), and would land on a full-color app icon of ours.
- tray: Papirus's tray icons for the system (network, battery, sound, notifications…) only;
  apps keep their own (Discord, Steam, KeePassXC…), except those in TRAY_PAPIRUS; localize.py
  links them, and Papirus as the fallback, on each computer. In <name>-Shell, Plasma's own,
  they and the tray's arrow are pure white, like the apps' tray icons beside them.

The theme built needs nothing installed: Papirus's system icons are copied into it.

usage: catppuccin-theme.py <installed theme folder> <name>
"""
import configparser
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "generator"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "teal"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import catppuccin  # noqa: E402
import draw  # noqa: E402
from localize import OWN  # noqa: E402

RECOLORED = ("apps/scalable", "mimetypes/scalable", "devices/scalable", "categories/32")
KEPT = RECOLORED + ("places/scalable",)
# the system's own apps, in the accent like the folders
TEAL = {"dolphin.svg", "system-file-manager.svg", "file-manager.svg", "preferences-system.svg",
        "systemsettings.svg", "softwarecenter.svg", "software-properties.svg", "plasmadiscover.svg"}
# Teal's own icons, drawn by teal/draw.py, in place of the base's
DRAWN = Path(__file__).resolve().parent / "teal/apps"
DRAWN_PLACES = Path(__file__).resolve().parent / "teal/places"
DRAWN_DEVICES = Path(__file__).resolve().parent / "teal/devices"
DRAWN_SETTINGS = Path(__file__).resolve().parent / "teal/settings"
DRAWN_SYMBOLS = Path(__file__).resolve().parent / "teal/symbols"
# Apps whose base icon is under the name of a page of System Settings, which Teal draws as a free
# shape: the app keeps a copy of the base's tile under its own name, and its other names follow
APP_COPIES = {"kdeconnect.svg": ("preferences-kde-connect.svg", ["org.kde.kdeconnect.svg"])}
# The base's app icons whose name Papirus uses for a system icon too, kept: the printing
# settings (cups and system-config-printer link to it)
APPS_KEPT = {"printer.svg"}
# Apps the base does not know by this name, under the icon it has for them
SAME_APP = {"brave-origin": "brave", "printer-settings": "printer", "hardinfo2": "hwinfo",
            "pavucontrol-qt": "multimedia-volume-control", "cachyos-package-installer": "cachyos-pi",
            "kdeconnect-app": "kdeconnect", "kmenuedit": "org.kde.kmenuedit", "org.kde.kwalletmanager": "kwalletmanager",
            "kwallet": "kwalletmanager"}
# Logos that spill over their tile, brought inside it
FIT_IN_TILE = {"krita.svg": .82, "transmission.svg": .84}
# Logos whose colored tile the recoloring turns into a candy gradient (Firefox's, magenta to
# violet): they go on the Mocha tile, like the apps' own logos, where their colors stand out
ON_MOCHA = {"firefox.svg"}
INHERITS = "{papirus},Adwaita,AdwaitaLegacy,hicolor,breeze"
PAPIRUS = Path("/usr/share/icons/Papirus-Dark")
# Papirus-Dark's color scheme classes -> Catppuccin Mocha
PAPIRUS_COLORS = {"#dfdfdf": "#cdd6f4", "#4285f4": "#94e2d5", "#ff9800": "#f9e2af",
                  "#f44336": "#f38ba8", "#4caf50": "#a6e3a1", "#444444": "#1e1e2e"}
PAPIRUS_COLORS_TEXT = PAPIRUS_COLORS["#dfdfdf"]  # Mocha's text, in place of Papirus's gray


# tray icons of the system, by their first word
TRAY_SYSTEM = re.compile(
    r"(audio|battery|network|nm|bluetooth|notification|notifications|microphone|mic|media|input|keyboard"
    r"|mouse|touchpad|phone|user|system|volume|weather|gsm|state|idle|transmitting|receiving|both|process"
    r"|display|brightness|airplane|wifi|cpu|drive|printer|preferences|update|software|security|dialog"
    r"|appointment|clock|computer|ac|gpm|xfpm|power|night|redshift|kalarm|klipper|mail)(-|$)")
# apps whose own tray icons are missing or poor: Papirus's instead
TRAY_PAPIRUS = set()
# names Papirus lacks, linked to one of its icons in every folder that has it. Without them,
# the lookup shortens the name inside Teal and lands on a full-color icon:
# video-display-brightness (Plasma's Brightness applet, next to the screen's slider) would
# show the video-display tile drawn for Info Center
SAME_AS = {"video-display-brightness.svg": "video-display-symbolic.svg"}


def is_system_tray(name, statuses):
    return (name in statuses or TRAY_SYSTEM.match(name) is not None
            or any(name.startswith(app) for app in TRAY_PAPIRUS))


def papirus_statuses():
    return {f.removesuffix(".svg").removesuffix("-symbolic")
            for d in ("16x16/status", "22x22/status", "24x24/status", "16x16/symbolic/status")
            if (PAPIRUS / d).is_dir() for f in os.listdir(PAPIRUS / d)}


def papirus_system_dirs():
    ini = configparser.ConfigParser(interpolation=None, strict=False)
    ini.optionxform = str
    ini.read(PAPIRUS / "index.theme")
    dirs = {}
    for d in ini["Icon Theme"]["Directories"].split(","):
        size, _, context = d.partition("/")
        if size in ("16x16", "18x18", "22x22", "24x24") and (context in ("actions", "panel", "status")
                                                                   or context.startswith("symbolic/")):
            dirs[d] = dict(ini[d])
    return dirs


def papirus_recolor(text):
    return catppuccin.HEX.sub(lambda m: PAPIRUS_COLORS.get(m.group(0).lower(), m.group(0)), text)


def copy_papirus(theme, dirs):
    """Papirus-Dark's system folders, at the same paths, in Catppuccin colors, its tray
    folders with the system's icons only. Links between files of one folder are kept; a link
    leading out of the copied folders becomes a file."""
    statuses = papirus_statuses()
    for d in dirs:
        src, dst = PAPIRUS / d, theme / d
        dst.mkdir(parents=True, exist_ok=True)
        for f in src.iterdir():
            if d.endswith("/panel") and not is_system_tray(f.name.removesuffix(".svg"), statuses):
                continue
            out = dst / f.name
            if f.is_symlink() and "/" not in os.readlink(f):
                out.symlink_to(os.readlink(f))
            elif f.suffix == ".svg" and f.exists():
                out.write_text(papirus_recolor(f.read_text(errors="ignore")))
    for d in dirs:  # links whose target is missing in the copy
        for f in (theme / d).iterdir():
            if f.is_symlink() and not f.exists():
                target = (PAPIRUS / d / os.readlink(f)).resolve()
                f.unlink()
                if target.exists():
                    f.write_text(papirus_recolor(target.read_text(errors="ignore")))
    for d in dirs:
        for name, other in SAME_AS.items():
            out = theme / d / name
            if (theme / d / other).exists() and not (out.exists() or out.is_symlink()):
                out.symlink_to(other)


def system_names(dirs):
    """Names of actions and statuses; Papirus's symbolic app, device and file type icons
    (firefox-symbolic…) do not make the full-color ones system icons."""
    return {f.removesuffix(".svg").removesuffix("-symbolic")
            for d in dirs if not d.endswith(("/apps", "/devices", "/mimetypes", "/places", "/categories"))
            for f in os.listdir(PAPIRUS / d)}


def drop_system_names(theme, names):
    dropped = 0
    for folder in ("apps/scalable", "devices/scalable", "mimetypes/scalable"):
        for f in (theme / folder).iterdir() if (theme / folder).is_dir() else []:
            if f.name.removesuffix(".svg") in names and f.name not in TEAL | APPS_KEPT:
                f.unlink()
                dropped += 1
    return dropped


def fit_in_tile(text, scale):
    """Everything drawn after the tile (its last rounded rect), scaled around the center."""
    end = list(re.finditer(r'<rect\b[^>]*\brx="[^"]+"[^>]*/>', text))[-1].end()
    close = text.rindex("</svg>")
    return (f'{text[:end]}<g transform="translate(32 32) scale({scale}) translate(-32 -32)">'
            f'{text[end:close]}</g>{text[close:]}')


# The base's tile: a rounded square of 56 px, a rect or the same outline as a path
TILE = re.compile(r'<(?:rect|path)\b[^>]*?(?:width="56(?:\.\d+)?"[^>]*?height="56(?:\.\d+)?"|id="plate-tile"'
                  r'|d="m17 4h30c7\.18)[^>]*?>')
STOP_COLOR = re.compile(r'stop-color(?::\s*|=")(#[0-9a-fA-F]{3,6})')
DARK_TILE = 0.5  # OKLab lightness under which a neutral tile is a dark one


def mocha_tile(text):
    """A dark neutral tile (the base has two, #171717 to #2c2c2c and #363636 to #525252, which the
    recoloring would turn into two more grays) becomes Teal's Mocha tile: surface 0 to base, on
    the diagonal, with the light on its top edge. Where the picture is not on the 64 px grid, or
    the gradient serves something else too, only its colors change."""
    tile = TILE.search(text)
    fill = tile and re.search(r'fill="url\(#([^)]+)\)"', tile.group(0))
    if not fill:
        return text
    name = re.escape(fill.group(1))
    gradient = re.search(rf'<linearGradient\b[^>]*\bid="{name}"[^>]*>(.*?)</linearGradient>', text, re.S)
    if not gradient:
        return text
    stops = re.findall(r"<stop\b[^>]*>", gradient.group(1))
    colors = [(STOP_COLOR.findall(stop) or [None])[-1] for stop in stops]  # a style wins over the attribute
    if len(colors) < 2 or None in colors:
        return text
    lab = [catppuccin.oklab(c if len(c) == 7 else "#" + "".join(ch * 2 for ch in c[1:])) for c in colors]
    if any((a * a + b * b) ** .5 >= catppuccin.NEUTRAL_CHROMA or light >= DARK_TILE for light, a, b in lab):
        return text
    on_grid = ('viewBox="0 0 64 64"' in text and "transform=" not in tile.group(0)
               and text.count(f"#{fill.group(1)})") == 1 and "xlink:href" not in gradient.group(0).split(">")[0])
    if on_grid:
        new = draw.diagonal(fill.group(1), draw.SURFACE0, draw.BASE)
        text = text.replace(gradient.group(0), new)
        end = text.index(tile.group(0)) + len(tile.group(0))
        return text[:end] + draw.rim(draw.MOCHA_RIM) + text[end:]
    low, high = min(l[0] for l in lab), max(l[0] for l in lab)
    body = gradient.group(1)
    for stop, color, (light, _, _) in zip(stops, colors, lab):
        t = (light - low) / (high - low) if high > low else 0
        body = body.replace(stop, STOP_COLOR.sub(lambda m: m.group(0).replace(m.group(1), draw.mix(draw.BASE, draw.SURFACE0, t)),
                                                 stop), 1)
    return text.replace(gradient.group(0), gradient.group(0).replace(gradient.group(1), body))


def onto_mocha(text):
    """The picture's tile, whatever its color, becomes the Mocha tile with its rim; the logo
    stays. The tile is the first rounded rect, a 56 px square on the 64 px grid, at the scale of
    the picture's own canvas."""
    side = float(re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+)', text).group(1))
    scale = side / 64
    tile = re.search(r'<rect\b[^>]*\brx="[^"]+"[^>]*/>', text[text.index("</defs>"):])
    width = tile and re.search(r'\bwidth="([\d.]+)"', tile.group(0))
    if not width or abs(float(width.group(1)) / scale - 56) > 1:
        raise ValueError("no tile to replace")
    mocha = (f'<g transform="scale({scale:.6f})"><rect {draw.TILE} fill="url(#teal-mocha)"/>'
             f'{draw.rim(draw.MOCHA_RIM)}</g>')
    text = text.replace(tile.group(0), mocha, 1)
    return text.replace("</defs>", draw.diagonal("teal-mocha", draw.SURFACE0, draw.BASE) + "</defs>", 1)


# The base's sheet of paper, and its folded corner: white at 35 % over the page's color
SHEET = re.compile(r'(<path fill=")(#[0-9a-fA-F]{3,6})(" d="M13 4c-2\.77 0-5 2\.23-5 5v46(?:\.\d+)?c0 2\.77 2\.23 5 5 5h38c2\.77 0 '
                   r'5-2\.23 5-5V16L44 4(?:\.\d+)?z"[^>]*/>)(<path fill=")#fff(")( d="[^"]*")?( opacity="\.35")')
PAPER_TYPES = re.compile(r"text-|application-(json|toml|xml|javascript|typescript|sql|x-(yaml|perl|php|ruby|java|python))")


def long_hex(color):
    color = color.lower()
    return color if len(color) == 7 else "#" + "".join(c * 2 for c in color[1:])


def paper_page(text):
    """A code or text file whose whole page has the language's color: the page becomes paper and
    its mark takes the color (what was white on the page takes the page's color, what had the
    page's color in the mark becomes paper). A page already neutral, or a mark with no white in
    it, stays as the base draws it."""
    sheet = SHEET.search(text)
    if not sheet:
        return text
    color = long_hex(sheet.group(2))
    _, a, b = catppuccin.oklab(color)
    if (a * a + b * b) ** .5 < catppuccin.NEUTRAL_CHROMA:
        return text

    def swap(m):
        found = long_hex(m.group(0))
        light, a, b = catppuccin.oklab(found)
        if (a * a + b * b) ** .5 < catppuccin.NEUTRAL_CHROMA and light > .93:
            return color
        return draw.PAPER if found == color else m.group(0)

    # the mark, and the gradients it may paint with, before the sheet
    before, mark = catppuccin.HEX.sub(swap, text[:sheet.start()]), catppuccin.HEX.sub(swap, text[sheet.end():])
    if (before, mark) == (text[:sheet.start()], text[sheet.end():]) or color not in before + mark:
        return text
    return (f"{before}{sheet.group(1)}{draw.PAPER}{sheet.group(3)}{sheet.group(4)}{draw.PAPER_EDGE}"
            f"{sheet.group(5)}{sheet.group(6) or ''}{mark}")


def recolor_tree(folder):
    count = 0
    for f in folder.rglob("*.svg"):
        if f.is_symlink() or not f.is_file():
            continue
        family = "teal" if f.name in TEAL else None
        text = f.read_text(errors="ignore")
        if f.name in FIT_IN_TILE:
            text = fit_in_tile(text, FIT_IN_TILE[f.name])
        if f.name in ON_MOCHA:
            text = onto_mocha(text)
        elif folder.parent.name == "apps":
            text = mocha_tile(text)
        elif folder.parent.name == "mimetypes" and PAPER_TYPES.match(f.name):
            text = paper_page(text)
        f.write_text(catppuccin.recolor_svg(text, everything=True, family=family))
        count += 1
    return count


def link_same_apps(folder):
    for name, known in SAME_APP.items():
        out = folder / f"{name}.svg"
        if (folder / f"{known}.svg").exists() and not (out.exists() or out.is_symlink()):
            out.symlink_to(f"{known}.svg")


def copy_app_icons(folder):
    for name, (source, others) in APP_COPIES.items():
        if (folder / source).is_file():
            (folder / name).unlink(missing_ok=True)
            shutil.copyfile((folder / source).resolve(), folder / name)
            for other in others:
                (folder / other).unlink(missing_ok=True)
                (folder / other).symlink_to(name)


def place_drawn(folder, drawn=DRAWN):
    """In place of the base's files or links, never through them (gwenview links to shotwell).
    Its own aliases link to the main names, and follow."""
    for f in sorted(drawn.iterdir(), key=lambda f: f.is_symlink()):
        out = folder / f.name
        if out.exists() or out.is_symlink():
            out.unlink()
        if f.is_symlink():
            out.symlink_to(os.readlink(f))
        else:
            shutil.copyfile(f, out)


def prune(theme):
    """Keep only the full-color folders, drop the base's monochrome ones and its cursors."""
    for child in theme.iterdir():
        if child.is_dir() and not any(k.split("/")[0] == child.name for k in KEPT):
            shutil.rmtree(child)
        elif child.name == "icon-theme.cache":
            child.unlink()
    for context in {k.split("/")[0] for k in KEPT}:
        for sub in (theme / context).iterdir() if (theme / context).is_dir() else []:
            if f"{context}/{sub.name}" not in KEPT:
                shutil.rmtree(sub) if sub.is_dir() and not sub.is_symlink() else sub.unlink()


def rewrite_index(theme, name, inherits, extra):
    ini = configparser.ConfigParser(interpolation=None, strict=False)
    ini.optionxform = str
    ini.read(theme / "index.theme")
    # Papirus's folders first: same names, our copies win over the full-color ones
    dirs = list(extra) + [d for d in ini["Icon Theme"].get("Directories", "").split(",") if (theme / d).is_dir()]
    for d, section in extra.items():
        ini[d] = section
    head = ini["Icon Theme"]
    head["Name"] = name.replace("-", " ")
    head["Comment"] = "Icons in Catppuccin colors, teal accent, with Papirus Dark's system icons"
    head["Inherits"] = inherits
    head["Directories"] = ",".join(dirs)
    head.pop("KDE-Extensions", None)  # the base's .svg only: the apps' own icons are often pictures
    for section in ini.sections():
        if section != "Icon Theme" and section not in dirs:
            ini.remove_section(section)
    with open(theme / "index.theme", "w") as f:
        ini.write(f, space_around_delimiters=False)


# Folders for the sizes where the large drawing blurs (the Places panel, lists): on the pixel
# grid, without the back's highlights, with the same emblem larger. Only at 1x: on a scaled
# screen, the icon loader takes the scalable drawing.
SMALL_FOLDERS = {
    16: {"l": 1, "r": 15, "t": 2, "b": 14, "tab": 6, "notch": 1, "front": 5, "rad": 1.5, "emblem": 8},
    22: {"l": 2, "r": 20, "t": 3, "b": 19, "tab": 8, "notch": 2, "front": 7, "rad": 2, "emblem": 11},
}
EMBLEM = re.compile(r'<g transform="translate\([^)]+\) scale\(([\d.]+),[\d.]+\) translate\([^"]*">(.*?)</g></svg>\s*$', re.S)
SHADOW_MARK = "stroke-opacity"  # the generated folders, which all have the shadow


def small_corners(r, b, l, rad):
    """Right and bottom sides and the left one back up, from the top right corner."""
    arc = f"a{rad} {rad} 0 0 1"
    return (f"{arc} {rad} {rad}V{b - rad}{arc} {-rad} {rad}H{l + rad}{arc} {-rad} {-rad}")


def small_folder(size, svg, name):
    g = SMALL_FOLDERS[size]
    l, r, t, b, rad = g["l"], g["r"], g["t"], g["b"], g["rad"]
    opened = "-open" in name or name == "folder-drag-accept"
    front = g["front"] + (1 if opened else 0)
    back = (f'M{l + rad} {t}H{l + g["tab"]}l{g["notch"]} {g["notch"]}H{r - rad}'
            f'{small_corners(r, b, l, rad)}V{t + rad}a{rad} {rad} 0 0 1 {rad} {-rad}z')
    panel = (f'M{l + rad} {front}H{r - rad}{small_corners(r, b, l, rad)}'
             f'V{front + rad}a{rad} {rad} 0 0 1 {rad} {-rad}z')
    # the shadow of the large folders, in whole pixels: one below, half of one around
    body = (f'<path d="{back}" fill="#11111b" fill-opacity=".38" transform="translate(0 1)"/>'
            f'<path d="{back}" fill="none" stroke="#11111b" stroke-opacity=".24"/>'
            f'<path d="{back}" fill="{draw.FOLDER_BACK}"/>')
    if opened:
        body += f'<rect x="{l + 2}" y="{t + g["notch"] + 1}" width="{r - l - 4}" height="{front - t - g["notch"]}" fill="#eff1f5"/>'
    body += f'<path d="{panel}" fill="{draw.FOLDER_FRONT}"/>'

    cx, cy, emblem = (l + r) / 2, (front + b) / 2, g["emblem"]
    if name == "user-desktop":  # a screen, in whole pixels
        w, h = (6, 4) if size == 16 else (9, 5)
        x, y = int(cx - w / 2), int(cy - (h + 2) / 2)
        body += (f'<g fill="none" stroke="#313244"><rect x="{x + .5}" y="{y + .5}" width="{w}" height="{h}" rx="1"/>'
                 f'<path d="M{x + 1} {y + h + 2.5}H{x + w}"/></g>')
    else:
        m = EMBLEM.search(svg)
        if m:
            # the emblem fills 20 of a 64 px canvas or 36 of a 128 px one: its own size, from its scale
            side = (20 if 'viewBox="0 0 64' in svg else 36) / float(m.group(1))
            body += (f'<g transform="translate({cx} {cy}) scale({emblem / side:.4f}) '
                     f'translate({-side / 2:.4f} {-side / 2:.4f})">{m.group(2)}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">{body}</svg>\n')


def draw_small_folders(theme):
    """Returns the new folders of the theme, for index.theme."""
    source = theme / "places/scalable"
    made = {f.stem: f.read_text(errors="ignore") for f in source.glob("*.svg")
            if not f.is_symlink() and SHADOW_MARK in f.read_text(errors="ignore")}
    dirs = {}
    for size in SMALL_FOLDERS:
        out = theme / f"places/{size}"
        out.mkdir()
        for name, svg in made.items():
            (out / f"{name}.svg").write_text(small_folder(size, svg, name))
        for link in source.glob("*.svg"):
            if link.is_symlink() and Path(os.readlink(link)).stem in made:
                (out / link.name).symlink_to(os.readlink(link))
        dirs[f"places/{size}"] = {"Size": str(size), "Context": "Places", "Type": "Fixed"}
    return dirs


# The file types seen every day, at the sizes of Dolphin's details view: a page on the pixel
# grid and one sign of its kind, in Catppuccin colors. The other types keep their large drawing.
SMALL_FILES = {16: {"l": 3, "r": 13, "t": 1, "b": 15, "fold": 3, "rad": 1},
               22: {"l": 4, "r": 18, "t": 2, "b": 20, "fold": 4, "rad": 1.5}}
FILE_KINDS = {
    "text": "text-plain text-x-generic text-x-log text-csv text-markdown text-x-markdown text-richtext",
    "code": "text-html text-css text-javascript text-json text-x-c text-x-csrc text-x-cpp text-x-c++src text-x-chdr "
            "text-x-c++hdr text-rust text-x-go text-x-java text-x-lua text-xml application-json application-xml "
            "application-javascript text-x-python text-x-cmake text-x-makefile",
    "script": "text-x-script application-x-shellscript text-x-shellscript",
    "pdf": "application-pdf",
    "image": "image image-generic image-x-generic image-png image-jpeg image-gif image-webp image-svg+xml image-bmp image-tiff",
    "video": "video-x-generic",
    "audio": "audio-x-generic",
    "archive": "application-zip application-x-tar application-x-7z-compressed application-gzip application-x-xz application-x-bzip "
               "application-x-compressed-tar application-x-rar application-x-archive package-x-generic",
    "program": "application-x-executable",
    "unknown": "unknown",
}


def small_file(size, kind):
    g = SMALL_FILES[size]
    l, r, t, b, fold, rad = g["l"], g["r"], g["t"], g["b"], g["fold"], g["rad"]
    arc = f"a{rad} {rad} 0 0 1"
    page = f"M{l + rad} {t}H{r - fold}L{r} {t + fold}V{b - rad}{arc} {-rad} {rad}H{l + rad}{arc} {-rad} {-rad}V{t + rad}{arc} {rad} {-rad}z"
    x, y, w = l + 2, t + fold + 1, r - l - 4
    h = b - y - 2
    cx, cy = x + w // 2, y + h // 2
    dark, paper, mocha, latte = draw.SURFACE0, draw.PAPER, draw.MOCHA, draw.LATTE
    fill = mocha["yellow"] if kind == "archive" else paper
    sign = ""
    if kind == "text":
        sign = "".join(f'<rect x="{x}" y="{y + i}" width="{w - (2 if i + 3 > h else 0)}" height="1" fill="{draw.SURFACE2}"/>'
                       for i in range(0, h, 2))
    elif kind in ("code", "script"):
        color = latte["blue"] if kind == "code" else dark
        s = max(2, w // 3)
        sign = (f'<path d="M{x + s} {cy - s + .5}L{x + .5} {cy + .5}L{x + s} {cy + s + .5}" fill="none" stroke="{color}"/>'
                + (f'<path d="M{x + w - s} {cy - s + .5}L{x + w - .5} {cy + .5}L{x + w - s} {cy + s + .5}" fill="none" stroke="{color}"/>'
                   if kind == "code" else f'<rect x="{x + s + 1}" y="{y + h - 2}" width="{w - s - 1}" height="1" fill="{color}"/>'))
    elif kind == "pdf":
        sign = (f'<rect x="{l}" y="{b - h + 1}" width="{r - l}" height="{h - 1}" fill="{latte["red"]}"/>'
                f'<rect x="{x}" y="{b - h + 3}" width="{w}" height="1" fill="{paper}"/>'
                f'<rect x="{x}" y="{b - h + 5}" width="{w - 2}" height="1" fill="{paper}"/>')
    elif kind == "image":
        sign = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{latte["mauve"]}"/>'
                f'<path d="M{x} {y + h}L{x + w // 3} {cy}L{x + w // 2 + 1} {cy + 2}L{x + w - 2} {cy - 1}L{x + w} {cy + 1}V{y + h}Z" fill="{mocha["lavender"]}"/>'
                f'<rect x="{x + w - 2}" y="{y + 1}" width="1" height="1" fill="{mocha["yellow"]}"/>')
    elif kind == "video":
        sign = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{dark}"/>'
                f'<path d="M{cx - 1} {cy - 2}v4.5l3.5 -2.25z" fill="{mocha["pink"]}"/>')
    elif kind == "audio":
        n = 1 if size == 16 else 1.5
        sign = (f'<path d="M{cx + 1} {y}h{2 * n}v{n}h{-n}V{y + h - 1}a{n * 1.6} {n * 1.3} 0 1 1 {-n} {-n}z" fill="{latte["pink"]}"/>')
    elif kind == "archive":
        sign = "".join(f'<rect x="{cx - (i % 2)}" y="{t + i}" width="1" height="1" fill="{latte["peach"]}"/>' for i in range(b - t - 1))
    elif kind == "program":
        sign = f'<path d="{draw.gear(cx, cy, w / 2, w / 2 - 1, 8, 1)}" fill="{dark}" fill-rule="evenodd"/>'
    elif kind == "unknown":
        sign = (f'<path d="M{cx - 2} {cy - 2}a2 2 0 1 1 3 1.7c-.8 .5-1 1-1 1.8" fill="none" stroke="{dark}"/>'
                f'<rect x="{cx - 1}" y="{cy + 3}" width="1" height="1" fill="{dark}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<path d="{page}" fill="#11111b" fill-opacity=".38" transform="translate(0 1)"/>'
            f'<path d="{page}" fill="none" stroke="#11111b" stroke-opacity=".24"/>'
            f'<path d="{page}" fill="{fill}"/>'
            f'<path d="M{r - fold} {t}v{fold}h{fold}z" fill="{draw.PAPER_EDGE}"/>{sign}</svg>\n')


def draw_small_files(theme):
    source = theme / "mimetypes/scalable"
    dirs = {}
    for size in SMALL_FILES:
        out = theme / f"mimetypes/{size}"
        out.mkdir()
        for kind, names in FILE_KINDS.items():
            for name in names.split():
                if (source / f"{name}.svg").exists():
                    (out / f"{name}.svg").write_text(small_file(size, kind))
        dirs[f"mimetypes/{size}"] = {"Size": str(size), "Context": "MimeTypes", "Type": "Fixed"}
    return dirs


def write_hidden_theme(theme, folder, title, comment, icons, rel, section):
    """A hidden theme beside Teal, that one app uses through its own config file ([Icons] Theme):
    its own icons (name -> file) in the folder rel, every other icon from Teal, which it inherits.

    KDE also tries shortened names within a theme, before going on to the next one: a page named
    preferences-system-time would find preferences-system here, whatever its own icon. So the
    longer names of these icons are kept here too, as they are in the themes behind."""
    shutil.rmtree(folder, ignore_errors=True)
    (folder / rel).mkdir(parents=True)
    for stem, f in icons.items():
        shutil.copyfile(f, folder / rel / f"{stem}.svg")
    source = configparser.ConfigParser(interpolation=None, strict=False)
    source.optionxform = str
    source.read(theme / "index.theme")
    prefixes = tuple(f"{stem}-" for stem in icons)
    sections = {rel: section}
    for root in (theme, PAPIRUS):
        for f in root.rglob("*.svg"):
            if f.stem in icons or not f.stem.startswith(prefixes) or not f.exists():
                continue
            there = f.parent.relative_to(root).as_posix()
            if root == PAPIRUS or there not in source:
                there = "apps/scalable"
            out = folder / there / f.name
            if not out.exists():
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(f, out)
                sections.setdefault(there, dict(source[there]) if there in source else
                                    {"Size": "64", "Context": "Applications", "Type": "Scalable",
                                     "MinSize": "16", "MaxSize": "512"})
    index = configparser.ConfigParser(interpolation=None)
    index.optionxform = str
    index["Icon Theme"] = {"Name": title, "Comment": comment, "Inherits": theme.name, "Hidden": "true",
                           "FollowsColorScheme": "true", "Directories": ",".join(sections)}
    for there, values in sections.items():
        index[there] = values
    with open(folder / "index.theme", "w") as f:
        index.write(f, space_around_delimiters=False)


def write_settings_theme(theme, name):
    """<name>-Settings: the tiles of the pages whose icon names Plasma also shows in the tray and
    on its logout and lock screens, and the sidebar's categories. Only System Settings uses it."""
    write_hidden_theme(theme, theme.parent / f"{name}-Settings", f"{name} Settings",
                       f"Icons for System Settings' sidebar, for {name}",
                       {f.stem: f for f in DRAWN_SETTINGS.glob("*.svg")}, "apps/scalable",
                       {"Size": "64", "Context": "Applications", "Type": "Scalable", "MinSize": "16", "MaxSize": "512"})


# Hardware without a monochrome symbol of its own name in Papirus: the one that stands for it
SHELL_SAME = {"preferences-desktop-keyboard": "input-keyboard", "preferences-desktop-mouse": "input-mouse",
              "input-touchscreen": "tablet", "monitor": "video-display", "video-television": "tv",
              "drive-harddisk-encrypted": "drive-harddisk", "processor": "cpu", "network-card": "network-wired",
              "network-rj45-female": "network-wired", "gnome-dev-wavelan": "network-wireless",
              "network_fs": "network-server", "preferences-system-bluetooth": "bluetooth"}


def write_shell_theme(theme, name):
    """<name>-Shell: Plasma's own. The tray's popups (Bluetooth, volume, battery, disks, KDE
    Connect) list hardware among the system's monochrome icons: there, the hardware is monochrome
    too, Papirus's symbols under their plain names; so are the night light and the theme in
    Brightness and Color, drawn as symbols (draw.SYMBOLS). Only plasmashell uses it; the names an
    app's launcher uses are taken out of it on each computer (localize.py), so the dock and the
    launcher keep their tiles."""
    symbols = theme / "16x16/symbolic/devices"
    have = {f.name.removesuffix("-symbolic.svg"): f for f in symbols.glob("*-symbolic.svg") if f.exists()}
    icons = dict(have)
    for main, design in draw.DEVICES.items():  # a drawing's other names share its symbol
        names = [Path(main).stem] + (design[1] if isinstance(design, tuple) else [])
        symbol = next((have[n] for n in names if n in have), None) or have.get(SHELL_SAME.get(names[0]))
        if symbol:
            icons.update({n: symbol for n in names if n not in have})
    icons.update({n: have[same] for n, same in SHELL_SAME.items() if same in have and n not in icons})
    icons.update({f.stem: f for f in DRAWN_SYMBOLS.glob("*.svg")})  # Teal's own drawings, as symbols
    write_hidden_theme(theme, theme.parent / f"{name}-Shell", f"{name} Shell",
                       f"Monochrome hardware for Plasma's panels and popups, for {name}", icons, "devices/symbolic",
                       {"Size": "16", "Context": "Devices", "Type": "Scalable", "MinSize": "8", "MaxSize": "256"})
    white_tray(theme, theme.parent / f"{name}-Shell")


# the tray's expander arrow; arrow-down is a link to pan-down in the theme, which every app uses
TRAY_ARROWS = {"arrow-down": "pan-down", "arrow-up": "pan-up", "arrow-left": "pan-start", "arrow-right": "pan-end"}
SCHEME_TEXT = re.compile(r'\s*class="ColorScheme-Text"')


def pure_white(text):
    """White where Plasma would put the scheme's text color (class ColorScheme-Text, currentColor)
    and where Mocha's text is written; the states (red, yellow, green) keep their classes."""
    def tag(m):
        t = m.group(0)
        if "ColorScheme-Text" in t:
            t = SCHEME_TEXT.sub("", t.replace("currentColor", "#ffffff"))
        return t
    return re.sub(PAPIRUS_COLORS_TEXT, "#ffffff", re.sub(r"<[^>]+>", tag, text), flags=re.I)


def white_tray(theme, shell):
    """In the tray, Papirus's icons in pure white, like the apps' own tray icons beside them,
    rather than in the text color. Only Plasma reads <name>-Shell: apps keep the text color."""
    source = configparser.ConfigParser(interpolation=None, strict=False)
    source.optionxform = str
    source.read(theme / "index.theme")
    index = configparser.ConfigParser(interpolation=None, strict=False)
    index.optionxform = str
    index.read(shell / "index.theme")
    dirs = index["Icon Theme"]["Directories"].split(",")
    for size in ("16x16", "22x22", "24x24"):
        made = {}
        for rel in (f"{size}/panel", f"{size}/symbolic/status"):
            for f in (theme / rel).iterdir() if (theme / rel).is_dir() else []:
                out = shell / rel / f.name
                if f.suffix == ".svg" and f.exists():
                    made[out] = (out if out.exists() else f).read_text(errors="ignore")
        for arrow, pan in TRAY_ARROWS.items():
            f = theme / size / "actions" / f"{pan}.svg"
            if f.exists():
                made[shell / size / "symbolic/actions" / f"{arrow}-symbolic.svg"] = f.read_text(errors="ignore")
        for out, text in made.items():
            out.parent.mkdir(parents=True, exist_ok=True)
            out.unlink(missing_ok=True)
            out.write_text(pure_white(text))
            rel = out.parent.relative_to(shell).as_posix()
            if rel not in dirs:
                dirs.append(rel)
                index[rel] = dict(source[rel]) if rel in source else {
                    "Size": size.split("x")[0], "Context": "Status", "Type": "Fixed"}
    index["Icon Theme"]["Directories"] = ",".join(dirs)
    with open(shell / "index.theme", "w") as f:
        index.write(f, space_around_delimiters=False)


def drop_system_copies(theme, dirs):
    """Papirus's sized drive and settings icons would be found first, at these sizes, instead of Teal's."""
    devices = [f.stem for f in DRAWN_DEVICES.glob("*.svg")]
    for d in dirs:
        for name in devices + [Path(n).stem for n in draw.SETTINGS_PAGES]:
            (theme / d / f"{name}.svg").unlink(missing_ok=True)
    # the apps' folder comes first: the base's copies of the devices would hide ours
    for name in devices:
        if not (DRAWN / f"{name}.svg").exists():
            (theme / "apps/scalable" / f"{name}.svg").unlink(missing_ok=True)


def main():
    theme, name = Path(sys.argv[1]), sys.argv[2]
    if not DRAWN.is_dir():  # Teal's own drawings are made, not kept in the repository
        draw.main()
    dirs = papirus_system_dirs()
    names = system_names(dirs)
    prune(theme)
    print(f"{drop_system_names(theme, names)} system icons left to Papirus")
    n = sum(recolor_tree(theme / d) for d in RECOLORED if (theme / d).is_dir())
    copy_app_icons(theme / "apps/scalable")
    place_drawn(theme / "apps/scalable")
    link_same_apps(theme / "apps/scalable")
    own = {Path(name).stem for name in draw.DESIGNS}  # their tile chosen already, but for a Mocha one
    print(f"{draw.tint_folder(theme / 'apps/scalable', own)} tiles in their app's color")
    place_drawn(theme / "places/scalable", drawn=DRAWN_PLACES)
    place_drawn(theme / "devices/scalable", drawn=DRAWN_DEVICES)
    small = draw_small_folders(theme) | draw_small_files(theme)
    copy_papirus(theme, dirs)
    drop_system_copies(theme, dirs)
    for d in OWN:  # filled on each computer by localize.py
        (theme / d).mkdir(parents=True)
    papirus_dirs = len(dirs)
    dirs |= OWN | small
    rewrite_index(theme, name, INHERITS.format(papirus=f"{name}-Papirus"), dirs)
    write_settings_theme(theme, name)
    write_shell_theme(theme, name)
    print(f"{name}: {n} icons recolored, {papirus_dirs} Papirus system folders")


if __name__ == "__main__":
    main()
