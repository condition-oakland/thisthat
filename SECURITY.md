# Security

## Reporting a vulnerability

Please report privately, not as a public issue: use
**[Report a vulnerability](https://github.com/condition-oakland/thisthat/security/advisories/new)**
under this repository's Security tab.

Expect an acknowledgement within about a week. thisthat is maintained by one
person in their own time, so a fix may take longer than that — but a report
will not be left unanswered.

If a report turns out to be a real vulnerability, the fix ships as a new
release with a GitHub Security Advisory, and the reporter is credited unless
they would rather not be.

## What thisthat does, and does not do

Most of the questions worth asking about a diff tool are answered by what it
never does:

- **It has no network code at all.** No telemetry, no update check, no crash
  reporting, no analytics. The two texts you compare never leave the machine,
  because there is nothing in the program that could send them anywhere.
- **It has no dependencies.** The app is pure Python standard library plus
  tkinter. PyInstaller and Pillow are used to *build* it and are not part of
  what runs.
- **It writes exactly two things**: the HTML file you explicitly save, where
  you tell it to save it, and `%APPDATA%\thisthat\settings.json`, which holds
  a theme name, a language code, two font sizes and four colours. Nothing is
  written beside the exe.

## In scope

Reports about any of these are wanted:

- **The exported HTML.** Every value that reaches the page is escaped, and the
  colours and wrap mode — the only two that land inside `<style>`, where
  escaping is not a defence — are validated rather than escaped. An export is
  meant to be safe to open and to forward even when the compared text came from
  somewhere untrusted. If you can make a saved page execute script, run style,
  or load a remote resource, that is a vulnerability.
- **`settings.json` parsing.** A hand-edited or hostile settings file must
  never do more than be ignored. Every field is validated and anything
  unrecognised is dropped.
- **Anything a compared text can do to the app itself** beyond being slow: a
  crash that is not a clean error, a path written that you did not choose.
- **The integrity of a release.** If a published asset does not match its
  checksum, or the checksums do not match a build of the tagged commit, say so
  immediately.

## Known and accepted

These are documented rather than fixed, so a report of one will be closed as
already known:

- **The exe is not code-signed**, so the first run raises Windows SmartScreen's
  "Windows protected your PC". A signing certificate is not something this
  project has. Verify the download against the SHA-256 published in the release
  notes instead, or
  [run from source](https://condition-oakland.github.io/thisthat/en/getting-started/#from-source),
  which SmartScreen does not apply to.
- **Comparing two very long texts with little in common is slow**, by the
  nature of the matching. It runs on a worker thread with a progress dialog, so
  the window stays responsive, but cancelling stops the waiting rather than the
  work. Self-inflicted only: nothing outside the app can start a comparison.
- **A saved page contains the full text of both sides**, unchanged parts
  included. That is the point of it — but it means an export is exactly as
  confidential as the documents it came from. See
  [Saving HTML](https://condition-oakland.github.io/thisthat/en/saving-html/).

## Supported versions

The latest release. Fixes go into a new version rather than being backported.
