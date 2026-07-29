"""thisthat -- a single-pane, Word-style desktop text comparer.

Paste "this" (the old text) on the left and "that" (the new text) on the right;
the result appears in ONE pane with deletions struck through on a red highlight
and insertions underlined on a green highlight, the way Word shows tracked
changes.  Hence the name, and hence the wordmark: ~~this~~ __that__.

Inspired by difff《ﾃﾞｭﾌﾌ》 (https://github.com/meso-cacase/difff), which shows
its result in two panes; see NOTICE.md.

Long texts are diffed on a worker thread and painted into the result pane in
time-sliced chunks, so the window never stops responding; a "Processing…"
dialog with a progress bar appears if the work takes longer than a moment.

Nothing is compared until Compare is pressed -- the result pane only ever
shows a result you asked for.

Pure standard library -- no dependencies beyond Python 3.9+ with tkinter.
"""

import os
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import colorchooser, filedialog, messagebox, ttk

import thisthat_engine as engine
import thisthat_html
import thisthat_prefs

APP_NAME = "thisthat"

# _MEIPASS is where a PyInstaller one-file build unpacks its bundled data.
HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
# Black ink on a white tile, so the mark carries its own contrast and one
# file serves both themes (see make_icon.py).
ICON_PATH = os.path.join(HERE, "thisthat.ico")

PREFERRED_FONTS = ("Yu Gothic UI", "Meiryo UI", "Meiryo", "Segoe UI",
                   "MS UI Gothic")

# Default window: a share of the desktop work area, with the width following
# the height rather than the monitor, and the sash placed so the result pane
# is visibly the taller half.
WINDOW_FILL = 0.94      # fraction of the work area's height to occupy
WINDOW_ASPECT = 0.90    # width as a multiple of height
INPUT_SHARE = 0.36      # of the split, how much goes to A and B

RESULT_POLL_MS = 30     # how often the main thread checks on the worker
READY_MESSAGE = "Paste text into A and B, then press Compare (Ctrl+Enter)."
PROGRESS_DELAY_MS = 400  # don't flash a dialog for work that finishes quickly
RENDER_SLICE_MS = 20    # painting budget per event-loop turn

CJK_RANGES = (
    (0x3000, 0x30FF), (0x3400, 0x4DBF), (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF), (0xFF00, 0xFF9F),
)

# Keys that may still reach the read-only result pane.
_NAV_KEYSYMS = {
    "Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next",
    "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
    "Escape", "Caps_Lock", "Num_Lock", "Scroll_Lock", "Win_L", "Win_R",
    "Menu", "Tab", "ISO_Left_Tab",
}
_NAV_KEYSYMS.update("F%d" % n for n in range(1, 13))
_CTRL_ALLOWED = {
    "c", "a", "s", "insert", "home", "end", "left", "right", "up", "down",
    "prior", "next", "plus", "equal", "minus", "0",
}
_CONTROL_MASK = 0x0004


def has_cjk(text, sample=4000):
    for ch in text[:sample]:
        code = ord(ch)
        for low, high in CJK_RANGES:
            if low <= code <= high:
                return True
    return False


def read_text_file(path):
    """Read a text file, trying the encodings a Windows translator will hit."""
    with open(path, "rb") as handle:
        raw = handle.read()
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "cp932", "cp1252"):
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("utf-8", errors="replace")


def mix(a, b, t):
    """Blend two #rrggbb colours; t of 0 gives *a*, 1 gives *b*."""
    parts = []
    for i in (1, 3, 5):
        first, second = int(a[i:i + 2], 16), int(b[i:i + 2], 16)
        parts.append(round(first + (second - first) * t))
    return "#%02x%02x%02x" % tuple(parts)


class FlatButton(tk.Frame):
    """A button, inside the one-pixel frame that draws its border.

    Every button in the app is drawn by Tk rather than by Windows.  The native
    ttk button ignores -background outright, so a blue Compare is not
    available through it at all -- and one hand-drawn blue button sitting
    among native grey ones reads as a mistake rather than as emphasis.  So the
    whole set is drawn here, sharing one shape, and Compare differs from its
    neighbours in nothing but its colours.

    The border has to be a frame around the button rather than the button's
    own: Tk draws a solid relief in black whatever the widget's colours, and
    on Windows it does not draw the highlight ring for buttons at all -- so
    that is the only way to have an outline that follows the theme, dark on
    the light one and light on the dark.
    """

    def __init__(self, parent, theme, font, accent=False, **kw):
        tk.Frame.__init__(self, parent, padx=1, pady=1)
        self.accent = accent
        self.button = tk.Button(self, font=font, relief="flat", borderwidth=0,
                                highlightthickness=0, cursor="hand2",
                                padx=8, pady=3, **kw)
        self.button.pack(fill="both", expand=True)
        self.paint(theme)

    def paint(self, theme):
        """Recolour for a theme.  Called again whenever the theme changes."""
        if self.accent:
            bg, fg = theme["accent"], theme["accent_fg"]
            hover = theme["accent_active"]
        else:
            bg, fg = theme["field"], theme["fg"]
            hover = mix(theme["field"], theme["muted"], 0.18)
        self.configure(background=theme["fg"])
        self.button.configure(
            background=bg, foreground=fg,
            activebackground=hover, activeforeground=fg,
            disabledforeground=theme["muted"],
        )

    def set_state(self, state):
        self.button.configure(state=state)


def _slug(name, limit=40):
    """A side's name reduced to something safe to put in a filename."""
    out = []
    for ch in name.strip()[:limit]:
        if ch.isalnum() or ch in "-_":
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def suggested_filename(name_a="", name_b=""):
    """What the Save dialog should offer, given whatever the sides are called.

    Named sides make far better filenames than a counter of identical
    thisthat-result files, but only if the names survive the trip: anything
    that is not safely a filename -- punctuation, spaces, Japanese -- is
    dropped, and if that leaves nothing usable the generic name stands.
    """
    a, b = _slug(name_a), _slug(name_b)
    if a and b:
        return "%s-vs-%s.html" % (a, b)
    return "thisthat-result.html"


def apply_icon(root):
    """Give every window the app icon."""
    if not os.path.exists(ICON_PATH):
        return
    try:
        # default=... makes it the icon for Toplevels too, not just the root.
        root.iconbitmap(default=ICON_PATH)
    except tk.TclError:
        pass


