#!/usr/bin/env bash
#
# dist.sh — builds the release archive, dist/teal-icons.tar.gz: the theme built,
# Papirus's system icons included, and what installs it and makes it at home on each
# computer. It installs with ./install.sh, offline, with nothing else needed.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"
OUT=dist/teal-icons
rm -rf dist
mkdir -p "$OUT/share/icons" "$OUT/make/teal" "$OUT/make/generator"

./install-adwair.sh -c mocha-teal -a -n Teal -p "$OUT/share/icons" >/dev/null
python3 -I make/catppuccin-theme.py "$OUT/share/icons/Teal" Teal
find "$OUT" -xtype l -delete

cp install.sh README.md LICENSE "$OUT/"
cp make/localize.py "$OUT/make/"
cp make/teal/draw.py make/teal/shadow.xml "$OUT/make/teal/"
cp make/generator/catppuccin.py "$OUT/make/generator/"
tar -czf dist/teal-icons.tar.gz -C dist teal-icons
echo dist/teal-icons.tar.gz
