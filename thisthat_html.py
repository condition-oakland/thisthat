"""Standalone HTML export of a single-pane diff result.

The page is rendered with whatever palette it is handed, so an export looks
like the window it came from -- same light/dark choice, same deletion and
insertion colours.  Because the colours are a deliberate user choice they are
baked in rather than left to a prefers-color-scheme media query.

The two sides can be named as well, and the names go into the title, the
header and the legend -- so a saved comparison still says what was compared
weeks later, when "A" and "B" have stopped meaning anything.

The page's own wording follows the interface language, for the same reason the
colours follow the theme: the export is a record of what you were looking at,
and it should read the way the window read.

The export also carries the window's Previous / Next navigation, so a long
comparison can be walked change by change in a browser instead of hunted
through by eye.  That is the only script on the page, it is inline, and the
page is complete without it: with scripting off the result still reads, only
without the bar.
"""

import json
from html import escape

import thisthat_i18n
import thisthat_prefs
import thisthat_version
from thisthat_i18n import t

_PAGE = """<!DOCTYPE html>
<html lang="{lang}">
<meta charset="utf-8">
<meta name="generator" content="thisthat {version}">
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
  /* The navigation bar sticks to the top of the viewport: walking a long
     comparison change by change is no use if the controls scroll away. */
  .nav {{ position: sticky; top: 0; z-index: 1;
         display: flex; align-items: center; gap: .4rem;
         margin: 0 0 .9rem; padding: .55rem 0;
         background: var(--page-bg); }}
  .nav button {{ font: inherit; font-size: .85rem; line-height: 1.2;
                color: var(--page-fg); background: transparent;
                border: 1px solid var(--muted); border-radius: 4px;
                padding: .3em .8em; cursor: pointer; }}
  .nav button:hover {{ border-color: var(--page-fg); }}
  .nav .count {{ color: var(--muted); font-size: .85rem;
                margin-left: .5rem; }}
  .result {{ white-space: pre-wrap; overflow-wrap: {wrap}; }}
  del {{ background: var(--del-bg); color: var(--del-fg);
        text-decoration: line-through; text-decoration-thickness: 1px;
        border-radius: 2px; padding: .05em 0; }}
  ins {{ background: var(--ins-bg); color: var(--ins-fg);
        text-decoration: underline; text-decoration-thickness: 1px;
        border-radius: 2px; padding: .05em 0; }}
  .pilcrow {{ opacity: .65; }}
  /* The change you are standing on.  An outline in the page's own foreground
     colour rather than a different fill, so it reads as "this one" in both
     themes without disturbing the deletion / insertion colours themselves. */
  .cur {{ outline: 2px solid var(--page-fg); outline-offset: 1px; }}
  /* A caret of our own.  A browser shows none on a page you cannot type into,
     so clicking to say "carry on from here" would otherwise be a control with
     no visible effect until the next keypress. */
  .tt-caret {{ position: absolute; width: 2px; background: var(--page-fg);
              pointer-events: none; }}
  .tt-caret[hidden] {{ display: none; }}
  @media (prefers-reduced-motion: no-preference) {{
    .tt-caret {{ animation: tt-blink 1.1s step-end infinite; }}
  }}
  @keyframes tt-blink {{ 50% {{ opacity: 0; }} }}
  .legend {{ margin-top: 2rem; font-size: .85rem; color: var(--muted); }}
  .legend span {{ margin-right: 1.25rem; }}
  @media print {{ .nav, .tt-caret {{ display: none; }}
                 .cur {{ outline: none; }} }}
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
{nav}  <div class="result">{body}</div>
  <p class="legend">
    <span><del>{legend_del}</del> &mdash; {legend_del_note}</span>
    <span><ins>{legend_ins}</ins> &mdash; {legend_ins_note}</span>
  </p>
</main>
{script}"""

# Only written out when there is something to navigate.
_NAV = """  <div class="nav">
    <button type="button" id="tt-prev" title="{tip_prev}">{prev}</button>
    <button type="button" id="tt-next" title="{tip_next}">{next}</button>
    <span class="count" id="tt-count">{count}</span>
  </div>
"""

