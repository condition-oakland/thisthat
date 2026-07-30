# Long Texts

thisthat is built so that **the window never stops responding, however big the input**. A comparison you asked for by mistake is always something you can back out of.

## Nothing blocks

Three things keep the window alive on a big job:

- The comparison runs on a **worker thread**, so the window carries on redrawing while it works.
- The result is painted into the pane in **time-sliced chunks** rather than in one blocking burst.
- If the work takes more than a moment, a **Processing…** dialog appears.

## The progress dialog

The dialog shows a progress bar and says which phase it is in — **Comparing texts…** or **Rendering result…** — plus a **Cancel** button.

Quick comparisons never flash it up. It only appears once the work has gone on long enough that you would otherwise be wondering whether anything was happening.

**Cancel** abandons the job cleanly and says so in the status line (*Comparison cancelled*). Whatever was on screen before stays there; nothing is half-replaced.

## Why most long comparisons are fast anyway

The engine **trims the common start and end** of the two texts before diffing them.

The matching algorithm costs far more than linear time, so halving the input does much better than halving the work. And a real edit usually touches a small part of a long document — a changed paragraph in a spec, a revised clause in a contract — leaving a large identical head and tail that need no examining at all.

For a 69,000-character text with one changed paragraph, this takes the comparison from **seconds to about 0.015 s**.

## The case that stays slow

What trimming cannot help is the genuinely hard case: **two long texts with almost nothing in common**. There is no common head, no common tail, and every token has to be considered against the others. Roughly **3.5 s for 3,000 completely different words**.

That is the case the progress dialog and the Cancel button exist for. If you see the dialog and realise you have compared the wrong pair of files, cancel it — you do not have to wait it out.

## Practical notes

- **Granularity affects the cost.** [Character mode](comparison-options.md) produces far more tokens than smart mode for the same text, so it is the slowest of the three on a long document. If a comparison is taking a while, smart mode is both faster and usually more readable.
- **Rendering is separate from comparing.** A result with a very large number of small scattered changes takes longer to *paint* than one with a few big ones, even though the comparison itself was the same speed. The progress dialog distinguishes the two phases so you can see which one you are waiting on.
- **The result pane holds the whole thing.** There is no paging or truncation — what was compared is what you can scroll through, and what gets [saved to HTML](saving-html.md).
