"""Generate splash.png, the image PyInstaller's bootloader shows at startup.

Development-time helper only -- it needs Pillow, the application itself does
not.  Re-run it if you want to change the splash:

    pip install pillow
    python make_splash.py

The bootloader puts this on screen the instant the process starts, before
Python is initialised, which is exactly the dead period a one-file exe has to
cover: everything in the archive has to be unpacked to a temp folder before a
single line of the app runs.  thisthat.spec wires it up; thisthat_app.py takes
it down again once the real window has painted.

The image is the wordmark in its stylized form and nothing else -- ~~this~~
that, which is the whole idea of the app in two words: the old text struck
through, the new text underlined.  Pillow has no notion of text decoration, so
both rules are measured and drawn by hand below.  The icon used to sit above
it; the name says more than the mark does at this size, and on its own it has
room to be read.

There is no room reserved for a status line, because thisthat.spec asks for a
splash without one -- see the comment there.  What is on this image is all the
splash ever shows.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "splash.png")

WIDTH = 560
HEIGHT = 240

BG = (255, 255, 255)
INK = (24, 24, 24)            # same near-black as the icon
MUTED = (122, 122, 122)
BORDER = (220, 220, 220)

# Tops, not centres: the font's ascent puts a good deal of air above the
# letters, so these sit lower than the numbers suggest.  They are set so the
# *ink* -- the strike, the letters, the underline, the tagline -- balances in
# the card rather than the text boxes doing so.
WORDMARK_SIZE = 72
WORDMARK_TOP = 60
TAGLINE_SIZE = 15
TAGLINE_TOP = 156

TAGLINE = "single-pane text comparison"


def load_font(size, bold=True):
    """A UI font that also covers CJK, so the tagline can never tofu."""
    candidates = (
        ("YuGothB.ttc", "YuGothR.ttc"),
        ("meiryob.ttc", "meiryo.ttc"),
        ("segoeuib.ttf", "segoeui.ttf"),
        ("arialbd.ttf", "arial.ttf"),
    )
    for bold_name, regular_name in candidates:
        path = os.path.join(r"C:\Windows\Fonts",
                            bold_name if bold else regular_name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_wordmark(draw, font, top):
    """Draw "thisthat" centred, with "this" struck through and "that" ruled.

    Both halves are drawn as separate runs so their widths are known exactly;
    the decorations are then plain rectangles over and under those runs.
    """
    width_this = draw.textlength("this", font=font)
    width_that = draw.textlength("that", font=font)
    x = (WIDTH - (width_this + width_that)) / 2.0

    draw.text((x, top), "this", font=font, fill=INK)
    draw.text((x + width_this, top), "that", font=font, fill=INK)

    rule = max(2, round(WORDMARK_SIZE / 18.0))

    # Strike "this" through the middle of the x-height, not the middle of the
    # bounding box: "th" have ascenders, so the box's midpoint sits too high
    # and the rule would cut across the letters' shoulders.  "s" has neither
    # ascender nor descender, so its box *is* the x-height band.
    _, x_top, _, x_bottom = draw.textbbox((x, top), "s", font=font)
    middle = (x_top + x_bottom) / 2.0
    draw.rectangle((x, middle - rule / 2.0,
                    x + width_this, middle - rule / 2.0 + rule), fill=INK)

    # Underline "that" just below the baseline, clear of the descender depth
    # the font reports (there are none in "that", but the offset should not
    # depend on which letters happen to be in the word).
    ascent, _descent = font.getmetrics()
    baseline = top + ascent
    gap = max(3, round(WORDMARK_SIZE * 0.10))
    draw.rectangle((x + width_this, baseline + gap,
                    x + width_this + width_that, baseline + gap + rule),
                   fill=INK)


def draw_centred(draw, text, font, fill, top):
    width = draw.textlength(text, font=font)
    draw.text(((WIDTH - width) / 2.0, top), text, font=font, fill=fill)


def main():
    # RGB, not RGBA: an image with an alpha channel sends PyInstaller down its
    # transparent-splash path, which fills the background with magenta and
    # keys it out -- not what a plain white card wants.
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    # A hairline frame.  The splash is a borderless, undecorated window, so
    # without one it bleeds into a light desktop and stops looking like a card.
    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=BORDER, width=1)

    draw_wordmark(draw, load_font(WORDMARK_SIZE), WORDMARK_TOP)
    draw_centred(draw, TAGLINE, load_font(TAGLINE_SIZE, bold=False), MUTED,
                 TAGLINE_TOP)

    image.save(OUT, "PNG")
    print("wrote %s (%dx%d, %d bytes)"
          % (OUT, WIDTH, HEIGHT, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