# Deliberately plain, old-fashioned JavaScript: an exported page may be opened
# anywhere, years from now, and there is nothing here worth a build step.
#
# Next and Previous move from where you are rather than from wherever they left
# off, which is what the window does with its caret.  A page you cannot type
# into has no caret, so "where you are" is taken from two places: a click or a
# selection in the result, and failing that the top of the viewport -- because
# having scrolled somewhere is itself a statement about where you are looking.
_SCRIPT = """<script>
(function () {{
  var result = document.querySelector(".result");
  var marks = Array.prototype.slice.call(
      document.querySelectorAll("[data-r]"));
  var total = {total};
  if (!result || !marks.length || !total) return;

  // The marks are in document order, so the first and last of each region
  // bound it -- that is all the navigation needs to know about it.
  var regions = [];
  for (var m = 0; m < marks.length; m++) {{
    var index = +marks[m].getAttribute("data-r");
    if (regions[index]) regions[index].last = marks[m];
    else regions[index] = {{first: marks[m], last: marks[m]}};
  }}

  var counter = document.getElementById("tt-count");
  var text = {strings};
  var caret = document.createElement("div");
  var anchor = null;   // a Range: where Next and Previous count from
  var cur = -1;        // the region lit up, for the counter

  caret.className = "tt-caret";
  caret.hidden = true;
  document.body.appendChild(caret);

  function fmt(template, a, b) {{
    var args = [a, b], i = 0;
    return template.replace(/%d/g, function () {{ return args[i++]; }});
  }}

  // --- positions ------------------------------------------------------------

  function point(el, atEnd) {{
    var range = document.createRange();
    if (atEnd) {{ range.setEndAfter(el); range.collapse(false); }}
    else {{ range.setStartBefore(el); range.collapse(true); }}
    return range;
  }}

  function edge(range, atEnd) {{
    var copy = range.cloneRange();
    copy.collapse(!atEnd);
    return copy;
  }}

  function before(a, b) {{
    // Both collapsed, so START_TO_START reads simply as "a is not past b".
    return a.compareBoundaryPoints(Range.START_TO_START, b) <= 0;
  }}

  function rectOf(range) {{
    var rect = range.getBoundingClientRect();
    if (rect && (rect.height || rect.width)) return rect;
    // No rect of its own: fall back to whatever the range sits in front of,
    // and only then to its parent.  Taking the container straight off would
    // land on the whole result -- which is always on screen somewhere, and so
    // would report every anchor as visible.
    var node = range.startContainer;
    if (node.nodeType === 1) node = node.childNodes[range.startOffset] || node;
    if (node.nodeType !== 1) node = node.parentNode;
    return node ? node.getBoundingClientRect() : null;
  }}

  function topEdge() {{
    var bar = document.querySelector(".nav");
    return bar ? bar.getBoundingClientRect().bottom : 0;
  }}

  // The anchor only counts while it is still on screen.  Click somewhere and
  // you carry on from there; scroll right away from it and what you are
  // looking at now is the better guess.
  function live() {{
    if (!anchor) return null;
    var rect = rectOf(anchor);
    return rect && rect.bottom > topEdge() &&
           rect.top < window.innerHeight ? anchor : null;
  }}

  function pick(delta) {{
    var start = live(), i;
    if (start) {{
      try {{
        // Next starts looking past the end of a selection, Previous before
        // its beginning -- with a bare caret the two are the same point.
        if (delta > 0) {{
          var from = edge(start, true);
          for (i = 0; i < total; i++) {{
            if (!before(point(regions[i].first, false), from)) return i;
          }}
          return 0;                       // wrapped past the last change
        }}
        var to = edge(start, false);
        for (i = total - 1; i >= 0; i--) {{
          if (before(point(regions[i].last, true), to)) return i;
        }}
        return total - 1;                 // wrapped back past the first
      }} catch (err) {{
        // An anchor we can no longer place: fall through to the viewport.
      }}
    }}
    var top = topEdge();
    if (delta > 0) {{
      for (i = 0; i < total; i++) {{
        if (regions[i].first.getBoundingClientRect().top >= top) return i;
      }}
      return 0;
    }}
    for (i = total - 1; i >= 0; i--) {{
      if (regions[i].last.getBoundingClientRect().bottom <= top) return i;
    }}
    return total - 1;
  }}

  // --- what you see ---------------------------------------------------------

  function light(target) {{
    for (var i = 0; i < marks.length; i++) {{
      marks[i].classList.toggle(
          "cur", +marks[i].getAttribute("data-r") === target);
    }}
  }}

  function paint() {{
    // Page coordinates, not viewport ones, so the caret rides with the text.
    var rect = anchor && anchor.collapsed
        ? anchor.getBoundingClientRect() : null;
    if (!rect || !rect.height) {{ caret.hidden = true; return; }}
    caret.style.top = (rect.top + (window.pageYOffset || 0)) + "px";
    caret.style.left = (rect.left + (window.pageXOffset || 0)) + "px";
    caret.style.height = rect.height + "px";
    caret.hidden = false;
  }}

  function setAnchor(range) {{
    anchor = range ? range.cloneRange() : null;
    paint();
  }}

  function moved() {{
    // You have put yourself somewhere else, so the lit change is no longer
    // where you are -- and the counter goes back to saying how many there are.
    cur = -1;
    light(-1);
    counter.textContent = text.count;
  }}

  function go(delta) {{
    cur = pick(delta);
    light(cur);
    // Leaving the anchor at the start of the change just landed on is what
    // makes the next press step on rather than land here again.
    setAnchor(point(regions[cur].first, false));
    regions[cur].first.scrollIntoView({{block: "center"}});
    counter.textContent = fmt(text.of, cur + 1, total);
  }}

  // --- putting yourself somewhere -------------------------------------------

  function fromPoint(x, y) {{
    if (document.caretRangeFromPoint) return document.caretRangeFromPoint(x, y);
    if (document.caretPositionFromPoint) {{
      var spot = document.caretPositionFromPoint(x, y);
      if (!spot) return null;
      var range = document.createRange();
      range.setStart(spot.offsetNode, spot.offset);
      range.collapse(true);
      return range;
    }}
    return null;
  }}

  function selectionInResult() {{
    var sel = window.getSelection();
    return sel && sel.rangeCount && result.contains(sel.anchorNode) ? sel : null;
  }}

  // Some browsers put a collapsed selection where you clicked and some do not,
  // so a plain click is read from the point itself; a drag is left to the
  // selection, which knows both ends of what was dragged over.
  result.addEventListener("mouseup", function (event) {{
    var sel = selectionInResult();
    if (sel && !sel.isCollapsed) return;
    var range = fromPoint(event.clientX, event.clientY);
    if (!range) return;
    setAnchor(range);
    moved();
  }});

  document.addEventListener("selectionchange", function () {{
    var sel = selectionInResult();
    if (!sel) return;
    setAnchor(sel.getRangeAt(0));
    moved();
  }});

  window.addEventListener("resize", paint);

  document.getElementById("tt-prev").onclick = function () {{ go(-1); }};
  document.getElementById("tt-next").onclick = function () {{ go(1); }};

  // n / p rather than the window's F3: in a browser F3 is Find, and taking
  // that away from the page would cost more than the shortcut is worth.
  document.addEventListener("keydown", function (event) {{
    if (event.ctrlKey || event.altKey || event.metaKey) return;
    var key = (event.key || "").toLowerCase();
    if (key !== "n" && key !== "p") return;
    event.preventDefault();
    go(key === "n" ? 1 : -1);
  }});
}}());
</script>
"""

