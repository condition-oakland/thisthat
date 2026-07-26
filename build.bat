@echo off
REM difff desktop build -- one-file exe.
REM   1. Pick/create the venv for this machine
REM   2. PyInstaller difff.spec (--onefile) -> dist\difff.exe
REM   3. Assemble dist\difff-vX.Y.Z\ with the licence files, zip it
REM
REM The app has no runtime dependencies, so the venv exists only to hold
REM PyInstaller.  That makes it cheap enough to create on the spot: if the
REM venv for this host is missing, this script builds it rather than telling
REM you to go and do it yourself.
REM
REM Usage: just double-click. The window stays open on success or failure.

setlocal EnableDelayedExpansion
set DIFFF_VERSION=1.0.0
cd /d "%~dp0"

echo ========================================
echo difff desktop v%DIFFF_VERSION% build
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
if not exist "difff_desktop.py" ( echo ERROR: difff_desktop.py not found! & goto :err )
if not exist "difff.spec"       ( echo ERROR: difff.spec not found!       & goto :err )
if not exist "difff.ico"        ( echo ERROR: difff.ico not found!        & goto :err )

REM --- Clean previous output ---
if exist "build" rmdir /s /q "build"
if exist "dist"  rmdir /s /q "dist"

echo === [1/2] Running PyInstaller ===
python -m PyInstaller difff.spec --clean --noconfirm
if errorlevel 1 goto :err
if not exist "dist\difff.exe" (
    echo   ERROR: dist\difff.exe was not produced.
    goto :err
)
echo.

echo === [2/2] Assembling release folder + zip ===
REM LICENSE and NOTICE.md travel next to the exe rather than inside it.
REM Lucide's ISC licence wants its notice reproduced "in the documentation
REM and/or other materials provided with the distribution" -- a copy sealed
REM inside the one-file bundle, unpacked to a temp folder at run time and
REM deleted on exit, does not meet that in any useful sense.
set RELEASE_DIR=dist\difff-v%DIFFF_VERSION%
mkdir "%RELEASE_DIR%"
copy /y "dist\difff.exe" "%RELEASE_DIR%\difff.exe" >nul
if errorlevel 1 goto :err
REM Renamed to .txt so Windows opens them on double-click.
copy /y "LICENSE"   "%RELEASE_DIR%\LICENSE.txt" >nul
if errorlevel 1 goto :err
copy /y "NOTICE.md" "%RELEASE_DIR%\NOTICE.txt" >nul
if errorlevel 1 goto :err

powershell -NoProfile -Command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath 'dist\difff-v%DIFFF_VERSION%.zip' -Force"
if errorlevel 1 goto :err
echo.

for %%F in ("dist\difff.exe") do set EXE_SIZE=%%~zF
echo ========================================
echo BUILD SUCCESSFUL
echo ========================================
echo   dist\difff.exe                  (%EXE_SIZE% bytes)
echo   dist\difff-v%DIFFF_VERSION%.zip  ^<- share this one
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
