#!/usr/bin/env bash
#
# install.sh — builds and installs the Teal icon theme (Adwair and Papirus Dark in
# Catppuccin colors, teal accent) into ~/.local/share/icons
#
# Usage:
#   ./install.sh [OPTIONS]
#
# Options:
#   -p, --path PATH      Base installation path (default: ~/.local/share/icons)
#   -s, --set [VARIANT]  After install, make it the icon theme: light (the apps' own tiles,
#                        the default) or dark (every app on a Mocha tile). KDE Plasma and GNOME.
#   -u, --uninstall      Remove PATH/Teal, PATH/Teal-dark and PATH/Teal-Papirus.
#   -h, --help           Show this help message
#
# Apps whose .desktop file names a picture instead of an icon (Nuvio) get a local copy of
# it naming the icon, in ~/.local/share/applications; --uninstall removes them.
#
# Two themes are installed: Teal (the apps' own tiles) and Teal-dark (every app on a Mocha
# tile, inherits Teal). From a release archive, nothing else is needed. From a clone of the
# repository, they are built first, which needs Papirus (papirus-icon-theme) and python3.
# With python3, they are made at home on this computer: the apps' own logos and tray icons,
# and, if Papirus is installed, Teal-Papirus, hidden: Papirus Dark without its tray icons,
# for the icons Teal does not have.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
NAME="Teal"
PAPIRUS="/usr/share/icons/Papirus-Dark"
VARIANT=""
UNINSTALL=0

# .desktop file -> icon name, for apps that name a picture
PICTURE_APPS=(nuvio.desktop:nuvio)
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

usage() {
  awk 'NR > 2 && /^#/ { sub(/^# ?/, ""); print; next } NR > 2 { exit }' "${BASH_SOURCE[0]}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--path) DEST="${2:?--path needs a folder}"; shift 2 ;;
    -s|--set)
      if [[ "${2:-}" == light || "${2:-}" == dark ]]; then VARIANT="$2"; shift 2
      else VARIANT=light; shift; fi ;;
    -u|--uninstall|-r|--remove) UNINSTALL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

refresh() {
  # theme caches, and KDE's icon cache, which outlives the files
  rm -f "$HOME/.cache/icon-cache.kcache"
}

name_icons() {
  local entry file icon
  for entry in "${PICTURE_APPS[@]}"; do
    file="${entry%%:*}"; icon="${entry#*:}"
    [[ -f "/usr/share/applications/$file" && ! -e "$APPS/$file" ]] || continue
    mkdir -p "$APPS"
    sed -e "s|^Icon=.*|Icon=$icon|" -e '/^\[Desktop Entry\]/a X-Teal-Icon=true' \
      "/usr/share/applications/$file" > "$APPS/$file"
  done
}

unname_icons() {
  local entry file
  for entry in "${PICTURE_APPS[@]}"; do
    file="${entry%%:*}"
    if grep -q '^X-Teal-Icon=true' "$APPS/$file" 2>/dev/null; then rm -f "$APPS/$file"; fi
  done
}

if [[ $UNINSTALL -eq 1 ]]; then
  rm -rf "${DEST:?}/$NAME" "${DEST:?}/$NAME-dark" "${DEST:?}/$NAME-Papirus"
  unname_icons
  refresh
  echo "Removed $DEST/$NAME and $DEST/$NAME-dark. Pick another icon theme if Teal was in use."
  exit 0
fi

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

if [[ -d "$SCRIPT_DIR/share/icons/$NAME" ]]; then
  # a release archive: the themes are built, Papirus's system icons included
  cp -a "$SCRIPT_DIR/share/icons/$NAME" "$SCRIPT_DIR/share/icons/$NAME-dark" "$STAGE/"
else
  # a clone of the repository: build them, from Adwair and Papirus
  if [[ ! -f "$PAPIRUS/index.theme" ]]; then
    echo "Building Teal needs Papirus: sudo pacman -S papirus-icon-theme" >&2
    echo "(or install it from a release archive, which needs nothing)" >&2
    exit 1
  fi
  command -v python3 >/dev/null || { echo "Building Teal needs python3." >&2; exit 1; }
  echo "Building $NAME…"
  "$SCRIPT_DIR/install-adwair.sh" -c mocha-teal -a -n "$NAME" -p "$STAGE" >/dev/null
  python3 -I "$SCRIPT_DIR/make/catppuccin-theme.py" "$STAGE/$NAME" "$NAME"
  # links to icons the theme leaves to Papirus, or to Adwair's removed monochrome folders
  find "$STAGE" -xtype l -delete
fi

# at home on this computer: the apps' logos and tray icons, Papirus as the fallback
if command -v python3 >/dev/null; then
  python3 -I "$SCRIPT_DIR/make/localize.py" "$STAGE" "$NAME" || echo "(Teal stays as built)" >&2
else
  echo "Without python3, Teal shows its own drawings for the apps' logos." >&2
fi

# the old version stays in place until the new one is complete
mkdir -p "$DEST"
for t in "$NAME" "$NAME-dark" "$NAME-Papirus"; do
  rm -rf "${DEST:?}/$t"
  [[ -d "$STAGE/$t" ]] || continue
  mv "$STAGE/$t" "$DEST/$t"
  if command -v gtk-update-icon-cache >/dev/null; then
    gtk-update-icon-cache -q -f "$DEST/$t" || true
  fi
done
name_icons
refresh
echo "Installed $DEST/$NAME and $DEST/$NAME-dark."

if [[ -n "$VARIANT" ]]; then
  theme="$NAME"; [[ "$VARIANT" == dark ]] && theme="$NAME-dark"
  # Plasma's tool applies it to the running session; without a session (a TTY), the setting
  # is written for the next one
  changeicons=$(command -v /usr/lib/plasma-changeicons /usr/libexec/plasma-changeicons | head -n 1)
  if ! { [[ -n "$changeicons" ]] && sh -c '"$0" "$1"; exit $?' "$changeicons" "$theme" >/dev/null 2>&1; }; then
    kwriteconfig6 --file kdeglobals --group Icons --key Theme "$theme" 2>/dev/null || true
  fi
  if command -v gsettings >/dev/null; then
    gsettings set org.gnome.desktop.interface icon-theme "$theme" 2>/dev/null || true
  fi
  echo "Icon theme set to $theme."
else
  echo "Pick Teal in System Settings → Colors & Themes → Icons, or run again with --set."
fi