_COLOUR_FIELDS = ("del_bg", "del_fg", "ins_bg", "ins_fg", "bg", "fg", "muted")


def _mark(text, tag, region):
    """Escape *text* and wrap it in <del>/<ins>, one element per line.

    A changed line break is shown as a marked-up pilcrow, then emitted as a
    real newline outside the element -- so the highlight never bleeds across
    the full width of the line.

    Every element carries the index of the change region it belongs to, which
    is what the navigation script steps through.  One region can become several
    elements -- a deletion and its replacement, each split across lines -- and
    they all light up together.
    """
    parts = escape(text).split("\n")
    pieces = []
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        inner = part if last else part + '<span class="pilcrow">¶</span>'
        if inner:
            pieces.append('<%s data-r="%d">%s</%s>' % (tag, region, inner, tag))
        if not last:
            pieces.append("\n")
    return "".join(pieces)


def render_body(segments):
    """(html, region_count) for a diff.

    A region is a run of consecutive changed segments -- a deletion and the
    insertion that replaces it are one change to step through, not two.  That
    is the same grouping the window's counter and F3 use, so an export is
    walked in the same number of steps as the result it came from.
    """
    out = []
    region = -1
    prev_changed = False
    for op, text in segments:
        if op == "equal":
            out.append(escape(text))
            prev_changed = False
            continue
        if not prev_changed:
            region += 1
        prev_changed = True
        out.append(_mark(text, "del" if op == "delete" else "ins", region))
    return "".join(out), region + 1


