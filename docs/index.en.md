# thisthat User Guide

Welcome to the thisthat user guide.

**thisthat** is a desktop text comparer. Paste *this* — the old text — into **A** on the left, *that* — the new text — into **B** on the right, and the difference comes back in **one pane**, marked up the way Word shows tracked changes: deleted text struck through, inserted text underlined.

Hence the name, and hence the wordmark — ~~this~~<u>that</u> is also the legend for every result you will read.

<div class="tt-result" markdown="0">
<p>The quick brown fox <span class="tt-del">jumped</span><span class="tt-ins">leapt</span> over the lazy dog.</p>
</div>

## Where to Start

If you are new to thisthat, start here:

- [Getting Started](getting-started.md) — getting the app, running it, and what the window contains
- [Running a Comparison](comparing.md) — pasting, comparing, and the basic controls
- [Reading the Result](reading-the-result.md) — what the colours and marks mean

## Quick Links

| I want to... | Go to |
|---|---|
| Compare two texts | [Running a Comparison](comparing.md) |
| Switch between character and word comparison | [Comparison Options](comparison-options.md) |
| Ignore case or spacing differences | [Comparison Options](comparison-options.md) |
| Step through the changes one at a time | [Moving Between Changes](navigating-changes.md) |
| Save or hand off a result | [Saving as HTML](saving-html.md) |
| Change the language, colours or theme | [Preferences](preferences.md) |
| Compare long documents | [Long Texts](long-texts.md) |
| Understand how the comparison works | [The Comparison Engine](comparison-engine.md) |
| Look up a keyboard shortcut | [Keyboard Shortcuts](keyboard-shortcuts.md) |

!!! keypoint "Keep in mind"
    thisthat **compares nothing until you ask it to.** Typing or pasting into a box never produces a result on its own. Press **Compare** (or **Ctrl+Enter**) when both sides are ready.

## About thisthat

thisthat is inspired by [difff《デュフフ》](https://github.com/meso-cacase/difff), and keeps difff's tokenizing approach — the thing that makes it work well on mixed Japanese and English text. It is an independent reimplementation, not affiliated with or endorsed by difff's author. See [The Comparison Engine](comparison-engine.md) for the details.
