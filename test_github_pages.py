import os
import time
import tempfile
import pytest
import github_pages as gp

def _token():
    p = os.path.join(os.path.dirname(__file__), "tokengenerarflipbook.txt")
    if not os.path.exists(p):
        pytest.skip("sin token para test real de red")
    return open(p).read().strip()

def _flipbook_tmp(n_paginas):
    d = tempfile.mkdtemp()
    open(os.path.join(d, "index.html"), "w").write("<h1>test</h1>")
    os.makedirs(os.path.join(d, "pages"))
    png = bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108"
                        "060000001f15c4890000000a49444154789c63000100000500"
                        "010d0a2db40000000049454e44ae426082")
    for i in range(1, n_paginas + 1):
        open(os.path.join(d, "pages", f"page_{i:03d}.png"), "wb").write(png)
    return d

def test_ciclo_real_publicar_listar_borrar():
    tok = _token()
    nombre = f"zz-test-{int(time.time())}"
    s = gp.slug(nombre)
    try:
        url = gp.publicar(tok, nombre, _flipbook_tmp(3))
        assert url == f"{gp.PAGES_URL}/{s}/"
        assert gp.existe(tok, nombre) is True
        assert any(it["nombre"] == s for it in gp.listar(tok))
        # republish con menos páginas -> sin huérfanos
        gp.publicar(tok, nombre, _flipbook_tmp(1))
        _, blobs = gp._arbol_actual(tok)
        pgs = [b["path"] for b in blobs if b["path"].startswith(f"{s}/pages/")]
        assert pgs == [f"{s}/pages/page_001.png"], pgs
    finally:
        gp.borrar(tok, nombre)
    assert gp.existe(tok, nombre) is False
    assert all(it["nombre"] != s for it in gp.listar(tok))

def test_slug_basico():
    assert gp.slug("Periódico Marzo 2025") == "periodico-marzo-2025"

def test_slug_acentos_y_enie():
    assert gp.slug("Edición Niños") == "edicion-ninos"

def test_slug_simbolos_y_guiones_dobles():
    assert gp.slug("Hola!!  ¿Qué tal??") == "hola-que-tal"

def test_slug_recorta_extremos():
    assert gp.slug("  ___hola___  ") == "hola"

def test_slug_vacio_por_defecto():
    assert gp.slug("   ") == "periodico"
    assert gp.slug("") == "periodico"

def test_slug_conserva_guion_bajo_interno():
    assert gp.slug("periodico_20_06_2026") == "periodico_20_06_2026"
