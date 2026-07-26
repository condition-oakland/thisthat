# Third-party notices

thisthat is released under the MIT License; see `LICENSE`.

Two other people's work is acknowledged below. Keep this file with the code
and with any binary you distribute.

---

## difff《ﾃﾞｭﾌﾌ》 — inspiration, no code

thisthat is an independent reimplementation inspired by difff《ﾃﾞｭﾌﾌ》
(https://github.com/meso-cacase/difff).

> Copyright © 2004-2026 Yuki Naito (@meso_cacase).
> This software is distributed under a BSD license.

**No code from that project is included here.** difff is Perl CGI that shells
out to the UNIX `diff` command through named pipes and renders two panes side
by side; thisthat is Python that diffs in-process with
`difflib.SequenceMatcher` and renders one. What is shared is the tokenizing
approach — Latin words and numbers compared whole, CJK compared character by
character — which is an idea rather than an expression, and so carries no
licence obligation. This notice is given as attribution, not because it is
required.

thisthat is **not affiliated with, endorsed by, or supported by** the author of
difff. Please do not report problems with this program to them.

---

## Lucide — the icon

`thisthat.ico` reproduces the geometry of the Lucide `diff` glyph
(https://lucide.dev/icons/diff), recoloured to a single flat ink on a rounded
white tile. The `diff` icon is not among those Lucide derives from Feather, so the
ISC licence below is the one that applies.

```
ISC License

Copyright (c) 2026 Lucide Icons and Contributors

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

---

## Python and Tk

thisthat imports only the Python standard library. Python and Tcl/Tk carry
their own permissive licences and are not redistributed by this project —
except inside a PyInstaller build, where PyInstaller's own documentation covers
what to include. A PyInstaller build also embeds PyInstaller's bootloader and
its splash-screen Tcl/Tk runtime, both covered by that same documentation.
