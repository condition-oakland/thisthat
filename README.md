# ~~this~~<u>that</u>

**thisthat** is a desktop text comparer. Paste *this* — the old text — on the
left, *that* — the new text — on the right, and the difference comes back in
**one pane**, marked up the way Word shows tracked changes.

Hence the name, and hence the wordmark: ~~this~~<u>that</u>. The old is struck
through, the new is underlined.

| | appearance |
|---|---|
| deleted (only in A, *this*) | ~~strikethrough~~ on a **red** highlight |
| inserted (only in B, *that*) | <u>underline</u> on a **green** highlight |
| unchanged | plain text |

A changed line break is shown as a `¶` in the same colour, again following
Word's convention.

Inspired by [difff《デュフフ》](https://github.com/meso-cacase/difff), which
shows its result in two panes. An independent reimplementation, not affiliated
with or endorsed by its author — see [Licence](#licence).

## Running it

Double-click **`thisthat.bat`**, or:

```
python thisthat_app.py
python thisthat_app.py old.txt new.txt      # pre-load both sides
```

Requires only Python 3.9+ with tkinter — no pip install, nothing to build.
Startup is effectively instantaneous.

## Using it

Paste the old text into **A** (*this*), the new text into **B** (*that*), then
press **Compare**.

**Nothing is compared until you ask for it.** Typing or pasting into a box
never produces a result on its own — half-entered text diffed against an empty
box is just noise. Loading a file into one side doesn't compare either.

Once a result *is* on screen, changing the granularity or an ignore option
re-runs it, since that is a request to see the same comparison differently.

| control | what it does |
|---|---|
| Load A… / Load B… | read a side from a file (UTF-8, UTF-16, CP932 and CP1252 are auto-detected) |
| Name | what to call that side in the exported HTML — see below |
| Swap | exchange A and B (their names go with them) |
| Clear | empty both boxes, both names and the result |
| Compare by | comparison granularity — see below |
| Ignore case | `Hello` and `hello` count as the same |
| Ignore spaces | spaces and tabs never count as a difference (line breaks still do) |
| Compare | run the comparison |
| Save HTML… | write the single-pane result to a standalone `.html` file |
| Appearance… | light / dark and the four diff colours — see below |
| ◀ Previous / Next ▶ | jump between changes — see below; hover for the shortcut |
| Font size, A− / A+ | text size of the result pane — see below |

Keyboard: **Ctrl+Enter** or **F5** compare · **F3 / Shift+F3** next / previous
change (**Ctrl+Down / Ctrl+Up** also work) · **Ctrl+S** save HTML ·
**Ctrl+plus / Ctrl+minus / Ctrl+0** text size · **Ctrl+scroll** text size of the
pane under the pointer.

### Zooming the result

The result pane keeps its own text size, separate from A and B: it is the pane
you read rather than the ones you paste into, so it is usually the one you want
larger. **A−** and **A+** on the result's own bar step it up and down between 7
and 32 pt, with the current size shown between them.

**Ctrl+plus**, **Ctrl+minus** and **Ctrl+0** (reset) apply to whichever pane the
cursor is in, and **Ctrl+scroll** to whichever pane the mouse is over — so the
same keys still resize A and B when that is where you are working. Both sizes
are remembered between runs.

### Appearance

**Appearance…** (bottom right) opens a dialog with the light/dark switch and a
colour picker for each of the four diff colours — deleted text, deleted
highlight, inserted text, inserted highlight. Light and dark keep their own
colours, so setting one doesn't disturb the other.

Changes apply to the window as you make them and a preview line shows how they
read together. **OK** keeps them, **Cancel** puts back what you started with,
and **Reset to defaults** restores the shipped colours for the theme you are
editing.

Switching the theme also swaps the window icon between its black and white
inks, so the mark stays visible against the title bar rather than sinking into
it.

Your choices — theme, colours and both text sizes — are remembered between runs
in:

```
%APPDATA%\thisthat\settings.json
```

Delete that file to go back to the defaults. A corrupt or hand-edited one is
ignored rather than fatal.

### Saving

**Save HTML…** writes a standalone page and then asks whether to **open the
file**, **show it in the folder**, both, or neither — Cancel and the window's
X both do nothing.

The exported page uses the colours and the light/dark choice you are actually
looking at, baked in rather than left to the browser's own dark-mode
preference, and carries the ~~this~~<u>that</u> wordmark at the top.

### Naming the two sides

Above each box is a **Name** field. Whatever you put there is baked into the
exported page — in the title, in the header beside the A and B chips, and in
the legend, so it reads *text only in Contract v1* rather than *text only in
A (this)*. It also seeds the suggested filename (`Contract-v1-vs-Contract-v2.html`).

The names are optional and export-only: nothing in the comparison itself reads
them, and an unnamed side keeps the wording the export has always had. Loading
a file into a side fills its name in from the filename, unless you have already
typed one there.

### Jumping between changes

**Next ▶** and **◀ Previous** move through the changes one at a time, wrapping
around at either end, and the counter next to them shows where you are
(`change 3 of 10`). Each jump selects the whole change and puts the cursor at
its start, so you can read it in place or copy it straight out.

A deletion and the insertion that replaces it count as **one** change, which is
what you usually want: `device` → `apparatus` is a single stop, not two.

The result pane is read-only but not inert — you can click into it, move the
caret with the arrow keys, select text and copy it (Ctrl+C, Ctrl+A). Typing and
pasting are ignored.

### Comparison granularity

- **smart (words + characters)** — the default: runs of Latin letters and
  numbers are compared as whole tokens, while CJK and punctuation are compared
  character by character. Best for mixed Japanese/English text, and the
  approach difff《デュフフ》 takes.
- **character** — every character compared separately. Finest-grained, noisiest.
- **word** — whitespace-delimited words only. Coarsest; useful for prose where
  you only care about which words changed.

## Long texts

The window never stops responding, however big the input:

- the comparison runs on a **worker thread**, and the result is painted into
  the pane in **time-sliced chunks** rather than in one blocking burst;
- if the work takes more than a moment, a **“Processing…” dialog** with a
  progress bar appears, showing whether it is still comparing or now
  rendering, and offering **Cancel**. Quick comparisons never flash it up;
- the engine **trims the common start and end** of the two texts before
  diffing. `difflib` costs far more than linear time, and a real edit usually
  touches a small part of a long document — for a 69,000-character text with
  one changed paragraph this takes the comparison from seconds to about
  **0.015 s**.

What stays slow is the genuinely hard case: two long texts with almost nothing
in common (roughly 3.5 s for 3,000 completely different words). That is the
case the progress dialog and Cancel button exist for.

## How it differs from difff

The original difff is a Perl CGI web application that shells out to the UNIX
`diff` command through named pipes and renders **two** panes side by side.
thisthat keeps difff's tokenizing approach — that is what makes it work well on
Japanese — but:

- diffs in-process with Python's `difflib.SequenceMatcher`, so there is no
  `diff` binary, no web server, no CGI, and no temporary files;
- merges the two panes into one inline result;
- adds the Word-style strikethrough/underline plus highlight styling.

## Files

| file | contents |
|---|---|
| `thisthat_app.py` | the tkinter application |
| `thisthat_engine.py` | tokenizer and diff — no GUI dependencies, importable on its own |
| `thisthat_html.py` | standalone HTML export |
| `thisthat_prefs.py` | defaults, loading and saving of the settings file |
| `thisthat.ico` | window and taskbar icon |
| `splash.png` | startup splash shown by the `.exe` while it unpacks |
| `make_icon.py` | regenerates `thisthat.ico` (needs Pillow; the app does not) |
| `make_splash.py` | regenerates `splash.png` (likewise) |
| `thisthat.bat` | Windows launcher (no console window) |
| `build.bat` | builds the standalone `.exe` — see below |
| `thisthat.spec` | PyInstaller configuration used by `build.bat` |
| `requirements_build.txt` | build-time packages only; the app needs none |
| `LICENSE` | MIT licence for this project |
| `NOTICE.md` | attributions to carry with any copy you distribute |

The icon is the [Lucide](https://lucide.dev/icons/diff) `diff` glyph — its
exact geometry, black on a rounded white tile, so one file serves a dark title
bar and a light one alike. Every stroke in it is axis-aligned, so `make_icon.py` snaps
each one to whole pixels at each of the nine sizes in the file rather than
scaling one drawing down: no size is ever resampled, and none of them are soft.

`thisthat_engine.py` is self-contained if you want to reuse it from another
script:

```python
import thisthat_engine as engine
for op, text in engine.diff_segments(old, new):
    ...  # op is "equal", "delete" or "insert"
```

## Making a standalone .exe

Double-click **`build.bat`**. It produces:

```
dist\thisthat.exe              a single self-contained file, ~11 MB
dist\thisthat-v1.0.0\          the same exe plus LICENSE.txt and NOTICE.txt
dist\thisthat-v1.0.0.zip       that folder, zipped -- this is the one to share
```

The exe needs no Python on the target machine and writes nothing next to
itself; settings still go to `%APPDATA%\thisthat\`.

A one-file exe has to unpack its whole archive to a temp folder before any
Python runs, so it shows a **splash screen** — the wordmark, and nothing else —
from the moment you double-click it. PyInstaller's bootloader draws that
natively, before the interpreter exists; `thisthat_app.py` closes it once the
real window has painted, so there is no gap between the two. Running from
source skips all of it: there is nothing to unpack, and `pyi_splash` simply
isn't there.

The build runs in a venv named for the machine — `.venv_work` on
DOUGHERTY-PC, `.venv_home` on JONSPC, `.venv_build` on anything else. **If it
isn't there, `build.bat` creates it** and installs `requirements_build.txt`,
so a new machine needs nothing but Python on `PATH`. Since the app itself has
no runtime dependencies, that venv holds only PyInstaller (and Pillow, for
`make_icon.py` and `make_splash.py`).

The artwork is checked in, so a build never needs Pillow — regenerate it only
when you want it to change:

```
python make_icon.py      # thisthat.ico
python make_splash.py    # splash.png
```

Bump `THISTHAT_VERSION` at the top of `build.bat` to change the release name.
`thisthat.spec` holds the PyInstaller configuration and is checked in.

## Licence

thisthat is [MIT licensed](LICENSE) — use it, change it, share it, sell it,
keep your changes to yourself if you like. Keep the copyright line with it.

It contains no code from difff《デュフフ》 and is not affiliated with or
endorsed by its author; the icon comes from Lucide under the ISC licence.
[`NOTICE.md`](NOTICE.md) has the details and the notices to carry with any
copy you distribute.
