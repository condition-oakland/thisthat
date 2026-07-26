@echo off
rem Launch thisthat without a console window.
rem Optional: thisthat.bat fileA.txt fileB.txt
start "" pythonw "%~dp0thisthat_app.py" %*
