#!/usr/bin/env python3
"""The contact sheet: Teal's icons side by side, where the odd one out shows.

- sheet.png: the icons of every day at 16, 22, 32 and 48 px, on the windows' color, on a light
  background and on a selection, drawn by QtSvg as Plasma draws them;
- on the terminal, a check of the whole pack against make/RULES.md: which shadow each colored
  icon has, and those that leave the grid.

usage: sheet.py <installed theme folder> <output folder>
"""
import collections
import io
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

QML = "/usr/lib/qt6/bin/qml"
SIZES = (16, 22, 32, 48)
BACKGROUNDS = ("#181825", "#eff1f5", "#61b6a9")
COLORED = ("apps/scalable", "mimetypes/scalable", "devices/scalable", "places/scalable")

DAILY = """
folder folder-open folder-documents folder-download folder-music folder-pictures folder-videos
user-desktop user-home user-trash user-trash-full folder-favorites folder-network folder-development
folder-recent folder-remote folder-templates folder-publicshare drive-harddisk drive-removable-media
media-optical computer phone
system-file-manager preferences-system utilities-terminal org.kde.konsole firefox zen-browser
spotify nuvio systemsettings plasmadiscover kate okular
gwenview ark spectacle org.kde.kcalc utilities-system-monitor
text-plain text-markdown text-html text-x-python text-x-script application-x-shellscript
application-json application-xml application-pdf image-png image-jpeg image-svg+xml image-gif
video-x-generic audio-x-generic application-zip application-x-tar
application-x-7z-compressed application-x-executable application-x-bittorrent unknown
preferences-desktop-theme preferences-desktop-wallpaper preferences-desktop-font preferences-desktop-display
preferences-desktop-sound preferences-system-network preferences-desktop-keyboard
preferences-desktop-mouse preferences-desktop-color preferences-desktop-locale preferences-system-users
""".split()


def find(theme, name, size):
    """As the icon loader would: the exact size first, then the scalable drawings."""
    for d in (f"places/{size}", f"mimetypes/{size}", "own/scalable", *COLORED, "categories/32"):
        f = theme / d / f"{name}.svg"
        if f.exists():
            return f
    return None


def contact_sheet(theme, out):
    found = [n for n in DAILY if find(theme, n, 48)]
    missing = [n for n in DAILY if n not in found]
    if missing:
        print("not in the theme:", " ".join(missing))
    columns = 8
    cell_w, cell_h = 142, 56
    rows = (len(found) + columns - 1) // columns
    items = []
    for band in range(len(BACKGROUNDS)):
        for i, name in enumerate(found):
            x0 = (i % columns) * cell_w + 6
            y0 = band * (rows * cell_h + 8) + (i // columns) * cell_h + 4
            x = x0
            for size in SIZES:
                items.append(f'Image {{ x:{x}; y:{y0 + (48 - size) / 2}; width:{size}; height:{size}; '
                             f'sourceSize.width:{size}; sourceSize.height:{size}; '
                             f'source:"file://{find(theme, name, size)}" }}')
                x += size + 4
    bands = "".join(f'Rectangle {{ y:{b * (rows * cell_h + 8)}; width:parent.width; height:{rows * cell_h + 8}; '
                    f'color:"{c}" }}' for b, c in enumerate(BACKGROUNDS))
    png = (out / "sheet.png").resolve()
    qml = (f'import QtQuick\nRectangle {{ id:r; width:{columns * cell_w + 8}; '
           f'height:{len(BACKGROUNDS) * (rows * cell_h + 8)}; color:"black"\n{bands}\n' + "\n".join(items) +
           f'\nTimer {{ interval:2500; running:true; onTriggered: r.grabToImage(function(i)'
           f'{{ i.saveToFile("{png}"); Qt.quit() }}) }}\n}}\n')
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "sheet.qml").write_text(qml)
        subprocess.run([QML, str(Path(tmp) / "sheet.qml")], check=True, timeout=120, capture_output=True,
                       env={"QT_QPA_PLATFORM": "offscreen", "QT_QUICK_BACKEND": "software", "PATH": "/usr/bin"})
    print(f"{png}: {len(found)} icons")


def shadow_of(text):
    if "data:image/png" in text and re.search(r"<image\b", text):
        return "picture"
    if 'stroke-opacity' in text and 'stroke-linejoin="round"' in text and 'fill="#000000" stroke="#000000"' in text:
        return "folder"
    return "none"


def measure(f):
    """Width and height of what shows at 64 px, without the soft shadow."""
    png = subprocess.run(["rsvg-convert", "-w", "64", "-h", "64", str(f)], capture_output=True, timeout=30)
    if png.returncode:
        return None
    alpha = Image.open(io.BytesIO(png.stdout)).convert("RGBA").getchannel("A").point(lambda a: 255 if a > 150 else 0)
    box = alpha.getbbox()
    return (box[2] - box[0], box[3] - box[1]) if box else None


def check(theme):
    for d in COLORED:
        files = sorted(f for f in (theme / d).glob("*.svg") if not f.is_symlink())
        with ThreadPoolExecutor(8) as pool:
            sizes = list(pool.map(measure, files))
        shadows = collections.Counter(shadow_of(f.read_text(errors="ignore")) for f in files)
        odd = [f.stem for f, s in zip(files, sizes) if s and (max(s) > 60 or max(s) < 44)]
        print(f"{d}: {len(files)} icons; shadow: {dict(shadows)}; out of the grid: {len(odd)}")
        if odd:
            print("   ", " ".join(odd[:40]) + (" …" if len(odd) > 40 else ""))


def main():
    theme, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    contact_sheet(theme, out)
    check(theme)


if __name__ == "__main__":
    main()
