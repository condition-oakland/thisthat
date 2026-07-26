"""Generate thisthat.ico from the Lucide "diff" glyph.

Development-time helper only -- it needs Pillow, the application itself does
not.  Re-run it if you want to change the icon:

    pip install pillow
    python make_icon.py

Lucide "diff" (ISC licence, https://lucide.dev/icons/diff) is drawn on a
24x24 grid with a stroke width of 2 and round caps:

    M12 3v14      the vertical stroke
    M5 10h14      the horizontal stroke that completes the plus
    M5 21h14      the minus below it

The geometry here is exactly that: black ink on a rounded white tile, the
same treatment the other tools in this collection use.  One tile serves every
surface -- a white card reads against a dark title bar as well as a light one,
so there is no second, inverted file for the app to swap between.

Sharpness is the whole point of how this draws.  Every stroke in the glyph is
axis-aligned, so at each icon size the stroke width is rounded to a whole
number of pixels and each edge is snapped to a pixel boundary *before*
anything is rasterised.  Supersampling then happens at an exact multiple of
that grid and is resolved with a box filter, which leaves the snapped edges
untouched and only averages the round caps.  The result is an icon with no
half-lit pixels along a stroke at any size -- which is what "blurry" was.
"""

import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

NAME = "thisthat.ico"

# 16/32/48 are what Windows actually asks for at 100/150/200% scaling; the
# rest fill in the sizes Explorer's larger views and the alt-tab switcher
# reach for, so nothing ever has to resample.
SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)

SS = 8                        # supersampling factor, for the round caps only

BACKGROUND = (255, 255, 255, 255)
# Rounded, because a square white card is the one shape a Windows 11 taskbar
# has none of -- everything beside it is a rounded tile, and the odd one out
# reads as unfinished rather than as deliberate.  As a fraction of the tile,
# so the curve looks the same at 16 pixels as at 256.
CORNER_RADIUS = 0.18
# Not pure black: a hair off the extreme matches the near-black the app uses
# for body text and stops the mark looking like a hole in the tile.
INK = (24, 24, 24, 255)

# How much of the tile's height the glyph spans.  The rest is margin, which a
# solid tile needs -- without it the mark runs into the edge of the card and
# into whatever icon sits next to it in a taskbar.
GLYPH_HEIGHT = 0.74

# Below this stroke width a round cap is a fraction of a pixel and buys
# nothing but a grey smear at the end of each stroke, so square off instead.
ROUND_CAP_MIN_WIDTH = 4

# Lucide's paths, as (x1, y1, x2, y2) on the 24x24 grid.  All axis-aligned.
STROKES = (
    (12, 3, 12, 17),          # M12 3v14
    (5, 10, 19, 10),          # M5 10h14
    (5, 21, 19, 21),          # M5 21h14
)


def draw_tile(size):
    """Render one square icon image at the given pixel size."""
    n = size * SS
    # Transparent outside the card, so the corners are actually rounded and
    # not merely painted a colour that happens to suit today's wallpaper.
    image = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, n - 1, n - 1),
                           radius=CORNER_RADIUS * n, fill=BACKGROUND)

    # Lucide's 24x24 grid is mostly padding: with the stroke included the ink
    # spans x 4..20 and y 2..22.  Scale to that box, not to the grid, so the
    # margin below is the margin you actually see.
    unit = size * GLYPH_HEIGHT / 20.0
    centre = size / 2.0

    def px(x):
        return centre + (x - 12) * unit

    # Lucide's stroke is 2 user units.  Whole pixels only, and never thinner
    # than one, or the minus disappears at 16px.
    width = max(1, int(round(2 * unit)))
    half = width / 2.0
    caps = width >= ROUND_CAP_MIN_WIDTH

    # The tile is square and the glyph is centred on both axes, so the one
    # mapping serves x and y alike.
    for x1, y1, x2, y2 in STROKES:
        vertical = x1 == x2
        # Along the stroke: half a width past each end, which is the extent a
        # round cap covers.  Across it: exactly `width` pixels, so the two
        # edges cannot round apart into a stroke a pixel too fat or too thin.
        if vertical:
            near = int(round(px(y1) - half))
            far = int(round(px(y2) + half))
            edge = int(round(px(x1) - half))
            box = (edge, near, edge + width, far)
        else:
            near = int(round(px(x1) - half))
            far = int(round(px(x2) + half))
            edge = int(round(px(y1) - half))
            box = (near, edge, far, edge + width)

        left, top, right, bottom = (v * SS for v in box)
        if not caps:
            draw.rectangle((left, top, right - 1, bottom - 1), fill=INK)
            continue

        # With caps the body stops short of each end and two discs finish it,
        # so the corners come off exactly as Lucide draws them.  The body's
        # edges are still on the pixel grid; only the discs get averaged.
        radius = width * SS / 2.0
        if vertical:
            draw.rectangle((left, top + radius, right - 1, bottom - 1 - radius),
                           fill=INK)
            ends = ((left + radius, top + radius),
                    (left + radius, bottom - radius))
        else:
            draw.rectangle((left + radius, top, right - 1 - radius, bottom - 1),
                           fill=INK)
            ends = ((left + radius, top + radius),
                    (right - radius, top + radius))
        for cx, cy in ends:
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                         fill=INK)

    # BOX, not LANCZOS: a box filter is a plain average over each output
    # pixel's SSxSS block, so a block that lies wholly inside or outside a
    # snapped stroke stays pure.  LANCZOS reaches past the block and rings,
    # which is exactly the softness this is avoiding.
    return image.resize((size, size), Image.BOX)


def main():
    path = os.path.join(HERE, NAME)
    tiles = [draw_tile(size) for size in SIZES]
    # bitmap_format="bmp" writes each entry as an uncompressed DIB.  Pillow's
    # default is PNG-compressed entries, which Tk's own .ico reader cannot
    # parse -- it walks the file itself expecting a bitmap header, so
    # iconbitmap() either fails outright or hands Windows something it then
    # has to guess at.  DIB entries are what every Tk version understands.
    tiles[-1].save(path, format="ICO",
                   sizes=[(s, s) for s in SIZES],
                   append_images=tiles[:-1],
                   bitmap_format="bmp")
    print("wrote %s (%d bytes, sizes %s)"
          % (path, os.path.getsize(path), ", ".join(str(s) for s in SIZES)))


if __name__ == "__main__":
    main()
