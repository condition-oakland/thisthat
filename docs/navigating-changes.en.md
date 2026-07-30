# Moving Between Changes

A long comparison with a handful of scattered edits is not something you want to scroll through hunting for colour. **◀ Previous** and **Next ▶** on the result pane's own bar walk you through the changes one at a time.

## The buttons and the counter

**Next ▶** goes forward, **◀ Previous** goes back, and both **wrap around** at the ends — Next past the last change returns to the first, and the status line says so (*Wrapped to the first change*).

The counter beside them tells you where you are:

| Counter | Meaning |
|---|---|
| *(blank)* | Nothing has been compared yet |
| **✓ no changes** | Compared, and the two texts are identical |
| **10 changes** | Compared, 10 changes found, you have not jumped yet |
| **change 3 of 10** | You are on the third of ten |

The two buttons are disabled when there is nothing to jump to.

## What counts as one change

A deletion and the insertion that replaces it count as **one** change, which is what you usually want: `device` → `apparatus` is a single stop, not two.

More generally, a change is a maximal run of consecutive changed text. If several edits sit immediately next to each other with no unchanged text between them, they are one stop.

## Each jump selects the change

Every jump **selects the whole change** and puts the caret at its start, then scrolls so the change is in view.

That means the change is on the clipboard the moment you want it: jump, then **Ctrl+C**. And because the caret lands at the start, you can read the change in place without hunting for where it begins.

## Moving from where you are

Navigation starts from **where the caret is**, not from wherever you last left off. So you can click anywhere in the result and carry on from there — useful when you have scrolled to a passage and want to work forward through it rather than resuming from the top.

## Keyboard

| Keys | What it does |
|---|---|
| **F3** | Next change |
| **Shift+F3** | Previous change |
| **Ctrl+Down** | Next change |
| **Ctrl+Up** | Previous change |

The shortcuts are on the buttons as hover tooltips too, so you do not have to come back here for them.

These work from anywhere in the window, including while the cursor is in A or B — you do not have to click into the result pane first.

## In the exported page

The [saved HTML page](saving-html.md) carries the same navigation bar, with the same changes in the same order and the same counter. In the browser the keys are **n** and **p** rather than F3, since F3 belongs to the browser's own Find.