def set_scaled_icon(window):
    """Hand Windows the icon sizes it actually asks for at this display scale.

    Tk does not read the .ico the way the shell does.  It builds its two class
    icons by resampling one image down rather than taking the entry drawn for
    that size -- so the 16 pixel title-bar icon arrives as a grey smudge even
    though the file has a crisp 16 in it -- and it never asks what the display
    is scaled to, so at 150% the taskbar gets a 32 stretched to 48.  Both of
    those are the icon "looking blurry".

    ``LoadImage`` picks the entry matching the size asked for, and the file
    carries every size Windows asks for, so nothing is resampled.  The result
    goes on in both places: WM_SETICON for this window, which is what the
    taskbar and alt-tab read, and the window class, which is where every
    dialog opened later gets its own title-bar icon from.

    Call this only once the window is on screen -- see main().
    """
    if sys.platform != "win32" or not os.path.exists(ICON_PATH):
        return
    try:
        from ctypes import c_int, c_uint, c_void_p, c_wchar_p, windll

        user32 = windll.user32
        # Handles are pointer-sized; ctypes would otherwise take them for
        # C ints and lop the top half off a 64-bit one.
        user32.GetParent.restype = c_void_p
        user32.GetParent.argtypes = [c_void_p]
        user32.LoadImageW.restype = c_void_p
        user32.LoadImageW.argtypes = [c_void_p, c_wchar_p, c_uint, c_int,
                                      c_int, c_uint]
        user32.SendMessageW.restype = c_void_p
        user32.SendMessageW.argtypes = [c_void_p, c_uint, c_void_p, c_void_p]
        # SetClassLongPtrW is the 64-bit spelling; 32-bit Windows has only
        # SetClassLong, where a LONG is already wide enough for a handle.
        set_class = getattr(user32, "SetClassLongPtrW", None) or \
            user32.SetClassLongW
        set_class.restype = c_void_p
        set_class.argtypes = [c_void_p, c_int, c_void_p]

        # Tk's window id is a child of the frame the shell draws, and the
        # frame is what carries the icon.  It does not exist until the window
        # is mapped, and sending to the child instead is silently useless.
        hwnd = user32.GetParent(c_void_p(window.winfo_id()))
        if not hwnd:
            return
        # ICON_SMALL is the title bar's, ICON_BIG the taskbar's and alt-tab's;
        # SM_CXSMICON/SM_CXICON are what each of them is currently drawn at.
        # GCLP_HICONSM/GCLP_HICON are the same pair on the window class.
        for which, metric, class_slot in ((0, 49, -34), (1, 11, -14)):
            extent = user32.GetSystemMetrics(metric)
            handle = user32.LoadImageW(None, ICON_PATH, 1,   # IMAGE_ICON
                                       extent, extent, 0x0010)  # FROMFILE
            if handle:
                user32.SendMessageW(c_void_p(hwnd), 0x0080,  # WM_SETICON
                                    c_void_p(which), c_void_p(handle))
                set_class(c_void_p(hwnd), class_slot, c_void_p(handle))
    except Exception:
        pass


def close_splash():
    """Dismiss PyInstaller's native splash, if this is a frozen build.

    ``pyi_splash`` only exists inside an exe whose spec included a
    ``Splash(...)`` (see thisthat.spec); running from source it is simply
    absent, so this is a no-op and callers need no guard of their own.
    """
    try:
        import pyi_splash  # type: ignore
    except ImportError:
        return
    try:
        pyi_splash.close()
    except Exception:
        pass


def open_path(path):
    """Open a file with whatever the desktop considers its default handler."""
    if sys.platform == "win32":
        os.startfile(path)  # noqa: S606 -- a path the user just chose
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def reveal_path(path):
    """Open the containing folder, selecting the file where that's possible."""
    if sys.platform == "win32":
        # explorer wants /select and the path as one argument, and returns a
        # non-zero exit code even when it works -- so don't check it.
        subprocess.Popen('explorer /select,"%s"' % os.path.normpath(path))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R", path])
    else:
        subprocess.Popen(["xdg-open", os.path.dirname(path)])


def set_titlebar_dark(window, dark):
    """Ask the Windows compositor for a title bar matching the theme.

    Without this the frame stays white in dark mode and the window looks only
    half-themed.  Nothing else supports it, so failure is ignored.
    """
    try:
        from ctypes import byref, c_int, c_void_p, sizeof, windll
        # A window handle is pointer-sized, so hand it over as a pointer at
        # both ends rather than letting ctypes take it for a C int.
        hwnd = windll.user32.GetParent(c_void_p(window.winfo_id()))
        if not hwnd:
            return
        hwnd = c_void_p(hwnd)
        value = c_int(1 if dark else 0)
        # 20 on current Windows 10/11; 19 on the first builds that had it.
        for attribute in (20, 19):
            if windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attribute, byref(value), sizeof(value)) == 0:
                break
    except Exception:
        pass


def work_area(window):
    """Usable desktop rectangle as (x, y, width, height).

    winfo_screenheight() counts the whole display, taskbar included, so sizing
    from it puts the bottom of a near-full-height window underneath the
    taskbar.  Windows can tell us the real work area; everywhere else fall
    back to the full screen.
    """
    try:
        from ctypes import Structure, byref, c_long, windll

        class RECT(Structure):
            _fields_ = [("left", c_long), ("top", c_long),
                        ("right", c_long), ("bottom", c_long)]

        rect = RECT()
        # SPI_GETWORKAREA = 0x0030
        if windll.user32.SystemParametersInfoW(0x0030, 0, byref(rect), 0):
            return (rect.left, rect.top,
                    rect.right - rect.left, rect.bottom - rect.top)
    except Exception:
        pass
    return (0, 0, window.winfo_screenwidth(), window.winfo_screenheight())


def default_geometry(window):
    """A tall default window, centred in the work area with a small margin.

    The comparison is the point of the app and the result pane is where you
    read it, so the window wants nearly all the height the desktop will give
    it.  Width tracks height rather than the screen: on a wide monitor a
    full-width text column is harder to read, not easier.
    """
    area_x, area_y, area_w, area_h = work_area(window)

    height = int(area_h * WINDOW_FILL)
    width = int(min(max(height * WINDOW_ASPECT, 900), area_w * 0.95))

    x = area_x + (area_w - width) // 2
    y = area_y + (area_h - height) // 2
    return "%dx%d+%d+%d" % (width, height, max(x, 0), max(y, 0))


def centre_on(window, parent):
    """Place a not-yet-shown window over its parent.

    The window must still be withdrawn: winfo_width() reads 1 before mapping,
    and moving an already-mapped window is unreliable while a worker thread is
    holding the GIL.

    Only the position is set, never the size.  Pinning WxH here freezes the
    window at whatever the layout happened to request at this instant, and
    anything that later changes the required height -- switching ttk theme
    swaps the widget metrics wholesale -- gets squeezed out of the bottom
    instead, which silently clips the labels off the last row of buttons.
    """
    window.update_idletasks()
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - height) // 3
    window.geometry("+%d+%d" % (max(x, 0), max(y, 0)))


