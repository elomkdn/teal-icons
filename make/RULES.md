# Teal's rules

An icon enters the pack if it follows these rules or can be brought to them. `make/sheet.py`
shows the icons side by side and checks the whole pack.

## The signature

**The icons stay light; the accent gives the theme its character.** System Settings' pages and
the hardware are free pastel shapes, colored by family; apps, the dock and tools with a launcher keep their tiles. Teal belongs to the interface (selections,
switches, links) and to the folders. Apps and logos keep their own colors. CachyOS's update and package tools stay teal.

## The free shapes' colors

Each page or device has its own color: the hue of Papirus's icon of the same name, in its closest
Catppuccin color (`PAGE_COLORS` in `draw.py`), so that neighbors differ. Where Papirus has no hue,
the symbol's family applies (`FREE_FAMILIES`).

## Three families

| Family | What | Drawing |
|---|---|---|
| Colored icons | apps, places, devices, file types | full color, below |
| Monochrome | actions, tray, status | Papirus Dark's, in the text color |
| Logos | an app's own mark | on the Mocha tile, in Catppuccin colors, recognizable first |

## The grid

- 64 px canvas, lit from above.
- App tile: 56 px, 13 px corners, from (4, 4), with a light rim on its top edge.
- A tile's object stays within about 13 to 51 on the grid; it is drawn on the free shapes' grid (4 to 60) and brought onto the tile at .68.
- Rounded joins and caps; lines are about 3 px on the grid, 4 for a single bold mark.

## Tiles

- An app: a tile of its own color, a paper object built in planes, with its soft shadow.
- A tool of the system with its own launcher: the Mocha tile, a silver object in planes.
- A page of the system or the hardware: a free object, no tile, filling the grid, built in planes of its color (ink, deep, mid, main, pale), each a diagonal gradient leaning toward the neighboring hue. `pale` only ever sits on another plane, or it vanishes on a light background. A thing keeps its real colors where they are the point: a palette's paints, a window's buttons.
- The system's two main apps may differ: Dolphin on a light tile, Settings with a silver gear on a lighter Mocha one.
- A tile's gradient is diagonal, from its color to the neighboring hue, and stays soft: never all the way to Latte's.

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
