# Mejoras PDF + UX — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir utilidades de PDF (dividir, unir offline explícito) y mejoras de UX (miniatura, arrastrar para reordenar, recordar carpeta, icono, aviso de PDF protegido).

**Architecture:** Lógica nueva de PDF en `pdf_tools.py` (puro, testeable con pypdf). La GUI (`crear_flipbook.py`, ttk.Notebook) gana una pestaña "✂ Dividir PDF" y mejoras en "Preparar PDF". Icono propio para el `.exe`.

**Tech Stack:** Python 3.12, pypdf, tkinter, pdf2image+ImageTk (miniatura), threading, pytest, PIL (generar icono y PDFs de test).

## Global Constraints

- Sin internet salvo la publicación (que no se toca).
- Toda operación de PDF/miniatura en `threading.Thread`; widgets solo vía `self.root.after`.
- PDF protegido (encriptado) → mensaje legible: "El PDF '<nombre>' está protegido con contraseña; quítasela e inténtalo de nuevo." (sin trazas técnicas).
- Salida de utilidades a `~/Descargas` (consistente con el resto de la app).
- No romper el flujo existente (publicar, 3 pestañas actuales).
- Dependencias: ya están `pypdf`, `pdf2image`, `Pillow`. No añadir nuevas.

---

### Task 1: `pdf_tools` — paginas/parsear_rango/dividir/encriptado

**Files:**
- Modify: `pdf_tools.py`
- Modify: `test_pdf_tools.py`

**Interfaces:**
- Consumes: `PdfToolsError`, `ConversionError`, `unir_pdfs` (ya existen).
- Produces:
  - `esta_encriptado(ruta) -> bool`
  - `paginas_de_pdf(ruta) -> int`
  - `parsear_rango(texto, total) -> list[int]`
  - `dividir_pdf(ruta, paginas, carpeta_salida, nombre_base, una_por_archivo=False) -> list[str]`
  - `unir_pdfs` ahora avisa si una entrada está encriptada.

- [ ] **Step 1: Write the failing tests**

```python
# añadir a test_pdf_tools.py
def _encriptar(path_in, path_out, clave="x"):
    from pypdf import PdfReader, PdfWriter
    r = PdfReader(path_in)
    w = PdfWriter()
    for pg in r.pages:
        w.add_page(pg)
    w.encrypt(clave)
    with open(path_out, "wb") as f:
        w.write(f)
    return path_out


def test_parsear_rango_basico():
    assert pt.parsear_rango("1-4, 7", 10) == [1, 2, 3, 4, 7]

def test_parsear_rango_vacio_es_todas():
    assert pt.parsear_rango("", 3) == [1, 2, 3]

def test_parsear_rango_fuera_de_rango():
    import pytest
    with pytest.raises(pt.PdfToolsError):
        pt.parsear_rango("1-99", 5)

def test_parsear_rango_sintaxis_invalida():
    import pytest
    with pytest.raises(pt.PdfToolsError):
        pt.parsear_rango("a-b", 5)

def test_paginas_de_pdf(tmp_path):
    p = _hacer_pdf(str(tmp_path / "x.pdf"), 3)
    assert pt.paginas_de_pdf(p) == 3

def test_dividir_pdf_rango(tmp_path):
    p = _hacer_pdf(str(tmp_path / "x.pdf"), 3)
    from pypdf import PdfReader
    salidas = pt.dividir_pdf(p, [1, 3], str(tmp_path / "out"), "trozo")
    assert len(salidas) == 1
    assert len(PdfReader(salidas[0]).pages) == 2

def test_dividir_pdf_una_por_archivo(tmp_path):
    p = _hacer_pdf(str(tmp_path / "x.pdf"), 3)
    salidas = pt.dividir_pdf(p, [1, 2, 3], str(tmp_path / "out"), "p", una_por_archivo=True)
    assert len(salidas) == 3

def test_esta_encriptado(tmp_path):
    p = _hacer_pdf(str(tmp_path / "x.pdf"), 1)
    assert pt.esta_encriptado(p) is False
    enc = _encriptar(p, str(tmp_path / "enc.pdf"))
    assert pt.esta_encriptado(enc) is True

def test_unir_avisa_encriptado(tmp_path):
    import pytest
    p = _hacer_pdf(str(tmp_path / "x.pdf"), 1)
    enc = _encriptar(p, str(tmp_path / "enc.pdf"))
    with pytest.raises(pt.ConversionError):
        pt.unir_pdfs([enc], str(tmp_path / "o.pdf"))
```

