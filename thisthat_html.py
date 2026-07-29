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
from thisthat_i18n import t

_PAGE = """<!DOCTYPE html>
<html lang="{lang}">
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
  .legend {{ margin-top: 2rem; font-size: .85rem; color: var(--muted); }}
  .legend span {{ margin-right: 1.25rem; }}
  @media print {{ .nav {{ display: none; }}
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
_SCRIPT = """<script>
(function () {{
  var marks = Array.prototype.slice.call(
      document.querySelectorAll("[data-r]"));
  var total = {total};
  if (!marks.length || !total) return;

  var counter = document.getElementById("tt-count");
  var text = {strings};
  var cur = -1;

  function fmt(template, a, b) {{
    var args = [a, b], i = 0;
    return template.replace(/%d/g, function () {{ return args[i++]; }});
  }}

  function go(delta) {{
    // Wraps at either end, the way the window's F3 does.
    cur = cur < 0 ? (delta > 0 ? 0 : total - 1)
                  : (cur + delta + total) % total;
    var first = null;
    for (var i = 0; i < marks.length; i++) {{
      var on = marks[i].getAttribute("data-r") === String(cur);
      marks[i].classList.toggle("cur", on);
      if (on && !first) first = marks[i];
    }}
    if (first) first.scrollIntoView({{block: "center", behavior: "smooth"}});
    counter.textContent = fmt(text.of, cur + 1, total);
  }}

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
    nav = _NAV.format(
        prev=escape(t("prev_change")),
        next=escape(t("next_change")),
        tip_prev=escape(t("html_tip_prev"), quote=True),
        tip_next=escape(t("html_tip_next"), quote=True),
        count=escape(t("change_count_one" if total == 1
                       else "change_count_many", total)),
    )
    script = _SCRIPT.format(
        total=total,
        strings=_js({"of": t("change_of")}),
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
