# -*- mode: python ; coding: utf-8 -*-
#
# One-file build of difff desktop.  Driven by build.bat, not run directly.
#
# difff desktop imports nothing outside the standard library, so there is no
# hiddenimports list to maintain here -- PyInstaller's tkinter hook finds
# everything on its own.  The only thing that has to be carried along is the
# icon: --icon below stamps it onto the exe, and the datas entry ships the
# same file inside the bundle so the running window and its dialogs can call
# iconbitmap() on it (difff_desktop.py resolves it through sys._MEIPASS).

a = Analysis(
    ['difff_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('difff.ico', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Nothing in the app imports these.  They are only ever present
        # because a build venv might also have make_icon.py's Pillow
        # installed; naming them keeps an accidental pip install out of
        # the exe.
        'PIL',
        'numpy',
        'setuptools',
        'pip',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='difff',
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
    icon='difff.ico',
)