(`_hacer_pdf` ya existe en el fichero de tests de tareas anteriores.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest test_pdf_tools.py -k "rango or paginas or dividir or encriptado" -v`
Expected: FAIL (`AttributeError`/funciones no definidas).

- [ ] **Step 3: Write the implementation** (añadir a `pdf_tools.py`)

```python
def esta_encriptado(ruta):
    """True si el PDF está protegido con contraseña. False si no es PDF/ilegible."""
    try:
        from pypdf import PdfReader
        return bool(PdfReader(ruta).is_encrypted)
    except Exception:
        return False


def paginas_de_pdf(ruta):
    """Número de páginas de un PDF. Lanza PdfToolsError si está protegido/ilegible."""
    from pypdf import PdfReader
    if esta_encriptado(ruta):
        raise PdfToolsError(
            f"El PDF '{os.path.basename(ruta)}' está protegido con contraseña; "
            "quítasela e inténtalo de nuevo.")
    try:
        return len(PdfReader(ruta).pages)
    except Exception:
        raise PdfToolsError(f"No se pudo leer el PDF: {os.path.basename(ruta)}")


def parsear_rango(texto, total):
    """Convierte '1-4, 7, 9-11' en [1,2,3,4,7,9,10,11]. Vacío = todas.
    Lanza PdfToolsError si hay sintaxis inválida o páginas fuera de 1..total."""
    texto = (texto or "").strip()
    if not texto:
        return list(range(1, total + 1))
    paginas = []
    for parte in texto.split(","):
        parte = parte.strip()
        if not parte:
            continue
        if "-" in parte:
            trozos = parte.split("-", 1)
            try:
                a, b = int(trozos[0].strip()), int(trozos[1].strip())
            except ValueError:
                raise PdfToolsError(f"Rango inválido: '{parte}'")
            if a > b:
                a, b = b, a
            paginas.extend(range(a, b + 1))
        else:
            try:
                paginas.append(int(parte))
            except ValueError:
                raise PdfToolsError(f"Rango inválido: '{parte}'")
    for p in paginas:
        if p < 1 or p > total:
            raise PdfToolsError(f"La página {p} está fuera de rango (1-{total}).")
    return paginas


def dividir_pdf(ruta, paginas, carpeta_salida, nombre_base, una_por_archivo=False):
    """Crea PDF(s) con las páginas indicadas (1-based) en orden. Devuelve rutas."""
    from pypdf import PdfReader, PdfWriter
    if esta_encriptado(ruta):
        raise ConversionError(
            f"El PDF '{os.path.basename(ruta)}' está protegido con contraseña; "
            "quítasela e inténtalo de nuevo.")
    os.makedirs(carpeta_salida, exist_ok=True)
    reader = PdfReader(ruta)
    salidas = []
    if una_por_archivo:
        for p in paginas:
            writer = PdfWriter()
            writer.add_page(reader.pages[p - 1])
            out = os.path.join(carpeta_salida, f"{nombre_base}_pagina_{p:03d}.pdf")
            with open(out, "wb") as f:
                writer.write(f)
            writer.close()
            salidas.append(out)
    else:
        writer = PdfWriter()
        for p in paginas:
            writer.add_page(reader.pages[p - 1])
        out = os.path.join(carpeta_salida, f"{nombre_base}.pdf")
        with open(out, "wb") as f:
            writer.write(f)
        writer.close()
        salidas.append(out)
    return salidas
```

Y en `unir_pdfs`, ANTES del `writer.append(r)`, comprobar encriptado. Reemplaza el bucle actual:

```python
        for r in rutas_ordenadas:
            writer.append(r)
```

por:

```python
        for r in rutas_ordenadas:
            if esta_encriptado(r):
                raise ConversionError(
                    f"El PDF '{os.path.basename(r)}' está protegido con contraseña; "
                    "quítasela e inténtalo de nuevo.")
            writer.append(r)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_pdf_tools.py -v`
Expected: PASS (todos, los antiguos + los nuevos).

- [ ] **Step 5: Commit**

```bash
git add pdf_tools.py test_pdf_tools.py
git commit -m "feat(pdf_tools): dividir, paginas_de_pdf, parsear_rango y aviso de encriptado"
```

---

### Task 2: Pestaña "✂ Dividir PDF"

**Files:**
- Modify: `crear_flipbook.py`

**Interfaces:**
- Consumes: `pdf_tools.paginas_de_pdf/parsear_rango/dividir_pdf/esta_encriptado`, `self.notebook`.
- Produces: `self.tab_dividir`, `_construir_tab_dividir`, `_abrir_carpeta_ruta`, atributo `self.dividir_pdf_path`.

- [ ] **Step 1: Añadir la pestaña en `__init__`**

Tras `self._construir_tab_preparar(self.tab_preparar)` (o donde se añaden las pestañas), añade una pestaña más:

```python
        self.tab_dividir = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dividir, text="✂ Dividir PDF")
        self._construir_tab_dividir(self.tab_dividir)
