# Novedad: enlaces del PDF pinchables en el flipbook

**Estado:** implementado, probado y en `main` (commit `731a88d`).
**Fecha:** 2026-06-22.

## Qué hace
Los hipervínculos reales que trae el PDF (p. ej. "ver vídeo") ahora se pueden
**pinchar en el flipbook**, en su sitio exacto. Antes cada página era una imagen y
los enlaces no funcionaban.

## Cómo funciona (técnico)
- **`enlaces_pdf.py`** (módulo puro): `extraer_enlaces(pdf_path)` recorre el PDF,
  lee las anotaciones `/Link` con `/URI` y devuelve, por página, una lista de
  `{url, left, top, width, height}` en fracciones 0–1 con origen arriba-izquierda
  (listo para CSS). Ignora enlaces internos y nunca lanza (PDF ilegible → `{}`).
- **`crear_flipbook.py`**:
  - `generar_flipbook` y la vista previa llaman a `extraer_enlaces(pdf)` y pasan el
    resultado a `generar_html(..., enlaces=...)`.
  - `generar_html` inyecta `enlacesPorPagina` en el JS y, al construir cada página,
    superpone un `<a class="enlace-pdf">` absoluto en `%` (`target="_blank"`,
    `rel="noopener noreferrer"`). CSS: transparente, con leve realce al `:hover`.
  - El gesto de pasar página (arrastre de StPageFlip) **no** se traga el clic:
    `mousedown/touchstart/pointerdown` sobre el enlace hacen `stopPropagation()`.
- **Alineación:** las páginas A4 (ratio 1,414) encajan con la caja del visor sin
  bandas, así que los `%` caen sobre el sitio correcto. Si un PDF no fuese A4 podría
  haber un pequeño desajuste (caso raro; los periódicos son A4).

## Requisito para que un enlace sea pinchable
El PDF debe llevar el **hipervínculo de verdad** (en Word: *Insertar → Vínculo*).
Si la dirección está solo como texto, no hay anotación `/URI` y no se puede pinchar.

## Pruebas
- `test_enlaces_pdf.py` (5 tests): genera un PDF con reportlab con enlaces en
  posiciones conocidas y valida URL + coordenadas + robustez. Suite total: 35 verdes.
- Verificado en vivo: demo publicado con un enlace a `bolsainterinos.app`, pinchado
  desde el navegador, abría correctamente. (El demo ya se borró de la web del cole.)

## PENDIENTE para que llegue a Pilar (Windows)
La función está en el código, pero el **.exe de Pilar es de la versión vieja**. Para
que produzca enlaces pinchables hay que **recompilar en Windows**:
1. En Windows, traer esta versión (`git pull` o descargar el ZIP del repo).
2. Ejecutar **`build.bat`** → genera `dist\` nuevo.
3. Dejar junto al .exe los 4 de siempre: `poppler\`, `tokengenerarflipbook.txt`,
   `repositorio.txt`. (Ver `PLAN_WINDOWS_MAÑANA.md`.)
4. Repartir la carpeta `dist\` a Pilar.

Además, los **periódicos ya publicados no tienen enlaces** (se subieron con la
versión vieja): para dárselos hay que **volver a generarlos desde su PDF original**
con la versión nueva y **republicar con el mismo nombre** (mantiene la dirección).