def side_labels(name_a="", name_b=""):
    """(side_a, side_b, label_a, label_b) for a pair of user-supplied names.

    Either name may be blank; a blank side keeps the generic wording -- two
    wordings of it, because they sit in different sentences: the first follows
    an "A" chip, the second stands alone in the legend, where a bare "this"
    would not say much.
    """
    a, b = (name_a or "").strip(), (name_b or "").strip()
    return (a or t("html_side_a"), b or t("html_side_b"),
            a or t("html_label_a"), b or t("html_label_b"))


def page_title(name_a="", name_b=""):
    """The <title> for an export: the two sides, once either has a name."""
    if not (name_a or "").strip() and not (name_b or "").strip():
        return t("html_title_plain")
    _side_a, _side_b, label_a, label_b = side_labels(name_a, name_b)
    return t("html_title_named", label_a, label_b)


def _js(value):
    """A Python value as a JavaScript literal, safe to inline in <script>.

    json.dumps leaves "<" alone, which would let a "</script>" anywhere in the
    text end the element early; escaping it closes that off.
    """
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


def _nav_and_script(total):
    """The navigation bar and its script -- both empty when nothing changed."""
    if not total:
        return "", ""
    count = t("change_count_one" if total == 1 else "change_count_many", total)
    nav = _NAV.format(
        prev=escape(t("prev_change")),
        next=escape(t("next_change")),
        tip_prev=escape(t("html_tip_prev"), quote=True),
        tip_next=escape(t("html_tip_next"), quote=True),
        count=escape(count),
    )
    script = _SCRIPT.format(
        total=total,
        strings=_js({"of": t("change_of"), "count": count}),
    )
    return nav, script


def render_page(segments, title=None, heading=None, meta="",
                wrap="normal", palette=None, name_a="", name_b=""):
    colours = dict(thisthat_prefs.DEFAULT_THEMES["light"])
    if palette:
        colours.update(palette)
    side_a, side_b, label_a, label_b = side_labels(name_a, name_b)
    body, total = render_body(segments)
    nav, script = _nav_and_script(total)
    return _PAGE.format(
        lang=escape(thisthat_i18n.language(), quote=True),
        version=escape(thisthat_version.__version__, quote=True),
        title=escape(title if title is not None
                     else page_title(name_a, name_b)),
        heading=escape(heading if heading is not None else t("html_heading")),
        meta=escape(meta),
        side_a=escape(side_a),
        side_b=escape(side_b),
        legend_del=escape(t("html_legend_del")),
        legend_ins=escape(t("html_legend_ins")),
        legend_del_note=escape(t("html_only_in", label_a)),
        legend_ins_note=escape(t("html_only_in", label_b)),
        body=body,
        nav=nav,
        script=script,
        wrap=wrap,
        **{key: escape(colours[key], quote=True) for key in _COLOUR_FIELDS}
    )