class ProgressDialog:
    """Small modeless 'Processing…' window with a progress bar and Cancel."""

    def __init__(self, root, on_cancel, ui_font, theme,
                 phase=("Processing…", None, 0), dark=False):
        self.top = tk.Toplevel(root)
        # Build the window hidden and only show it once it has been placed:
        # positioning an already-mapped window is unreliable here, because the
        # worker thread is holding the GIL and Tk can miss the move request.
        self.top.withdraw()
        self.top.title(APP_NAME)
        self.top.resizable(False, False)
        self.top.transient(root)
        self.top.protocol("WM_DELETE_WINDOW", on_cancel)
        set_titlebar_dark(self.top, dark)

        frame = ttk.Frame(self.top, padding=(22, 18))
        frame.pack(fill="both", expand=True)

        self.message = tk.StringVar(value=phase[0])
        ttk.Label(frame, textvariable=self.message,
                  font=ui_font).pack(anchor="w")
        self.bar = ttk.Progressbar(frame, mode="indeterminate", length=340)
        self.bar.pack(fill="x", pady=(12, 14))
        FlatButton(frame, theme, ui_font, text="Cancel", width=8,
                   command=on_cancel).pack(anchor="e")

        self._mode = "indeterminate"
        self.bar.start(12)
        # Settle the phase before the first paint -- a later change would not
        # be redrawn until the worker thread next yields.
        self.apply_phase(*phase)
        centre_on(self.top, root)
        self.top.deiconify()
        # Draw it now, while this thread still holds the GIL -- left to the
        # event loop the first paint gets starved by the worker and the dialog
        # appears as an empty white box.  It must be update_idletasks() and
        # not update(): the latter loops until no event is pending, and with
        # the worker contending for the GIL each pass takes longer than the
        # progress bar's animation timer, so an event is always due and the
        # call never returns.
        self.top.update_idletasks()

    def apply_phase(self, text, maximum=None, value=0):
        self.message.set(text)
        if maximum is None:
            if self._mode != "indeterminate":
                self.bar.config(mode="indeterminate")
                self.bar.start(12)
                self._mode = "indeterminate"
        else:
            if self._mode != "determinate":
                self.bar.stop()
                self.bar.config(mode="determinate")
                self._mode = "determinate"
            self.bar.config(maximum=max(maximum, 1), value=value)

    def set_value(self, value):
        if self._mode == "determinate":
            self.bar.config(value=value)

    def close(self):
        try:
            self.bar.stop()
            self.top.destroy()
        except tk.TclError:
            pass


class AppearanceDialog:
    """Light/dark plus free choice of the four diff colours.

    Every change is applied to the main window immediately so it can be judged
    against real text; Cancel puts back the snapshot taken on entry.
    """

    PREVIEW = [
        ("equal", "The quick brown fox "),
        ("delete", "jumped"),
        ("insert", "leapt"),
        ("equal", " over the lazy dog."),
    ]

    def __init__(self, app):
        self.app = app
        self.restore = app.snapshot_appearance()

        self.top = tk.Toplevel(app.root)
        self.top.withdraw()
        self.top.title("Appearance")
        self.top.resizable(False, False)
        self.top.transient(app.root)
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)
        set_titlebar_dark(self.top, app.theme_name == "dark")

        frame = ttk.Frame(self.top, padding=(18, 14))
        frame.pack(fill="both", expand=True)

        self.theme_var = tk.StringVar(value=app.theme_name)
        modes = ttk.LabelFrame(frame, text="Theme", padding=(12, 8))
        modes.pack(fill="x")
        for label, value in (("Light", "light"), ("Dark", "dark")):
            ttk.Radiobutton(modes, text=label, value=value,
                            variable=self.theme_var,
                            command=self._on_theme).pack(side="left",
                                                         padx=(0, 16))

        colours = ttk.LabelFrame(frame, text="Colours", padding=(12, 10))
        colours.pack(fill="x", pady=(12, 0))
        colours.columnconfigure(1, weight=1)
        self.swatches = {}
        self.hex_labels = {}
        for row, (key, label) in enumerate(thisthat_prefs.COLOUR_KEYS):
            ttk.Label(colours, text=label).grid(row=row, column=0, sticky="w",
                                                pady=3)
            button = tk.Button(colours, width=6, relief="solid", borderwidth=1,
                               cursor="hand2",
                               command=lambda k=key: self._pick(k))
            button.grid(row=row, column=1, sticky="e", padx=(18, 8), pady=3)
            value = ttk.Label(colours, width=9, font=app.ui_font)
            value.grid(row=row, column=2, sticky="w", pady=3)
            self.swatches[key] = button
            self.hex_labels[key] = value

        # No explicit colours on this label: it should follow the TLabel style,
        # which apply_theme() restyles the moment light/dark changes.
        ttk.Label(frame, text="Preview").pack(anchor="w", pady=(14, 3))
        self.preview = tk.Text(frame, height=2, width=44, wrap="word",
                               font=app.text_font, borderwidth=1,
                               relief="solid", highlightthickness=0,
                               padx=8, pady=6, cursor="arrow")
        self.preview.pack(fill="x")
        self.preview.bind("<Key>", lambda e: "break")

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(14, 0))
        # Kept so _refresh can recolour them: this dialog can switch the theme
        # under itself, and its own buttons have to follow.
        self.buttons = [
            FlatButton(buttons, app.theme, app.ui_font,
                       text="Reset to defaults", command=self._reset),
            FlatButton(buttons, app.theme, app.ui_font, text="OK", width=8,
                       command=self.accept),
            FlatButton(buttons, app.theme, app.ui_font, text="Cancel",
                       width=8, command=self.cancel),
        ]
        self.buttons[0].pack(side="left")
        self.buttons[1].pack(side="right")
        self.buttons[2].pack(side="right", padx=(0, 6))

        self.top.bind("<Escape>", lambda e: self.cancel())
        self.top.bind("<Return>", lambda e: self.accept())

        self._refresh()
        centre_on(self.top, app.root)
        self.top.deiconify()
        self.top.grab_set()
        self.top.focus_set()
        app.root.wait_window(self.top)

    # -- helpers --------------------------------------------------------------

    def _refresh(self):
        """Redraw the swatches and preview from the app's live palette."""
        theme = self.app.theme
        for button in self.buttons:
            button.paint(theme)
        for key, _label in thisthat_prefs.COLOUR_KEYS:
            colour = theme[key]
            self.swatches[key].configure(background=colour,
                                         activebackground=colour)
            self.hex_labels[key].configure(text=colour)

        self.preview.configure(background=theme["field"],
                               foreground=theme["fg"],
                               insertbackground=theme["field"])
        self.preview.tag_configure("delete", background=theme["del_bg"],
                                   foreground=theme["del_fg"], overstrike=True)
        self.preview.tag_configure("insert", background=theme["ins_bg"],
                                   foreground=theme["ins_fg"], underline=True)
        self.preview.delete("1.0", "end")
        for tag, text in self.PREVIEW:
            self.preview.insert("end", text, "" if tag == "equal" else tag)

    def _on_theme(self):
        self.app.set_theme(self.theme_var.get())
        set_titlebar_dark(self.top, self.app.theme_name == "dark")
        self._refresh()

    def _pick(self, key):
        label = dict(thisthat_prefs.COLOUR_KEYS)[key]
        chosen = colorchooser.askcolor(
            color=self.app.theme[key], parent=self.top,
            title="%s — %s theme" % (label, self.app.theme_name))[1]
        if chosen:
            self.app.set_colour(key, chosen.lower())
            self._refresh()

    def _reset(self):
        self.app.reset_colours()
        self._refresh()

    def accept(self):
        error = self.app.save_preferences()
        self.top.destroy()
        if error is not None:
            messagebox.showwarning(
                APP_NAME,
                "Your colours are applied, but could not be saved for next "
                "time:\n%s" % error)

    def cancel(self):
        self.app.restore_appearance(self.restore)
        self.top.destroy()


