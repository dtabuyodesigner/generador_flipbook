@echo off
echo ============================================
echo  Construyendo Generador de Periodicos...
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado.
    echo Instalalo desde https://www.python.org/downloads/ y marca "Add Python to PATH".
    pause
    exit /b 1
)

if not exist crear_flipbook.py (
    echo ERROR: no encuentro crear_flipbook.py en esta carpeta.
    pause
    exit /b 1
)

if not exist github_pages.py (
    echo ERROR: falta github_pages.py en esta carpeta.
    echo Descarga el proyecto COMPLETO desde GitHub, no solo crear_flipbook.py.
    pause
    exit /b 1
)

rem --- Localizar Poppler (se COPIA junto al .exe, NO se mete dentro) ---
rem Meter Poppler dentro del .exe falla por DLLs (gio/glib). Copiarlo al lado
rem funciona igual que el Poppler suelto, que ya sabemos que va bien.
set "POPPLER_ROOT="
if exist "C:\poppler\Library\bin\pdftoppm.exe" set "POPPLER_ROOT=C:\poppler"
if not defined POPPLER_ROOT if exist "C:\poppler\bin\pdftoppm.exe" set "POPPLER_ROOT=C:\poppler"
if not defined POPPLER_ROOT if exist "C:\Program Files\poppler\Library\bin\pdftoppm.exe" set "POPPLER_ROOT=C:\Program Files\poppler"

if not defined POPPLER_ROOT (
    echo AVISO: no encontre Poppler en C:\poppler.
    echo Sin Poppler la app no podra leer PDFs. Instala Poppler en C:\poppler
    echo - mira INSTRUCCIONES_WINDOWS.md - y vuelve a ejecutar este build.
    echo.
    pause
)

echo Instalando dependencias: pdf2image, pillow, pyinstaller, pypdf, pywin32...
pip install --quiet pdf2image pillow pyinstaller pypdf pywin32

set "ICON_ARG="
if exist icono.ico set "ICON_ARG=--icon=icono.ico"

echo Construyendo el .exe, esto tarda 1-2 minutos...
pyinstaller --onefile --windowed --name "GeneradorPeriodico" --clean %ICON_ARG% crear_flipbook.py

if errorlevel 1 (
    echo.
    echo ERROR: fallo la construccion del .exe.
    pause
    exit /b 1
)

rem --- Copiar Poppler JUNTO al .exe (la app lo busca en dist\poppler) ---
if defined POPPLER_ROOT (
    echo Copiando Poppler a dist\poppler ...
    xcopy /E /I /Y "%POPPLER_ROOT%" "dist\poppler" >nul
    echo Poppler copiado a dist\poppler
)

rem El token es necesario para publicar en internet; va JUNTO al .exe.
if exist tokengenerarflipbook.txt (
    copy /Y tokengenerarflipbook.txt dist\tokengenerarflipbook.txt >nul
    echo Token copiado a dist\tokengenerarflipbook.txt
) else (
    echo AVISO: no encontre tokengenerarflipbook.txt.
    echo Debes copiarlo a la carpeta dist\ junto al .exe antes de usarlo.
)

rem Opcional: repositorio.txt (owner/repo) para publicar en otra cuenta/organizacion.
if exist repositorio.txt (
    copy /Y repositorio.txt dist\repositorio.txt >nul
    echo repositorio.txt copiado a dist\
)

if exist build rmdir /s /q build
if exist GeneradorPeriodico.spec del GeneradorPeriodico.spec

echo.
echo ============================================
echo  EXITO!
echo  Reparte la carpeta dist\ COMPLETA:
echo  - GeneradorPeriodico.exe
echo  - carpeta poppler
echo  - tokengenerarflipbook.txt
echo  - repositorio.txt
echo ============================================
pause
