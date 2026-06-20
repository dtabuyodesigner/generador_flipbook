@echo off
echo Construyendo Generador de Periodicos...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    pause
    exit /b 1
)

pip install --quiet pdf2image pillow pyinstaller

pyinstaller --onefile --windowed --name "GeneradorPeriodico" --clean crear_flipbook.py

if exist build rmdir /s /q build
if exist GeneradorPeriodico.spec del GeneradorPeriodico.spec

echo.
echo EXITO! El EXE esta en: dist\GeneradorPeriodico.exe
pause
