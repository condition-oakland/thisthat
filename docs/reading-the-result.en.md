# Reading the Result

The result pane shows the whole of both texts merged into one, with the differences marked. Everything the two texts have in common is printed once, as plain text; everything that differs is highlighted.

## The marking convention

The marks follow Word's tracked changes, and the wordmark ~~this~~<u>that</u> is the legend:

| | Appearance |
|---|---|
| **Deleted** — only in A (*this*) | <span class="tt-del">strikethrough</span> on a red highlight |
| **Inserted** — only in B (*that*) | <span class="tt-ins">underline</span> on a green highlight |
| **Unchanged** | plain text |

The old is struck through, the new is underlined. Read the plain text plus the struck-through runs and you have A back; read the plain text plus the underlined runs and you have B.

<div class="tt-result" markdown="0">
<p>The <span class="tt-del">apparatus</span><span class="tt-ins">device</span> of claim 1, wherein the <span class="tt-ins">first </span>member is <span class="tt-del">fixed to</span><span class="tt-ins">integral with</span> the frame.</p>
</div>

A replacement shows as the old text struck out, immediately followed by the new text underlined. That pairing is deliberate: you read what it *was* and then what it *became*, in that order.

The lines are kept at a hairline weight rather than a heavy rule. The strikethrough in particular has to leave the deleted text legible, and the highlight is already doing most of the work of saying *this changed*.

!!! keypoint "Good to know"
    All four colours — deleted text, deleted highlight, inserted text, inserted highlight — are yours to change in [Preferences](preferences.md). Red and green are only the shipped defaults, and light and dark themes each keep their own set.

## Changed line breaks

A line break that is itself part of a change is shown as a **¶** in the same colour as the change it belongs to — again following Word's convention.

<div class="tt-result" markdown="0">
<p>…of the first embodiment.<span class="tt-ins">¶</span><br>The second embodiment differs…</p>
</div>

So a paragraph that was split in two shows an inserted ¶ at the split, and two paragraphs joined into one show a deleted ¶ where the break used to be. Without it, the most common structural edit in a document would be invisible.

The pilcrow marks the break; the break itself is not highlighted, so the coloured band stops at the end of the text rather than running out to the window edge.

## When there are no differences

If the two texts are identical, the status line says so — **✓ The two texts are identical** — and the counter beside the navigation buttons reads **✓ no changes**.

Both sit on a tinted blue band rather than being ordinary grey text. *No differences at all* is the result you most want to be able to trust without reading closely, and it is exactly the one a grey sentence in a grey bar invites you to skip past. The band carries across the window as a shape.

The band has no border, so it cannot be mistaken for a button — every button in thisthat is field-coloured inside a one-pixel border.

Note the difference between **no changes** and a blank counter: blank means nothing has been compared yet. A verdict on a comparison that never happened is the one thing you would most likely take at face value, so the app declines to give one.

## Selecting and copying

The result pane is read-only but **not inert**. You can:

- click into it to place the caret
- move around with the arrow keys
- select text with the mouse or with Shift and the arrow keys
- copy with **Ctrl+C**, and select the whole result with **Ctrl+A**

Typing and pasting are ignored — the pane holds a comparison, not a draft.

This matters more than it sounds: a change you have jumped to is already selected, so **Ctrl+C** straight afterwards puts exactly that change on the clipboard. See [Moving Between Changes](navigating-changes.md).

## Text size

The result pane keeps **its own text size**, separate from A and B. It is the pane you read rather than the ones you paste into, so wanting it larger is the normal case rather than an oddity.

**A−** and **A+** on the result's own bar step it between **7 and 32 pt**, with the current size shown between them. Both carry a hover tooltip, because what the two buttons resize — the result and not A or B — is not something a bar labelled **Font size** has the room to say.

For the input boxes — and for the result too, when the cursor is there:

| Keys | Effect |
|---|---|
| **Ctrl+plus** / **Ctrl+minus** | Larger / smaller, in whichever pane the cursor is in |
| **Ctrl+0** | Reset that pane to the default size |
| **Ctrl+scroll** | Larger / smaller, in whichever pane the mouse is over |

Both sizes — the one for A and B, and the one for the result — are remembered between runs.

## Long results

A large result is painted into the pane in **time-sliced chunks** rather than in one blocking burst, so the window never stops responding while it draws. If it takes more than a moment you get a progress dialog with a **Cancel** button. See [Long Texts](long-texts.md).
