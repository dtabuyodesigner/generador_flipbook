# Mejoras PDF + UX (unir offline, dividir, miniaturas, arrastrar, icono, etc.)

Fecha: 2026-06-21
Rama: `feature/pdf-tools-ux`

## Contexto y objetivo

Tras añadir "Preparar PDF" y la publicación en GitHub Pages, se piden mejoras de
usabilidad y una herramienta nueva de dividir PDF. Todo offline salvo la
publicación (que ya existe y no se toca).

## Alcance (7 mejoras)

1. **Modo "solo unir" (offline) explícito.**
2. **Cortador de PDF** (nueva pestaña "✂ Dividir PDF").
3. **Recordar la última carpeta** usada en los selectores de archivo.
4. **Icono propio** para el `.exe`.
5. **Reordenar arrastrando** dentro de la lista de Preparar PDF (+ flechas, que se mantienen).
6. **Miniatura** de la primera página del archivo seleccionado en Preparar PDF.
7. **Aviso de PDF protegido** (encriptado) al añadir/unir/dividir.

Fuera de alcance: soltar archivos desde el Explorador de Windows (necesita
`tkinterdnd2`, frágil en el .exe — se pospone); cambiar el nombre de la URL
(organización/Netlify, se decide aparte). 

## Arquitectura

- `pdf_tools.py` (existente): se añaden `paginas_de_pdf`, `dividir_pdf`,
  `esta_encriptado`, y se refuerzan `unir_pdfs`/`convertir_a_pdf` para avisar de
  PDFs encriptados.
- `crear_flipbook.py` (GUI): nueva pestaña "✂ Dividir PDF"; mejoras en la
  pestaña "Preparar PDF" (solo-unir, arrastrar, miniatura, aviso protegido);
  helper de "última carpeta".
- `icono.ico` (nuevo) + `build.bat` (`--icon`).

### `pdf_tools.py` — nuevas funciones

- `esta_encriptado(ruta) -> bool` — `PdfReader(ruta).is_encrypted` (False si no es PDF o no se puede leer, capturando excepciones).
- `paginas_de_pdf(ruta) -> int` — número de páginas (lanza `PdfToolsError` si está encriptado o no se puede leer).
- `dividir_pdf(ruta, paginas, carpeta_salida, nombre_base, una_por_archivo=False) -> list[str]`
  - `paginas`: lista de enteros 1-based ya validados.
  - Si `una_por_archivo` es False: crea UN PDF `nombre_base.pdf` con esas páginas en ese orden. Devuelve `[ruta]`.
  - Si es True: crea un PDF por página: `nombre_base_pagina_001.pdf`, etc. Devuelve la lista de rutas.
- `parsear_rango(texto, total) -> list[int]` — convierte `"1-4, 7, 9-11"` en `[1,2,3,4,7,9,10,11]`; valida 1..total; lanza `PdfToolsError` con mensaje legible si hay algo fuera de rango o sintaxis inválida. Cadena vacía → todas las páginas.
- `unir_pdfs`/`convertir_a_pdf`: si un PDF de entrada está encriptado, lanzar
  `ConversionError("El PDF '<nombre>' está protegido con contraseña; quítasela e inténtalo de nuevo.")`.

### GUI

**Pestañas:** se mantienen "1. Preparar PDF", "2. Generar flipbook",
"3. Mis periódicos" y se añade **"✂ Dividir PDF"** como pestaña adicional.

**Última carpeta (#3):** helpers `_dir_inicial()` (devuelve `cfg["ultima_carpeta"]`
si existe, si no `~`) y `_recordar_dir(ruta)` (guarda `os.path.dirname` en config).
Todos los `filedialog.ask*` usan `initialdir=self._dir_inicial()` y al elegir
llaman `self._recordar_dir(...)`.

