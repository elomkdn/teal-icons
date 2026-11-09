# Teal's rules

An icon enters the pack if it follows these rules or can be brought to them. `make/sheet.py`
shows the icons side by side and checks the whole pack.

## The signature

**The icons stay light; the accent gives the theme its character.** System Settings' pages and
the hardware are free pastel shapes, colored by family; apps, the dock and tools with a launcher keep their tiles. Teal belongs to the interface (selections,
switches, links) and to the folders. Apps and logos keep their own colors. CachyOS's update and package tools stay teal.

## What the free shapes' colors mean

| Color | Meaning |
|---|---|
| Silver | the system itself, text, motion, sound, search and the wallet |
| Mauve | the look |
| Pink | media |
| Lavender | the hardware |
| Blue | windows, apps and documents; Bluetooth; users |
| Sky | connections and the world |
| Yellow | light, energy and time |
| Green | security |
| Peach | your session and what calls for you |

## Three families

| Family | What | Drawing |
|---|---|---|
| Colored icons | apps, places, devices, file types | full color, below |
| Monochrome | actions, tray, status | Papirus Dark's, in the text color |
| Logos | an app's own mark | on the Mocha tile, in Catppuccin colors, recognizable first |

## The grid

- 64 px canvas, lit from above.
- App tile: 56 px, 13 px corners, from (4, 4), with a light rim on its top edge.
- Symbols stay within about 16 to 48 on the grid.
- Rounded joins and caps; lines are about 3 px on the grid, 4 for a single bold mark.

## Tiles

- An app: a tile of its own color, a paper symbol.
- A tool of the system with its own launcher: the Mocha tile, a silver symbol, details in the tile's color.
- A page of the system or the hardware: a free pastel shape, no tile, filling the grid, in its family's color (Mocha's shade toward Latte's); its details are real holes (SVG masks, Qt 6.7 or later).
- The system's two main apps may differ: Dolphin on a light tile, Settings with a silver gear on a lighter Mocha one.
- A tile's gradient is chosen by hand, top lighter than bottom: Mocha's shade to Latte's.

## Shadow

| Shape | Shadow |
|---|---|
| Tile | the soft picture below it (`shadow.xml`) |
| Folder, trash | stacked copies of its outline, offset by 1 px (`colors.py`, `draw.py`) |
| Page (a file type) | none, except at small sizes |

No SVG filters: Plasma's QtSvg may not draw them.

## Names shared with Plasma

Four of System Settings' pages use icon names that the tray and the logout and lock screens use
too. Their tiles live in the hidden `Teal-Settings` theme, which only System Settings uses, so
Plasma keeps its monochrome icons.

## Small sizes

At 16 and 22 px an icon is redrawn, not scaled: whole pixels, one idea, its emblem larger.
Folders and the everyday file types have these drawings; the shadow becomes one pixel below
and half of one around. They apply at 1x only.

## Color

Only Catppuccin colors. Dark shades come from Latte, light ones from Mocha. The rare icons that
are not drawn by hand are recolored by hue (`generator/catppuccin.py`).

## Order of work

Frequency first: the icons seen every day (the list in `sheet.py`) are drawn by hand; the long
tail is recolored and checked.
