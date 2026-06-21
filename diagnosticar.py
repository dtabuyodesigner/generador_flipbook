"""Diagnostico de publicacion: muestra el motivo REAL si la subida falla.
Ejecutar en la carpeta del proyecto (donde esta github_pages.py).
NO imprime el token; solo su longitud, para no exponerlo."""
import os, sys, traceback

aqui = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, aqui)

def buscar_token():
    candidatos = [
        os.path.join(aqui, "dist", "tokengenerarflipbook.txt"),
        os.path.join(aqui, "tokengenerarflipbook.txt"),
    ]
    for p in candidatos:
        if os.path.exists(p):
            tok = open(p, encoding="utf-8-sig").read().strip()
            print(f"Token encontrado en: {p}")
            print(f"  longitud={len(tok)}  empieza_por='{tok[:10]}...'")
            return tok
    print("ERROR: no encuentro tokengenerarflipbook.txt ni en dist\\ ni aqui.")
    return None

def buscar_repo_txt():
    for p in (os.path.join(aqui, "dist", "repositorio.txt"),
              os.path.join(aqui, "repositorio.txt")):
        if os.path.exists(p):
            print(f"repositorio.txt en: {p}")
            print(f"  contenido='{open(p, encoding='utf-8-sig').read().strip()}'")
            return
    print("Aviso: no hay repositorio.txt (se usara el repo por defecto).")

print("=" * 50)
print("DIAGNOSTICO DE PUBLICACION")
print("=" * 50)
buscar_repo_txt()
import github_pages as gp
print(f"Repo destino: {gp.OWNER}/{gp.REPO}")
print(f"API: {gp.API}")
print("-" * 50)

tok = buscar_token()
if tok:
    print("Probando conexion con GitHub (listar publicaciones)...")
    try:
        items = gp.listar(tok)
        print(f"OK CONEXION. Publicaciones actuales: {len(items)}")
        print("=> El acceso funciona. El fallo esta en otra parte.")
    except Exception as e:
        print("FALLO LA CONEXION. Motivo real:")
        print(f"  {type(e).__name__}: {e}")
        print("-" * 50)
        traceback.print_exc()

print("=" * 50)
input("Pulsa ENTER para cerrar...")