**Preparar PDF — solo unir (#1):** al terminar `_preparar_unir`, en vez de saltar
a la pestaña 2, mostrar en la propia pestaña: etiqueta "✅ PDF guardado en: <ruta>",
botón **"📂 Abrir carpeta"** (abre la carpeta del PDF) y botón
**"➡ Generar flipbook con este PDF"** (hace `self.pdf_path.set(ruta)` y
`self.notebook.select(self.tab_flipbook)`). Guardar la última ruta en
`self.pdf_preparado`.

**Preparar PDF — arrastrar (#5):** además de las flechas, permitir reordenar la
`lista_preparar` arrastrando: bind `<Button-1>` (guarda índice origen),
`<B1-Motion>` (calcula índice destino con `nearest(y)` y reordena en vivo la
lista interna `archivos_preparar` + refresco), `<ButtonRelease-1>` (fin). El
orden interno y el Listbox quedan sincronizados.

**Preparar PDF — miniatura (#6):** al seleccionar un item (`<<ListboxSelect>>`),
mostrar en un `Label`/`Canvas` la miniatura de la 1ª página del archivo:
- PDF: renderizar 1ª página con `pdf2image` (dpi bajo, ~60) en un hilo y mostrar
  con `ImageTk` (si `HAS_IMAGETK`).
- Word o sin `ImageTk`: mostrar texto "Vista previa no disponible (se convertirá
  al unir)".
Cancelar/ignorar miniaturas obsoletas si se cambia de selección rápido (guardar
el índice pedido y descartar si cambió).

**Preparar PDF — aviso protegido (#7):** en `_preparar_anadir`, tras elegir, si
algún PDF `pdf_tools.esta_encriptado(...)`, avisar y NO añadир ese (añadir los
demás). En `_preparar_unir`, si `preparar_periodico` lanza por encriptado, el
mensaje legible ya se muestra en `_err`.

**Pestaña Dividir PDF (#2):** 
- Botón "Examinar…" (elige 1 PDF) → muestra "Páginas: N" (via `paginas_de_pdf`;
  si encriptado, aviso y no carga).
- Campo de texto para el rango (placeholder "ej. 1-4, 7, 9-11; vacío = todas").
- Checkbox "Una página por archivo".
- Botón "✂ Dividir" → en hilo: `parsear_rango` + `dividir_pdf` a `~/Descargas`;
  al terminar, etiqueta con "✅ Creado(s) N archivo(s) en: <carpeta>" + botón
  "📂 Abrir carpeta". Errores → mensaje legible, sin romper.

**Icono (#4):** archivo `icono.ico` en la raíz (un periódico estilizado, generado
con PIL). `build.bat`: si existe `icono.ico`, añadir `--icon=icono.ico` al comando
de PyInstaller.

## Manejo de errores

- Toda operación de PDF (dividir, miniatura) en `threading.Thread`; widgets solo
  vía `self.root.after`.
- Encriptado/!legible/rango inválido → `messagebox` con texto claro, sin trazas.
- El resto de la app nunca se rompe por un fallo de estas utilidades.

## Tests (`test_pdf_tools.py`, ampliado)

- `parsear_rango`: "1-4,7" → [1,2,3,4,7]; vacío → todas; fuera de rango → error;
  sintaxis inválida → error.
- `paginas_de_pdf`: PDF de 3 páginas → 3.
- `dividir_pdf`: rango [1,3] de un PDF de 3 → 1 PDF de 2 páginas;
  `una_por_archivo=True` de 3 → 3 PDFs de 1 página.
- `esta_encriptado`: PDF normal → False. (PDF encriptado: generar uno con pypdf
  `encrypt("x")` → True; y `unir_pdfs`/`paginas_de_pdf` lanzan mensaje legible.)
- GUI: smoke (4 pestañas; widgets nuevos presentes).

## Plan de tareas/agentes

- Tarea A: `pdf_tools` (parsear_rango, paginas_de_pdf, dividir_pdf, esta_encriptado, avisos encriptado) + tests. Independiente.
- Tarea B: GUI pestaña "✂ Dividir PDF". (crear_flipbook.py)
- Tarea C: GUI Preparar PDF — solo-unir + arrastrar + miniatura + aviso protegido. (crear_flipbook.py)
- Tarea D: "Última carpeta" en todos los selectores. (crear_flipbook.py)
- Tarea E: icono.ico + build.bat `--icon`. Independiente.
- B/C/D tocan `crear_flipbook.py` → secuenciales. A y E independientes.
