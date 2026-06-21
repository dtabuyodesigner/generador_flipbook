# Pendiente: quitar el nombre personal de la URL

## El problema

La URL pública de cada periódico es hoy:

    https://dtabuyodesigner.github.io/generador_flipbook/<periodico>/

Aparece **dtabuyodesigner** (nombre personal de la cuenta de GitHub).

**El acortador (is.gd) NO lo soluciona:** un acortador solo *redirige*. Al abrir
el enlace corto, el navegador termina mostrando la URL real en la barra de
direcciones, así que el nombre se sigue viendo. El acortador sirve para repartir
un enlace más corto, pero no esconde el destino.

Para que el nombre NO se vea, el contenido tiene que servirse desde un sitio que
no lo lleve.

## Opciones

### A. Organización de GitHub con nombre del cole (recomendada)
- Gratis. La URL pasa a `https://<nombre-org>.github.io/generador_flipbook/<periodico>/`.
- **Ya NO hace falta recompilar el `.exe`**: el `owner/repo` se lee de un archivo
  `repositorio.txt` junto al `.exe` (formato `owner/repo`). Si no existe, usa el
  valor por defecto (`dtabuyodesigner/generador_flipbook`).
- Pasos cuando se decida:
  1. Crear una organización gratuita en GitHub con un nombre neutro/del cole
     (p. ej. `ceip-virgen-hoz` o `periodico-cole`).
  2. **Transferir** el repo `generador_flipbook` a esa organización (Settings →
     Transfer ownership). Conserva la rama `gh-pages` y todos los periódicos.
  3. Generar un **token fine-grained nuevo** para el repo en la org
     (Contents: Read and write, Pages: Read and write) y reemplazar
     `tokengenerarflipbook.txt`.
  4. Crear (o editar) `repositorio.txt` junto al `.exe` con `<nombre-org>/generador_flipbook`.
  5. Listo: la app ya publica/lee de la organización. **Sin recompilar.**
- Esfuerzo: muy pequeño (editar dos archivos de texto junto al `.exe`).

### B. Dominio propio
- `https://periodicocole.es/<periodico>/`. ~12 €/año + configurar DNS (CNAME a
  GitHub Pages) una vez. Lo más profesional, pero de pago y requiere que el cole
  lo quiera.

### C. Cambiar a Netlify / Cloudflare Pages
- URL tipo `https://periodicocole.netlify.app/<periodico>/` (nombre elegido, sin
  nombre personal). Gratis. Pero implica **reescribir la capa de publicación**
  (`github_pages.py`) para usar la API de Netlify/Cloudflare en vez de GitHub.
- Más trabajo que la A.

## Estado

Pendiente de que **Pilar decida** (charla de la noche del 2026-06-20),
principalmente el **nombre de la organización** (opción A). Cuando lo diga, Dani
aplica el cambio de `OWNER` + token y queda resuelto.
