# Changelog

Notable changes to thisthat, newest first. This file is the source for the
notes on each [GitHub release](https://github.com/condition-oakland/thisthat/releases).

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the numbering is [semantic](https://semver.org/spec/v2.0.0.html): PATCH for
fixes, MINOR for features, MAJOR for breaking something a user relied on -- a
settings file older versions cannot read, a shortcut that moves, a feature that
goes away.

Add to `## [Unreleased]` as you land things, rather than reconstructing it at
release time. Cutting a release renames that heading to the version and date.

## [Unreleased]

Nothing yet.

## [1.0.0] -- 2026-07-30

First release.

### Added

- Single-pane comparison in the style of Word's tracked changes: deletions
  struck through on a highlight, insertions underlined on a highlight, both in
  one reading order rather than in two panes you have to scan side by side.
- **A -- this** and **B -- that** input boxes, with Load, Swap and Clear, and
  an optional Name for each side that labels it in the exported page.
- **Compare by** granularity, plus **Ignore case** and **Ignore spaces**.
- **Previous** / **Next** change navigation with a counter, and adjustable
  result text size.
- **Save HTML…** -- a standalone page with the marks, the legend and its own
  change navigation, needing nothing else to open it.
- Preferences: interface language (Japanese and English), light and dark
  themes, and free choice of all four diff colours, with light and dark keeping
  separate sets. Settings live in the user profile, so the exe stays portable.
- Long texts are diffed on a worker thread and painted in time-sliced chunks,
  so the window keeps responding; a progress dialog appears if the work runs
  long.
- Keyboard shortcuts throughout, in the app and in the exported page.
- A bilingual user guide at
  <https://condition-oakland.github.io/thisthat/>.
- Distribution as a one-file Windows exe with no installer and no runtime
  dependencies, alongside running the same program from source on Python 3.9+.

[Unreleased]: https://github.com/condition-oakland/thisthat/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/condition-oakland/thisthat/releases/tag/v1.0.0