```

- [ ] **Step 2: Implementar la pestaña y helpers**

```python
    def _abrir_carpeta_ruta(self, ruta):
        carpeta = os.path.dirname(os.path.abspath(ruta))
        if platform.system() == "Windows":
            os.startfile(carpeta)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", carpeta])
        else:
            subprocess.Popen(["xdg-open", carpeta])

    def _construir_tab_dividir(self, parent):
        self.dividir_pdf_path = None
        cont = ttk.Frame(parent, padding="12")
        cont.pack(fill=tk.BOTH, expand=True)
        cont.columnconfigure(0, weight=1)

        ttk.Label(cont, text="Divide un PDF: elige el archivo y di qué páginas "
                             "quieres quedarte.", wraplength=560,
                  justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)

        fila = ttk.Frame(cont)
        fila.grid(row=1, column=0, sticky=tk.W, pady=(6, 4))
        ttk.Button(fila, text="Examinar…", command=self._dividir_examinar).pack(side=tk.LEFT)
        self.dividir_info = ttk.Label(fila, text="(ningún PDF elegido)", foreground="gray")
        self.dividir_info.pack(side=tk.LEFT, padx=8)

        ttk.Label(cont, text="Páginas (ej. 1-4, 7, 9-11; vacío = todas):").grid(
            row=2, column=0, sticky=tk.W, pady=(6, 0))
        self.dividir_rango = ttk.Entry(cont, width=40)
        self.dividir_rango.grid(row=3, column=0, sticky=tk.W, pady=(2, 4))

        self.dividir_una = tk.BooleanVar(value=False)
        ttk.Checkbutton(cont, text="Una página por archivo (trocear todo)",
                        variable=self.dividir_una).grid(row=4, column=0, sticky=tk.W)

        self.dividir_estado = ttk.Label(cont, text="", foreground="blue")
        self.dividir_estado.grid(row=5, column=0, sticky=tk.W, pady=(6, 2))
        self.dividir_progress = ttk.Progressbar(cont, mode="indeterminate")
        self.dividir_progress.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=2)

        self.btn_dividir = ttk.Button(cont, text="✂ Dividir", command=self._dividir_ejecutar)
        self.btn_dividir.grid(row=7, column=0, sticky=tk.W, pady=(4, 0))
        self.btn_dividir_abrir = ttk.Button(cont, text="📂 Abrir carpeta",
                                            command=self._dividir_abrir_carpeta, state=tk.DISABLED)
        self.btn_dividir_abrir.grid(row=8, column=0, sticky=tk.W, pady=(4, 0))
        self._dividir_ultima_salida = None

    def _dividir_examinar(self):
        ruta = filedialog.askopenfilename(title="Elige un PDF",
                                          filetypes=[("PDF", "*.pdf")])
        if not ruta:
            return
        if pdf_tools.esta_encriptado(ruta):
            messagebox.showwarning("PDF protegido",
                f"El PDF «{os.path.basename(ruta)}» está protegido con contraseña; "
                "quítasela e inténtalo de nuevo.")
            return
        try:
            n = pdf_tools.paginas_de_pdf(ruta)
        except Exception as e:
            messagebox.showwarning("No se pudo leer", str(e))
            return
        self.dividir_pdf_path = ruta
        self.dividir_info.config(text=f"{os.path.basename(ruta)} — {n} páginas",
                                 foreground="black")

    def _dividir_ejecutar(self):
        if not self.dividir_pdf_path:
            messagebox.showinfo("Sin PDF", "Elige un PDF primero.")
            return
        ruta = self.dividir_pdf_path
        texto = self.dividir_rango.get()
        una = self.dividir_una.get()
        carpeta = os.path.abspath(os.path.expanduser("~/Descargas"))
        base = os.path.splitext(os.path.basename(ruta))[0] + "_dividido"
        self.dividir_progress.start()
        self.dividir_estado.config(text="Dividiendo...", foreground="orange")
        self.btn_dividir.config(state=tk.DISABLED)

        def _w():
            try:
                total = pdf_tools.paginas_de_pdf(ruta)
                paginas = pdf_tools.parsear_rango(texto, total)
                salidas = pdf_tools.dividir_pdf(ruta, paginas, carpeta, base, una_por_archivo=una)
                self.root.after(0, lambda: _ok(salidas))
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda: _err(msg))

        def _ok(salidas):
            self.dividir_progress.stop()
            self.btn_dividir.config(state=tk.NORMAL)
            self._dividir_ultima_salida = salidas[0]
            self.btn_dividir_abrir.config(state=tk.NORMAL)
            self.dividir_estado.config(
                text=f"✅ Creado(s) {len(salidas)} archivo(s) en Descargas",
                foreground="green")

        def _err(msg):
            self.dividir_progress.stop()
            self.btn_dividir.config(state=tk.NORMAL)
            self.dividir_estado.config(text="❌ No se pudo dividir", foreground="red")
            messagebox.showwarning("No se pudo dividir", msg)

        threading.Thread(target=_w, daemon=True).start()

    def _dividir_abrir_carpeta(self):
        if self._dividir_ultima_salida:
            self._abrir_carpeta_ruta(self._dividir_ultima_salida)
