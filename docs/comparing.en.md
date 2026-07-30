# Running a Comparison

The whole workflow is three steps: get the old text into **A**, get the new text into **B**, press **Compare**.

## The basic run

1. Paste the old text into **A** (*this*).
2. Paste the new text into **B** (*that*).
3. Press **Compare**, or **Ctrl+Enter**, or **F5**.

The result appears in the pane below, and the status line tells you what was found.

!!! keypoint "Keep in mind"
    **Nothing is compared until you ask for it.** Typing or pasting into a box never produces a result on its own, and loading a file into one side doesn't compare either — half-entered text diffed against an empty box is just noise.

    The one exception is a result that is already on screen: changing the granularity or an ignore option re-runs it, because that is a request to see the same comparison differently.

## Loading from a file

**Load A…** and **Load B…** read one side in from a file. The file dialog offers plain-text formats by name — `.txt`, `.md`, `.csv`, `.tsv`, `.srt`, `.json`, `.xml`, `.html`, `.py`, `.bas`, `.ahk` — and **All files** if what you want isn't among them.

Encodings are detected for you: **UTF-8** (with or without a byte-order mark), **UTF-16**, **CP932** (Shift-JIS) and **CP1252** are each tried in turn. Line endings are normalised too, so a file saved on Windows and one saved on Mac or Linux never differ merely in how they end their lines.

Loading a file also fills in that side's **Name** from the filename — unless you have already typed one there, in which case what you typed stands.

Loading one side deliberately does **not** start a comparison. Load both, then press Compare.

## Swap

**Swap** exchanges the two texts. The names go with them, because a name belongs to the text rather than to the box it happens to be sitting in.

If a result is already on screen, Swap re-runs it — so the deletions become insertions and vice versa, which is the whole point of pressing it.

## Clear

**Clear** empties both boxes, both name fields and the result, and puts the cursor back in A ready for the next pair.

## Naming the two sides

Above each box is a **Name** field: *Contract v1*, *as filed*, *client's revision* — whatever tells you which text is which.

The names are **optional and export-only**. Nothing in the comparison itself reads them; they exist so the [saved HTML page](saving-html.md) can say *text only in Contract v1* rather than *text only in A (this)*, and so the suggested filename comes out as `Contract-v1-vs-Contract-v2.html`.

## What the status line tells you

| When | What it says |
|---|---|
| Before anything is compared | *Paste text into A and B, then press Compare (Ctrl+Enter).* |
| While it is working | *Comparing…* |
| After a comparison with differences | The number of change regions, and how many characters were deleted and inserted |
| After a comparison with none | *✓ The two texts are identical* — highlighted so you can confirm it at a glance |
| After loading a file | Which file went into which side, and a reminder to press Compare |

## Next

[Comparison Options](comparison-options.md) covers granularity and the two ignore switches — the settings that change what counts as a difference in the first place.
