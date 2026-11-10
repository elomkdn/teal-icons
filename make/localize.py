#!/usr/bin/env python3
"""Make an installed Teal at home on this computer (install.sh runs it; Python 3 alone):

- the apps' own logos, where the app is installed, in Catppuccin colors on Teal's tile, in
  place of Teal's drawing (SVG logos; PNG ones need Pillow, python-pillow);
- the apps' own icons a Teal icon would hide: KDE shortens an unknown name inside a theme
  before trying the next one (spotify-linux-32 -> spotify, qbittorrent-tray -> qbittorrent);
- Papirus Dark as the fallback for icons Teal does not have, without its tray icons (apps
  keep their own), if Papirus is installed: a hidden <name>-Papirus theme.
- in <name>-Shell, Plasma's own theme with monochrome hardware, the names an app's launcher uses
  are taken out: the dock and the launcher keep their tiles.

Nothing here is needed: without it, Teal shows its drawings and falls back to Adwaita.

usage: localize.py <folder holding the theme> <name>
"""
import configparser
import glob
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "generator"))
sys.path.insert(0, str(HERE / "teal"))
import draw  # noqa: E402

PAPIRUS = Path("/usr/share/icons/Papirus-Dark")
# KDE reads only SVGs in a scalable folder: pictures go in one of fixed size
OWN = {"own/scalable": {"Size": "32", "MinSize": "8", "MaxSize": "512", "Type": "Scalable", "Context": "Status"},
       "own/32": {"Size": "32", "Type": "Threshold", "Threshold": "512", "Context": "Status"}}


def link_own_icons(theme):
    """Links to the apps' own icons a Teal icon would hide by shortening. The icons apps
    name in their .desktop files are left to the shortening: the theme has their look."""
    ours = {f.rsplit(".", 1)[0] for _, _, files in os.walk(theme) for f in files}
    launchers = set()
    for d in ("/usr/share/applications", os.path.expanduser("~/.local/share/applications"),
              "/var/lib/flatpak/exports/share/applications"):
        for f in glob.glob(f"{d}/*.desktop"):
            launchers |= {line[5:].strip() for line in open(f, errors="ignore") if line.startswith("Icon=")}
    found = {}
    for root in ["/usr/share/icons/hicolor", "/usr/share/pixmaps", *glob.glob("/opt/*/icons"),
                 *glob.glob("/opt/*/*/icons")]:
        for f in Path(root).rglob("*"):
            if f.suffix in (".svg", ".png", ".xpm") and f.is_file():
                found.setdefault(f.stem, []).append(f)
    for d in OWN:
        shutil.rmtree(theme / d, ignore_errors=True)
        (theme / d).mkdir(parents=True)
    count = 0
    for name, files in found.items():
        parts = name.split("-")
        if name in ours or name in launchers or not any("-".join(parts[:i]) in ours for i in range(1, len(parts))):
            continue
        best = max(files, key=lambda f: (f.suffix == ".svg", f.stat().st_size))
        folder = theme / ("own/scalable" if best.suffix == ".svg" else "own/32")
        (folder / f"{name}{best.suffix}").symlink_to(best)
        count += 1
    return count


def keep_launchers_tiles(shell):
    """In Plasma's own theme, the hardware is monochrome; a name an app's launcher uses
    (printer, scanner…) leaves it, or the dock and the launcher would show the symbol."""
    icons = shell / "devices/symbolic"
    if not icons.is_dir():
        return
    launchers = set()
    for d in ("/usr/share/applications", os.path.expanduser("~/.local/share/applications"),
              "/var/lib/flatpak/exports/share/applications"):
        for f in glob.glob(f"{d}/*.desktop"):
            lines = open(f, errors="ignore").read().splitlines()
            if "NoDisplay=true" not in lines:  # a launcher nobody sees keeps nothing
                launchers |= {line[5:].strip() for line in lines if line.startswith("Icon=")}
    for name in launchers:
        (icons / f"{name}.svg").unlink(missing_ok=True)


def place_logos(folder):
    """Where the app is installed, its own logo on our tile, in place of our drawing."""
    count, missing_pillow = 0, set()
    for name, candidates in draw.LOGOS.items():
        out = folder / name
        logo = draw.find_logo(candidates)
        if logo is None:
            continue
        try:
            if name in draw.REBUILT_LOGOS:
                svg = draw.REBUILT_LOGOS[name](logo)
            else:
                svg = draw.logo_tile(logo, disc=draw.ROUND_LOGOS.get(name), square=name in draw.SQUARE_LOGOS)
            svg = draw.tinted(svg, candidates)
        except ImportError:  # a PNG logo, without Pillow
            missing_pillow.add(name)
            continue
        except Exception as error:  # a logo we cannot read keeps our drawing
            print(f"{logo}: {error}")
            continue
        if out.exists() or out.is_symlink():
            out.unlink()
        out.write_text(svg)
        count += 1
    if missing_pillow:
        print(f"{len(missing_pillow)} logos are pictures: they need python-pillow, Teal's drawings stay")
    return count


def papirus_without_tray(folder):
    """Papirus-Dark minus its tray folders, linked: the fallback for icons we do not have."""
    folder.mkdir()
    ini = configparser.ConfigParser(interpolation=None, strict=False)
    ini.optionxform = str
    ini.read(PAPIRUS / "index.theme")
    head = ini["Icon Theme"]
    kept = []
    for key in ("Directories", "ScaledDirectories"):
        dirs = [d for d in head.get(key, "").split(",") if d and not d.endswith("/panel")]
        head[key] = ",".join(dirs)
        kept += dirs
    for section in ini.sections():
        if section != "Icon Theme" and section not in kept:
            ini.remove_section(section)
    head["Name"] = folder.name.replace("-", " ")
    head["Comment"] = "Papirus Dark without its tray icons, for Teal"
    head["Hidden"] = "true"
    head.pop("Example", None)
    with open(folder / "index.theme", "w") as f:
        ini.write(f, space_around_delimiters=False)
    for top in sorted({d.split("/")[0] for d in kept}):
        (folder / top).symlink_to(PAPIRUS / top)


def main():
    root, name = Path(sys.argv[1]), sys.argv[2]
    theme = root / name
    logos = place_logos(theme / "apps/scalable")
    own = link_own_icons(theme)
    keep_launchers_tiles(root / f"{name}-Shell")
    papirus = root / f"{name}-Papirus"
    shutil.rmtree(papirus, ignore_errors=True)
    if (PAPIRUS / "index.theme").is_file():
        papirus_without_tray(papirus)
    print(f"{logos} apps' logos, {own} apps' own icons"
          + (", Papirus as fallback" if papirus.is_dir() else ", no Papirus: Adwaita as fallback"))


if __name__ == "__main__":
    main()