```

- [ ] **Step 3: Smoke test**

Run:
```bash
python3 -c "import ast;ast.parse(open('crear_flipbook.py').read());print('parse OK')"
python3 - <<'PY'
import importlib.util, tkinter as tk
spec=importlib.util.spec_from_file_location("cf","crear_flipbook.py")
cf=importlib.util.module_from_spec(spec); spec.loader.exec_module(cf)
r=tk.Tk(); a=cf.CreadorFlipbook(r); r.update()
assert a.notebook.index("end")==4, "deben ser 4 pestañas"
assert hasattr(a,"_construir_tab_dividir") and hasattr(a,"btn_dividir")
print("smoke OK"); r.destroy()
PY
```
Expected: `parse OK` y `smoke OK`.

- [ ] **Step 4: Commit**

```bash
git add crear_flipbook.py
git commit -m "feat(gui): pestaña Dividir PDF"
```

---

### Task 3: Preparar PDF — solo-unir, arrastrar, miniatura, aviso protegido

**Files:**
- Modify: `crear_flipbook.py`

**Interfaces:**
- Consumes: `pdf_tools.esta_encriptado`, `self.pdf_path`, `self.notebook`,
  `self.tab_flipbook`, `_abrir_carpeta_ruta` (Task 2), `convert_from_path`,
  `Image`, `ImageTk`, `HAS_IMAGETK`, `detectar_poppler`.
- Produces: miniatura, drag-reorder y resultado solo-unir en la pestaña Preparar.

- [ ] **Step 1: Añadir miniatura y bind de selección/arrastre en `_construir_tab_preparar`**

En `_construir_tab_preparar`, tras crear `self.lista_preparar` (el Listbox) y el
frame de orden, añade un panel de miniatura a la derecha y los binds. Inserta:

```python
        # Miniatura del archivo seleccionado
        self.preparar_miniatura = ttk.Label(cont, text="(selecciona un archivo)",
                                             anchor=tk.CENTER, relief="solid",
                                             borderwidth=1, width=24)
        self.preparar_miniatura.grid(row=2, column=2, sticky=(tk.N, tk.S), padx=(8, 0))
        self._mini_photo = None       # referencia viva del PhotoImage
        self._mini_pedido = 0         # para descartar miniaturas obsoletas
        self.lista_preparar.bind("<<ListboxSelect>>", self._preparar_miniatura_sel)
        # Arrastrar para reordenar
        self.lista_preparar.bind("<Button-1>", self._preparar_drag_inicio)
        self.lista_preparar.bind("<B1-Motion>", self._preparar_drag_mueve)
        self._drag_idx = None
