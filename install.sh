#!/usr/bin/env bash
#
# install.sh — builds and installs the Teal icon theme (in Catppuccin colors, teal
# accent, with Papirus Dark's system icons) into ~/.local/share/icons
#
# Usage:
#   ./install.sh [OPTIONS]
#
# Options:
#   -p, --path PATH      Base installation path (default: ~/.local/share/icons)
#   -s, --set            After install, make it the icon theme. KDE Plasma and GNOME.
#   -u, --uninstall      The same as ./uninstall.sh: remove PATH/Teal and its hidden themes.
#   -h, --help           Show this help message
#
# Apps whose .desktop file names a picture instead of an icon (Nuvio, HP's tools) get a local copy of
# it naming the icon, in ~/.local/share/applications; ./uninstall.sh removes them.
#
# From a release archive, nothing else is needed. From a clone of the repository, Teal is
# built first, which needs Papirus (papirus-icon-theme) and python3. With python3, it is made
# at home on this computer: the apps' own logos and tray icons, and, if Papirus is installed,
# Teal-Papirus, hidden: Papirus Dark without its tray icons, for the icons Teal does not have.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
NAME="Teal"
PAPIRUS="/usr/share/icons/Papirus-Dark"
SET=0
UNINSTALL=0

# .desktop file -> icon name, for apps that name a picture
PICTURE_APPS=(nuvio.desktop:nuvio hplip.desktop:hp-logo hp-uiscan.desktop:hp-uiscan)
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

usage() {
  awk 'NR > 2 && /^#/ { sub(/^# ?/, ""); print; next } NR > 2 { exit }' "${BASH_SOURCE[0]}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--path) DEST="${2:?--path needs a folder}"; shift 2 ;;
    -s|--set) SET=1; shift ;;
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

if [[ $UNINSTALL -eq 1 ]]; then
  exec "$SCRIPT_DIR/uninstall.sh" -p "$DEST"
fi

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

if [[ -d "$SCRIPT_DIR/share/icons/$NAME" ]]; then
  # a release archive: the theme is built, Papirus's system icons included
  cp -a "$SCRIPT_DIR/share/icons/$NAME" "$SCRIPT_DIR/share/icons/$NAME-Settings" "$SCRIPT_DIR/share/icons/$NAME-Shell" "$STAGE/"
else
  # a clone of the repository: build it, with Papirus
  if [[ ! -f "$PAPIRUS/index.theme" ]]; then
    echo "Building Teal needs Papirus: sudo pacman -S papirus-icon-theme" >&2
    echo "(or install it from a release archive, which needs nothing)" >&2
    exit 1
  fi
  command -v python3 >/dev/null || { echo "Building Teal needs python3." >&2; exit 1; }
  echo "Building $NAME…"
  "$SCRIPT_DIR/install-base.sh" -c mocha-teal -a -n "$NAME" -p "$STAGE" >/dev/null
  python3 -I "$SCRIPT_DIR/make/teal/draw.py" >/dev/null  # Teal's own drawings, for the builder
  python3 -I "$SCRIPT_DIR/make/catppuccin-theme.py" "$STAGE/$NAME" "$NAME"
  # links to icons the theme leaves to Papirus, or to the base's removed monochrome folders
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
for t in "$NAME" "$NAME-Papirus" "$NAME-Settings" "$NAME-Shell"; do
  rm -rf "${DEST:?}/$t"
  [[ -d "$STAGE/$t" ]] || continue
  mv "$STAGE/$t" "$DEST/$t"
  if command -v gtk-update-icon-cache >/dev/null; then
    gtk-update-icon-cache -q -f "$DEST/$t" || true
  fi
done
name_icons
refresh
# System Settings alone uses the theme with its pages' tiles
if [[ "$DEST" == "${XDG_DATA_HOME:-$HOME/.local/share}/icons" ]] && command -v kwriteconfig6 >/dev/null; then
  kwriteconfig6 --file systemsettingsrc --group Icons --key Theme "$NAME-Settings"
  # and Plasma itself the one with monochrome hardware, for its tray's popups (after its next start)
  kwriteconfig6 --file plasmashellrc --group Icons --key Theme "$NAME-Shell"
fi
echo "Installed $DEST/$NAME."

if [[ $SET -eq 1 ]]; then
  theme="$NAME"
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
