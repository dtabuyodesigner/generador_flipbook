# Generador de Periódicos Digitales

Convierte PDFs en flipbooks HTML interactivos estilo revista, listos para subir a WordPress.

## Características

- Efecto revista realista (doble página, hojeo con animación)
- Portada y contraportada como libro cerrado
- Numeración automática de páginas
- Pantalla completa
- Auto-compresión a ZIP
- Compatible Windows y Linux

## Uso en Linux (Zorin OS / Ubuntu)

Instalar dependencias del sistema:

    sudo apt-get install python3-tk poppler-utils

Instalar dependencias Python:

    pip install --break-system-packages pdf2image pillow

Ejecutar:

    python3 crear_flipbook.py

## Uso en Windows

1. Instala Python desde python.org (marca "Add to PATH")
2. Descarga Poppler para Windows desde GitHub (oschwartz10612/poppler-windows)
3. Extrae en C:\Program Files\poppler-XX.XX.X\
4. Doble clic en build.bat para crear el .exe
5. El ejecutable estará en dist\GeneradorPeriodico.exe

## Flujo de uso

1. Doble clic en el .exe (o python3 crear_flipbook.py en Linux)
2. Selecciona el PDF
3. Pulsa "Generar Flipbook"
4. Se abre el flipbook en el navegador y se crea un ZIP listo para WordPress

## Estructura del proyecto

- crear_flipbook.py - Script principal con interfaz Tkinter
- build.bat - Constructor del .exe para Windows
- requirements.txt - Dependencias Python
- INSTRUCCIONES_WINDOWS.md - Guía detallada de instalación en Windows

## Licencia

MIT
