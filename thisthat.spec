# -*- mode: python ; coding: utf-8 -*-
#
# One-file build of thisthat.  Driven by build.bat, not run directly.
#
# thisthat imports nothing outside the standard library, so there is no
# hiddenimports list to maintain here -- PyInstaller's tkinter hook finds
# everything on its own, and pyi_splash is injected by Splash() below rather
# than imported from the source tree.
#
# What has to be carried along is the artwork:
#   * icon= stamps thisthat.ico onto the exe itself;
#   * the same .ico also ships inside the bundle, because the running window
#     loads it by path -- for iconbitmap() and for the DPI-matched taskbar
#     icon (thisthat_app.py resolves it through sys._MEIPASS);
#   * splash.png is consumed by Splash() at build time, not at run time, so it
#     is deliberately NOT in datas.

a = Analysis(
    ['thisthat_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('thisthat.ico', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Nothing in the app imports these.  They are only ever present
        # because a build venv also has make_icon.py / make_splash.py's
        # Pillow installed; naming them keeps that out of the exe.
        'PIL',
        'numpy',
        'setuptools',
        'pip',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# A one-file exe has to unpack its whole archive to a temp folder before the
# first line of Python runs, which is a second or two of nothing happening
# after a double-click.  The bootloader can put this image on screen straight
# away; thisthat_app.main() takes it down once the real window has painted.
#
# No text_pos, and so no status line at all.  It is tempting -- but in onefile
# mode the bootloader commandeers that text to name each file as it extracts
# it, so what you actually get is a flicker of "_tcl_data\encoding\jis0212.enc"
# and friends across the card.  There is no switch to keep the text and lose
# the firehose, and internal paths scrolling past is worse than silence: the
# card itself is the "we're loading" signal, and it is only up for a second.
splash = Splash(
    'splash.png',
    binaries=a.binaries,
    datas=a.datas,
    always_on_top=False,
)

exe = EXE(
    pyz,
    a.scripts,
    # One-file: the splash and its own Tk runtime go into the exe alongside
    # everything else.  (A one-dir build would pass splash.binaries to
    # COLLECT instead.)
    splash,
    splash.binaries,
    a.binaries,
    a.datas,
    [],
    name='thisthat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX is off deliberately.  It saves a few MB, but a compressed one-file
    # exe is markedly more likely to be quarantined by corporate antivirus,
    # and an app you cannot hand to a colleague is not worth 4 MB.
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # GUI app -- no console window behind it
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='thisthat.ico',
)