class SavedDialog:
    """Offered after a successful export: open the file, the folder, or neither."""

    def __init__(self, root, path, ui_font, theme, dark=False):
        self.path = path
        self.open_file = tk.BooleanVar(value=True)
        self.open_folder = tk.BooleanVar(value=False)

        self.top = tk.Toplevel(root)
        self.top.withdraw()
        self.top.title(APP_NAME)
        self.top.resizable(False, False)
        self.top.transient(root)
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)
        set_titlebar_dark(self.top, dark)

        frame = ttk.Frame(self.top, padding=(20, 16))
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Saved %s" % os.path.basename(path),
                  font=ui_font).pack(anchor="w")
        folder = os.path.dirname(os.path.abspath(path))
        ttk.Label(frame, text=folder, font=ui_font,
                  wraplength=380).pack(anchor="w", pady=(2, 12))

        ttk.Checkbutton(frame, text="Open the file",
                        variable=self.open_file).pack(anchor="w")
        ttk.Checkbutton(frame, text="Show it in the folder",
                        variable=self.open_folder).pack(anchor="w", pady=(2, 0))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(16, 0))
        FlatButton(buttons, theme, ui_font, text="OK", width=8,
                   command=self.accept).pack(side="right")
        FlatButton(buttons, theme, ui_font, text="Cancel", width=8,
                   command=self.cancel).pack(side="right", padx=(0, 6))

        self.top.bind("<Escape>", lambda e: self.cancel())
        self.top.bind("<Return>", lambda e: self.accept())

        centre_on(self.top, root)
        self.top.deiconify()
        self.top.grab_set()
        self.top.focus_set()
        root.wait_window(self.top)

    def accept(self):
        wanted = (self.open_file.get(), self.open_folder.get())
        self.top.destroy()
        want_file, want_folder = wanted
        try:
            # Reveal first, so the file's own window ends up in front.
            if want_folder:
                reveal_path(self.path)
            if want_file:
                open_path(self.path)
        except OSError as exc:
            messagebox.showerror(APP_NAME, "Could not open it:\n%s" % exc)

    def cancel(self):
        self.top.destroy()


