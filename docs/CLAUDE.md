# thisthat User Guide — CLAUDE.md

This directory contains the MkDocs Material user guide for thisthat, published
to GitHub Pages at <https://condition-oakland.github.io/thisthat/>.

## Scope

**Usage only.** The guide describes how to use the app: what each control does,
what the result means, what the options change. It is not a design document and
not a competitive comparison.

The one permitted exception is the **Comparison Engine** page, which explains
how the tokenizing diff works and its relationship to difff《デュフフ》 —
because that is what explains why the result looks the way it does, and because
the attribution matters. Do not spread difff comparisons across the other pages.

**No screenshots.** Prose, tables and inline examples only. A diff tool can show
its own marks inline, which is what `.tt-del` / `.tt-ins` / `.tt-result` in
`stylesheets/extra.css` are for:

```html
<div class="tt-result" markdown="0">
<p>The <span class="tt-del">apparatus</span><span class="tt-ins">device</span> of claim 1</p>
</div>
```

Those three classes carry the app's **shipped light-theme defaults**. Never write
as though red and green were the only possibility — the user can change all four
colours in Preferences, and light and dark keep separate sets.

## Languages

**Japanese is the default language.** Because the `i18n` plugin uses
`docs_structure: suffix`, the default language must own the unsuffixed files:

- **Japanese** (default) → unsuffixed `.md` (e.g. `preferences.md`). Served at `/`.
- **English** → `.en.md` suffix (e.g. `preferences.en.md`). Served under `/en/`.

Every page exists in both. Write both when filling in content — never leave a
page in one language only.

### Anchors in cross-page links

`mkdocs.yml` sets a Unicode-aware `toc.slugify`, so a Japanese heading's anchor
is the heading text (`## 文字サイズ` → `#文字サイズ`) rather than a throwaway
`_2`. That means **the Japanese pages must link to Japanese anchors and the
English pages to English ones** — the two are not interchangeable. `validation:
anchors: warn` is on, so `mkdocs build` will tell you if you get one wrong.

## Content source rule

**Source everything from the actual code**, not from `README.md`, `backlog.txt`,
or anything else that could have drifted:

| For | Read |
|---|---|
| UI wording, in either language | `thisthat_i18n.py` — the complete string table |
| Controls, layout, key bindings | `thisthat_app.py` (`_build_toolbar`, `_build_panes`, `_bind_keys`) |
| Granularity, ignore options, change regions | `thisthat_engine.py` |
| Defaults, colours, settings file | `thisthat_prefs.py` |
| The exported page | `thisthat_html.py` |

`README.md` is accurate and well-maintained, but it is a summary written for a
different audience — use it as a map to the source, not as the source.

**Quote UI labels exactly as `thisthat_i18n.py` has them**, in the language of
the page being written. The Japanese labels are deliberately terse (`A を読込…`,
`空白を無視`) because a toolbar translated at natural length pushes controls off
a narrow window; do not "improve" them into longer wording in the docs.

## Custom admonition

One custom type is defined in `stylesheets/extra.css`:

```markdown
!!! keypoint "Keep in mind"
    Your text here.
```

Use `keypoint` for facts the user must not miss. The Japanese title is
`"覚えておきましょう"`; common English titles are "Keep in mind" and "Good to
know". Do not use it where a standard `note`/`warning`/`tip` would do.

## File editing rules

**Never use PowerShell `Get-Content` / `Set-Content` on the Japanese files** —
the unsuffixed `.md` ones. The system ANSI code page here is CP932 (Shift-JIS);
PowerShell reads BOM-less UTF-8 as CP932 and writes it back as CP932,
irreversibly corrupting the multibyte sequences. Recovery needs a git backup.

Use the **Edit** or **Write** tools. If a shell substitution is genuinely
needed, use Python with an explicit `encoding='utf-8'`. `git mv` / `git add`
never decode content and are safe for any file.

## Building

Use the **machine's build venv** — the same one `build.bat` uses: `.venv_home`
on JONSPC, `.venv_work` on DOUGHERTY-PC. Never the system Python.

```
.venv_home\Scripts\python.exe -m pip install -r docs-requirements.txt
.venv_home\Scripts\python.exe -m mkdocs serve    # preview at localhost:8000
.venv_home\Scripts\python.exe -m mkdocs build    # writes site/ (gitignored)
```

Run all of these from the **project root**, not from `docs/`. Note that the app
itself has no runtime dependencies — `docs-requirements.txt` is for building this
guide only, exactly as `requirements_build.txt` is for building the exe.

`.github/workflows/docs.yml` builds and deploys on every push to `main` that
touches `docs/`, `mkdocs.yml` or `docs-requirements.txt`. Nothing needs pushing
by hand, and `site/` is never committed.

## Structure

```
docs/
  index.md                  Home
  getting-started.md        Getting the app, running it, the window
  comparing.md              The basic run, Load / Swap / Clear, names
  comparison-options.md     Compare by, Ignore case, Ignore spaces
  reading-the-result.md     Marks, pilcrow, the identical verdict, text size
  navigating-changes.md     Previous / Next, the counter, what is one change
  saving-html.md            Save HTML and everything in the exported page
  preferences.md            Language, theme, colours, the settings file
  long-texts.md             Threading, the progress dialog, head/tail trimming
  comparison-engine.md      Tokenizing, difflib, difff, reusing the engine
  keyboard-shortcuts.md     Every shortcut, app and exported page
  assets/diff.svg           Logo, favicon and the keypoint admonition icon
  stylesheets/extra.css     Theme, adapted from atta's guide
```

Plus, outside `docs/`, one theme override:

```
overrides/partials/header.html
```

A verbatim copy of Material's partial with a single change: the site name's
leading `thisthat` is split out and drawn as the wordmark, `<s>this</s>` +
`<u>that</u>`, styled by `.tt-wm-del` / `.tt-wm-ins` in `extra.css`. **On a
Material upgrade, re-copy the partial from the installed theme and re-apply
that block** — the file says so at the top too. Nothing else is overridden.

## Two things that break silently

Both of these cost real time once, so they are worth knowing before they bite:

- **`assets/diff.svg` must not contain `--` anywhere**, including in a comment.
  XML forbids a double hyphen inside a comment, and an invalid SVG does not
  error — it serves with a 200 and `image/svg+xml`, and the header quietly falls
  back to its `alt="logo"` text. Write em dashes as `—` or reword. Validate with
  `python -c "import xml.dom.minidom;xml.dom.minidom.parse('docs/assets/diff.svg')"`.
- **`~~strikethrough~~` needs `pymdownx.tilde`**, which base Markdown has no
  syntax for. Without it `~~this~~` renders as literal tildes rather than as the
  wordmark, and nothing warns you.

The nav groups `comparing` / `comparison-options` / `reading-the-result` /
`navigating-changes` under **Comparing Texts**. Files are flat on disk — the
grouping is `nav` in `mkdocs.yml` only, which keeps every relative link simple.

Adding a page means: both language files, an entry in `nav`, and an entry in
`nav_translations` for the Japanese title.