```

- [ ] **Step 2: Métodos de arrastre y miniatura**

```python
    def _preparar_drag_inicio(self, event):
        self._drag_idx = self.lista_preparar.nearest(event.y)

    def _preparar_drag_mueve(self, event):
        if self._drag_idx is None:
            return
        destino = self.lista_preparar.nearest(event.y)
        if destino < 0 or destino == self._drag_idx or destino >= len(self.archivos_preparar):
            return
        i = self._drag_idx
        self.archivos_preparar[i], self.archivos_preparar[destino] = \
            self.archivos_preparar[destino], self.archivos_preparar[i]
        self._preparar_refrescar_lista()
        self.lista_preparar.selection_set(destino)
        self._drag_idx = destino

    def _preparar_miniatura_sel(self, event=None):
        sel = self.lista_preparar.curselection()
        if not sel:
            return
        ruta = self.archivos_preparar[sel[0]]
        self._mini_pedido += 1
        pedido = self._mini_pedido
        if not ruta.lower().endswith(".pdf") or not HAS_IMAGETK:
            self.preparar_miniatura.config(
                image="", text="Vista previa no disponible\n(se convertirá al unir)")
            self._mini_photo = None
            return
        self.preparar_miniatura.config(image="", text="Cargando…")

        def _w():
            try:
                pop = detectar_poppler()
                kw = {"dpi": 60, "first_page": 1, "last_page": 1}
                if pop:
                    kw["poppler_path"] = pop
                imgs = convert_from_path(ruta, **kw)
                img = imgs[0]
                img.thumbnail((180, 240), Image.Resampling.LANCZOS)
                self.root.after(0, lambda: _set(img, pedido))
            except Exception:
                self.root.after(0, lambda: _fail(pedido))

        def _set(img, pedido):
            if pedido != self._mini_pedido:
                return  # selección cambió; descartar
            self._mini_photo = ImageTk.PhotoImage(img)
            self.preparar_miniatura.config(image=self._mini_photo, text="")

        def _fail(pedido):
            if pedido != self._mini_pedido:
                return
            self.preparar_miniatura.config(image="", text="Vista previa no disponible")
            self._mini_photo = None

        threading.Thread(target=_w, daemon=True).start()
```

- [ ] **Step 3: Aviso de PDF protegido al añadir**

En `_preparar_anadir`, sustituye el bucle que añade rutas por uno que filtra los
encriptados y avisa:

```python
    def _preparar_anadir(self):
        rutas = filedialog.askopenfilenames(
            title="Elige documentos (Word o PDF)",
            filetypes=[("Documentos", "*.pdf *.doc *.docx"),
                       ("PDF", "*.pdf"), ("Word", "*.doc *.docx")])
        protegidos = []
        for r in rutas:
            if r.lower().endswith(".pdf") and pdf_tools.esta_encriptado(r):
                protegidos.append(os.path.basename(r))
                continue
            self.archivos_preparar.append(r)
        self._preparar_refrescar_lista()
        if protegidos:
            messagebox.showwarning("PDF(s) protegidos",
                "Estos PDF están protegidos con contraseña y no se han añadido:\n\n"
                + "\n".join(protegidos) +
                "\n\nQuítales la contraseña e inténtalo de nuevo.")
```

- [ ] **Step 4: Resultado "solo unir" (no saltar; ofrecer abrir carpeta / ir a flipbook)**

En `_preparar_unir`, en la función interna `_ok(ruta)`, sustituye el salto a la
pestaña 2 por mostrar opciones. Cambia el cuerpo de `_ok` a:

```python
        def _ok(ruta):
            self.preparar_progress.stop()
            self.btn_unir.config(state=tk.NORMAL)
            self.pdf_preparado = ruta
            self.preparar_estado.config(text=f"✅ PDF guardado en: {ruta}", foreground="green")
            self.btn_preparar_abrir.config(state=tk.NORMAL)
            self.btn_preparar_flipbook.config(state=tk.NORMAL)
            messagebox.showinfo("PDF listo",
                "He unido los documentos en un PDF, guardado en tu carpeta Descargas.\n\n"
                "Puedes abrir la carpeta, o pulsar «Generar flipbook con este PDF» "
                "si quieres publicarlo en internet.")
