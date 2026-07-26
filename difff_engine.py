"""Tokenizing diff engine for difff-desktop.

Follows the approach of difff (https://github.com/meso-cacase/difff): the two
texts are split into small tokens -- Latin words and numbers stay whole while
CJK is compared character by character -- and the two token sequences are
diffed against each other.  Unlike difff, the result is returned as a single
stream of (op, text) segments so it can be rendered inline, Word-style, in one
pane instead of two.

Public API:
    tokenize(text, mode) -> list[str]
    diff_segments(text_a, text_b, ...) -> list[tuple[str, str]]
    summarize(segments) -> dict
"""

import re
from difflib import SequenceMatcher

# --- granularity modes -------------------------------------------------------

DIFFF = "difff"  # Latin words / numbers atomic, everything else per character
CHAR = "char"  # every character is its own token
WORD = "word"  # whitespace-delimited words

MODES = (DIFFF, CHAR, WORD)

MODE_LABELS = {
    DIFFF: "difff (words + characters)",
    CHAR: "character",
    WORD: "word",
}

_SPACE_CLASS = r"[ \t　 ]"

# Latin word (with internal apostrophes), or a number, or any single character.
_TOKEN_DIFFF = re.compile(
    r"\n"
    r"|" + _SPACE_CLASS + r"+"
    r"|[A-Za-zÀ-ɏ]+(?:['’][A-Za-z]+)*"
    r"|\d+(?:[.,]\d+)*"
    r"|.",
    re.S,
)

_TOKEN_CHAR = re.compile(r".|\n", re.S)

_TOKEN_WORD = re.compile(r"\n|" + _SPACE_CLASS + r"+|[^\s]+", re.S)

_TOKENIZERS = {DIFFF: _TOKEN_DIFFF, CHAR: _TOKEN_CHAR, WORD: _TOKEN_WORD}


def normalize_newlines(text):
    """CRLF / CR -> LF, so line endings never show up as spurious changes."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def tokenize(text, mode=DIFFF):
    """Split *text* into comparison tokens according to *mode*."""
    pattern = _TOKENIZERS.get(mode, _TOKEN_DIFFF)
    return pattern.findall(text)


def is_blank(token):
    """True for a whitespace token that is not a line break."""
    return token != "\n" and token.strip() == "" and token != ""


# --- diffing -----------------------------------------------------------------


def _comparable(tokens, ignore_case, ignore_space):
    """Return (indices, keys): the tokens that take part in the comparison.

    Tokens excluded here (spaces when *ignore_space* is on) still appear in the
    output -- they simply never count as a difference.
    """
    indices = []
    keys = []
    for i, tok in enumerate(tokens):
        if ignore_space and is_blank(tok):
            continue
        indices.append(i)
        keys.append(tok.casefold() if ignore_case else tok)
    return indices, keys


def _bound(indices, k, total):
    """Map a position in comparison space back to a position in token space."""
    if k <= 0:
        return 0
    if k >= len(indices):
        return total
    return indices[k]


def _emit(out, op, tokens):
    if not tokens:
        return
    text = "".join(tokens)
    if out and out[-1][0] == op:
        out[-1] = (op, out[-1][1] + text)
    else:
        out.append((op, text))


def diff_segments(text_a, text_b, mode=DIFFF, ignore_case=False,
                  ignore_space=False):
    """Diff two texts and return a flat list of (op, text) segments.

    *op* is one of ``"equal"``, ``"delete"`` (present only in A) or
    ``"insert"`` (present only in B).  Concatenating the ``equal`` + ``delete``
    text reproduces A; ``equal`` + ``insert`` reproduces B.
    """
    a = normalize_newlines(text_a)
    b = normalize_newlines(text_b)

    tok_a = tokenize(a, mode)
    tok_b = tokenize(b, mode)

    idx_a, key_a = _comparable(tok_a, ignore_case, ignore_space)
    idx_b, key_b = _comparable(tok_b, ignore_case, ignore_space)

    out = []

    # Degenerate cases: one or both sides have nothing to compare.
    if not key_a and not key_b:
        # Both sides are empty or (ignoring spaces) pure whitespace.
        _emit(out, "equal", tok_a or tok_b)
        return out
    if not key_a or not key_b:
        _emit(out, "delete", tok_a)
        _emit(out, "insert", tok_b)
        return out

    def from_a(op, c1, c2):
        _emit(out, op, tok_a[_bound(idx_a, c1, len(tok_a)):
                             _bound(idx_a, c2, len(tok_a))])

    def from_b(op, c1, c2):
        _emit(out, op, tok_b[_bound(idx_b, c1, len(tok_b)):
                             _bound(idx_b, c2, len(tok_b))])

    # Trim the common head and tail before handing the rest to difflib.
    # SequenceMatcher cost grows far faster than linearly, and a real edit
    # usually touches a small part of a long document -- on a 100k-character
    # text with one changed paragraph this is the difference between seconds
    # and milliseconds.
    limit = min(len(key_a), len(key_b))
    head = 0
    while head < limit and key_a[head] == key_b[head]:
        head += 1
    tail = 0
    while tail < limit - head and key_a[-1 - tail] == key_b[-1 - tail]:
        tail += 1

    from_a("equal", 0, head)

    matcher = SequenceMatcher(a=key_a[head:len(key_a) - tail],
                              b=key_b[head:len(key_b) - tail],
                              autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        i1, i2, j1, j2 = i1 + head, i2 + head, j1 + head, j2 + head
        if tag == "equal":
            from_a("equal", i1, i2)
        elif tag == "delete":
            from_a("delete", i1, i2)
        elif tag == "insert":
            from_b("insert", j1, j2)
        else:  # replace -- show the old text struck out, then the new text
            from_a("delete", i1, i2)
            from_b("insert", j1, j2)

    from_a("equal", len(key_a) - tail, len(key_a))
    return out


def change_regions(segments, mark_line_breaks=True):
    """Character offsets of each change region in the rendered result.

    A region is a maximal run of consecutive changed segments -- a deletion
    immediately followed by its replacement counts as one.  Offsets are into
    the *rendered* text, which is why the pilcrow a renderer adds for a changed
    line break has to be counted here too.

    Returns a list of (start, end) character offsets.
    """
    regions = []
    offset = 0
    start = None
    for op, text in segments:
        if op == "equal":
            if start is not None:
                regions.append((start, offset))
                start = None
            offset += len(text)
        else:
            if start is None:
                start = offset
            offset += len(text)
            if mark_line_breaks:
                offset += text.count("\n")  # each "\n" renders as "¶\n"
    if start is not None:
        regions.append((start, offset))
    return regions


def summarize(segments):
    """Counts for the status bar."""
    deleted = sum(len(t) for op, t in segments if op == "delete")
    inserted = sum(len(t) for op, t in segments if op == "insert")
    regions = 0
    prev_changed = False
    for op, _ in segments:
        changed = op != "equal"
        if changed and not prev_changed:
            regions += 1
        prev_changed = changed
    return {
        "deleted_chars": deleted,
        "inserted_chars": inserted,
        "regions": regions,
        "identical": deleted == 0 and inserted == 0,
    }
