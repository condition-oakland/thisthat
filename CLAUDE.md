# thisthat — CLAUDE.md

A desktop text comparer: tkinter GUI, pure standard library, shipped as a
Windows one-file exe. `README.md` documents the app, its controls and the build.
`docs/CLAUDE.md` documents the user guide and **must be read before touching
anything under `docs/`** — the Japanese pages have an encoding rule that
corrupts them silently if ignored.

## Cutting a release

Triggered by "cut a release", "cut a new release", "ship X.Y.Z", "release this"
and the like.

Ask which part to bump if the user has not said. Numbering is semantic: PATCH
for fixes, MINOR for features, MAJOR for breaking something a user relied on —
a settings file older versions cannot read, a shortcut that moves, a feature
that goes away.

Then, in order:

1. **Check the tree is clean and on `main`.** The tag has to name a commit that
   really is what got built, so never cut a release from a dirty tree.
2. **Bump `__version__` in `thisthat_version.py`.** It is the single source of
   truth: Preferences shows it in its corner, the exported HTML carries it as
   its `generator`, and `build.bat` names the release folder and zip from it.
   One edit moves all three.
3. **Update `CHANGELOG.md`**: rename `## [Unreleased]` to
   `## [X.Y.Z] -- YYYY-MM-DD` with today's real date, add a fresh empty
   `## [Unreleased]` above it, and fix the two link definitions at the bottom.
4. **Commit** both files together.
5. **Build**: `cmd /c "<repo>\build.bat"`. Pass the full path — a bare
   `cmd /c build.bat` is not found even when the shell's own cwd is the project
   root. It wipes `build/` and `dist/` first, takes a couple of minutes, and
   ends in `pause`, which is harmless non-interactively. Confirm it echoes the
   version you just set and produces `dist\thisthat-vX.Y.Z.zip`.
6. **Tag the built commit and push**:

   ```
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin main --follow-tags
   ```

7. **Take the zip's SHA-256** with `(Get-FileHash dist\thisthat-vX.Y.Z.zip).Hash`
   and append it to the notes, as a fenced block under a `## Checksum` heading.
   This is not optional: the exe is unsigned and the guide teaches users to
   click past SmartScreen, so `SECURITY.md` and both getting-started pages tell
   them to verify against a hash published in the release notes. A release
   without one makes those three pages wrong.

8. **Publish**, with notes taken from the CHANGELOG section just written:

   ```
   gh release create vX.Y.Z dist\thisthat-vX.Y.Z.zip --title vX.Y.Z --notes-file <file>
   ```

9. **Report the release URL**, and remind the user to download the asset, check
   its hash against the notes, and run it once. An asset nobody has opened is a
   release nobody has tested.

Nothing in the user guide needs updating per release — every download link
points at `/releases/latest`, which GitHub resolves to the newest one.

### Do not

- **Do not commit `dist/`.** It is gitignored and must stay so: an 11 MB exe
  does not delta-compress, so one per version would sit in the history forever.
  Release assets live on the release, not in the tree.
- **Do not hardcode a version anywhere.** Anything that needs to name it imports
  `thisthat_version`.
- **Do not tag before the build succeeds.** A tag on a commit that does not
  build is worse than no tag.
- **Do not add a version string to `thisthat_i18n.py`.** "thisthat 1.0.0" reads
  the same in every language.
- **Do not loosen a dependency pin.** `requirements_build.txt` and
  `docs-requirements.txt` pin every package in their trees to an exact version
  and to the SHA-256 of every distribution PyPI holds for it, and both are
  installed with `--require-hashes`. Bumping or adding one means regenerating
  the whole file — `pip download --only-binary :all: -d <dir> <pins>` to resolve
  the tree, then each package's hashes from
  `https://pypi.org/pypi/<name>/<version>/json`, or `pip-compile
  --generate-hashes`, which does both. Verify with a `--require-hashes` install
  into a throwaway venv: it fails loudly if any transitive dep is left
  floating.

## gh authentication

`gh` authenticates from the Windows keyring (a `gho_` token with `repo` and
`workflow` scopes). If a `gh` call reports an invalid token, look for a stale
`GH_TOKEN` environment variable before anything else: it silently overrides the
keyring, so an expired one there fails every call while `gh auth login` appears
to have worked. Check both the process environment and the User scope.

## Verifying changes

The app has no test suite. What is worth actually running:

- **Python**: `py_compile` the modules, and exercise `thisthat_html.render_page`
  directly — it needs no display.
- **The GUI**: `PreferencesDialog` blocks in `wait_window()`, so drive it by
  scheduling callbacks on the root beforehand and tearing the dialog down from
  one. Invoke the real widgets (`Radiobutton.invoke()`) rather than calling app
  methods directly, or the dialog's own refresh path never runs and the test
  proves nothing.
- **Screenshots of tkinter**: grab only after `update()` plus a short pause.
  Grabbing straight after a theme switch captures a half-repainted window that
  looks exactly like a layout bug.
- **The guide**: build it with `--strict` from the project root using the
  machine's build venv, per `docs/CLAUDE.md`.
