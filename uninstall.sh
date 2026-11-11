#!/usr/bin/env bash
#
# uninstall.sh — removes the Teal icon theme for your user: PATH/Teal and its hidden themes
# (Teal-Papirus, Teal-Settings, Teal-Shell), the icon themes System Settings and Plasma were
# given, and the local copies of .desktop files the installer made to name Teal's icons.
# If Teal is the icon theme in use, Breeze Dark takes its place.
#
# Usage:
#   ./uninstall.sh [OPTIONS]
#
# Options:
#   -p, --path PATH      Base installation path (default: ~/.local/share/icons)
#   -h, --help           Show this help message

set -euo pipefail

DEST="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
NAME="Teal"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
FALLBACK="breeze-dark"

usage() {
  awk 'NR > 2 && /^#/ { sub(/^# ?/, ""); print; next } NR > 2 { exit }' "${BASH_SOURCE[0]}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--path) DEST="${2:?--path needs a folder}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

# Teal in use: Breeze Dark first, so nothing points to a theme that is gone
if [[ "$(kreadconfig6 --file kdeglobals --group Icons --key Theme 2>/dev/null)" == "$NAME" ]]; then
  changeicons=$(command -v /usr/lib/plasma-changeicons /usr/libexec/plasma-changeicons | head -n 1 || true)
  if ! { [[ -n "$changeicons" ]] && sh -c '"$0" "$1"; exit $?' "$changeicons" "$FALLBACK" >/dev/null 2>&1; }; then
    kwriteconfig6 --file kdeglobals --group Icons --key Theme "$FALLBACK" 2>/dev/null || true
  fi
  echo "Icon theme set to $FALLBACK."
fi
if command -v gsettings >/dev/null &&
    [[ "$(gsettings get org.gnome.desktop.interface icon-theme 2>/dev/null)" == "'$NAME'" ]]; then
  gsettings reset org.gnome.desktop.interface icon-theme 2>/dev/null || true
fi

rm -rf "${DEST:?}/$NAME" "${DEST:?}/$NAME-Papirus" "${DEST:?}/$NAME-Settings" "${DEST:?}/$NAME-Shell"

# System Settings' own icon theme, Teal-Settings, and Plasma's, Teal-Shell
if command -v kwriteconfig6 >/dev/null; then
  kwriteconfig6 --file systemsettingsrc --group Icons --key Theme --delete || true
  kwriteconfig6 --file plasmashellrc --group Icons --key Theme --delete || true
fi

# the local copies of .desktop files made to name Teal's icons, marked as Teal's
{ grep -l '^X-Teal-Icon=true' "$APPS"/*.desktop 2>/dev/null || true; } | xargs -r rm -f

# KDE's icon cache, which outlives the files
rm -f "$HOME/.cache/icon-cache.kcache"

echo "Removed $DEST/$NAME."
