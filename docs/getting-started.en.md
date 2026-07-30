# Getting Started

This page covers getting thisthat onto your machine, starting it, and finding your way around the window.

## Downloading thisthat

[Download the latest release](https://github.com/condition-oakland/thisthat/releases/latest){ .md-button .md-button--primary }

The **Assets** list on that page carries `thisthat-vX.Y.Z.zip` — the exe and its licence files. That link always resolves to the newest release, so it is the one worth bookmarking; the address of any particular zip goes stale the moment the next version lands.

None of this is needed if you intend to [run from source](#from-source).

## Running the app

There are two ways to run thisthat, and they behave identically.

### The standalone .exe

The release zip contains **`thisthat.exe`** plus `LICENSE.txt` and `NOTICE.txt`. Extract it anywhere you like and double-click the exe. Nothing needs installing, and nothing is written next to the file — your [preferences](preferences.md) go to your own user profile instead.

Because a single-file exe has to unpack itself before any of the program runs, you will see a **splash screen** — the wordmark, nothing else — from the moment you double-click it. It closes as soon as the real window has painted.

### Windows SmartScreen

thisthat is not code-signed, so the first time you run the downloaded exe, Windows will almost certainly put up a blue panel reading **"Windows protected your PC"**. The only button on it is **Don't run**. The way through is to click **More info**, which reveals a **Run anyway** button underneath.

What that panel means is that Windows has not seen this file from a known publisher often enough to vouch for it — not that it examined the file and found something wrong with it. Removing the panel takes a code-signing certificate, which thisthat does not have yet.

If you would rather not click through it at all, [run from source](#from-source) instead; SmartScreen does not apply to Python scripts.

### From source

If you have Python, double-click **`thisthat.bat`**, or run:

```
python thisthat_app.py
```

You can also hand it the two files to compare, which loads one into each side:

```
python thisthat_app.py old.txt new.txt
```

Python **3.9 or newer** with tkinter is the only requirement — there is nothing to `pip install` and nothing to build. Startup is effectively instantaneous, and running from source skips the splash screen entirely.

!!! keypoint "Good to know"
    Both routes are the same program with the same settings file, so you can switch between them freely — your colours, language and text sizes follow you.

## The window at a glance

The window is a toolbar, three text areas, and a status line.

### The toolbar

Along the top, from left to right:

| Control | What it does |
|---|---|
| **Load A… / Load B…** | Read one side in from a file |
| **Swap** | Exchange A and B |
| **Clear** | Empty both boxes, both names and the result |
| **Compare by** | The comparison granularity — see [Comparison Options](comparison-options.md) |
| **Ignore case** | `Hello` and `hello` count as the same |
| **Ignore spaces** | Spaces and tabs never count as a difference |
| **Compare** | Run the comparison — the blue button on the right |
| **Save HTML…** | Write the result out as a standalone page |

**Compare** is the only coloured button in the window. Everything else is deliberately grey: the one button that does the thing should be the one your eye lands on.

### The two input boxes

**A — this** on the left, **B — that** on the right: A takes the old text, B the new. Above each box is a **Name** field, which is optional and only affects the [exported HTML](saving-html.md#naming-the-two-sides).

### The result pane

Below the boxes, filling the lower part of the window. Its own bar carries:

- **◀ Previous** and **Next ▶** with a counter — see [Moving Between Changes](navigating-changes.md)
- **Font size** with **A−** and **A+** — see [Reading the Result](reading-the-result.md#text-size)

The divider between the input boxes and the result can be dragged, as can the divider between A and B, so you can give whichever pane you are working in more room.

### The status line

Along the very bottom. Before you compare anything it tells you what to do; afterwards it carries the summary — how many change regions, how many characters deleted and inserted, or a highlighted note that the two texts are identical.

**Preferences…** sits at the bottom right, next to the status line. See [Preferences](preferences.md).

## Next

[Running a Comparison](comparing.md) walks through the basic workflow.
