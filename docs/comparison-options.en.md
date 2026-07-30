# Comparison Options

Three controls on the toolbar decide what counts as a difference: **Compare by**, **Ignore case** and **Ignore spaces**.

All three take effect immediately. If a result is already on screen, changing any of them re-runs the comparison, because that is a request to see the same two texts a different way. If nothing has been compared yet, they simply wait until you press Compare.

## Compare by

The **Compare by** list sets the granularity — how finely the two texts are chopped up before they are matched against each other.

### smart (words + characters)

The default, and the one to leave alone unless you have a reason. Runs of Latin letters and numbers are compared as **whole tokens**, while CJK characters and punctuation are compared **one character at a time**.

That mix is what makes it work on Japanese. Japanese has no spaces to divide words on, so word-by-word comparison has nothing to work with; but comparing English character by character gives you a mess of single-letter changes inside words that were simply replaced. Smart mode does the right thing on each script in the same document.

This is also the approach difff《デュフフ》 takes — see [The Comparison Engine](comparison-engine.md).

<div class="tt-result" markdown="0">
<p>The <span class="tt-del">apparatus</span><span class="tt-ins">device</span> of claim 1</p>
</div>

The whole word changes at once, which is what you want to read.

### character

Every character is compared separately, including inside Latin words. This is the finest granularity and the noisiest — the same edit as above comes back broken into fragments:

<div class="tt-result" markdown="0">
<p>The <span class="tt-ins">d</span><span class="tt-del">app</span><span class="tt-ins">e</span><span class="tt-del">a</span><span class="tt-ins">vi</span><span class="tt-del">ratu</span><span class="tt-ins">c</span><span class="tt-del">s</span><span class="tt-ins">e</span> of claim 1</p>
</div>

Useful when you genuinely need to see a single-character edit — a typo fixed, a digit changed in a reference number, a full-width character swapped for a half-width one — and the word-level view is hiding it.

### word

Whitespace-delimited words only. The coarsest setting: anything between two spaces is either the same or entirely changed.

Useful for prose in a spaced language where you only care about which words changed, and not at all useful for Japanese, where a whole paragraph without spaces is one single token.

## Ignore case

With **Ignore case** on, `Hello` and `hello` are the same. Case differences never register as changes anywhere in the comparison.

The text itself is not altered — the result still shows whatever was actually written, in whatever case it was written. Only the matching is case-blind.

## Ignore spaces

With **Ignore spaces** on, spaces and tabs never count as a difference. Half-width spaces, full-width spaces (`　`) and tabs are all covered.

Use it when the two texts have been reflowed, re-indented, or run through different formatting, and you want to see only the changes to the words rather than to the whitespace between them.

!!! keypoint "Keep in mind"
    **Line breaks still count.** Ignore spaces covers spaces and tabs, not newlines — a paragraph that was split in two is a real change, and thisthat continues to report it. See [Reading the Result](reading-the-result.md) for how a changed line break is marked.

    Ignored spaces are also still **shown**. They simply never register as a difference; they are not removed from the text you are reading.

## Choosing between them

| Situation | Setting |
|---|---|
| Japanese, or mixed Japanese and English | **smart** |
| Ordinary English prose | **smart** |
| Hunting a typo or a single changed digit | **character** |
| A reflowed or re-indented document | **smart** + **Ignore spaces** |
| Only care about which words changed, English | **word** |
| A text retyped with different capitalisation | **Ignore case** |
