import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse


def crear_nombre_archivo(url, nombre_predeterminado="archivo.zip"):
    nombre = Path(urlparse(url).path).name or nombre_predeterminado
    base = re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(nombre).stem).strip(".-")
    identificador = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    return f"{base[:100] or 'archivo'}-{identificador}.zip"


def crear_nombre_carpeta(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")[:80] or "sin-nombre"
