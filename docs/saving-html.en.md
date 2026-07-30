# Saving as HTML

**Save HTML…** writes the result out as a **standalone `.html` file** — one file, nothing beside it, no folder of assets. It opens in any browser, on any machine, and can be emailed, filed or archived as it is.

Press **Ctrl+S** for the same thing. If nothing has been compared yet, thisthat says so rather than saving an empty page.

## The save dialog and what follows

The file dialog suggests a name (see [below](#the-suggested-filename)) and defaults to `.html`.

Once the file is written, a small dialog asks what to do with it:

| Choice | Effect |
|---|---|
| **Open the file** | Open it in your default browser |
| **Show it in the folder** | Open the containing folder with the file selected |
| Both | Tick both — they are independent |
| Neither | Just close the dialog |

**Cancel**, and the dialog's **X**, both do nothing further. The file has already been written either way.

The status line confirms the save with the filename.

## What the exported page contains

The page is a faithful copy of what you were looking at:

- the ~~this~~<u>that</u> **wordmark** at the top, with the result heading beside it
- an **A** and a **B** chip naming the two sides
- the **summary** — how many change regions, how many characters deleted and inserted, or *identical*
- the **result itself**, marked up exactly as in the window
- a **legend** at the bottom spelling out what the strikethrough and the underline mean

### The colours are baked in

The page uses **the colours and the light/dark choice you are actually looking at**, written into the file rather than left to the browser's own dark-mode preference. A comparison you read in dark mode reads the same way when you open it next month, and the same way for whoever you send it to.

That includes any [colour changes of your own](preferences.md#colours) — the export follows your palette, not the shipped defaults.

### The language is baked in too

A comparison saved while the app is in Japanese has a **Japanese title, heading and legend**, so the page reads the way the window read when you saved it. See [Preferences](preferences.md#language).

What the language setting never touches is the text being compared, which is only ever your own.

## Navigating changes in the browser

The exported page carries the window's **Next ▶** / **◀ Previous** bar, which **sticks to the top** of the browser window as you scroll. Same changes, same order, same counter, and the one you are on is outlined.

In the browser the keys are **n** and **p** rather than F3 — F3 belongs to the browser's own Find, and the page has no business taking it away.

### It moves from where you are

Like the window, the page moves from **where you are** rather than from wherever it left off:

- **Click anywhere in the result** and a caret appears; **n** carries on from there.
- **Select a passage**, and Next starts past the end of it while Previous starts before the beginning.
- **Scrolled somewhere and never clicked at all?** Next takes the first change below the top of the window — which is usually the one you were about to look for anyway.

### About the script

The navigation bar is the page's **only** script. It is inline like everything else in the file, and the page still reads perfectly without it: turning scripting off costs you the navigation and nothing more.

The bar does **not print**. Neither does the caret, and the outline on the current change is dropped for print too — so a printed copy is just the comparison.

## Naming the two sides

Whatever you type in the **Name** field above each box is baked into the exported page:

- in the page **title**
- in the **header**, beside the A and B chips
- in the **legend**, so it reads *text only in Contract v1* rather than *text only in A (this)*

The names are optional. An unnamed side keeps the generic wording the export has always had, and you can name one side and not the other.

Nothing in the comparison itself reads the names — they are export-only. See [Running a Comparison](comparing.md#naming-the-two-sides).

## The suggested filename

When both sides are named, the save dialog offers `Contract-v1-vs-Contract-v2.html`.

Names are reduced to something safe to put in a filename first: anything that is not a letter, digit, hyphen or underscore is dropped. So punctuation, spaces and Japanese do not survive the trip — and if that leaves nothing usable, the dialog falls back to the generic **`thisthat-result.html`**.

The suggestion is only ever a suggestion; type whatever you like over it.