```

Y añade, en `_construir_tab_preparar`, debajo del botón `self.btn_unir`, dos
botones (inicialmente deshabilitados) y el atributo `self.pdf_preparado = None`:

```python
        self.pdf_preparado = None
        self.btn_preparar_abrir = ttk.Button(cont, text="📂 Abrir carpeta",
                                              command=self._preparar_abrir_carpeta, state=tk.DISABLED)
        self.btn_preparar_abrir.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(4, 0))
        self.btn_preparar_flipbook = ttk.Button(cont, text="➡ Generar flipbook con este PDF",
                                                 command=self._preparar_ir_flipbook, state=tk.DISABLED)
        self.btn_preparar_flipbook.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(2, 0))
```

(Ajusta los números de `row` si chocan con los existentes del método; el botón
`btn_unir` y los de estado deben quedar por encima de estos dos.)

Y los métodos:

```python
    def _preparar_abrir_carpeta(self):
        if self.pdf_preparado:
            self._abrir_carpeta_ruta(self.pdf_preparado)

    def _preparar_ir_flipbook(self):
        if self.pdf_preparado:
            self.pdf_path.set(self.pdf_preparado)
            self.notebook.select(self.tab_flipbook)
```

- [ ] **Step 5: Smoke test**

Run:
```bash
python3 -c "import ast;ast.parse(open('crear_flipbook.py').read());print('parse OK')"
python3 - <<'PY'
import importlib.util, tkinter as tk
spec=importlib.util.spec_from_file_location("cf","crear_flipbook.py")
cf=importlib.util.module_from_spec(spec); spec.loader.exec_module(cf)
r=tk.Tk(); a=cf.CreadorFlipbook(r); r.update()
for m in ("preparar_miniatura","_preparar_drag_inicio","_preparar_miniatura_sel",
          "btn_preparar_abrir","btn_preparar_flipbook","_preparar_ir_flipbook"):
    assert hasattr(a,m), m
print("smoke OK"); r.destroy()
PY
```
Expected: `parse OK` y `smoke OK`.

- [ ] **Step 6: Commit**

```bash
git add crear_flipbook.py
git commit -m "feat(gui): Preparar PDF con miniatura, arrastrar, solo-unir y aviso de protegido"
```

---

### Task 4: Recordar la última carpeta en los selectores

**Files:**
- Modify: `crear_flipbook.py`

**Interfaces:**
- Consumes: `cargar_config`, `guardar_config` (ya existen), todos los `filedialog`.
- Produces: `_dir_inicial()`, `_recordar_dir(ruta)`; todos los selectores los usan.

- [ ] **Step 1: Helpers**

Añade a la clase:

```python
    def _dir_inicial(self):
        d = cargar_config().get("ultima_carpeta", "")
        return d if d and os.path.isdir(d) else os.path.expanduser("~")

    def _recordar_dir(self, ruta):
        if not ruta:
            return
        cfg = cargar_config()
        cfg["ultima_carpeta"] = os.path.dirname(os.path.abspath(ruta))
        guardar_config(cfg)
```

- [ ] **Step 2: Usar en todos los selectores**

En CADA llamada `filedialog.askopenfilename(...)`, `askopenfilenames(...)` del
archivo (en `seleccionar_pdf`, `_preparar_anadir`, `_dividir_examinar`), añade el
argumento `initialdir=self._dir_inicial()` y, tras obtener ruta(s) no vacías,
llama `self._recordar_dir(ruta)` (para `askopenfilenames`, usa la primera:
`self._recordar_dir(rutas[0])` si `rutas`).

Ejemplo para `seleccionar_pdf` (mantén el resto igual):

```python
    def seleccionar_pdf(self):
        pdf = filedialog.askopenfilename(
            title="Selecciona el PDF", initialdir=self._dir_inicial(),
            filetypes=[("PDF", "*.pdf")])
        if pdf:
            self._recordar_dir(pdf)
            self.pdf_path.set(pdf)
            self.status_label.config(text=f"PDF: {os.path.basename(pdf)}", foreground="green")
