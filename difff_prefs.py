"""User preferences for difff desktop -- defaults, loading and saving.

Settings live in a small JSON file under the user's roaming profile
(%APPDATA%\\difff-desktop\\settings.json on Windows, ~/.config/difff-desktop
elsewhere).  Nothing here touches tkinter, so the palette can also be used by
the HTML exporter.
"""

import copy
import json
import os

APP_DIR_NAME = "difff-desktop"
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
DEFAULT_THEMES = {
    "light": {
        "bg": "#ffffff", "fg": "#1b1b1b", "sel": "#b9d4ff",
        "del_bg": "#ffd9dc", "del_fg": "#8b1a24",
        "ins_bg": "#d6f2d8", "ins_fg": "#14612a",
        "muted": "#6b6b6b", "field": "#ffffff",
    },
    "dark": {
        "bg": "#1e1e1e", "fg": "#e6e6e6", "sel": "#3a5f92",
        "del_bg": "#55232a", "del_fg": "#ffb3bb",
        "ins_bg": "#1f4a2c", "ins_fg": "#a8e6b4",
        "muted": "#9a9a9a", "field": "#252525",
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


def settings_path():
    base = os.environ.get("APPDATA")
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, APP_DIR_NAME, FILE_NAME)


def _is_colour(value):
    return (isinstance(value, str) and len(value) == 7 and value[0] == "#"
            and all(c in "0123456789abcdefABCDEF" for c in value[1:]))


def load():
    """Return the stored preferences, falling back to defaults on any problem.

    Bad or hand-edited settings must never stop the application starting, so
    every value is validated and anything unrecognised is quietly dropped.
    """
    prefs = copy.deepcopy(DEFAULTS)
    try:
        with open(settings_path(), "r", encoding="utf-8") as handle:
            stored = json.load(handle)
    except (OSError, ValueError):
        return prefs
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
