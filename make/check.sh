#!/usr/bin/env bash
#
# check.sh — what must hold before Teal is published: the scripts parse, the drawings are valid
# pictures, the theme builds, every colored icon is on the grid (make/RULES.md), and Plasma's
# own theme answers as it should. Builds into a temporary folder, with a temporary home.
#
# Needs what the build needs (python3, Papirus) and librsvg, python-pillow, kiconthemes'
# kiconfinder6 for the last check (skipped without it).

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
failed=0
ok() { echo "  ✓ $1"; }
bad() { echo "  ✗ $1" >&2; failed=1; }

echo "Scripts"
for f in install.sh dist.sh make/install-base.sh make/check.sh; do bash -n "$f" || bad "$f"; done
python3 -I -m py_compile make/*.py make/teal/*.py make/generator/catppuccin.py && ok "they parse" || bad "a Python script does not parse"

echo "Drawings"
python3 -I make/teal/draw.py > /dev/null
python3 -I - <<'EOF' && ok "valid pictures" || bad "a drawing is not a valid picture"
import sys
from pathlib import Path
from xml.dom import minidom
bad = []
for f in Path("make/teal").rglob("*.svg"):
    if f.is_symlink():
        if not f.exists():
            bad.append(f"{f}: a link to nothing")
        continue
    try:
        minidom.parse(str(f))
    except Exception as error:
        bad.append(f"{f}: {error}")
if bad:
    sys.exit("\n".join(bad))
EOF

echo "Theme"
mkdir -p "$WORK/home" "$WORK/data/icons"
env -i HOME="$WORK/home" XDG_DATA_HOME="$WORK/data" XDG_CONFIG_HOME="$WORK/home/.config" PATH=/usr/bin:/bin \
  ./install.sh -p "$WORK/data/icons" > "$WORK/install.log" 2>&1 && ok "it builds and installs" || { cat "$WORK/install.log" >&2; bad "the build"; }
for theme in Teal Teal-Settings Teal-Shell; do
  [ -f "$WORK/data/icons/$theme/index.theme" ] || bad "$theme is missing"
done
[ -z "$(find "$WORK/data/icons/Teal" "$WORK/data/icons/Teal-Settings" "$WORK/data/icons/Teal-Shell" -xtype l | head -n 1)" ] &&
  ok "no link to nothing" || bad "links to nothing in the theme"
python3 -I - "$WORK/data/icons/Teal" <<'EOF' && ok "every folder of index.theme is there" || bad "index.theme names a missing folder"
import configparser, sys
from pathlib import Path
theme = Path(sys.argv[1])
ini = configparser.ConfigParser(interpolation=None, strict=False)
ini.read(theme / "index.theme")
missing = [d for d in ini["Icon Theme"]["Directories"].split(",") if d and not (theme / d).is_dir()]
if missing:
    sys.exit(" ".join(missing))
EOF

echo "The grid (make/RULES.md)"
python3 - "$WORK/data/icons/Teal" <<'EOF' && ok "hardware, places and file types are on it" || bad "icons out of the grid"
import sys
from pathlib import Path
sys.path.insert(0, "make")
import sheet
theme, odd = Path(sys.argv[1]), []
for folder in ("devices/scalable", "places/scalable", "mimetypes/scalable"):
    for f in sorted((theme / folder).glob("*.svg")):
        if f.is_symlink():
            continue
        size = sheet.measure(f)
        if size and (max(size) > 60 or max(size) < 44):
            odd.append(f"{folder}/{f.stem} {size}")
if odd:
    sys.exit("\n".join(odd))
EOF

echo "Plasma's own theme"
if command -v kiconfinder6 >/dev/null; then
  mkdir -p "$WORK/config"
  # an app's own theme, as plasmashellrc gives Plasma its own: kiconfinder6's config file
  printf '[Icons]\nTheme=Teal-Shell\n' | tee "$WORK/config/kiconfinderrc" > "$WORK/config/kiconfinder6rc"
  find_icon() { env XDG_DATA_HOME="$WORK/data" XDG_CONFIG_HOME="$WORK/config" XDG_CACHE_HOME="$WORK/cache" QT_QPA_PLATFORM=offscreen kiconfinder6 "$1" 2>/dev/null; }
  # monochrome hardware; the tray's longer names not cut down to it; everything else from Teal
  [[ $(find_icon audio-headphones) == */Teal-Shell/devices/symbolic/audio-headphones.svg ]] && ok "hardware is monochrome there" || bad "audio-headphones: $(find_icon audio-headphones)"
  [[ $(find_icon battery-080-charging) == */battery-080-charging.svg ]] && ok "longer names keep their own icon" || bad "battery-080-charging: $(find_icon battery-080-charging)"
  [[ $(find_icon folder-documents) == */Teal/places/scalable/folder-documents.svg ]] && ok "the rest comes from Teal" || bad "folder-documents: $(find_icon folder-documents)"
  # the tray in pure white, its arrow too; apps keep the text color
  white() { [[ $1 == */Teal-Shell/* ]] && grep -q '#ffffff' "$1" && ! grep -q 'ColorScheme-Text"' "$1"; }
  tray=$(find_icon network-wireless-100) arrow=$(find_icon arrow-down-symbolic)
  white "$tray" && white "$arrow" && ok "the tray is white" || bad "not white: $tray $arrow"
  ! grep -q '#ffffff' "$WORK/data/icons/Teal/22x22/panel/network-wireless-100.svg" && ok "apps keep the text color" || bad "Teal's own tray icons turned white"
  # at the menu's sizes, a tray copy under an app's name would be found before its tile
  kept=$(find "$WORK/data/icons/Teal" "$WORK/data/icons/Teal-Shell" -path '*/panel/printer.svg')
  [[ -z $kept ]] && ok "the printing settings keep their tile" || bad "printer in the tray folders: $kept"
else
  echo "  (kiconfinder6 is not installed: skipped)"
fi

[ "$failed" -eq 0 ] && echo "All good." || { echo "Something is wrong." >&2; exit 1; }
