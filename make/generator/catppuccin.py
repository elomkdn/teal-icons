#!/usr/bin/env python3
"""Recolor the base icons with Catppuccin shades.

- Neutrals (whites, paper, grays, blacks) follow one continuous ramp, from Mocha's crust
  to Latte's base, so gradients and shading keep their modeling: dark parts in Mocha
  tones, light parts in Latte tones.
- The base's own colors (its signature blue, the colored templates, the GNOME palette)
  take the Catppuccin color of the same hue: dark shades in its Latte version, light
  shades in its Mocha version.
- Any other color is a brand color and stays as it is, except with --all (file types,
  places, devices: no brands there), where every color takes its Catppuccin hue.

With --family=<name> (e.g. teal), every hue goes to that Catppuccin color instead.

usage: catppuccin.py [--all] [--family=<name>] <source svg>... <output folder>
"""
import math
import re
import sys
from pathlib import Path

LATTE = {"rosewater": "#dc8a78", "flamingo": "#dd7878", "pink": "#ea76cb", "mauve": "#8839ef",
         "red": "#d20f39", "maroon": "#e64553", "peach": "#fe640b", "yellow": "#df8e1d",
         "green": "#40a02b", "teal": "#179299", "sky": "#04a5e5", "sapphire": "#209fb5",
         "blue": "#1e66f5", "lavender": "#7287fd"}
MOCHA = {"rosewater": "#f5e0dc", "flamingo": "#f2cdcd", "pink": "#f5c2e7", "mauve": "#cba6f7",
         "red": "#f38ba8", "maroon": "#eba0ac", "peach": "#fab387", "yellow": "#f9e2af",
         "green": "#a6e3a1", "teal": "#94e2d5", "sky": "#89dceb", "sapphire": "#74c7ec",
         "blue": "#89b4fa", "lavender": "#b4befe"}
# accent families an icon color may land on (rosewater, flamingo and maroon are too close to
# their neighbors to tell apart from a hue)
FAMILIES = ("red", "peach", "yellow", "green", "teal", "sky", "blue", "lavender", "mauve", "pink")
# neutral ramp, dark to light: Mocha's crust to overlay, then Latte's overlay to base
RAMP = ["#11111b", "#181825", "#1e1e2e", "#313244", "#45475a", "#585b70", "#6c7086", "#7f849c",
        "#9399b2", "#9ca0b0", "#acb0be", "#bcc0cc", "#ccd0da", "#dce0e8", "#e6e9ef", "#eff1f5"]
# The base's own colors: GNOME palette, its signature blue and its colored templates
BASE_COLORS = {
    "#99c1f1", "#62a0ea", "#3584e4", "#1c71d8", "#1a5fb4", "#8ff0a4", "#57e389", "#33d17a",
    "#2ec27e", "#26a269", "#f9f06b", "#f8e45c", "#f6d32d", "#f5c211", "#e5a50a", "#ffbe6f",
    "#ffa348", "#ff7800", "#e66100", "#c64600", "#f66151", "#ed333b", "#e01b24", "#c01c28",
    "#a51d2d", "#dc8add", "#c061cb", "#9141ac", "#813d9c", "#613583",
    "#0e71de", "#25c9ff", "#26a16a", "#ff5c5c", "#b81e31", "#ffb200", "#f54800", "#fff63f",
    "#ffc30d", "#ff5cbc", "#d51683", "#438de6", "#a4caee",
}
NEUTRAL_CHROMA = 0.03
# how far an app's lightest shade goes from the Latte color toward the Mocha one
LATTE_REACH = 0.7


def rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def hexcolor(c):
    return "#" + "".join(f"{round(min(max(v, 0), 1) * 255):02x}" for v in c)


def oklab(h):
    lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb(h)]
    l = 0.4122214708 * lin[0] + 0.5363325363 * lin[1] + 0.0514459929 * lin[2]
    m = 0.2119034982 * lin[0] + 0.6806995451 * lin[1] + 0.1073969566 * lin[2]
    s = 0.0883024619 * lin[0] + 0.2817188376 * lin[1] + 0.6299787005 * lin[2]
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def mix(a, b, t):
    return hexcolor([x + (y - x) * t for x, y in zip(rgb(a), rgb(b))])


RAMP_L = [oklab(c)[0] for c in RAMP]


def neutral(h):
    """Same place on the ramp as on black-to-white."""
    lo, hi = RAMP_L[0], RAMP_L[-1]
    target = lo + oklab(h)[0] * (hi - lo)
    for i in range(len(RAMP) - 1):
        if target <= RAMP_L[i + 1]:
            t = (target - RAMP_L[i]) / (RAMP_L[i + 1] - RAMP_L[i])
            return mix(RAMP[i], RAMP[i + 1], max(0, min(1, t)))
    return RAMP[-1]


def hue(h):
    _, a, b = oklab(h)
    return math.degrees(math.atan2(b, a)) % 360


def accent(h, family=None):
    """Catppuccin color of the same hue, from Latte (dark) to Mocha (light)."""
    def distance(f):
        d = abs(hue(MOCHA[f]) - hue(h)) % 360
        return min(d, 360 - d)
    # a given family (the system's teal) spans the whole range; other hues lean to Latte's
    # saturated shades, so apps stay easy to tell apart from each other and from the system
    reach = 1 if family else LATTE_REACH
    family = family or min(FAMILIES, key=distance)
    dark, light = LATTE[family], MOCHA[family]
    t = (oklab(h)[0] - 0.45) / (0.85 - 0.45)  # the base's dark shades sit near 0.45, its light ones near 0.85
    if t < 0:  # darker than the Latte version: toward Mocha's crust, a little
        return mix(dark, "#11111b", min(0.5, -t))
    return mix(dark, light, min(t, 1) * reach)  # no lighter than the Mocha version, which would wash out


# colors already in the palettes (Catppuccin neutrals are slightly blue: not to be taken for hues)
CATPPUCCIN = set(LATTE.values()) | set(MOCHA.values()) | set(RAMP) | {
    "#cdd6f4", "#bac2de", "#a6adc8", "#4c4f69", "#5c5f77", "#6c6f85"}


def recolor(h, everything=False, family=None):
    h = h.lower()
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    if h in CATPPUCCIN:
        return h
    _, a, b = oklab(h)
    if math.hypot(a, b) < NEUTRAL_CHROMA:
        return neutral(h)
    if everything or h in BASE_COLORS:
        return accent(h, family)
    return h


HEX = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def recolor_svg(text, everything=False, family=None):
    return HEX.sub(lambda m: recolor(m.group(0), everything, family), text)


def main():
    args = sys.argv[1:]
    everything = "--all" in args
    family = next((a.split("=", 1)[1] for a in args if a.startswith("--family=")), None)
    *sources, out = [a for a in args if a != "--all" and not a.startswith("--family=")]
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for src in map(Path, sources):
        (out / src.name).write_text(recolor_svg(src.read_text(errors="ignore"), everything, family))


if __name__ == "__main__":
    main()
