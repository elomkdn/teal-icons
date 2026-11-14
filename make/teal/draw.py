#!/usr/bin/env python3
"""Draw Teal's own icons into make/teal/apps, places, devices and settings: which icon gets
which shape, and under which other names. The shapes are in shapes.py, the apps' own logos in
logos.py. The theme builder runs it, and copies these icons as they are, after the recoloring.

usage: draw.py
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # with python -I, the script's folder is not searched
import shapes  # noqa: E402
from logos import *  # noqa: E402,F401,F403
from shapes import *  # noqa: E402,F401,F403


def kde(*names):
    """An app's names: its own, and KDE's org.kde ones."""
    return [n for name in names for n in (name, f"org.kde.{name}")]


# name: design, or (design, other names linked to it)
DESIGNS = {
    "terminal.svg": terminal,
    # the system's main app: the folders it shows, teal, on the light Latte tile (the base's is a
    # bare folder, like those it shows)
    "system-file-manager.svg": (lambda: on_latte(folder),
                                ["dolphin", "file-manager", "org.gnome.Nautilus", "nautilus", "org.gnome.Files"]),
    "assistant.svg": (lambda: on_color(qt_badge(QT_A), "green"), ["qtassistant", "assistant-qt6", "assistant6"]),
    "designer.svg": (lambda: on_color(qt_badge(QT_D), "green"), ["qtdesigner", "designer-qt6", "designer6"]),
    "linguist.svg": (lambda: on_color(qt_badge(QT_L), "green"), ["qtlinguistic", "linguist-qt6", "linguist6"]),
    "qdbusviewer.svg": (lambda: on_color(qt_badge(QT_DV), "green"), ["qtdbusviewer", "qdbusviewer-qt6", "qdbusviewer6"]),
    "btrfs-assistant.svg": lambda: on_color(btrfs, "teal"),
    "org.cachyos.hello.svg": (cachyos_hello, ["cachyos-hello"]),
    "org.cachyos.KernelManager.svg": (lambda: on_mocha(kernel), ["cachyos-kernel-manager"]),
    "org.cachyos.scx-manager.svg": (lambda: on_color(quarter_gear, "teal"), ["scx-manager"]),
    "cachy-update-blue.svg": (lambda: on_mocha(refresh, "teal"), ["cachy-update", "arch-update", "system-software-update"]),
    # Shelly, the package manager: its own scallop rising out of a cardboard box, in its colors, on the light Latte tile
    "shelly.svg": lambda: on_latte(shell, "lavender"),
    "elisa.svg": (elisa, kde("elisa")[1:]),
    "haruna.svg": (haruna, kde("haruna")[1:]),
    "qv4l2.svg": (lambda: on_color(webcam, "sky"), ["qvidcap", "kamoso", "org.kde.kamoso", "cheese", "org.gnome.Cheese"]),
    "gwenview.svg": (lambda: on_color(lens, "pink"), kde("gwenview")[1:]),
    "filelight.svg": (lambda: on_color(rings, "blue"), kde("filelight")[1:] + ["baobab", "org.gnome.baobab"]),
    "kate.svg": (lambda: on_color(bird, "blue"), kde("kate")[1:]),
    "klassy-settings.svg": lambda: on_mocha(traffic_window),
    "preferences-desktop-theme-windowdecorations.svg": lambda: free_form(traffic_window),
    "preferences-system-windows.svg": (lambda: free_form(window_gear), ["preferences-system-windows-actions"]),
    "preferences-devices-cpu.svg": lambda: free_form(chip),
    # the base links it here too, and the apps' folder comes first
    "video-display.svg": lambda: free_form(display),
    "kvantum.svg": (kvantum_logo, ["kvantummanager"]),
    "okular.svg": (okular, kde("okular")[1:]),
    "qbittorrent.svg": lambda: on_color(qb, "blue"),
    "preferences-desktop-emoticons.svg": (lambda: on_color(smiley, "yellow"), ["org.kde.plasma.emojier"]),
    "utilities-system-monitor.svg": (pulse,
                                     kde("plasma-systemmonitor") + ["ksysguard", "gnome-system-monitor",
                                                                    "org.gnome.SystemMonitor"]),
    "LimineSnapperSync.svg": (lambda: on_color(snapshot_back, "teal"), ["limine-snapper-restore", "limine-snapper-sync"]),
    "micro.svg": lambda: on_color(mu, "lavender"),
    "io.github.Faugus.faugus-launcher.svg": (lambda: on_color(penguin, "mauve"), ["faugus-launcher"]),
    "spotify-linux-32.svg": (spotify_tray, [f"spotify-linux-{size}" for size in (16, 22, 24, 48, 64, 128, 256, 512)]),
    # its .desktop file names a picture, not an icon: install.sh adds a local copy naming this one
    "nuvio.svg": nuvio,
    "zapfast.svg": lambda: on_color(zap_bubble, "green"),
    "hypnotix.svg": hypnotix,
    # its .desktop file names a picture too (install.sh)
    "hp-uiscan.svg": lambda: on_color(scanner, "blue"),
}


PLACES = {
    "user-desktop.svg": (desktop_folder, ["folder-desktop"]),
    "user-trash.svg": (trash, ["user-trash-dark"]),
    "user-trash-full.svg": (lambda: trash(full=True), ["user-trash-full-dark"]),
}


DRIVE_NAMES = ["drive-harddisk-ieee1394", "drive-harddisk-root", "drive-harddisk-scsi", "drive-harddisk-solidstate",
               "drive-harddisk-system", "drive-harddisk-usb", "drive-partition", "harddrive", "device-harddisk-usb",
               "gnome-dev-harddisk", "gnome-dev-harddisk-1394", "gnome-dev-harddisk-usb", "gnome-fs-blockdev"]
USB_NAMES = ["drive-removable-media-usb", "drive-removable-media-usb-pendrive", "drive-removable-usb", "media-removable",
             "removable-media", "gnome-dev-removable", "gnome-dev-removable-usb", "gnome-dev-removable-1394",
             "gnome-dev-flashkey", "gnome-dev-flashdisk", "gnome-dev-unknown-usb", "usbpendrive_unmount"]
DISC_NAMES = ["media-optical-audio", "media-optical-blu-ray", "media-optical-cd", "media-optical-cd-r", "media-optical-dvd",
              "media-cdrom", "media-cdr", "media-cdrom-audio", "media-dvd", "media-dvdrw", "media-optical-cd-video",
              "media-optical-cdr", "media-optical-data", "media-optical-dvd-ram", "media-optical-dvd-rom",
              "media-optical-dvd-rw", "media-optical-dvd-video", "media-optical-mixed-cd", "media-optical-recordable",
              "media-optical-video", "media-write-cd", "media-write-dvd", "gnome-cd", "gnome-dev-cdrom-audio",
              "gnome-dev-disc-audio", "gnome-dev-disc-cdr", "gnome-dev-disc-cdrom", "gnome-dev-disc-cdrw",
              "gnome-dev-disc-dvdr", "gnome-dev-disc-dvdr-plus", "gnome-dev-disc-dvdram", "gnome-dev-disc-dvdrom",
              "gnome-dev-disc-dvdrw", "gnome-dev-dvd", "gnome-dev-dvd-alt", "cdrom_unmount", "cdwriter_unmount",
              "dvd_unmount"]
PRINTER_NAMES = ["printer-network", "cupsprinter", "cups-launcher", "gnome-dev-printer", "gnome-dev-printer-new",
                 "gnome-cups-manager", "kdeprint_printer", "kprinter", "kprinter4", "printmgr", "printer1", "printer-mdk",
                 "preferences-desktop-printer", "stock_printers", "xfce-printer", "yast-printer", "yast_printer",
                 "cs-printer", "gtklp", "foomatic-gui-logo"]
# the hardware in the Info Center and in the Places panel, among the devices
DEVICES = {
    "cpu.svg": lambda: free_form(chip),
    "video-display.svg": lambda: free_form(display),
    "audio-card.svg": lambda: free_form(sound_card),
    "computer.svg": (lambda: free_form(display), ["gnome-dev-computer", "computer-desktop"]),
    "drive-harddisk.svg": (lambda: free_form(hard_drive), DRIVE_NAMES),
    "drive-removable-media.svg": (lambda: free_form(usb_stick), USB_NAMES),
    "media-optical.svg": (lambda: free_form(disc), DISC_NAMES),
    "phone.svg": (lambda: free_form(phone), ["smartphone", "stock_cell-phone", "blueman-cellular", "blueman-smart-phone",
                                             "blueman-handheld", "phone-apple-iphone", "phone-motorola-droid",
                                             "gnome-phone-manager"]),
    "preferences-desktop-keyboard.svg": lambda: free_form(keyboard),
    "preferences-desktop-mouse.svg": lambda: free_form(mouse),
    # what the volume, Bluetooth and battery applets list, and KDE Connect
    "audio-headphones.svg": lambda: free_form(headphones),
    "audio-headset.svg": lambda: free_form(headset),
    "audio-input-microphone.svg": (lambda: free_form(microphone), ["microphone"]),
    "audio-speakers.svg": (lambda: free_form(speaker), ["blueman-loudspeaker"]),
    "soundcard.svg": (lambda: free_form(sound_card), ["yast_soundcard"]),
    "input-keyboard.svg": (lambda: free_form(keyboard), ["keyboard", "blueman-keyboard", "gnome-dev-keyboard",
                                                         "xfce4-keyboard", "system-config-keyboard", "kxkb"]),
    "input-mouse.svg": (lambda: free_form(mouse), ["mouse", "blueman-mouse", "blueman-pointing", "gnome-mouse", "cs-mouse",
                                                   "gnome-dev-mouse-ball", "gnome-dev-mouse-optical", "gnome-mouse-properties",
                                                   "gnome-settings-mouse", "xfce-mouse", "yast_mouse",
                                                   "preferences_desktop_mouse"]),
    "input-touchpad.svg": (lambda: free_form(touchpad), ["touchpad"]),
    "input-touchscreen.svg": lambda: free_form(touch_screen),
    "input-tablet.svg": lambda: free_form(drawing_tablet),
    "input-gamepad.svg": (lambda: free_form(gamepad), ["input-gaming"]),
    "computer-laptop.svg": (lambda: free_form(laptop), ["laptop", "blueman-laptop"]),
    "monitor.svg": (lambda: free_form(display), ["display", "blueman-desktop"]),
    "video-television.svg": lambda: free_form(television),
    "tablet.svg": (lambda: free_form(tablet), ["cs-tablet", "ebook-reader"]),
    "multimedia-player.svg": (lambda: free_form(media_player), ["music-player", "gnome-dev-ipod", "multimedia-player-ipod-touch",
                                                                "multimedia-player-apple-ipod-touch"]),
    "camera-photo.svg": (lambda: free_form(camera), ["camera", "blueman-camera", "camera_unmount"]),
    "camera-video.svg": lambda: free_form(video_camera),
    "camera-web.svg": lambda: free_form(webcam),
    "battery.svg": (lambda: free_form(battery), ["gnome-dev-battery"]),
    "bluetooth.svg": (lambda: free_form(bluetooth), ["blueman-device"]),
    "auth-sim.svg": lambda: free_form(sim_card),
    # printers and scanners
    "printer-network.svg": (lambda: free_form(printer), PRINTER_NAMES[1:]),
    "scanner.svg": (lambda: free_form(scanner), ["blueman-scanner"]),
    # the disks and cards of the Places panel, and the Info Center's hardware
    "drive-optical.svg": (lambda: free_form(optical_drive), ["drive-cdrom", "gnome-dev-cdrom"]),
    "drive-multidisk.svg": lambda: free_form(drives),
    "drive-harddisk-encrypted.svg": lambda: free_form(locked_drive),
    "media-flash.svg": (lambda: free_form(sd_card), ["media-flash-sd-mmc", "media-flash-cf", "media-flash-memory-stick",
                                                     "media-flash-ms", "media-flash-smart-media", "media-memory-sd",
                                                     "media-memory-sm", "gnome-dev-media-cf", "gnome-dev-media-ms",
                                                     "gnome-dev-media-sdmmc", "gnome-dev-media-sm"]),
    "memory.svg": lambda: free_form(memory),
    "processor.svg": (lambda: free_form(chip), ["firmware", "gnome-dev-pci"]),
    "network-card.svg": lambda: free_form(network_card),
    "network-modem.svg": (lambda: free_form(router), ["modem"]),
    "network-rj45-female.svg": (lambda: free_form(ethernet), ["gnome-dev-ethernet", "network-rj11-female"]),
    "gnome-dev-wavelan.svg": lambda: free_form(wifi),
    "network_fs.svg": lambda: free_form(network),
}


# the servers of older network settings: one shape for them all
SERVER_NAMES = [f"preferences-system-network-{name}" for name in (
    "server-boot", "server-dhcp", "server-dns", "server-ftp", "server-installation", "server-iscsi", "server-kerberos",
    "server-ldap", "server-mail", "server-nis", "server-share", "server-share-windows", "server-slp", "server-web",
    "iscsi", "nis", "ntp", "remote", "dsl", "wakeonlan")]


# System Settings' pages: the system's teal, like its tools
SETTINGS_PAGES = {
    "preferences-desktop-theme.svg": (lambda: free_form(palette_brush), ["theme-config"]),
    "preferences-desktop-wallpaper.svg": lambda: free_form(landscape),
    "preferences-desktop-font.svg": (lambda: free_form(letter), ["fonts"]),
    "preferences-desktop-display.svg": lambda: free_form(display),
    "preferences-desktop-sound.svg": lambda: free_form(sound_card),
    "preferences-system-network.svg": (lambda: free_form(network), ["network-workgroup"]),
    "preferences-desktop-color.svg": (lambda: free_form(color_circles), ["preferences-color"]),
    "preferences-desktop-locale.svg": lambda: free_form(globe),
    "preferences-system-users.svg": (lambda: free_form(people), ["cs-user"]),
    "preferences-desktop.svg": lambda: free_form(sliders),
    "tools-check-spelling.svg": lambda: free_form(spelling),
    "lighttable.svg": lambda: free_form(day_night),
    "system-run.svg": lambda: free_form(autostart),
    "redshift-status-on.svg": lambda: free_form(moon),
    "network-wireless-hotspot.svg": lambda: free_form(hotspot),
    "preferences-web-browser-shortcuts.svg": lambda: free_form(magnifier),
    "preferences-desktop-keyboard-shortcut.svg": lambda: free_form(key_combo),
    "network-wired-symbolic.svg": lambda: free_form(ethernet),
    "network-wireless-symbolic.svg": lambda: free_form(wifi),
    "emblem-music-symbolic.svg": lambda: free_form(music_note),
    "preferences-desktop-accessibility.svg": lambda: free_form(accessibility),
    "preferences-desktop-activities.svg": lambda: free_form(activities),
    "preferences-desktop-animations.svg": lambda: free_form(animations),
    "preferences-desktop-default-applications.svg": lambda: free_form(app_grid),
    "preferences-desktop-filetype-association.svg": lambda: free_form(page_check),
    "preferences-system-bluetooth.svg": lambda: free_form(bluetooth),
    "preferences-desktop-virtual.svg": lambda: free_form(desktops),
    "preferences-online-accounts.svg": lambda: free_form(cloud),
    "krunner.svg": lambda: free_form(search_bar),
    "preferences-desktop-gaming.svg": lambda: free_form(gamepad),
    "preferences-system-time.svg": lambda: free_form(clock),
    "preferences-desktop-effects.svg": lambda: free_form(sparkles),
    "preferences-desktop-font-installer.svg": lambda: free_form(letter_down),
    "preferences-desktop-icons.svg": lambda: free_form(icon_shapes),
    "preferences-security-firewall.svg": lambda: free_form(shield_check),
    "preferences-desktop-touchpad.svg": lambda: free_form(touchpad),
    "preferences-desktop-cursors.svg": lambda: free_form(arrow_cursor),
    "xorg.svg": lambda: free_form(x_mark),
    "preferences-system-network-connection.svg": lambda: free_form(two_arrows),
    "preferences-desktop-baloo.svg": lambda: free_form(page_search),
    "plasma-search.svg": lambda: free_form(magnifier),
    "preferences-desktop-feedback.svg": lambda: free_form(bubble),
    "preferences-system-network-proxy.svg": lambda: free_form(relay),
    "preferences-system-session-services.svg": lambda: free_form(two_gears),
    "preferences-desktop-theme-applications.svg": lambda: free_form(app_window),
    "preferences-desktop-plasma-theme.svg": lambda: free_form(desktop_panel),
    "preferences-system-tabbox.svg": lambda: free_form(stacked_windows),
    "preferences-desktop-tablet.svg": lambda: free_form(drawing_tablet),
    "preferences-desktop-thunderbolt.svg": lambda: free_form(bolt),
    "preferences-desktop-theme-global.svg": lambda: free_form(paint_roller),
    "preferences-desktop-user-password.svg": lambda: free_form(padlock),
    "ktip.svg": lambda: free_form(info),
    "preferences-system-login.svg": lambda: free_form(person_frame),
    "preferences-system-splash.svg": lambda: free_form(splash_screen),
    "preferences-desktop-touchscreen.svg": lambda: free_form(touch_screen),
    "preferences-system-power-management.svg": (lambda: free_form(battery), ["preferences-system-power", "preferences-power"]),
    # the last pages of System Settings and the Info Center the base still drew
    "preferences-desktop-user.svg": lambda: free_form(person),
    "preferences-system-network-sharing.svg": (lambda: free_form(share_nodes), ["preferences-system-sharing",
                                                                                "preferences-system-network-share"]),
    "kwin.svg": lambda: free_form(window_gear),
    # older names, which the apps' own settings windows still ask for
    "preferences-desktop-display-color.svg": lambda: free_form(color_circles),
    "preferences-desktop-display-nightcolor.svg": lambda: free_form(moon),
    "preferences-desktop-cryptography.svg": (lambda: free_form(padlock), ["preferences-desktop-screensaver"]),
    "preferences-system-privacy.svg": lambda: free_form(shield),
    "preferences-system-search.svg": (lambda: free_form(magnifier), ["preferences-desktop-accessibility-zoom"]),
    "preferences-system-services.svg": lambda: free_form(two_gears),
    "preferences-system-startup.svg": lambda: free_form(autostart),
    "preferences-system-session.svg": lambda: free_form(leave),
    "preferences-desktop-workspaces.svg": lambda: free_form(desktops),
    "preferences-desktop-online-accounts.svg": lambda: free_form(cloud),
    "preferences-desktop-applications.svg": (lambda: free_form(app_grid), ["preferences-desktop-apps"]),
    "preferences-desktop-assistive-technology.svg": lambda: free_form(accessibility),
    "preferences-bluetooth.svg": lambda: free_form(bluetooth),
    "preferences-system-windows-move.svg": (lambda: free_form(stacked_windows), ["preferences-system-windows-effect-flipswitch"]),
    "preferences-system-hotcorners.svg": lambda: free_form(screen_edges),
    "preferences-kde-connect.svg": lambda: free_form(phone),
    "preferences-system-network-ethernet.svg": lambda: free_form(ethernet),
    "preferences-system-network-server.svg": (lambda: free_form(server), SERVER_NAMES),
}
DESIGNS.update(SETTINGS_PAGES)
# Pages whose icon names the tray, the logout and the lock screens use too: their tiles live in a
# theme of their own, Teal-Settings, that only System Settings uses (systemsettingsrc).
SETTINGS_ONLY = {
    "input-keyboard-virtual.svg": lambda: free_form(virtual_keyboard),
    "preferences-desktop-display-randr.svg": lambda: free_form(two_screens),
    "preferences-desktop-notification-bell.svg": lambda: free_form(bell),
    "system-log-out.svg": lambda: free_form(leave),
    # the sidebar's categories, and the pages named like an app or the launcher's menu
    "applications-all.svg": lambda: free_form(app_grid),
    "kwalletmanager.svg": lambda: free_form(wallet),
    "preferences-desktop-gestures-screenedges.svg": lambda: free_form(screen_edges),
    "preferences-desktop-gestures-touch.svg": lambda: free_form(swipe),
    "preferences-desktop-multimedia.svg": lambda: free_form(media_frame),
    "preferences-desktop-peripherals.svg": lambda: free_form(plug),
    "preferences-desktop-search.svg": lambda: free_form(magnifier),
    "preferences-security.svg": lambda: free_form(shield),
    "preferences-system-disks.svg": lambda: free_form(hard_drive),
}
# Plasma's popups show these pages' icons among monochrome ones (the night light and the theme, in
# Brightness and Color): their symbols, in Teal-Shell, that only plasmashell uses.
SYMBOLS = {"redshift-status-on.svg": moon, "lighttable.svg": day_night}


def write_all(designs, out):
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir()
    for name, design in designs.items():
        design, aliases = design if isinstance(design, tuple) else (design, [])
        shapes._page = Path(name).stem  # the icon being written, for its own color (free_form)
        (out / name).write_text(design())
        for alias in aliases:
            (out / f"{alias}.svg").symlink_to(name)


def main():
    SHADOW.write_text(shadow())
    write_all(DESIGNS, HERE / "apps")
    write_all(PLACES, HERE / "places")
    write_all(DEVICES, HERE / "devices")
    write_all(SETTINGS_ONLY, HERE / "settings")
    write_all({name: lambda glyph=glyph: symbolic(glyph) for name, glyph in SYMBOLS.items()}, HERE / "symbols")
    print(f"{len(DESIGNS)} icons in {HERE / 'apps'}, {len(PLACES)} in {HERE / 'places'}, "
          f"{len(DEVICES)} in {HERE / 'devices'}")


if __name__ == "__main__":
    main()
