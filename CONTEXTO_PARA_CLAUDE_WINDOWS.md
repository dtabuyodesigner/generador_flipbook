# Contexto para retomar en Windows (handoff entre sesiones)

> Si eres una sesión nueva de Claude Code: lee esto entero antes de actuar.
> El trabajo venía de una sesión en Linux. Aquí está el estado y qué hacer.

## Qué es la app
App de escritorio (Python + tkinter) para **Pilar** (CEIP Virgen de la Hoz, Molina
de Aragón). Convierte PDFs de periódicos en **flipbooks HTML** y los **publica en
GitHub Pages** para pegar el enlace en el Drupal del cole. Archivos clave:
- `crear_flipbook.py` — GUI (5 pestañas).
- `github_pages.py` — capa de red (GitHub Git Data API, rama `gh-pages`).
- `pdf_tools.py`, `acortador.py` (is.gd).

## Repo / publicación
- Repo: `ceipvirgendelahoz/generador_flipbook` (configurado en `repositorio.txt`).
- Rama de publicación: `gh-pages`. URL: `https://ceipvirgendelahoz.github.io/generador_flipbook/<slug>/`.
- `tokengenerarflipbook.txt` = token fine-grained (Contents RW + Pages RW). **GITIGNORED.**

## EL PROBLEMA QUE HAY QUE ARREGLAR
- Desde **Linux publica perfectamente** con el mismo token y repo (confirmado).
- En **Windows, el .exe NO publica**: extrae las páginas (Poppler OK) pero al subir
  falla y solo muestra "No se ha podido publicar / revisa tu conexión".
- El GUI **se traga el error real** (`_publicar_seguro` hace `except: return None`),
  por eso no sabemos la causa. Hay que **capturar el error real**.

## Qué ya se intentó / se cambió
- Sospecha 1: **BOM** del Bloc de notas en `tokengenerarflipbook.txt`/`repositorio.txt`.
  - Arreglado: ahora se leen con `encoding="utf-8-sig"` (en `crear_flipbook.py` `_leer_token_github`
    y en `github_pages.py` `_repo_desde_archivo`).
  - El usuario reguardó los .txt como ANSI y **AÚN ASÍ no publicó** → el BOM
    probablemente NO era la causa (o no la única). Sigue pendiente ver el error real.
- Se añadió `diagnosticar.py` (y un `diagnosticar.bat`) que prueba la conexión y
  enseña el motivo. También se añadió un log `diagnostico_publicacion.txt` junto al
  .exe cuando falla la publicación (solo en el código nuevo; el .exe que probó el
  usuario era el viejo).

## PRIMER PASO EN WINDOWS (hazlo ya)
Ejecuta el diagnóstico de conexión directamente con Python (no hace falta el .exe):

```
python diagnosticar.py
```

o, si el token está junto al .exe, en la carpeta del proyecto con `dist\` al lado.
Mira el `RESULTADO:`:
- **ERROR HTTP 401** → token rechazado (caducado/mal/expuesto) → regenerar token.
- **ERROR HTTP 404** → `repositorio.txt` mal o repo/rama incorrectos.
- **ERROR DE RED O SSL** → cortafuegos/antivirus/proxy del cole, o falta de
  certificados CA en el Python/exe de Windows (posible en PyInstaller). Si es SSL,
  la pista está en el tipo de excepción (`SSLCertVerificationError`, etc.).

Con la causa concreta, aplicar el arreglo y **verificar publicando de verdad**.

## REGLAS DE SEGURIDAD (IMPORTANTES, no romper)
- **NUNCA** hacer commit/push de `tokengenerarflipbook.txt` (está en `.gitignore`).
- El token de la org **se filtró en un chat** → el usuario DEBE regenerarlo y
  reemplazar el archivo. No reutilizarlo en sitios nuevos.
- En la UI de Pilar el token **no debe verse jamás**; el botón de publicar no se
  llama "subir a git". Los mensajes de error dicen **"avisa a Dani"**, nunca la
  palabra "token". No imprimir el token en salidas (el diagnóstico solo enseña su longitud).

## Estado git
- Todo lo de arriba está commiteado y pusheado a `main` (commit del fix BOM + diagnóstico).
- En Linux quedó sin pushear una versión "autocontenida" de `diagnosticar.bat`
  (mete el Python dentro del .bat). Da igual: en Windows se diagnostica en vivo.
