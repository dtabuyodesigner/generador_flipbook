"""Preparar el PDF del periódico: detectar convertidor, convertir Word->PDF
y unir varios PDFs en el orden dado. Sin tkinter."""
import os
import shutil
import platform
import tempfile
import subprocess
from shutil import which


class PdfToolsError(Exception):
    """Error legible de la preparación de PDF."""


class ConversionError(PdfToolsError):
    """No se pudo convertir un archivo a PDF."""


_LIBRE_PATHS_WIN = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]


def _buscar_soffice():
    if platform.system() == "Windows":
        for p in _LIBRE_PATHS_WIN:
            if os.path.exists(p):
                return p
        return which("soffice")
    return which("soffice") or which("libreoffice")


def _word_disponible():
    if platform.system() != "Windows":
        return False
    try:
        import winreg
        try:
            winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Word.Application")
            return True
        except OSError:
            return False
    except Exception:
        return False


def detectar_convertidor():
    """Devuelve 'word', 'libreoffice' o None segun lo instalado."""
    if _word_disponible():
        return "word"
    if _buscar_soffice():
        return "libreoffice"
    return None


def _convertir_word(archivo, carpeta_salida):
    import win32com.client  # solo Windows con Word
    salida = os.path.join(
        carpeta_salida,
        os.path.splitext(os.path.basename(archivo))[0] + ".pdf")
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        try:
            doc = word.Documents.Open(os.path.abspath(archivo))
            doc.SaveAs(os.path.abspath(salida), FileFormat=17)  # 17 = wdFormatPDF
            doc.Close()
        finally:
            word.Quit()
    except ConversionError:
        raise
    except Exception as e:
        # Errores COM crudos -> mensaje legible para la GUI
        raise ConversionError(
            f"Word no pudo convertir {os.path.basename(archivo)}: {e}")
    if not os.path.exists(salida):
        raise ConversionError(f"No se pudo convertir: {os.path.basename(archivo)}")
    return salida


def _convertir_libreoffice(archivo, carpeta_salida):
    soffice = _buscar_soffice()
    if not soffice:
        raise ConversionError("No encuentro LibreOffice para convertir.")
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir",
         os.path.abspath(carpeta_salida), os.path.abspath(archivo)],
        check=True, timeout=180,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    salida = os.path.join(
        carpeta_salida,
        os.path.splitext(os.path.basename(archivo))[0] + ".pdf")
    if not os.path.exists(salida):
        raise ConversionError(f"No se pudo convertir: {os.path.basename(archivo)}")
    return salida


def convertir_a_pdf(archivo, carpeta_salida):
    """Devuelve la ruta a un PDF: copia si ya es PDF, o convierte si es Word."""
    os.makedirs(carpeta_salida, exist_ok=True)
    ext = os.path.splitext(archivo)[1].lower()
    if ext == ".pdf":
        destino = os.path.join(carpeta_salida, os.path.basename(archivo))
        if os.path.abspath(archivo) != os.path.abspath(destino):
            shutil.copy(archivo, destino)
        return destino
    if ext in (".doc", ".docx"):
        motor = detectar_convertidor()
        if motor == "word":
            return _convertir_word(archivo, carpeta_salida)
        if motor == "libreoffice":
            return _convertir_libreoffice(archivo, carpeta_salida)
        raise ConversionError(
            "No encuentro Word ni LibreOffice para convertir los archivos de "
            "Word. Pásalos a PDF a mano, o instala LibreOffice.")
    raise ConversionError(f"Formato no soportado: {ext}")


def unir_pdfs(rutas_ordenadas, ruta_salida):
    """Une los PDFs en el orden EXACTO de la lista. Devuelve ruta_salida."""
    from pypdf import PdfWriter
    carpeta = os.path.dirname(os.path.abspath(ruta_salida))
    os.makedirs(carpeta, exist_ok=True)
    writer = PdfWriter()
    try:
        for r in rutas_ordenadas:
            if esta_encriptado(r):
                raise ConversionError(
                    f"El PDF '{os.path.basename(r)}' está protegido con contraseña; "
                    "quítasela e inténtalo de nuevo.")
            writer.append(r)
        with open(ruta_salida, "wb") as f:
            writer.write(f)
    finally:
        writer.close()
    return ruta_salida


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
            try:
                writer.add_page(reader.pages[p - 1])
                out = os.path.join(carpeta_salida, f"{nombre_base}_pagina_{p:03d}.pdf")
                with open(out, "wb") as f:
                    writer.write(f)
            finally:
                writer.close()
            salidas.append(out)
    else:
        writer = PdfWriter()
        try:
            for p in paginas:
                writer.add_page(reader.pages[p - 1])
            out = os.path.join(carpeta_salida, f"{nombre_base}.pdf")
            with open(out, "wb") as f:
                writer.write(f)
        finally:
            writer.close()
        salidas.append(out)
    return salidas


def preparar_periodico(archivos_ordenados, carpeta_salida, nombre_pdf):
    """Convierte cada archivo a PDF (en orden) y los une en
    carpeta_salida/<nombre_pdf>.pdf. Devuelve la ruta del PDF combinado."""
    os.makedirs(carpeta_salida, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="prep_periodico_")
    try:
        pdfs = []
        for i, archivo in enumerate(archivos_ordenados):
            sub = os.path.join(tmp, str(i))  # subcarpeta por índice: evita choques de nombre
            os.makedirs(sub, exist_ok=True)
            pdfs.append(convertir_a_pdf(archivo, sub))
        nombre = nombre_pdf if nombre_pdf.lower().endswith(".pdf") else nombre_pdf + ".pdf"
        salida = os.path.join(carpeta_salida, nombre)
        unir_pdfs(pdfs, salida)
        return salida
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
