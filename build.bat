@echo off
REM thisthat build -- one-file exe.
REM   1. Pick/create the venv for this machine
REM   2. PyInstaller thisthat.spec (--onefile) -> dist\thisthat.exe
REM   3. Assemble dist\thisthat-vX.Y.Z\ with the licence files, zip it
REM
REM The app has no runtime dependencies, so the venv exists only to hold
REM PyInstaller.  That makes it cheap enough to create on the spot: if the
REM venv for this host is missing, this script builds it rather than telling
REM you to go and do it yourself.
REM
REM The artwork (thisthat.ico, splash.png) is checked in, so a build does not
REM need Pillow.  Regenerate it with make_icon.py / make_splash.py only when
REM you want it to change.
REM
REM Usage: just double-click. The window stays open on success or failure.

setlocal EnableDelayedExpansion
set THISTHAT_VERSION=1.0.0
cd /d "%~dp0"

echo ========================================
echo thisthat v%THISTHAT_VERSION% build
echo ========================================
echo.

REM --- Pick the venv for this machine ---
IF "%COMPUTERNAME%"=="DOUGHERTY-PC" (
    set VENV=.venv_work
) ELSE IF "%COMPUTERNAME%"=="JONSPC" (
    set VENV=.venv_home
) ELSE (
    echo   Hostname %COMPUTERNAME% not recognized; falling back to .venv_build.
    set VENV=.venv_build
)
echo Using !VENV! on %COMPUTERNAME%.

if not exist "!VENV!\Scripts\activate.bat" (
    echo   !VENV! not found -- creating it.
    where python >nul 2>&1 || (echo   ERROR: python not found on PATH. && goto :err)
    python -m venv "!VENV!"
    if errorlevel 1 goto :err
    call "!VENV!\Scripts\activate.bat"
    python -m pip install --upgrade pip
    if errorlevel 1 goto :err
    python -m pip install -r requirements_build.txt
    if errorlevel 1 goto :err
) else (
    call "!VENV!\Scripts\activate.bat"
)

python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo   ERROR: PyInstaller missing from !VENV!.
    echo   Run: !VENV!\Scripts\activate.bat ^&^& pip install -r requirements_build.txt
    goto :err
)
echo   venv active, PyInstaller present.
echo.

REM --- Verify sources ---
if not exist "thisthat_app.py"        ( echo ERROR: thisthat_app.py not found!        & goto :err )
if not exist "thisthat.spec"          ( echo ERROR: thisthat.spec not found!          & goto :err )
if not exist "thisthat.ico"           ( echo ERROR: thisthat.ico not found!           & goto :err )
if not exist "splash.png"             ( echo ERROR: splash.png not found!             & goto :err )

REM --- Clean previous output ---
if exist "build" rmdir /s /q "build"
if exist "dist"  rmdir /s /q "dist"

echo === [1/2] Running PyInstaller ===
python -m PyInstaller thisthat.spec --clean --noconfirm
if errorlevel 1 goto :err
if not exist "dist\thisthat.exe" (
    echo   ERROR: dist\thisthat.exe was not produced.
    goto :err
)
echo.

echo === [2/2] Assembling release folder + zip ===
REM LICENSE and NOTICE.md travel next to the exe rather than inside it.
REM Lucide's ISC licence wants its notice reproduced "in the documentation
REM and/or other materials provided with the distribution" -- a copy sealed
REM inside the one-file bundle, unpacked to a temp folder at run time and
REM deleted on exit, does not meet that in any useful sense.
set RELEASE_DIR=dist\thisthat-v%THISTHAT_VERSION%
mkdir "%RELEASE_DIR%"
copy /y "dist\thisthat.exe" "%RELEASE_DIR%\thisthat.exe" >nul
if errorlevel 1 goto :err
REM Renamed to .txt so Windows opens them on double-click.
copy /y "LICENSE"   "%RELEASE_DIR%\LICENSE.txt" >nul
if errorlevel 1 goto :err
copy /y "NOTICE.md" "%RELEASE_DIR%\NOTICE.txt" >nul
if errorlevel 1 goto :err

powershell -NoProfile -Command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath 'dist\thisthat-v%THISTHAT_VERSION%.zip' -Force"
if errorlevel 1 goto :err
echo.

for %%F in ("dist\thisthat.exe") do set EXE_SIZE=%%~zF
echo ========================================
echo BUILD SUCCESSFUL
echo ========================================
echo   dist\thisthat.exe                  (%EXE_SIZE% bytes)
echo   dist\thisthat-v%THISTHAT_VERSION%.zip  ^<- share this one
echo.
pause
exit /b 0

:err
echo.
echo ========================================
echo BUILD FAILED.
echo ========================================
pause
exit /b 1
