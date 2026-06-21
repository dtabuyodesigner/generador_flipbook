import importlib.util
def _cf():
    spec=importlib.util.spec_from_file_location("cf","crear_flipbook.py")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def test_credito_aparece():
    cf=_cf()
    h=cf.generar_html("T", 3, "", "Pilar Huerta Checa")
    assert "Pilar Huerta Checa" in h
    assert "credito-contraportada" in h

def test_sin_credito_si_vacio():
    cf=_cf()
    h=cf.generar_html("T", 3, "", "")
    assert 'const montadoPor = "";' in h
