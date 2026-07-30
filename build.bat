@echo off
"%~dp0.venv\Scripts\python.exe" -m PyInstaller "%~dp0FreightPass.spec"
echo.
echo Executavel gerado em dist\FreightPass.exe
pause
