"""User preferences for thisthat -- defaults, loading and saving.

Settings live in a small JSON file under the user's roaming profile
(%APPDATA%\\thisthat\\settings.json on Windows, ~/.config/thisthat
elsewhere).  Nothing here touches tkinter, so the palette can also be used by
the HTML exporter.
"""

import copy
import json
import os

APP_DIR_NAME = "thisthat"
# The folder the app used before it was renamed.  Anyone who ran it as difff
# has their colours sitting in there, and a rename is no reason to lose them,
# so load() reads it once if the current folder has nothing in it yet.
LEGACY_APP_DIR_NAME = "difff-desktop"
FILE_NAME = "settings.json"

# The four colours the user can change, in the order the settings dialog
# shows them: (key, label).
COLOUR_KEYS = (
    ("del_fg", "Deleted text"),
    ("del_bg", "Deleted highlight"),
    ("ins_fg", "Inserted text"),
    ("ins_bg", "Inserted highlight"),
)

# Everything a theme needs.  Only the four COLOUR_KEYS entries are editable;
# the rest follow light/dark and are not worth exposing.
#
# The diff colours are deliberately loud.  The muted pastels this shipped with
# read as tasteful and scan badly: at a glance down a long comparison the eye
# wants the changed runs to shout, and these do.  The ink over each highlight
# is a deep tint of the highlight itself rather than plain black, so a run
# stays legible as text and not just as a marked band.
#
# accent* is the blue worn by Compare alone.  Every other control in the
# window is grey on purpose: the one button that does the thing should be the
# one your eye lands on.
#
# verdict* is the band the "the two texts are identical" message sits on.  It
# is a tint of the same blue rather than a colour of its own: green and pink
# already mean "inserted" and "deleted" here, and a third hue would be a new
# word in the app's vocabulary for the sake of one sentence.  What that
# sentence needed was not a different colour but more of it -- a band carries
# across the window in a way coloured text alone does not -- and a borderless
# tint cannot be mistaken for a button, since every button in the app is
# field-coloured inside a one-pixel dark border.
DEFAULT_THEMES = {
    "light": {
        "bg": "#ffffff", "fg": "#1b1b1b", "sel": "#b9d4ff",
        "del_bg": "#ff73b9", "del_fg": "#42001f",
        "ins_bg": "#3eff73", "ins_fg": "#175e40",
        "muted": "#6b6b6b", "field": "#ffffff",
        "accent": "#0b63ce", "accent_fg": "#ffffff",
        "accent_active": "#094fa6",
        "verdict_bg": "#d8e8fb", "verdict_fg": "#08417f",
    },
    "dark": {
        "bg": "#1e1e1e", "fg": "#e6e6e6", "sel": "#3a5f92",
        "del_bg": "#ff80c0", "del_fg": "#400040",
        "ins_bg": "#68ff68", "ins_fg": "#316200",
        "muted": "#9a9a9a", "field": "#252525",
        "accent": "#2f7ff0", "accent_fg": "#ffffff",
        "accent_active": "#1f66cc",
        "verdict_bg": "#20344e", "verdict_fg": "#a8cdff",
    },
}

# Text size, in points, for the input boxes and the result pane.  The result
# pane keeps its own size: it is the pane you read rather than edit, so wanting
# it larger than the boxes you paste into is the normal case, not an oddity.
FONT_DEFAULT = 11
FONT_MIN = 7
FONT_MAX = 32

DEFAULTS = {
    "theme": "light",
    "font_size": FONT_DEFAULT,
    "result_font_size": FONT_DEFAULT,
    # Per-theme overrides of the COLOUR_KEYS entries; empty means "as shipped".
    "colours": {"light": {}, "dark": {}},
}


def settings_path(app_dir=APP_DIR_NAME):
    base = os.environ.get("APPDATA")
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, app_dir, FILE_NAME)


def _is_colour(value):
    return (isinstance(value, str) and len(value) == 7 and value[0] == "#"
            and all(c in "0123456789abcdefABCDEF" for c in value[1:]))


def _read(path):
    """The parsed contents of a settings file, or None if it is unusable."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def load():
    """Return the stored preferences, falling back to defaults on any problem.

    Bad or hand-edited settings must never stop the application starting, so
    every value is validated and anything unrecognised is quietly dropped.
    """
    prefs = copy.deepcopy(DEFAULTS)
    stored = _read(settings_path())
    # Nothing under the current name.  Before settling for the defaults, look
    # where the app kept its settings when it was called difff -- on an
    # upgraded machine that is where the user's colours still are.
    inherited = stored is None
    if inherited:
        stored = _read(settings_path(LEGACY_APP_DIR_NAME))
    if not isinstance(stored, dict):
        return prefs

    if stored.get("theme") in DEFAULT_THEMES:
        prefs["theme"] = stored["theme"]
    for key in ("font_size", "result_font_size"):
        size = stored.get(key)
        if isinstance(size, int) and FONT_MIN <= size <= FONT_MAX:
            prefs[key] = size

    colours = stored.get("colours")
    if isinstance(colours, dict):
        for name in DEFAULT_THEMES:
            entry = colours.get(name)
            if not isinstance(entry, dict):
                continue
            for key, _label in COLOUR_KEYS:
                if _is_colour(entry.get(key)):
                    prefs["colours"][name][key] = entry[key].lower()

    if inherited:
        # Write what was inherited forward under the current name, so this
        # happens exactly once and the old file stops mattering.  It is left
        # on disk rather than deleted: an older copy of the app may still be
        # installed, and settings are not ours to throw away.
        save(prefs)
    return prefs


def save(prefs):
    """Write preferences out.  Returns None on success, else the error."""
    path = settings_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(prefs, handle, indent=2)
            handle.write("\n")
    except OSError as exc:
        return exc
    return None


def palette(prefs, theme_name=None):
    """The full colour set for a theme, with the user's overrides applied."""
    name = theme_name or prefs.get("theme", "light")
    if name not in DEFAULT_THEMES:
        name = "light"
    colours = dict(DEFAULT_THEMES[name])
    colours.update(prefs.get("colours", {}).get(name, {}))
    return colours
