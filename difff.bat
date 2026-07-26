@echo off
rem Launch difff desktop without a console window.
rem Optional: difff.bat fileA.txt fileB.txt
start "" pythonw "%~dp0difff_desktop.py" %*
