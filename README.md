# Generador de Periódicos Digitales

App de escritorio (Python + tkinter) que convierte un **PDF** de periódico en un
**flipbook** HTML interactivo (efecto revista) y lo **publica en internet**
(GitHub Pages), devolviendo un **enlace público** listo para pegar.

Pensada para un colegio: la usuaria (Pilar) genera el periódico, copia el enlace
y lo pega en el portal del centro (Drupal de Castilla-La Mancha), que no admite
iframes/HTML embebido — por eso se publica fuera y se enlaza.

## Características

- Efecto revista realista (doble página, hojeo con animación) con StPageFlip.
- Título y descripción opcionales en la cabecera de la página publicada.
- **Publicación automática en GitHub Pages**: un enlace público por periódico.
- **Panel "Mis periódicos"**: listar, copiar enlace, abrir, actualizar y borrar.
- Nombre saneado a URL-segura (slug) con vista previa "Se publicará como: …".
- Subida en segundo plano (la ventana no se congela).
- Sin tecnicismos para la usuaria: el token de GitHub no aparece en la interfaz.

## Arquitectura

- `crear_flipbook.py` — interfaz tkinter y generación del flipbook local.
- `github_pages.py` — capa de red pura (sin tkinter) que habla con la API de
  GitHub: `slug`, `publicar`, `listar`, `borrar`, `existe`. Publica/borra
  reconstruyendo el árbol completo (sin huérfanos) en la rama `gh-pages`.
- `test_github_pages.py` — tests (incluye un ciclo real contra el repo).

Repo de publicación: `dtabuyodesigner/generador_flipbook`, rama `gh-pages`.
URL por periódico: `https://dtabuyodesigner.github.io/generador_flipbook/<slug>/`.

## Token (publicación)

La app lee el token de GitHub en silencio desde `tokengenerarflipbook.txt`
(junto al script o al .exe) o desde la config. Es un token **fine-grained**
limitado al repo, con permisos **Contents: RW** y **Pages: RW**. El archivo del
token está excluido de git (`.gitignore`) y nunca debe subirse.

## Uso en Linux (Zorin OS / Ubuntu)

Dependencias del sistema:

    sudo apt-get install python3-tk poppler-utils

Dependencias Python:

    pip install --break-system-packages pdf2image pillow

Ejecutar:

    python3 crear_flipbook.py

## Uso en Windows (.exe para Pilar)

- **INSTALAR_WINDOWS_FACIL.md** — guía paso a paso "para tontos" (recomendada).
- **INSTRUCCIONES_WINDOWS.md** — versión técnica (descargar de GitHub →
  `build.bat` → repartir `dist\` con el .exe + el token).
- **GUIA_PILAR.md** — uso diario de la usuaria final.

`build.bat` empaqueta Python y Poppler dentro del `.exe`, así que el equipo de
Pilar no necesita instalar nada (solo el `.exe` + `tokengenerarflipbook.txt`).

## Tests

    python3 -m pytest test_github_pages.py -v

(El ciclo real de red usa el token de `tokengenerarflipbook.txt`; si no está, se
salta.)

## Estructura del proyecto

- `crear_flipbook.py` — script principal (GUI + flipbook).
- `github_pages.py` — capa de red (GitHub Pages).
- `test_github_pages.py` — tests.
- `build.bat` — constructor del .exe para Windows.
- `requirements.txt` — dependencias Python.
- `INSTRUCCIONES_WINDOWS.md` — crear el .exe en Windows.
- `GUIA_PILAR.md` — guía de uso para la usuaria final.
- `docs/superpowers/` — spec y plan de la gestión de periódicos.

## Licencia

MIT
