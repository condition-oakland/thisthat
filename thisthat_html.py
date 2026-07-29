"""Standalone HTML export of a single-pane diff result.

The page is rendered with whatever palette it is handed, so an export looks
like the window it came from -- same light/dark choice, same deletion and
insertion colours.  Because the colours are a deliberate user choice they are
baked in rather than left to a prefers-color-scheme media query.

The two sides can be named as well, and the names go into the title, the
header and the legend -- so a saved comparison still says what was compared
weeks later, when "A" and "B" have stopped meaning anything.
"""

from html import escape

import thisthat_prefs

_PAGE = """<!DOCTYPE html>
<meta charset="utf-8">
<title>{title}</title>
<style>
  :root {{
    --del-bg: {del_bg}; --del-fg: {del_fg};
    --ins-bg: {ins_bg}; --ins-fg: {ins_fg};
    --page-fg: {fg}; --page-bg: {bg}; --muted: {muted};
  }}
  body {{
    margin: 0; padding: 2rem 1.5rem;
    background: var(--page-bg); color: var(--page-fg);
    font-family: "Yu Gothic UI", "Meiryo", "Segoe UI", system-ui, sans-serif;
    font-size: 16px; line-height: 1.8;
  }}
  main {{ max-width: 60rem; margin: 0 auto; }}
  /* The wordmark uses <s>/<u> rather than <del>/<ins> on purpose: it is the
     app's name, not part of the compared text, so it must not pick up the
     diff highlight colours or read as an edit to a screen reader. */
  h1 {{ font-size: 1.35rem; font-weight: 600; letter-spacing: -.01em;
       margin: 0 0 .1rem; }}
  h1 s, h1 u {{ text-decoration-thickness: 1px;
               text-underline-offset: .18em; }}
  h1 .sub {{ font-size: .8rem; font-weight: 400; color: var(--muted);
            letter-spacing: .04em; text-transform: uppercase;
            margin-left: .6rem; }}
  .head {{ margin: 0 0 1.5rem; padding-bottom: 1rem;
          border-bottom: 1px solid var(--muted); }}
  .head p {{ margin: .35rem 0 0; }}
  .sides {{ font-size: .95rem; }}
  .sides span {{ margin-right: 1.5rem; white-space: nowrap; }}
  .sides b {{ display: inline-block; min-width: 1.1em; text-align: center;
             font-size: .75rem; padding: .1em .35em; border-radius: 3px;
             margin-right: .4rem; vertical-align: .08em;
             background: var(--muted); color: var(--page-bg); }}
  .meta {{ color: var(--muted); font-size: .85rem; }}
  .result {{ white-space: pre-wrap; overflow-wrap: {wrap}; }}
  del {{ background: var(--del-bg); color: var(--del-fg);
        text-decoration: line-through; text-decoration-thickness: 1px;
        border-radius: 2px; padding: .05em 0; }}
  ins {{ background: var(--ins-bg); color: var(--ins-fg);
        text-decoration: underline; text-decoration-thickness: 1px;
        border-radius: 2px; padding: .05em 0; }}
  .pilcrow {{ opacity: .65; }}
  .legend {{ margin-top: 2rem; font-size: .85rem; color: var(--muted); }}
  .legend span {{ margin-right: 1.25rem; }}
</style>
<main>
  <h1><s>this</s><u>that</u><span class="sub">{heading}</span></h1>
  <div class="head">
    <p class="sides">
      <span><b>A</b>{side_a}</span>
      <span><b>B</b>{side_b}</span>
    </p>
    <p class="meta">{meta}</p>
  </div>
  <div class="result">{body}</div>
  <p class="legend">
    <span><del>deleted</del> &mdash; text only in {label_a}</span>
    <span><ins>inserted</ins> &mdash; text only in {label_b}</span>
  </p>
</main>
"""

# What each side is called when the user has not named it.  Two wordings
# because they sit in different sentences: the first follows an "A" chip, the
# second stands alone in the legend, where a bare "this" would not say much.
DEFAULT_SIDE_A = "this (original)"
DEFAULT_SIDE_B = "that (revised)"
DEFAULT_LABEL_A = "A (this)"
DEFAULT_LABEL_B = "B (that)"

_COLOUR_FIELDS = ("del_bg", "del_fg", "ins_bg", "ins_fg", "bg", "fg", "muted")


def _mark(text, tag):
    """Escape *text* and wrap it in <del>/<ins>, one element per line.

    A changed line break is shown as a marked-up pilcrow, then emitted as a
    real newline outside the element -- so the highlight never bleeds across
    the full width of the line.
    """
    parts = escape(text).split("\n")
    pieces = []
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        inner = part if last else part + '<span class="pilcrow">¶</span>'
        if inner:
            pieces.append("<%s>%s</%s>" % (tag, inner, tag))
        if not last:
            pieces.append("\n")
    return "".join(pieces)


def render_body(segments):
    out = []
    for op, text in segments:
        if op == "equal":
            out.append(escape(text))
        elif op == "delete":
            out.append(_mark(text, "del"))
        else:
            out.append(_mark(text, "ins"))
    return "".join(out)


def side_labels(name_a="", name_b=""):
    """(side_a, side_b, label_a, label_b) for a pair of user-supplied names.

    Either name may be blank; a blank side keeps the generic wording, so an
    export nobody bothered to name reads exactly as it always has.
    """
    a, b = (name_a or "").strip(), (name_b or "").strip()
    return (a or DEFAULT_SIDE_A, b or DEFAULT_SIDE_B,
            a or DEFAULT_LABEL_A, b or DEFAULT_LABEL_B)


def page_title(name_a="", name_b=""):
    """The <title> for an export: the two sides, once either has a name."""
    if not (name_a or "").strip() and not (name_b or "").strip():
        return "thisthat result"
    _side_a, _side_b, label_a, label_b = side_labels(name_a, name_b)
    return "thisthat — %s vs %s" % (label_a, label_b)


def render_page(segments, title=None, heading="result", meta="",
                wrap="normal", palette=None, name_a="", name_b=""):
    colours = dict(thisthat_prefs.DEFAULT_THEMES["light"])
    if palette:
        colours.update(palette)
    side_a, side_b, label_a, label_b = side_labels(name_a, name_b)
    return _PAGE.format(
        title=escape(title if title is not None
                     else page_title(name_a, name_b)),
        heading=escape(heading),
        meta=escape(meta),
        side_a=escape(side_a),
        side_b=escape(side_b),
        label_a=escape(label_a),
        label_b=escape(label_b),
        body=render_body(segments),
        wrap=wrap,
        **{key: escape(colours[key], quote=True) for key in _COLOUR_FIELDS}
    )
