import os
import pytest
import pdf_tools as pt
from pypdf import PdfReader


def _hacer_pdf(path, paginas=1):
    from PIL import Image
    imgs = [Image.new("RGB", (240, 320), "white") for _ in range(paginas)]
    imgs[0].save(path, "PDF", save_all=True, append_images=imgs[1:])
    return path


def test_unir_pdfs_respeta_paginas(tmp_path):
    a = _hacer_pdf(str(tmp_path / "a.pdf"), 2)
    b = _hacer_pdf(str(tmp_path / "b.pdf"), 3)
    out = pt.unir_pdfs([a, b], str(tmp_path / "out.pdf"))
    assert os.path.exists(out)
    assert len(PdfReader(out).pages) == 5


def test_convertir_a_pdf_passthrough(tmp_path):
    a = _hacer_pdf(str(tmp_path / "ya.pdf"), 1)
    out = pt.convertir_a_pdf(a, str(tmp_path / "salida"))
    assert out.lower().endswith(".pdf") and os.path.exists(out)
    assert len(PdfReader(out).pages) == 1


def test_detectar_convertidor_hay_alguno():
    # En el PC de desarrollo (Zorin) hay LibreOffice.
    assert pt.detectar_convertidor() in ("word", "libreoffice")


def test_convertir_docx_si_hay_convertidor(tmp_path):
    if pt.detectar_convertidor() is None:
        pytest.skip("sin convertidor")
    from docx import Document
    doc = Document()
    doc.add_paragraph("Hola periódico de prueba")
    src = str(tmp_path / "noticia.docx")
    doc.save(src)
    out = pt.convertir_a_pdf(src, str(tmp_path / "conv"))
    assert out.lower().endswith(".pdf") and os.path.exists(out)
    assert len(PdfReader(out).pages) >= 1


def test_preparar_periodico_combina(tmp_path):
    a = _hacer_pdf(str(tmp_path / "uno.pdf"), 2)
    b = _hacer_pdf(str(tmp_path / "dos.pdf"), 1)
    out = pt.preparar_periodico([a, b], str(tmp_path / "fin"), "periodico")
    assert out.endswith("periodico.pdf") and os.path.exists(out)
    assert len(PdfReader(out).pages) == 3


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
    with pytest.raises(pt.PdfToolsError):
        pt.parsear_rango("1-99", 5)


def test_parsear_rango_sintaxis_invalida():
    with pytest.raises(pt.PdfToolsError):
        pt.parsear_rango("a-b", 5)


def test_paginas_de_pdf(tmp_path):
    p = _hacer_pdf(str(tmp_path / "x.pdf"), 3)
    assert pt.paginas_de_pdf(p) == 3


def test_dividir_pdf_rango(tmp_path):
    p = _hacer_pdf(str(tmp_path / "x.pdf"), 3)
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
    p = _hacer_pdf(str(tmp_path / "x.pdf"), 1)
    enc = _encriptar(p, str(tmp_path / "enc.pdf"))
    with pytest.raises(pt.ConversionError):
        pt.unir_pdfs([enc], str(tmp_path / "o.pdf"))
