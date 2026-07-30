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

There is a **user guide** at
<https://condition-oakland.github.io/thisthat/> — in Japanese and English,
covering the same ground as this file at more length and with fewer asides.
Its source is in [`docs/`](docs/).

## Download

Windows builds are on the
[releases page](https://github.com/condition-oakland/thisthat/releases/latest):
`thisthat-vX.Y.Z.zip` holds the exe and its licence files. There is nothing to
install, and nothing is written next to the exe — settings go to
`%APPDATA%\thisthat\`.

The exe is not code-signed, so the first run brings up a **"Windows protected
your PC"** panel with only a **Don't run** button; **More info** reveals **Run
anyway**. The guide has
[the longer explanation](https://condition-oakland.github.io/thisthat/en/getting-started/#windows-smartscreen).

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
| Preferences… | UI language, light / dark and the four diff colours — see below |
| ◀ Previous / Next ▶ | jump between changes — see below; hover for the shortcut |
| Font size, A− / A+ | text size of the result pane — see below; hover for the shortcut |

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

### Preferences

**Preferences…** (bottom right) opens a dialog with the UI language, the
light/dark switch, and a colour picker for each of the four diff colours —
deleted text, deleted highlight, inserted text, inserted highlight. Light and
dark keep their own colours, so setting one doesn't disturb the other.

Changes apply to the window as you make them and a preview line shows how they
read together. **OK** keeps them, **Cancel** puts back what you started with,
and **Reset to defaults** restores the shipped colours for the theme you are
editing.

Switching the theme also swaps the window icon between its black and white
inks, so the mark stays visible against the title bar rather than sinking into
it.

### UI language

The interface is available in **English** and **日本語**. It is the language of
the buttons and labels only — nothing about it concerns the language of the two
texts, which can be anything. The choice takes effect immediately — the window
is relabelled around whatever you have in it, so nothing is lost — and it is
remembered for next time.

It also reaches the HTML export: a comparison saved while the app is in
Japanese has a Japanese title, header and legend, so the page reads the way the
window read when you saved it. What it never touches is the text being
compared, which is only ever your own.

The app ships in English and stays there until you choose otherwise; it does
not guess from the system locale.

Your choices — language, theme, colours and both text sizes — are remembered
between runs in:

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

It also carries the window's **Next ▶** / **◀ Previous** bar, which sticks to
the top of the browser window: the same changes, in the same order, with the
same counter, and the one you are on outlined. In the browser the keys are
**n** and **p** rather than F3, which belongs to the browser's own Find. The
bar is the page's only script, it is inline like everything else, and the page
still reads without it — scripting off costs you the navigation and nothing
more. It does not print.

Like the window, the exported page moves from where you are rather than from
wherever it left off. Click anywhere in the result — a caret appears, and
**n** carries on from there. Select a passage and Next starts past the end of
it while Previous starts before the beginning. And if you have simply scrolled
somewhere and never clicked at all, Next takes the first change below the top
of the window, which is usually the one you were about to look for anyway.

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
| `thisthat_i18n.py` | every string the interface shows, in each language |
| `thisthat_prefs.py` | defaults, loading and saving of the settings file |
| `thisthat_version.py` | the version number — read by the app, the export and `build.bat` |
| `thisthat.ico` | window and taskbar icon |
| `splash.png` | startup splash shown by the `.exe` while it unpacks |
| `make_icon.py` | regenerates `thisthat.ico` (needs Pillow; the app does not) |
| `make_splash.py` | regenerates `splash.png` (likewise) |
| `thisthat.bat` | Windows launcher (no console window) |
| `build.bat` | builds the standalone `.exe` — see below |
| `thisthat.spec` | PyInstaller configuration used by `build.bat` |
| `requirements_build.txt` | build-time packages only; the app needs none |
| `CHANGELOG.md` | what changed in each release; the source for the release notes |
| `LICENSE` | MIT licence for this project |
| `NOTICE.md` | attributions to carry with any copy you distribute |
| `docs/` | the user guide — MkDocs Material, Japanese and English |
| `mkdocs.yml` | its configuration |
| `docs-requirements.txt` | packages needed to build the guide; the app needs none |

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
dist\thisthat-vX.Y.Z\          the same exe plus LICENSE.txt and NOTICE.txt
dist\thisthat-vX.Y.Z.zip       that folder, zipped -- this is the one to share
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

The build runs in a venv named after the machine — `.venv_%COMPUTERNAME%`, so
`.venv_SOMEBOX` on a host called SOMEBOX. A venv is not portable between
machines, and the project tree may sit on a shared drive that more than one of
them reaches at the same path, so they have to stay separate; `.venv*/` is
gitignored. **If it isn't there, `build.bat` creates it** and installs
`requirements_build.txt` with `--require-hashes`, so a new machine needs
nothing but Python on `PATH`. Since the app itself has no runtime
dependencies, that venv holds only PyInstaller (and Pillow, for `make_icon.py`
and `make_splash.py`).

The artwork is checked in, so a build never needs Pillow — regenerate it only
when you want it to change:

```
python make_icon.py      # thisthat.ico
python make_splash.py    # splash.png
```

`build.bat` reads the version out of `thisthat_version.py`, so the zip can never
be labelled something the exe inside it disagrees with. `thisthat.spec` holds
the PyInstaller configuration and is checked in.

## Cutting a release

Numbering is [semantic](https://semver.org/): PATCH for fixes, MINOR for
features, MAJOR for breaking something a user relied on — a settings file older
versions cannot read, a shortcut that moves, a feature that goes away.

`thisthat_version.py` is the single source of truth. Preferences shows it in the
corner, the exported HTML carries it as its `generator`, and `build.bat` names
the folder and the zip from it, so one edit moves all three.

1. Move `## [Unreleased]` in [`CHANGELOG.md`](CHANGELOG.md) down to
   `## [X.Y.Z] -- YYYY-MM-DD`, bump `__version__` in `thisthat_version.py`, and
   commit both.
2. Double-click `build.bat`, which writes `dist\thisthat-vX.Y.Z.zip`.
3. Tag the commit that was built, and push it:

   ```
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin main --follow-tags
   ```

4. Take the zip's SHA-256 and put it at the end of the release notes:

   ```
   (Get-FileHash dist\thisthat-vX.Y.Z.zip).Hash
   ```

   The exe is not code-signed, and the guide tells people to click past the
   SmartScreen warning it raises. The checksum is the only thing they have to
   check the download against, so a release without one asks them to run an
   unverifiable binary — publish it every time.

5. Publish the release with the zip attached — either paste that CHANGELOG
   section into a new release on GitHub and drag the zip in, or:

   ```
   gh release create vX.Y.Z dist\thisthat-vX.Y.Z.zip --title vX.Y.Z --notes-file <file>
   ```

6. Download the zip from GitHub, check its hash against the notes, and run it.
   An asset nobody has opened is a release nobody has tested.

The zip is never committed: `dist/` is gitignored, and an 11 MB exe does not
delta-compress, so committing one per version would grow the history by that
much forever. Release assets live outside it. Nothing in the guide needs
updating per release either — every download link points at
`/releases/latest`, which GitHub resolves to the newest one.

## Licence

thisthat is [MIT licensed](LICENSE) — use it, change it, share it, sell it,
keep your changes to yourself if you like. Keep the copyright line with it.

It contains no code from difff《デュフフ》 and is not affiliated with or
endorsed by its author; the icon comes from Lucide under the ISC licence.
[`NOTICE.md`](NOTICE.md) has the details and the notices to carry with any
copy you distribute.
