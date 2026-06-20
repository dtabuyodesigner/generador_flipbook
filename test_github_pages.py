import github_pages as gp

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
