"""The version number, in one place.

Everything that needs to name a version reads it from here: the Preferences
dialog shows it so a bug report can state it, the exported page carries it as
its generator, and build.bat reads it out with a python -c one-liner to name
the release folder and the zip.  Cutting a release is therefore one edit to
this file -- see the release checklist in README.md.

Its own module rather than a constant in thisthat_app.py because
thisthat_html.py needs it too, and importing the app module from the exporter
that the app imports would be a cycle.

Semantic versioning, MAJOR.MINOR.PATCH: PATCH for fixes, MINOR for features,
MAJOR for breaking what a user relied on -- a settings file older versions
cannot read, a shortcut that moves, a feature that goes away.
"""

__version__ = "1.0.1"
