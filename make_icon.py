"""Generate difff.ico from the Lucide "diff" glyph.

Development-time helper only -- it needs Pillow, the application itself does
not.  Re-run it if you want to change the icon:

    pip install pillow
    python make_icon.py

Lucide "diff" (MIT licence, https://lucide.dev/icons/diff) is drawn on a
24x24 grid with a stroke width of 2 and round caps:

    M12 3v14      the vertical stroke
    M5 10h14      the horizontal stroke that completes the plus
    M5 21h14      the minus below it

The geometry here is exactly that.  The glyph sits on a transparent
background so it reads as a mark rather than a tile, and the two halves are
coloured -- green for the plus, red for the minus -- to match how the
application marks insertions and deletions, and because a two-tone glyph
stays readable at 16px where a monochrome one turns to mush.
"""

import os

from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "difff.ico")

SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)
SS = 8                      # supersampling factor

PLUS = (52, 199, 123, 255)       # insertion green, dark enough for light bars
MINUS = (239, 83, 80, 255)       # deletion red

# With no backdrop the glyph can fill the tile; leave just enough margin for
# the round caps not to touch the edge.
GLYPH_SCALE = 0.92


def draw_tile(size):
    """Render one square icon image at the given pixel size."""
    n = size * SS
    image = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Lucide's 24x24 grid is mostly padding: the inked area, stroke included,
    # only spans x 4..20 and y 2..22.  Scale to that box rather than to the
    # grid, so the mark is as large as it can be without a tile behind it.
    unit = n * GLYPH_SCALE / 20.0
    centre = n / 2.0

    def pt(x, y):
        return (centre + (x - 12) * unit, centre + (y - 12) * unit)

    # Lucide's stroke is 2 user units; below ~32px that rounds down to a
    # single hairline and the minus all but disappears, so hold a floor.
    width = max(int(round(2 * unit)), 2)
    for (x1, y1, x2, y2), colour in (
        ((12, 3, 12, 17), PLUS),     # M12 3v14
        ((5, 10, 19, 10), PLUS),     # M5 10h14
        ((5, 21, 19, 21), MINUS),    # M5 21h14
    ):
        draw.line([pt(x1, y1), pt(x2, y2)], fill=colour, width=width,
                  joint="curve")
        # Pillow's line() has butt caps; add the round caps Lucide specifies.
        for x, y in ((x1, y1), (x2, y2)):
            cx, cy = pt(x, y)
            r = width / 2.0
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=colour)

    return image.resize((size, size), Image.LANCZOS)


def main():
    tiles = [draw_tile(size) for size in SIZES]
    # save() writes every image passed in append_images as its own ICO entry.
    tiles[-1].save(OUT, format="ICO",
                   sizes=[(s, s) for s in SIZES],
                   append_images=tiles[:-1])
    print("wrote %s (%d bytes, sizes %s)"
          % (OUT, os.path.getsize(OUT), ", ".join(str(s) for s in SIZES)))


if __name__ == "__main__":
    main()
