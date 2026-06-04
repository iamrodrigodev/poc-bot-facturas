import re
from pathlib import Path
from urllib.parse import urlparse


def crear_nombre_archivo(url, nombre_predeterminado="archivo.zip"):
    nombre = Path(urlparse(url).path).name
    return nombre or nombre_predeterminado


def crear_nombre_carpeta(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")[:80] or "sin-nombre"
