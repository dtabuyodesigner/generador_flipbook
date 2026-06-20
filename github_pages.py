"""Capa de red para publicar flipbooks en GitHub Pages. Sin tkinter."""
import os
import re
import json
import base64
import unicodedata
import urllib.request
import urllib.error

OWNER = "dtabuyodesigner"
REPO = "generador_flipbook"
BRANCH = "gh-pages"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
PAGES_URL = f"https://{OWNER}.github.io/{REPO}"


class GitHubError(Exception):
    """Error legible de la capa GitHub (para mostrar al usuario)."""


def slug(nombre):
    """Convierte un nombre en una cadena URL-segura."""
    s = unicodedata.normalize("NFKD", nombre or "")
    s = s.encode("ascii", "ignore").decode("ascii").lower().strip()
    s = re.sub(r"[^a-z0-9_-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-_")
    return s or "periodico"
