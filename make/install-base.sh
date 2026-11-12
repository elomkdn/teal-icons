#!/usr/bin/env bash
#
# install-base.sh — lays out the base icons Teal is made from, in Catppuccin Mocha teal:
# src/ and its aliases (links/, same layout), then the folders and apps drawn in that color by
# make/generator/colors.py. make/catppuccin-theme.py makes Teal out of it.
#
# usage: make/install-base.sh <icons folder> <name>      (the base goes to <icons folder>/<name>)

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
GENERATED=$ROOT/make/generator
[ $# -eq 2 ] || { echo "usage: make/install-base.sh <icons folder> <name>" >&2; exit 1; }
DEST=$1/$2

mkdir -p "$DEST"
for dir in "$ROOT"/src/*/; do
  mkdir -p "$DEST/$(basename "$dir")"
  cp -a --remove-destination "$dir." "$DEST/$(basename "$dir")/"
done
cp -a --remove-destination "$ROOT/links/." "$DEST/"
sed "s/^Name=.*/Name=$2/" "$ROOT/src/index.theme" > "$DEST/index.theme"

# the folders and the apps in the accent, over the base's
mkdir -p "$DEST/places/scalable" "$DEST/apps/scalable"
cp -f --remove-destination "$GENERATED"/colors/mocha-teal/* "$DEST/places/scalable/"
cp -f --remove-destination "$GENERATED"/apps/mocha-teal/* "$DEST/apps/scalable/"