class ThisThatApp:
    def __init__(self, root):
        # Hand the GIL back more often than the 5 ms default, so the event
        # loop keeps getting slices while a comparison runs on the worker
        # thread.  The cost to the worker is negligible next to the
        # responsiveness gained.
        sys.setswitchinterval(0.002)

        self.root = root
        self.prefs = thisthat_prefs.load()
        self.theme_name = self.prefs["theme"]
        self.theme = thisthat_prefs.palette(self.prefs)
        self.font_size = self.prefs["font_size"]
        self.result_font_size = self.prefs["result_font_size"]
        self.segments = []
        self.regions = []
        self._current_region = -1
        self._buttons = []       # FlatButtons, all repainted by apply_theme

        # Async comparison state.
        self._job = 0            # bumped to invalidate work in flight
        self._busy = False
        self._dialog = None
        self._dialog_after = None
        self._render_after = None
        self._phase = ("Processing…", None, 0)
        self._save_after = None

        family = self._pick_font_family()
        self.text_font = tkfont.Font(family=family, size=self.font_size)
        self.result_font = tkfont.Font(family=family,
                                       size=self.result_font_size)
        self.ui_font = tkfont.Font(family=family, size=9)

        root.title(APP_NAME)
        root.geometry(default_geometry(root))
        root.minsize(720, 480)
        apply_icon(root)

        self.mode = tk.StringVar(value=engine.SMART)
        self.ignore_case = tk.BooleanVar(value=False)
        self.ignore_space = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value=READY_MESSAGE)
        # Optional labels for the two sides, used only by the HTML export.
        # Left empty rather than pre-filled, so an export that was never named
        # falls back to the generic wording instead of shipping a placeholder.
        self.name_a = tk.StringVar(value="")
        self.name_b = tk.StringVar(value="")
        self.counter = tk.StringVar(value="no changes")
        self.result_zoom = tk.StringVar(value="%d pt" % self.result_font_size)

        # Order matters: the status bar must claim its strip before the
        # expanding paned window swallows the remaining height.
        self._build_toolbar()
        self._build_statusbar()
        self._build_panes()
        self._bind_keys()
        self.apply_theme()

        self.text_a.focus_set()
        self._place_sash()

    # -- construction ---------------------------------------------------------

    def _button(self, parent, accent=False, **kw):
        """A button in the app's own style, kept on the list apply_theme paints."""
        button = FlatButton(parent, self.theme, self.ui_font, accent, **kw)
        self._buttons.append(button)
        return button

    def _pick_font_family(self):
        available = set(tkfont.families(self.root))
        for name in PREFERRED_FONTS:
            if name in available:
                return name
        return "TkDefaultFont"

    def _build_toolbar(self):
        bar = ttk.Frame(self.root, padding=(8, 6))
        bar.pack(side="top", fill="x")
        self.toolbar = bar

        self._button(bar, text="Load A…", width=8,
                     command=lambda: self.load_into("a")).pack(side="left")
        self._button(bar, text="Load B…", width=8,
                     command=lambda: self.load_into("b")).pack(side="left",
                                                               padx=(4, 0))
        self._button(bar, text="Swap", width=5,
                     command=self.swap).pack(side="left", padx=(4, 0))
        self._button(bar, text="Clear", width=5,
                     command=self.clear).pack(side="left", padx=(4, 0))

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y",
                                                   padx=10)

        ttk.Label(bar, text="Compare by:").pack(side="left")
        combo = ttk.Combobox(
            bar, width=24, state="readonly", textvariable=self.mode,
            values=[engine.MODE_LABELS[m] for m in engine.MODES],
        )
        combo.set(engine.MODE_LABELS[engine.SMART])
        combo.pack(side="left", padx=(6, 0))
        combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_result())
        self.mode_combo = combo

        ttk.Checkbutton(bar, text="Ignore case", variable=self.ignore_case,
                        command=self._refresh_result).pack(side="left",
                                                           padx=(10, 0))
        ttk.Checkbutton(bar, text="Ignore spaces", variable=self.ignore_space,
                        command=self._refresh_result).pack(side="left",
                                                           padx=(8, 0))

        self._button(bar, text="Save HTML…",
                     command=self.save_html).pack(side="right")
        self.compare_button = self._button(bar, text="Compare", accent=True,
                                           command=self.compare)
        self.compare_button.pack(side="right", padx=(0, 6))

    def _build_panes(self):
        outer = ttk.PanedWindow(self.root, orient="vertical")
        outer.pack(side="top", fill="both", expand=True, padx=8, pady=(0, 4))
        self.outer_pane = outer

        inputs = ttk.PanedWindow(outer, orient="horizontal")
        self.text_a = self._labelled_text(inputs, "A  —  this  (original)",
                                          self.name_a)
        self.text_b = self._labelled_text(inputs, "B  —  that  (revised)",
                                          self.name_b)
        outer.add(inputs, weight=2)

        frame = ttk.LabelFrame(outer, text="Result  —  single pane",
                               padding=(2, 2))

        nav = ttk.Frame(frame, padding=(4, 2, 4, 4))
        nav.pack(side="top", fill="x")
        self.prev_button = self._button(nav, text="◀ Previous", width=10,
                                        command=lambda: self.goto_change(-1))
        self.prev_button.pack(side="left")
        self.next_button = self._button(nav, text="Next ▶", width=10,
                                        command=lambda: self.goto_change(1))
        self.next_button.pack(side="left", padx=(4, 0))
        ttk.Label(nav, textvariable=self.counter).pack(side="left", padx=(10, 0))

        # Zoom lives on the result pane's own bar, not in a menu: enlarging the
        # text you are reading is a thing you do while reading it.
        self._button(nav, text="A+", width=2,
                     command=lambda: self.zoom_result(1)).pack(side="right")
        ttk.Label(nav, textvariable=self.result_zoom, width=6,
                  anchor="center").pack(side="right", padx=(2, 2))
        self._button(nav, text="A−", width=2,
                     command=lambda: self.zoom_result(-1)).pack(side="right")
        ttk.Label(nav, text="F3 / Shift+F3").pack(side="right", padx=(0, 12))

        self.result = self._scrolled_text(frame, readonly=True)
        outer.add(frame, weight=3)

    def _place_sash(self, attempt=0):
        """Split the window so the result pane is the taller half.

        A ttk.PanedWindow's initial sash sits wherever the children's
        requested sizes put it -- ``weight`` only governs how *later* resizing
        is shared out -- so the split has to be set once by hand.  Until the
        window is mapped winfo_height() reads 1, hence the retry.
        """
        height = self.outer_pane.winfo_height()
        if height <= 1:
            if attempt < 50:
                self.root.after(20, self._place_sash, attempt + 1)
            return
        self.outer_pane.sashpos(0, int(height * INPUT_SHARE))

    def _labelled_text(self, parent, label, name_var):
        """One input box, with the field that names its side above it.

        The name is export-only -- nothing in the comparison itself reads it --
        so it sits out of the way in a single short row and never steals the
        height the text box wants.
        """
        frame = ttk.LabelFrame(parent, text=label, padding=(2, 2))

        row = ttk.Frame(frame, padding=(6, 2, 6, 4))
        row.pack(side="top", fill="x")
        ttk.Label(row, text="Name:").pack(side="left")
        entry = ttk.Entry(row, textvariable=name_var, font=self.ui_font)
        entry.pack(side="left", fill="x", expand=True, padx=(6, 0))
        # Comparing from the name field is the same request as comparing from
        # the text box, and Enter there would otherwise do nothing at all.
        entry.bind("<Return>", lambda e: (self.compare(), "break")[1])

        widget = self._scrolled_text(frame)
        parent.add(frame, weight=1)
        return widget

    def _scrolled_text(self, parent, readonly=False):
        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True)
        bar = ttk.Scrollbar(wrap, orient="vertical")
        widget = tk.Text(
            wrap, wrap="word", undo=not readonly,
            font=self.result_font if readonly else self.text_font,
            borderwidth=0, highlightthickness=0, padx=8, pady=6,
            yscrollcommand=bar.set, spacing1=1, spacing3=2,
        )
        bar.config(command=widget.yview)
        bar.pack(side="right", fill="y")
        widget.pack(side="left", fill="both", expand=True)
        if readonly:
            self._make_readonly(widget)
        self._bind_zoom(widget,
                        self.zoom_result if readonly else self.zoom_inputs)
        return widget

    def _make_readonly(self, widget):
        """Read-only, but still focusable with a real insertion cursor.

        Leaving the widget in the 'disabled' state would be simpler, but that
        also removes the caret and makes the pane unnavigable -- so instead
        every editing key and event is swallowed.
        """
        def block(event):
            if event.keysym in _NAV_KEYSYMS:
                return None
            if event.state & _CONTROL_MASK:
                if event.keysym.lower() in _CTRL_ALLOWED:
                    return None
            return "break"

        widget.bind("<Key>", block)
        for sequence in ("<<Paste>>", "<<Cut>>", "<<Clear>>", "<<PasteSelection>>",
                         "<Button-2>"):
            widget.bind(sequence, lambda e: "break")
        widget.bind("<Control-a>", self._select_all_result)
        widget.config(insertwidth=2)

    def _select_all_result(self, _event=None):
        self.result.tag_remove("sel", "1.0", "end")
        self.result.tag_add("sel", "1.0", "end-1c")
        return "break"

    def _build_statusbar(self):
        bar = ttk.Frame(self.root, padding=(10, 4))
        bar.pack(side="bottom", fill="x")
        self.statusbar = bar
        self.status_label = ttk.Label(bar, textvariable=self.status)
        self.status_label.pack(side="left")
        self._button(bar, text="Appearance…", width=12,
                     command=self.open_appearance).pack(side="right")

    def _bind_zoom(self, widget, zoom):
        """Give one pane its own zoom: Ctrl+wheel and Ctrl+plus/minus/0.

        Bound on the widget rather than the root for both halves.  The wheel
        then follows the pointer, and the keys run before the root's own
        fallback, so they resize the pane the caret is actually in -- asking
        focus_get() instead would be wrong exactly when the answer matters,
        since it reads None whenever the window is not the active one.
        """
        def wheel(event):
            # Windows and macOS report a signed delta; X11 sends button 4/5.
            if event.num == 5 or event.delta < 0:
                return zoom(-1)
            return zoom(1)

        widget.bind("<Control-MouseWheel>", wheel)
        widget.bind("<Control-Button-4>", wheel)
        widget.bind("<Control-Button-5>", wheel)
        for sequence, delta in (("<Control-plus>", 1), ("<Control-equal>", 1),
                                ("<Control-KP_Add>", 1),
                                ("<Control-minus>", -1),
                                ("<Control-KP_Subtract>", -1),
                                ("<Control-Key-0>", 0)):
            # "break" keeps the root-level fallback from firing as well.
            widget.bind(sequence, lambda e, d=delta: zoom(d))

    def _bind_keys(self):
        self.root.bind("<Control-Return>", lambda e: (self.compare(), "break"))
        self.root.bind("<Control-s>", lambda e: (self.save_html(), "break"))
        # Fallback for when the focus is on the toolbar rather than in a pane.
        self.root.bind("<Control-plus>", lambda e: self.zoom_inputs(1))
        self.root.bind("<Control-equal>", lambda e: self.zoom_inputs(1))
        self.root.bind("<Control-minus>", lambda e: self.zoom_inputs(-1))
        self.root.bind("<Control-0>", lambda e: self.zoom_inputs(0))
        self.root.bind("<F5>", lambda e: self.compare())
        self.root.bind("<F3>", lambda e: self.goto_change(1))
        self.root.bind("<Shift-F3>", lambda e: self.goto_change(-1))
        self.root.bind("<Control-Down>", lambda e: self.goto_change(1))
        self.root.bind("<Control-Up>", lambda e: self.goto_change(-1))

    # -- theming --------------------------------------------------------------

    def apply_theme(self):
        theme = self.theme = thisthat_prefs.palette(self.prefs, self.theme_name)
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam" if self.theme_name == "dark" else "vista")
        except tk.TclError:
            style.theme_use("clam")

        self.root.configure(background=theme["bg"])
        for name in ("TFrame", "TPanedwindow", "TLabelframe"):
            style.configure(name, background=theme["bg"])
        style.configure("TLabelframe.Label", background=theme["bg"],
                        foreground=theme["muted"], font=self.ui_font)
        for name in ("TLabel", "TCheckbutton", "TRadiobutton"):
            style.configure(name, background=theme["bg"],
                            foreground=theme["fg"], font=self.ui_font)

        # clam-only options; the native Windows theme ignores/rejects them.
        for name, options in (
            ("TLabelframe", {"bordercolor": theme["muted"]}),
            ("TCheckbutton", {"indicatorbackground": theme["field"],
                              "indicatorforeground": theme["fg"]}),
            ("TRadiobutton", {"indicatorbackground": theme["field"],
                              "indicatorforeground": theme["fg"]}),
        ):
            try:
                style.configure(name, **options)
            except tk.TclError:
                pass
        for name in ("TCheckbutton", "TRadiobutton"):
            try:
                style.map(name,
                          indicatorbackground=[("selected", theme["ins_fg"]),
                                               ("!selected", theme["field"])])
            except tk.TclError:
                pass

        if self.theme_name == "dark":
            # clam's default white entry field is a hole punched in a dark
            # window.  (Buttons used to need the same treatment; they are all
            # tk.Buttons now, painted below.)
            try:
                style.configure("TEntry", fieldbackground=theme["field"],
                                foreground=theme["fg"],
                                insertcolor=theme["fg"],
                                bordercolor=theme["muted"],
                                lightcolor=theme["field"],
                                darkcolor=theme["field"])
            except tk.TclError:
                pass
        set_titlebar_dark(self.root, self.theme_name == "dark")

        for button in self._buttons:
            button.paint(theme)

        for widget in (self.text_a, self.text_b, self.result):
            widget.configure(
                background=theme["field"], foreground=theme["fg"],
                insertbackground=theme["fg"], selectbackground=theme["sel"],
                selectforeground=theme["fg"],
            )

        self.result.tag_configure(
            "delete", background=theme["del_bg"], foreground=theme["del_fg"],
            overstrike=True,
        )
        self.result.tag_configure(
            "insert", background=theme["ins_bg"], foreground=theme["ins_fg"],
            underline=True,
        )
        # Available from Tk 8.6.6 onwards; harmless to skip if missing.
        for tag, colour in (("delete", theme["del_fg"]),
                            ("insert", theme["ins_fg"])):
            for option in ("overstrikefg", "underlinefg"):
                try:
                    self.result.tag_configure(tag, **{option: colour})
                except tk.TclError:
                    pass
        # The jump-to-change selection must sit on top of the diff colours.
        self.result.tag_raise("sel")

    def zoom_inputs(self, delta):
        """Resize A and B.  delta of 0 means back to the shipped size."""
        self.font_size = self._zoomed(self.font_size, delta)
        self.text_font.configure(size=self.font_size)
        self.prefs["font_size"] = self.font_size
        self._save_soon()
        return "break"

    def zoom_result(self, delta):
        """Resize the result pane alone, independently of A and B."""
        self.result_font_size = self._zoomed(self.result_font_size, delta)
        self.result_font.configure(size=self.result_font_size)
        self.prefs["result_font_size"] = self.result_font_size
        self.result_zoom.set("%d pt" % self.result_font_size)
        self._save_soon()
        return "break"

    @staticmethod
    def _zoomed(size, delta):
        if delta == 0:
            return thisthat_prefs.FONT_DEFAULT
        return max(thisthat_prefs.FONT_MIN,
                   min(thisthat_prefs.FONT_MAX, size + delta))

    def _save_soon(self):
        # Debounced: Ctrl+plus held down should not mean one write per repeat.
        if self._save_after is not None:
            self.root.after_cancel(self._save_after)
        self._save_after = self.root.after(800, self._save_font_size)

    def _save_font_size(self):
        self._save_after = None
        self.save_preferences()

    # -- appearance preferences -----------------------------------------------

    def open_appearance(self):
        AppearanceDialog(self)

    def set_theme(self, name):
        self.theme_name = name
        self.prefs["theme"] = name
        self.apply_theme()

    def set_colour(self, key, value):
        self.prefs["colours"].setdefault(self.theme_name, {})[key] = value
        self.apply_theme()

    def reset_colours(self):
        """Put the current theme's four diff colours back as shipped."""
        self.prefs["colours"][self.theme_name] = {}
        self.apply_theme()

    def snapshot_appearance(self):
        return (self.theme_name,
                {name: dict(entry)
                 for name, entry in self.prefs["colours"].items()})

    def restore_appearance(self, snapshot):
        theme_name, colours = snapshot
        self.theme_name = theme_name
        self.prefs["theme"] = theme_name
        self.prefs["colours"] = {name: dict(entry)
                                 for name, entry in colours.items()}
        self.apply_theme()

    def save_preferences(self):
        error = thisthat_prefs.save(self.prefs)
        if error is not None:
            self.status.set("Preferences could not be saved: %s" % error)
        return error

    # -- text helpers ---------------------------------------------------------

    def get_a(self):
        return self.text_a.get("1.0", "end-1c")

    def get_b(self):
        return self.text_b.get("1.0", "end-1c")

    def _set_input(self, widget, text):
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.edit_reset()

    def _selected_mode(self):
        label = self.mode_combo.get()
        for key, value in engine.MODE_LABELS.items():
            if value == label:
                return key
        return engine.SMART

    # -- the comparison pipeline ----------------------------------------------

    def compare(self):
        """Run a comparison.  Nothing else in the app may call this.

        Comparing is strictly opt-in: typing or pasting into A or B must never
        produce a result on its own, because a half-entered comparison against
        an empty box is just confusing.
        """
        self._begin_job(self.get_a(), self.get_b())

    def _refresh_result(self):
        """Re-run only if a result is already on screen.

        Changing granularity or an ignore option is a request to see the same
        comparison differently -- but with nothing compared yet it must stay
        silent.
        """
        if self.segments:
            self.compare()

    def _clear_result(self):
        self._job += 1
        self._close_dialog()
        if self._render_after is not None:
            self.root.after_cancel(self._render_after)
            self._render_after = None
        self._busy = False
        self.segments = []
        self.regions = []
        self._current_region = -1
        self.result.delete("1.0", "end")
        self._update_counter()

    def _begin_job(self, a, b):
        if not a and not b:
            self._clear_result()
            self.status.set(READY_MESSAGE)
            return

        self._job += 1
        job = self._job
        self._close_dialog()
        if self._render_after is not None:
            self.root.after_cancel(self._render_after)
            self._render_after = None

        options = dict(
            mode=self._selected_mode(),
            ignore_case=self.ignore_case.get(),
            ignore_space=self.ignore_space.get(),
        )
        outcome = {}

        def work():
            try:
                segments = engine.diff_segments(a, b, **options)
                outcome["segments"] = segments
                outcome["regions"] = engine.change_regions(segments)
            except Exception as exc:  # surfaced on the main thread
                outcome["error"] = exc
            outcome["done"] = True

        self._busy = True
        self._set_phase("Comparing texts…")
        self.status.set("Comparing…")
        threading.Thread(target=work, daemon=True).start()
        self._dialog_after = self.root.after(
            PROGRESS_DELAY_MS, lambda: self._show_dialog(job))
        self.root.after(RESULT_POLL_MS, lambda: self._await(job, outcome))

    def _await(self, job, outcome):
        if job != self._job:
            return
        if self._dialog is not None:
            # Keep the dialog repainting while the worker starves the idle
            # queue.  update_idletasks() only runs redraw handlers, so unlike
            # update() it cannot re-enter this callback or livelock on timers.
            try:
                self._dialog.top.update_idletasks()
            except tk.TclError:
                pass
        if not outcome.get("done"):
            self.root.after(RESULT_POLL_MS, lambda: self._await(job, outcome))
            return
        if "error" in outcome:
            self._finish()
            messagebox.showerror(
                APP_NAME, "The comparison failed:\n%s" % outcome["error"])
            self.status.set("Comparison failed.")
            return
        self.segments = outcome["segments"]
        self.regions = outcome["regions"]
        self._start_render(job)

    def _set_phase(self, text, maximum=None, value=0):
        self._phase = (text, maximum, value)
        if self._dialog is not None:
            self._dialog.apply_phase(text, maximum, value)

    def _show_dialog(self, job):
        self._dialog_after = None
        if job != self._job or not self._busy or self._dialog is not None:
            return
        self._dialog = ProgressDialog(self.root, self._cancel, self.ui_font,
                                      self.theme, phase=self._phase,
                                      dark=self.theme_name == "dark")

    def _close_dialog(self):
        if self._dialog_after is not None:
            self.root.after_cancel(self._dialog_after)
            self._dialog_after = None
        if self._dialog is not None:
            self._dialog.close()
            self._dialog = None

    def _cancel(self):
        """Abandon the comparison in flight (Cancel button / dialog close)."""
        self._job += 1
        if self._render_after is not None:
            self.root.after_cancel(self._render_after)
            self._render_after = None
        self._finish()
        self.regions = []
        self._update_counter()
        self.status.set("Comparison cancelled.")

    def _finish(self):
        self._busy = False
        self._close_dialog()

    # -- rendering ------------------------------------------------------------

    def _start_render(self, job):
        widget = self.result
        self._render_scroll = widget.yview()[0]
        widget.tag_remove("sel", "1.0", "end")
        widget.delete("1.0", "end")
        widget.config(
            wrap="char" if any(has_cjk(t) for _, t in self.segments[:40])
            else "word")
        self._current_region = -1
        self._set_phase("Rendering result…", maximum=len(self.segments))
        self._render_step(job, 0)

    def _render_step(self, job, index):
        """Paint segments for at most RENDER_SLICE_MS, then yield to Tk."""
        self._render_after = None
        if job != self._job:
            return

        widget = self.result
        segments = self.segments
        total = len(segments)
        deadline = time.perf_counter() + RENDER_SLICE_MS / 1000.0
        args = []

        while index < total:
            op, text = segments[index]
            if op == "equal":
                args.append(text)
                args.append("")
            else:
                tag = "delete" if op == "delete" else "insert"
                parts = text.split("\n")
                for i, part in enumerate(parts):
                    if part:
                        args.append(part)
                        args.append(tag)
                    if i < len(parts) - 1:
                        # Mark a changed line break the way Word shows a
                        # pilcrow, then emit the break itself untagged so the
                        # highlight does not run to the window edge.
                        args.append("¶")
                        args.append(tag)
                        args.append("\n")
                        args.append("")
            index += 1
            if time.perf_counter() >= deadline:
                break

        if args:
            widget.insert("end", *args)

        if index < total:
            if self._dialog is not None:
                self._dialog.set_value(index)
            self._render_after = self.root.after(
                1, lambda: self._render_step(job, index))
            return

        widget.yview_moveto(self._render_scroll)
        widget.mark_set("insert", "1.0")
        self._finish()
        self._update_counter()
        self._update_status()

    def _update_status(self):
        stats = engine.summarize(self.segments)
        if stats["identical"]:
            self.status.set("The two texts are identical.")
        else:
            self.status.set(
                "%d change region(s)   —   %d character(s) deleted, "
                "%d character(s) inserted"
                % (stats["regions"], stats["deleted_chars"],
                   stats["inserted_chars"])
            )

    # -- change navigation ----------------------------------------------------

    def _update_counter(self):
        count = len(self.regions)
        if not count:
            self.counter.set("no changes")
        elif self._current_region < 0:
            self.counter.set("%d change%s" % (count, "" if count == 1 else "s"))
        else:
            self.counter.set("change %d of %d"
                             % (self._current_region + 1, count))
        state = "normal" if count else "disabled"
        self.prev_button.set_state(state)
        self.next_button.set_state(state)

    def _region_index(self, offset):
        return self.result.index("1.0 + %d chars" % offset)

    def goto_change(self, delta):
        """Move the cursor to the next / previous change region, wrapping."""
        if self._busy:
            return "break"
        if not self.regions:
            self.status.set("There are no changes to jump to.")
            return "break"

        widget = self.result
        cursor = widget.index("insert")
        target = None

        if delta > 0:
            for i, (start, _end) in enumerate(self.regions):
                if widget.compare(self._region_index(start), ">", cursor):
                    target = i
                    break
            wrapped = target is None
            if wrapped:
                target = 0
        else:
            for i in range(len(self.regions) - 1, -1, -1):
                start, end = self.regions[i]
                if widget.compare(self._region_index(end), "<=", cursor):
                    target = i
                    break
            wrapped = target is None
            if wrapped:
                target = len(self.regions) - 1

        start, end = self.regions[target]
        first, last = self._region_index(start), self._region_index(end)
        widget.tag_remove("sel", "1.0", "end")
        widget.tag_add("sel", first, last)
        widget.mark_set("insert", first)
        widget.see(last)
        widget.see(first)
        widget.focus_set()

        self._current_region = target
        self._update_counter()
        if wrapped:
            self.status.set("Wrapped to the %s change."
                            % ("first" if delta > 0 else "last"))
        else:
            self._update_status()
        return "break"

    # -- commands -------------------------------------------------------------

    def load_into(self, side):
        path = filedialog.askopenfilename(
            title="Load text into %s" % side.upper(),
            filetypes=[("Text files", "*.txt *.md *.csv *.tsv *.srt *.json "
                                      "*.xml *.html *.py *.bas *.ahk"),
                       ("All files", "*.*")],
        )
        if not path:
            return
        try:
            text = read_text_file(path)
        except OSError as exc:
            messagebox.showerror(APP_NAME, "Could not read the file:\n%s" % exc)
            return
        widget = self.text_a if side == "a" else self.text_b
        self._set_input(widget, engine.normalize_newlines(text))
        # A loaded file already has a name, and it is almost always the one
        # wanted in the export.  Only offered into an empty field: a name the
        # user typed outranks a guess.
        name_var = self.name_a if side == "a" else self.name_b
        if not name_var.get().strip():
            name_var.set(os.path.splitext(os.path.basename(path))[0])
        # Deliberately no comparison here: loading one side is half the job,
        # and diffing it against whatever is in the other box is noise.
        self.status.set("Loaded %s into %s. Press Compare when both sides "
                        "are ready." % (os.path.basename(path), side.upper()))

    def swap(self):
        a, b = self.get_a(), self.get_b()
        self._set_input(self.text_a, b)
        self._set_input(self.text_b, a)
        # The names belong to the texts, not to the boxes.
        name_a, name_b = self.name_a.get(), self.name_b.get()
        self.name_a.set(name_b)
        self.name_b.set(name_a)
        self._refresh_result()

    def clear(self):
        self._set_input(self.text_a, "")
        self._set_input(self.text_b, "")
        self.name_a.set("")
        self.name_b.set("")
        self._clear_result()
        self.status.set(READY_MESSAGE)
        self.text_a.focus_set()

    def save_html(self):
        if not self.segments:
            messagebox.showinfo(APP_NAME, "There is no result to save yet.")
            return
        name_a, name_b = self.name_a.get(), self.name_b.get()
        path = filedialog.asksaveasfilename(
            title="Save result as HTML",
            defaultextension=".html",
            initialfile=suggested_filename(name_a, name_b),
            filetypes=[("HTML file", "*.html"), ("All files", "*.*")],
        )
        if not path:
            return
        stats = engine.summarize(self.segments)
        meta = ("identical" if stats["identical"] else
                "%d change region(s), %d character(s) deleted, "
                "%d character(s) inserted"
                % (stats["regions"], stats["deleted_chars"],
                   stats["inserted_chars"]))
        wrap = ("anywhere"
                if any(has_cjk(t) for _, t in self.segments[:40])
                else "normal")
        # Export in the theme and colours the user actually chose, rather than
        # letting the browser pick with a prefers-color-scheme query.
        page = thisthat_html.render_page(self.segments,
                                         meta=meta, wrap=wrap,
                                         palette=self.theme,
                                         name_a=name_a, name_b=name_b)
        try:
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(page)
        except OSError as exc:
            messagebox.showerror(APP_NAME, "Could not save the file:\n%s" % exc)
            return
        self.status.set("Saved to %s" % os.path.basename(path))
        SavedDialog(self.root, path, self.ui_font, self.theme,
                    dark=self.theme_name == "dark")


def main():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)   # crisper text on high-DPI
        # Without its own AppUserModelID the taskbar groups the window under
        # pythonw.exe and shows Python's icon instead of ours.
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("thisthat.app")
    except Exception:
        pass

    root = tk.Tk()
    app = ThisThatApp(root)

    # Optional: thisthat_app.py fileA fileB
    loaded = 0
    for side, arg in zip(("a", "b"), sys.argv[1:3]):
        try:
            text = read_text_file(arg)
        except OSError:
            continue
        widget = app.text_a if side == "a" else app.text_b
        app._set_input(widget, engine.normalize_newlines(text))
        name_var = app.name_a if side == "a" else app.name_b
        name_var.set(os.path.splitext(os.path.basename(arg))[0])
        loaded += 1

    # Paint the real window before dismissing the splash, so there is no flash
    # of empty desktop between the two.  update() rather than
    # update_idletasks(): the window has to be mapped, not merely laid out.
    root.update()
    # And now that it is mapped it has a frame to hang a taskbar icon on.
    set_scaled_icon(root)
    close_splash()

    if loaded == 2:      # one file alone is not a comparison
        app.compare()

    root.mainloop()


if __name__ == "__main__":
    main()
