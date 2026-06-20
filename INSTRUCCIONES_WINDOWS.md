# 🚀 Cómo hacer el .EXE para Pilar (Windows)

Pasos para crear el ejecutable que Pilar usará en Windows con un solo doble clic.

---

## **PASO 1: En el PC de Pilar (Windows), instalar requisitos UNA SOLA VEZ**

### 1.1 Instalar Python
- Descarga Python 3.11+ desde https://www.python.org/downloads/
- **IMPORTANTE:** Al instalar, marca la casilla **"Add Python to PATH"**

### 1.2 Instalar Poppler (necesario para leer PDFs)
- Descarga Poppler para Windows: https://github.com/oschwartz10612/poppler-windows/releases
- Descarga el archivo `Release-XX.XX.XX-X.zip` más reciente
- Extrae el ZIP en: `C:\Program Files\poppler-24.02.0\`
- La carpeta `bin` debe quedar en: `C:\Program Files\poppler-24.02.0\Library\bin`

### 1.3 Abrir CMD como Administrador e instalar dependencias

```cmd
pip install pdf2image pillow pyinstaller
```

---

## **PASO 2: Crear el .EXE (una sola vez)**

### 2.1 Copia el script `crear_flipbook.py` al PC de Pilar

Ponlo en, por ejemplo: `C:\Users\Pilar\Desktop\GeneradorPeriodico\`

### 2.2 Abre CMD en esa carpeta y ejecuta:

```cmd
cd C:\Users\Pilar\Desktop\GeneradorPeriodico
pyinstaller --onefile --windowed --name "GeneradorPeriodico" --icon=icono.ico crear_flipbook.py
```

(Si no tienes icono `icono.ico`, quita el `--icon=icono.ico`)

### 2.3 El .EXE se crea en:

```
C:\Users\Pilar\Desktop\GeneradorPeriodico\dist\GeneradorPeriodico.exe
```

### 2.4 Copia el .EXE al Escritorio de Pilar

Ya está. Pilar solo tiene que **hacer doble clic en `GeneradorPeriodico.exe`** en su escritorio.

---

## **PASO 3: Flujo de Pilar (usar el .exe)**

1. Doble clic en **`GeneradorPeriodico.exe`** del escritorio
2. Clic en **"Examinar"** y selecciona su PDF
3. Clic en **"Generar Flipbook"**
4. ✅ Se abre el flipbook en el navegador automáticamente
5. ✅ Se crea un ZIP listo para subir a WordPress
6. Clic en **"📋 Instrucciones"** para ver cómo subirlo

---

## **PASO 4: Subir a WordPress**

### **Opción A: Manual (recomendado)**

1. En WordPress → **Medios → Añadir nuevo**
2. Sube el ZIP creado (ej: `periodico_19_06_2026.zip`)

> ⚠️ **Importante:** WordPress por defecto **no acepta ZIPs**. Para activarlo:
> - Pide al admin del colegio que instale el plugin **"WP Extra File Types"**
> - O usa el plugin **"WPvivid Backup"** (muchos colegios lo tienen)
> - O simplemente sube `index.html` + carpeta `pages` por separado

### **Opción B: Carpeta directa (más fácil)**

En vez del ZIP, sube los archivos por FTP/SFTP a la carpeta del WordPress:
- Pide al admin del colegio los datos FTP
- Sube la carpeta completa generada
- URL final: `https://colegio.com/periodicos/nombre_carpeta/`

### **Opción C: Netlify Drop (sin WordPress, en 30 segundos)**

1. Ve a https://app.netlify.com/drop
2. Arrastra la carpeta completa del periódico
3. ¡Listo! Te da una URL tipo `https://periodico-xxxxx.netlify.app`
4. Comparte esa URL con los padres

---

## 🔧 Si quieres hacer .exe sin el CMD

Crea un archivo `build.bat` con este contenido:

```bat
@echo off
pyinstaller --onefile --windowed --name "GeneradorPeriodico" crear_flipbook.py
echo.
echo ============================================
echo  El EXE esta en: dist\GeneradorPeriodico.exe
echo ============================================
pause
```

Doble clic en `build.bat` y se construye el .exe.

---

## 📌 Resumen de archivos

```
GeneradorPeriodico/
├── crear_flipbook.py        ← Script Python
├── build.bat                ← (opcional) Para crear el .exe
└── dist/
    └── GeneradorPeriodico.exe ← El ejecutable final
```
