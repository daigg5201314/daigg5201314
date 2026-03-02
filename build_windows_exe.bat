@echo off
setlocal enabledelayedexpansion

REM Build one-file Windows EXE for the Gradio app.
REM Run this script on a Windows machine with Python 3.10+ installed.

if not exist venv (
    py -m venv venv
)

call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Clear old build outputs
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist app.spec del /f /q app.spec

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --name MangaColorizationUI ^
  --collect-all gradio ^
  --collect-submodules gradio ^
  app.py

echo.
echo Build complete. EXE path: dist\MangaColorizationUI.exe
echo.
endlocal
