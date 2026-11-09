#!/usr/bin/env python3
"""Build the Teal icon theme from an Adwair install (install-adwair.sh -c mocha-teal -a):

- full-color icons (apps, file types, devices, categories): Adwair's, recolored with
  Catppuccin by generator/catppuccin.py, brands included. Teal is kept for what belongs to
  the system (folders, file manager, settings, software center), so the accent still means
  something; other apps take their own Catppuccin hue, leaning to the saturated Latte shades
  so they stay easy to tell apart in a dock;
- icons drawn for Teal (teal/draw.py): the terminal, settings, LibreOffice, the KDE,
  Qt and CachyOS tools Adwair gives a generic or borrowed icon (on each computer,
  localize.py puts the apps' own logos in their place, where the app is installed);
- monochrome icons (actions, statuses, tray, symbolic icons): Papirus-Dark's system folders,
  copied with Catppuccin colors (Mocha text instead of Papirus's gray, teal instead of its
  blue, Catppuccin red, yellow and green for states). GTK apps show these colors as they are,
  KDE apps recolor them with the color scheme. Adwair's own monochrome icons are removed, and
  so are its full-color icons named like a Papirus system icon (edit-find, bluetooth-active…).
  The copies sit inside the theme, not only in an inherited one: icon lookups shorten an
  unknown name inside a theme before moving on to the next one (bluetooth-active ->
  bluetooth), and would land on a full-color app icon of ours.
- tray: Papirus's tray icons for the system (network, battery, sound, notifications…) only;
  apps keep their own (Discord, Steam, KeePassXC…), except those in TRAY_PAPIRUS; localize.py
  links them, and Papirus as the fallback, on each computer.

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
# Teal's own icons, drawn by teal/draw.py, in place of Adwair's
DRAWN = Path(__file__).resolve().parent / "teal/apps"
DRAWN_PLACES = Path(__file__).resolve().parent / "teal/places"
DRAWN_DEVICES = Path(__file__).resolve().parent / "teal/devices"
# Adwair's logos that spill over their tile, brought inside it
FIT_IN_TILE = {"krita.svg": .82, "transmission.svg": .84}
INHERITS = "{papirus},Adwaita,AdwaitaLegacy,hicolor,breeze"
PAPIRUS = Path("/usr/share/icons/Papirus-Dark")
# Papirus-Dark's color scheme classes -> Catppuccin Mocha
PAPIRUS_COLORS = {"#dfdfdf": "#cdd6f4", "#4285f4": "#94e2d5", "#ff9800": "#f9e2af",
                  "#f44336": "#f38ba8", "#4caf50": "#a6e3a1", "#444444": "#1e1e2e"}


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
            if f.name.removesuffix(".svg") in names and f.name not in TEAL:
                f.unlink()
                dropped += 1
    return dropped


def fit_in_tile(text, scale):
    """Everything drawn after the tile (its last rounded rect), scaled around the center."""
    end = list(re.finditer(r'<rect\b[^>]*\brx="[^"]+"[^>]*/>', text))[-1].end()
    close = text.rindex("</svg>")
    return (f'{text[:end]}<g transform="translate(32 32) scale({scale}) translate(-32 -32)">'
            f'{text[end:close]}</g>{text[close:]}')


def recolor_tree(folder):
    count = 0
    for f in folder.rglob("*.svg"):
        if f.is_symlink() or not f.is_file():
            continue
        family = "teal" if f.name in TEAL else None
        text = f.read_text(errors="ignore")
        if f.name in FIT_IN_TILE:
            text = fit_in_tile(text, FIT_IN_TILE[f.name])
        f.write_text(catppuccin.recolor_svg(text, everything=True, family=family))
        count += 1
    return count


def place_drawn(folder, drawn=DRAWN):
    """In place of Adwair's files or links, never through them (gwenview links to shotwell).
    Adwair's own aliases link to the base names, and follow."""
    for f in sorted(drawn.iterdir(), key=lambda f: f.is_symlink()):
        out = folder / f.name
        if out.exists() or out.is_symlink():
            out.unlink()
        if f.is_symlink():
            out.symlink_to(os.readlink(f))
        else:
            shutil.copyfile(f, out)


def prune(theme):
    """Keep only the full-color folders, drop Adwair's monochrome ones and its cursors."""
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
    head["Comment"] = "Adwair and Papirus Dark in Catppuccin colors, teal accent"
    head["Inherits"] = inherits
    head["Directories"] = ",".join(dirs)
    head.pop("KDE-Extensions", None)  # Adwair's .svg only: the apps' own icons are often pictures
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


def main():
    theme, name = Path(sys.argv[1]), sys.argv[2]
    dirs = papirus_system_dirs()
    names = system_names(dirs)
    prune(theme)
    print(f"{drop_system_names(theme, names)} system icons left to Papirus")
    n = sum(recolor_tree(theme / d) for d in RECOLORED if (theme / d).is_dir())
    place_drawn(theme / "apps/scalable")
    place_drawn(theme / "places/scalable", drawn=DRAWN_PLACES)
    place_drawn(theme / "devices/scalable", drawn=DRAWN_DEVICES)
    small = draw_small_folders(theme)
    copy_papirus(theme, dirs)
    for d in OWN:  # filled on each computer by localize.py
        (theme / d).mkdir(parents=True)
    papirus_dirs = len(dirs)
    dirs |= OWN | small
    rewrite_index(theme, name, INHERITS.format(papirus=f"{name}-Papirus"), dirs)
    print(f"{name}: {n} icons recolored, {papirus_dirs} Papirus system folders")


if __name__ == "__main__":
    main()
