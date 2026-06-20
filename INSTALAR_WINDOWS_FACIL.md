# 🟢 Crear el programa en Windows — paso a paso (fácil)

Sigue los pasos **en orden**. No hace falta saber de informática. Tardarás unos
20 minutos la primera vez.

> ⚠️ **TODO esto se hace en un PC con WINDOWS** (el "PC de construcción").
> **No en Zorin/Linux**: el `.exe` de Windows solo se puede crear desde Windows.
> Ese PC con Windows es el único que necesita Python y Poppler. El equipo donde
> Pilar solo USA el programa no necesita instalar nada.

---

## 1) Descargar el programa

1. Abre el navegador y entra en:
   **https://github.com/dtabuyodesigner/generador_flipbook**
2. Pulsa el botón verde **`<> Code`** (arriba a la derecha).
3. Pulsa **`Download ZIP`**.
4. Ve a tu carpeta **Descargas**, haz **clic derecho** en el ZIP →
   **«Extraer todo…»** → **Extraer**.
5. Te quedará una carpeta llamada `generador_flipbook-main` (o parecida).
6. Para que sea fácil: **renómbrala a `GeneradorPeriodico`** y muévela a
   `C:\` (la raíz del disco). Debe quedar así: **`C:\GeneradorPeriodico`**.

---

## 2) Instalar Python (una vez)

1. Entra en **https://www.python.org/downloads/**
2. Pulsa el botón amarillo **«Download Python 3.x»**.
3. Abre el archivo descargado.
4. 🔴 **MUY IMPORTANTE:** abajo del todo, marca la casilla
   **«Add Python to PATH»** (o «Add python.exe to PATH»).
5. Pulsa **«Install Now»** y espera a que diga *Setup was successful*. Cierra.

---

## 3) Instalar Poppler (una vez)

1. Entra en:
   **https://github.com/oschwartz10612/poppler-windows/releases**
2. En la versión de arriba del todo, pulsa en el archivo que pone
   **`Release-XX.XX.X-X.zip`** para descargarlo.
3. En Descargas, **clic derecho** en ese ZIP → **«Extraer todo…»** → **Extraer**.
4. Entra en la carpeta extraída. Dentro habrá una carpeta como `poppler-XX.XX.X`.
5. **Renómbrala a `poppler`** y muévela a `C:\`.
   Tiene que quedar exactamente así:
   **`C:\poppler\Library\bin`**
   (dentro de `bin` verás muchos archivos, uno se llama `pdftoppm.exe`).

---

## 4) Poner la contraseña secreta (token)

1. Entra en la carpeta **`C:\GeneradorPeriodico`**.
2. **Clic derecho** en un sitio vacío → **Nuevo → Documento de texto**.
3. Renómbralo exactamente a: **`tokengenerarflipbook.txt`**
   (si te avisa de cambiar la extensión, di que **sí**).
4. Ábrelo (doble clic) y **pega dentro el token** (la clave larga que empieza
   por `github_pat_...`). Solo eso, nada más.
5. Guarda (Archivo → Guardar) y cierra.

> ¿No tienes el token a mano? Está guardado en tu Linux, en el archivo
> `tokengenerarflipbook.txt` del proyecto. Cópialo de ahí.

---

## 5) Crear el programa (.exe)

1. Entra en **`C:\GeneradorPeriodico`**.
2. Busca el archivo **`build.bat`** y haz **doble clic**.
3. Se abrirá una ventana negra que va escribiendo cosas sola. **No la cierres.**
   Tarda 1-2 minutos.
4. Cuando ponga **`EXITO!`**, ya está. Pulsa una tecla para cerrar.

El programa terminado está en:
**`C:\GeneradorPeriodico\dist\GeneradorPeriodico.exe`**
(y al lado, su `tokengenerarflipbook.txt`).

---

## 6) Dárselo a Pilar

1. Entra en la carpeta **`C:\GeneradorPeriodico\dist`**.
2. Copia los **dos** archivos juntos a un USB o por email:
   - `GeneradorPeriodico.exe`
   - `tokengenerarflipbook.txt`
3. En el equipo de Pilar, pon los dos en una carpeta (p. ej. el Escritorio).
4. Pilar abre el programa con **doble clic en `GeneradorPeriodico.exe`**.
   No tiene que instalar nada.

> Cómo lo usa ella día a día: archivo **`GUIA_PILAR.md`**.

---

## ❓ Si algo falla

- **La ventana negra dice "Python no esta instalado"** → repite el paso 2 y
  asegúrate de marcar **«Add Python to PATH»**. Reinicia el PC y prueba otra vez.
- **Dice "falta github_pages.py"** → descargaste mal; repite el paso 1
  (descarga el ZIP entero).
- **Dice "no encontre Poppler"** → revisa el paso 3: tiene que existir
  `C:\poppler\Library\bin\pdftoppm.exe`.
- **El programa abre pero no da enlace** → falta el `tokengenerarflipbook.txt`
  junto al `.exe`, o el token caducó. Repite el paso 4.