```

(Aplica el mismo patrón —`initialdir` + `_recordar_dir`— en `_preparar_anadir` y
`_dividir_examinar`.)

- [ ] **Step 3: Smoke test**

Run:
```bash
python3 -c "import ast;ast.parse(open('crear_flipbook.py').read());print('parse OK')"
python3 - <<'PY'
import importlib.util, tkinter as tk
spec=importlib.util.spec_from_file_location("cf","crear_flipbook.py")
cf=importlib.util.module_from_spec(spec); spec.loader.exec_module(cf)
r=tk.Tk(); a=cf.CreadorFlipbook(r); r.update()
assert hasattr(a,"_dir_inicial") and hasattr(a,"_recordar_dir")
assert os.path.isdir(a._dir_inicial())
print("smoke OK"); r.destroy()
PY
```
Expected: `parse OK` y `smoke OK`.

- [ ] **Step 4: Commit**

```bash
git add crear_flipbook.py
git commit -m "feat(gui): recordar la última carpeta en los selectores de archivo"
```

---

### Task 5: Icono propio para el `.exe`

**Files:**
- Create: `icono.ico`
- Modify: `build.bat`

**Interfaces:**
- Consumes: nada.
- Produces: `icono.ico` en la raíz; `build.bat` lo usa si existe.

- [ ] **Step 1: Generar el icono con PIL**

Run (genera un icono sencillo de periódico, multi-tamaño):
```bash
python3 - <<'PY'
from PIL import Image, ImageDraw
base = 256
img = Image.new("RGBA", (base, base), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
# fondo redondeado morado (estilo de la app)
d.rounded_rectangle([8, 8, base-8, base-8], radius=40, fill=(102, 126, 234, 255))
# "hoja" de periódico
d.rounded_rectangle([60, 50, base-60, base-40], radius=12, fill=(255, 255, 255, 255))
# líneas de texto
for i, y in enumerate(range(80, 190, 22)):
    x2 = base-80 if i % 2 == 0 else base-110
    d.rectangle([80, y, x2, y+8], fill=(102, 126, 234, 255))
img.save("icono.ico", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
print("icono.ico creado")
PY
test -f icono.ico && echo OK
```
Expected: `icono.ico creado` y `OK`.

- [ ] **Step 2: Cablear en `build.bat`**

En `build.bat`, donde está la línea de `pyinstaller` (hay dos: con y sin
Poppler), añade `--icon=icono.ico` cuando exista el archivo. Sustituye el bloque
de construcción por:

```bat
set "ICON_ARG="
if exist icono.ico set "ICON_ARG=--icon=icono.ico"

if defined POPPLER_BIN (
    echo Empaquetando Poppler desde: %POPPLER_BIN%
    pyinstaller --onefile --windowed --name "GeneradorPeriodico" --clean %ICON_ARG% --add-data "%POPPLER_BIN%;poppler/bin" crear_flipbook.py
) else (
    pyinstaller --onefile --windowed --name "GeneradorPeriodico" --clean %ICON_ARG% crear_flipbook.py
)
```

- [ ] **Step 3: Verificar**

Run:
```bash
python3 -c "from PIL import Image; im=Image.open('icono.ico'); print('icono OK', im.size)"
grep -q "ICON_ARG" build.bat && echo "build.bat OK"
```
Expected: `icono OK ...` y `build.bat OK`.

- [ ] **Step 4: Commit**

```bash
git add icono.ico build.bat
git commit -m "feat(build): icono propio para el .exe"
```

---

## Notas de coordinación de agentes

- **Task 1** (pdf_tools) y **Task 5** (icono/build) son independientes.
- **Tasks 2, 3, 4** tocan `crear_flipbook.py` → **secuenciales** en ese orden
  (2 añade la pestaña y `_abrir_carpeta_ruta`; 3 usa ese helper; 4 actualiza los
  selectores que 2 y 3 introdujeron).
- Modelo: Task 1 y 5 baratos (código completo dado); 2/3/4 estándar (GUI).
- Cierre tras las 5: actualizar docs (GUIA_PILAR con "Dividir PDF" y "solo unir") + memoria.
