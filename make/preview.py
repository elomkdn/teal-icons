#!/usr/bin/env python3
"""The README's picture, preview/teal.png: what Teal looks like, family by family.

Apps, then folders and hardware, System Settings' pages and file types, each under its name, on
the windows' color. Drawn from a theme as dist.sh builds it, before a computer's own logos take
their places (localize.py): the picture is the same everywhere.

usage: preview.py <built theme folder> <output.png>
  e.g. ./dist.sh && make/preview.py dist/teal-icons/share/icons/Teal preview/teal.png
"""
import io
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BACKGROUND, LABEL = "#1e1e2e", "#a6adc8"  # Mocha base, subtext 0
COLUMNS, CELL_W, CELL_H, ICON = 12, 147, 148, 76
FOLDERS = ("apps/scalable", "places/scalable", "devices/scalable", "mimetypes/scalable")

# name in the theme: what to call it
ROWS = """
system-file-manager:Files preferences-system:Settings plasmadiscover:Discover utilities-terminal:Konsole
utilities-system-monitor:System Monitor org.cachyos.hello:CachyOS Hello firefox:Firefox chromium:Chromium
brave:Brave thunderbird:Thunderbird telegram:Telegram discord:Discord

signal-desktop:Signal spotify:Spotify elisa:Elisa haruna:Haruna vlc:VLC mpv:mpv com.obsproject.Studio:OBS Studio
kdenlive:Kdenlive gimp:GIMP inkscape:Inkscape krita:Krita blender:Blender

gwenview:Gwenview okular:Okular kate:Kate libreoffice-writer:Writer libreoffice-calc:Calc steam:Steam lutris:Lutris
spectacle:Spectacle accessories-calculator:Calculator ark:Ark filelight:Filelight qbittorrent:qBittorrent

folder:Folder folder-documents:Documents folder-download:Downloads folder-music:Music user-trash-full:Trash
drive-harddisk:Disk drive-removable-media:USB stick media-optical:Disc computer-laptop:Laptop
audio-headphones:Headphones camera-photo:Camera printer-network:Printer

preferences-desktop-theme:Appearance preferences-desktop-wallpaper:Wallpaper preferences-desktop-font:Fonts
preferences-desktop-display:Display preferences-desktop-sound:Sound preferences-system-network:Network
preferences-system-bluetooth:Bluetooth preferences-desktop-accessibility:Accessibility
preferences-system-users:Users preferences-desktop-effects:Effects preferences-security-firewall:Firewall
preferences-system-power-management:Energy

text-plain:Text text-x-python:Python text-x-csrc:C text-html:HTML text-css:CSS application-json:JSON
application-pdf:PDF image-png:Picture video-x-generic:Video audio-x-generic:Music application-zip:Archive
application-x-executable:Program
"""


def find(theme, name):
    for folder in FOLDERS:
        if (theme / folder / f"{name}.svg").exists():
            return theme / folder / f"{name}.svg"
    return None


def render(svg, size):
    png = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), str(svg)], capture_output=True, check=True)
    return Image.open(io.BytesIO(png.stdout)).convert("RGBA")


def font(size):
    path = subprocess.run(["fc-match", "-f", "%{file}", "sans"], capture_output=True, text=True).stdout
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def main():
    theme, out = Path(sys.argv[1]), Path(sys.argv[2])
    # a name may hold spaces: the words up to the next "name:" belong to it
    rows = []
    for row in ROWS.strip().split("\n\n"):
        items = []
        for word in row.split():
            if ":" in word:
                items.append(word.split(":", 1))
            else:
                items[-1][1] += f" {word}"
        rows.append(items)
    scale = 2  # drawn at twice the size, then reduced: smoother than rsvg's small sizes
    picture = Image.new("RGB", (COLUMNS * CELL_W * scale, (len(rows) * CELL_H + 16) * scale), BACKGROUND)
    pen, face = ImageDraw.Draw(picture), font(14 * scale)
    missing = []
    for r, items in enumerate(rows):
        for c, (name, label) in enumerate(items[:COLUMNS]):
            svg = find(theme, name)
            if svg is None:
                missing.append(name)
                continue
            x = (c * CELL_W + (CELL_W - ICON) // 2) * scale
            y = (r * CELL_H + 30) * scale
            icon = render(svg, ICON * scale)
            picture.paste(icon, (x, y), icon)
            pen.text(((c * CELL_W + CELL_W // 2) * scale, y + (ICON + 10) * scale), label, fill=LABEL, font=face, anchor="ma")
    picture.resize((picture.width // scale, picture.height // scale), Image.LANCZOS).save(out, optimize=True)
    print(f"{out}: {sum(len(items) for items in rows) - len(missing)} icons"
          + (f"; not in the theme: {' '.join(missing)}" if missing else ""))


if __name__ == "__main__":
    main()
