# difff desktop

A desktop text comparer in the spirit of
[difff《デュフフ》](https://github.com/meso-cacase/difff), with one deliberate
change: **the result is shown in a single pane instead of two**, marked up the
way Word shows tracked changes.

An independent reimplementation, not affiliated with or endorsed by the author
of difff — see [Licence](#licence).

| | appearance |
|---|---|
| deleted (only in A) | ~~strikethrough~~ on a **red** highlight |
| inserted (only in B) | <u>underline</u> on a **green** highlight |
| unchanged | plain text |

A changed line break is shown as a `¶` in the same colour, again following
Word's convention.

## Running it

Double-click **`difff.bat`**, or:

```
python difff_desktop.py
python difff_desktop.py old.txt new.txt      # pre-load both sides
```

Requires only Python 3.9+ with tkinter — no pip install, nothing to build.
Startup is effectively instantaneous.

## Using it

Paste the old text into **A**, the new text into **B**, then press
**Compare**.

**Nothing is compared until you ask for it.** Typing or pasting into a box
never produces a result on its own — half-entered text diffed against an empty
box is just noise. Loading a file into one side doesn't compare either.

Once a result *is* on screen, changing the granularity or an ignore option
re-runs it, since that is a request to see the same comparison differently.

| control | what it does |
|---|---|
| Load A… / Load B… | read a side from a file (UTF-8, UTF-16, CP932 and CP1252 are auto-detected) |
| Swap | exchange A and B |
| Clear | empty both boxes and the result |
| Compare by | comparison granularity — see below |
| Ignore case | `Hello` and `hello` count as the same |
| Ignore spaces | spaces and tabs never count as a difference (line breaks still do) |
| Compare | run the comparison |
| Save HTML… | write the single-pane result to a standalone `.html` file |
| Appearance… | light / dark and the four diff colours — see below |
| ◀ Previous / Next ▶ | jump between changes — see below |

Keyboard: **Ctrl+Enter** or **F5** compare · **F3 / Shift+F3** next / previous
change (**Ctrl+Down / Ctrl+Up** also work) · **Ctrl+S** save HTML ·
**Ctrl+plus / Ctrl+minus / Ctrl+0** text size.

### Appearance

**Appearance…** (bottom right) opens a dialog with the light/dark switch and a
colour picker for each of the four diff colours — deleted text, deleted
highlight, inserted text, inserted highlight. Light and dark keep their own
colours, so setting one doesn't disturb the other.

Changes apply to the window as you make them and a preview line shows how they
read together. **OK** keeps them, **Cancel** puts back what you started with,
and **Reset to defaults** restores the shipped colours for the theme you are
editing.

Your choices — theme, colours and text size — are remembered between runs in:

```
%APPDATA%\difff-desktop\settings.json
```

Delete that file to go back to the defaults. A corrupt or hand-edited one is
ignored rather than fatal.

### Saving

**Save HTML…** writes a standalone page and then asks whether to **open the
file**, **show it in the folder**, both, or neither — Cancel and the window's
X both do nothing.

The exported page uses the colours and the light/dark choice you are actually
looking at, baked in rather than left to the browser's own dark-mode
preference.

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

- **difff (words + characters)** — the default, and what the original difff
  does: runs of Latin letters and numbers are compared as whole tokens, while
  CJK and punctuation are compared character by character. Best for mixed
  Japanese/English text.
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

## How it differs from the original

The original difff is a Perl CGI web application that shells out to the UNIX
`diff` command through named pipes and renders **two** panes side by side.
This version keeps difff's tokenizing approach — that is what makes it work
well on Japanese — but:

- diffs in-process with Python's `difflib.SequenceMatcher`, so there is no
  `diff` binary, no web server, no CGI, and no temporary files;
- merges the two panes into one inline result;
- adds the Word-style strikethrough/underline plus highlight styling.

## Files

| file | contents |
|---|---|
| `difff_desktop.py` | the tkinter application |
| `difff_engine.py` | tokenizer and diff — no GUI dependencies, importable on its own |
| `difff_html.py` | standalone HTML export |
| `difff_prefs.py` | defaults, loading and saving of the settings file |
| `difff.ico` | window and taskbar icon |
| `make_icon.py` | regenerates `difff.ico` (needs Pillow; the app does not) |
| `difff.bat` | Windows launcher (no console window) |
| `LICENSE` | MIT licence for this project |
| `NOTICE.md` | attributions to carry with any copy you distribute |

The icon is the [Lucide](https://lucide.dev/icons/diff) `diff` glyph — its
exact geometry, coloured green over red to match how insertions and deletions
are marked, on a transparent background.

`difff_engine.py` is self-contained if you want to reuse it from another
script:

```python
import difff_engine as engine
for op, text in engine.diff_segments(old, new):
    ...  # op is "equal", "delete" or "insert"
```

## Making a standalone .exe

Not required, but if you want one:

```
pip install pyinstaller
pyinstaller --noconsole --onefile --name difff --icon difff.ico ^
            --add-data "difff.ico;." difff_desktop.py
```

`--icon` sets the icon on the `.exe`; `--add-data` ships the same file so the
running window and its dialogs can load it too.

Ship `LICENSE` and `NOTICE.md` alongside the `.exe`.

## Licence

difff desktop is [MIT licensed](LICENSE) — use it, change it, share it, sell
it, keep your changes to yourself if you like. Keep the copyright line with
it.

It contains no code from difff《デュフフ》 and is not affiliated with or
endorsed by its author; the icon comes from Lucide under the ISC licence.
[`NOTICE.md`](NOTICE.md) has the details and the notices to carry with any
copy you distribute.
