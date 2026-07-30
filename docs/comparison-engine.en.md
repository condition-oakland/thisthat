# The Comparison Engine

This page is about what happens between pressing **Compare** and the result appearing. You do not need any of it to use thisthat, but it explains *why* the result looks the way it does — and in particular why [smart mode](comparison-options.md) behaves as it does on Japanese.

## Tokenize, then match

The comparison happens in two steps.

**First, both texts are split into tokens.** A token is the smallest unit that can be reported as changed. What counts as a token is exactly what the **Compare by** setting controls:

| Mode | One token is |
|---|---|
| **smart** | a run of Latin letters, or a number, or a run of spaces, or a line break, or any single other character |
| **character** | any single character |
| **word** | a run of non-whitespace, or a run of spaces, or a line break |

**Then the two token sequences are matched against each other**, and the result is a flat stream of segments, each marked *equal*, *delete* (present only in A) or *insert* (present only in B).

Concatenating the *equal* and *delete* segments reproduces A exactly; the *equal* and *insert* segments reproduce B. Nothing is lost or invented in between.

## Why smart mode splits the way it does

Smart mode keeps runs of Latin letters and digits whole and treats everything else — CJK, punctuation — one character at a time.

That is not a compromise; it is the right answer for each script:

- **Japanese has no spaces to divide words on.** A word-level comparison has nothing to split on, so a whole paragraph becomes one token and any edit inside it reports the paragraph as replaced. Character-level comparison is what works.
- **English compared character by character** breaks a replaced word into a mess of single-letter changes — the letters two different words happen to share get reported as unchanged, which is technically true and useless to read.

Handling both in the same pass means a document that mixes them — a Japanese specification with English terms and reference numerals, say — reads correctly throughout rather than correctly in half of it.

Numbers stay whole too, including decimals and thousands separators, so `1,000` → `10,000` is one change rather than an inserted digit somewhere in the middle.

## Ignoring things without hiding them

**Ignore case** and **Ignore spaces** work by changing what the matcher *sees*, not what the renderer *shows*.

Tokens excluded from the comparison — spaces, when Ignore spaces is on — still appear in the result exactly where they were. They simply never count as a difference. Similarly, Ignore case folds case for matching purposes only; the result shows whatever was actually written, in whatever case it was written.

That distinction matters: an option that silently removed the whitespace from your text would be a different and much worse feature.

## Trimming before matching

Before the two token sequences reach the matcher, the engine strips the **common head and common tail** and matches only what is left in the middle.

This is the single biggest reason long comparisons are fast; see [Long Texts](long-texts.md) for what it buys and what it cannot help with.

## Change regions

A **change region** is a maximal run of consecutive changed segments. A deletion immediately followed by the insertion that replaces it is one region, not two — which is why `device` → `apparatus` is a single stop for [Next ▶](navigating-changes.md) and counts as one in the summary.

Region boundaries are computed as offsets into the *rendered* result rather than into the source texts, so the ¶ that marks a changed line break is counted along with everything else. The counter, the navigation and the saved HTML page all work from the same set of regions, which is why the exported page steps through changes in exactly the same order as the window.

## Relationship to difff《デュフフ》

thisthat is an **independent reimplementation inspired by** [difff《デュフフ》](https://github.com/meso-cacase/difff) by Yuki Naito (@meso_cacase).

What the two share is the **tokenizing approach** — Latin words and numbers compared whole, CJK compared character by character. That is the idea that makes either program work on Japanese, and it is an idea rather than an expression: **no code from difff is included in thisthat.**

Everything around it is different:

| | difff | thisthat |
|---|---|---|
| Kind of program | Perl CGI web application | Python desktop application |
| How it diffs | shells out to the UNIX `diff` command through named pipes | in-process, with Python's `difflib.SequenceMatcher` |
| Needs | a web server, CGI, the `diff` binary, temporary files | none of those |
| Result layout | **two** panes, side by side | **one** merged inline pane |
| Marking | its own scheme | Word-style strikethrough / underline plus highlight |

!!! keypoint "Keep in mind"
    thisthat is **not affiliated with, endorsed by, or supported by** the author of difff. Please do not report problems with thisthat to them.

    The attribution in `NOTICE.md` is given because credit is due, not because a licence requires it.

## Using the engine from your own code

`thisthat_engine.py` has **no GUI dependencies** and is importable on its own, if you want a tokenizing diff in another script:

```python
import thisthat_engine as engine

for op, text in engine.diff_segments(old, new):
    ...  # op is "equal", "delete" or "insert"
```

`diff_segments` also takes `mode` (`engine.SMART`, `engine.CHAR`, `engine.WORD`), `ignore_case` and `ignore_space`. `engine.summarize(segments)` gives you the counts the status line shows, and `engine.change_regions(segments)` gives you the change regions described above.

The whole app imports nothing outside the Python standard library, so there is nothing to install to use any of this.
