import os
import shutil
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile, ZipInfo

from app.config.ajustes import ajustes


def validar_contenido_zip(archivo_zip):
    elementos = archivo_zip.infolist()
    tamanio_maximo = ajustes.zip_tamanio_extraido_maximo_mb * 1024 * 1024
    rutas = set()

    if len(elementos) > ajustes.zip_archivos_maximos:
        raise ValueError("El ZIP contiene demasiados archivos")

    tamanio_total = sum(elemento.file_size for elemento in elementos)

    if tamanio_total > tamanio_maximo:
        raise ValueError("El contenido extraído supera el tamaño máximo permitido")

    for elemento in elementos:
        ruta_normalizada = Path(elemento.filename).as_posix().lower()

        if ruta_normalizada in rutas:
            raise ValueError("El ZIP contiene rutas duplicadas")

        rutas.add(ruta_normalizada)

        if elemento.is_dir():
            continue

        if elemento.compress_size == 0 and elemento.file_size > 0:
            raise ValueError(
                "El ZIP contiene una relación de compresión no permitida",
            )

        if elemento.compress_size:
            ratio = elemento.file_size / elemento.compress_size

            if ratio > ajustes.zip_ratio_compresion_maximo:
                raise ValueError(
                    "El ZIP contiene una relación de compresión no permitida",
                )

        if (elemento.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError("El ZIP contiene enlaces simbólicos no permitidos")


def extraer_elemento(archivo_zip, elemento: ZipInfo, carpeta_temporal):
    ruta_destino = (carpeta_temporal / elemento.filename).resolve()

    if not ruta_destino.is_relative_to(carpeta_temporal.resolve()):
        raise ValueError("El ZIP contiene rutas no permitidas")

    if elemento.is_dir():
        ruta_destino.mkdir(parents=True, exist_ok=True)
        return

    ruta_destino.parent.mkdir(parents=True, exist_ok=True)

    with archivo_zip.open(elemento) as origen, ruta_destino.open("wb") as destino:
        shutil.copyfileobj(origen, destino)
        destino.flush()
        os.fsync(destino.fileno())


def extraer_archivo_zip(ruta_zip, carpeta_destino):
    ruta_zip = Path(ruta_zip)
    carpeta_raiz = Path(carpeta_destino)
    carpeta_raiz.mkdir(parents=True, exist_ok=True)
    carpeta_destino = carpeta_raiz / ruta_zip.stem
    carpeta_temporal = Path(mkdtemp(prefix=f".{ruta_zip.stem}.", dir=carpeta_raiz))
    carpeta_respaldo = carpeta_raiz / f".{ruta_zip.stem}.respaldo"

    try:
        with ZipFile(ruta_zip, "r") as archivo_zip:
            validar_contenido_zip(archivo_zip)

            for elemento in archivo_zip.infolist():
                extraer_elemento(archivo_zip, elemento, carpeta_temporal)

        shutil.rmtree(carpeta_respaldo, ignore_errors=True)

        if carpeta_destino.exists():
            carpeta_destino.replace(carpeta_respaldo)

        try:
            carpeta_temporal.replace(carpeta_destino)
        except Exception:
            if carpeta_respaldo.exists():
                carpeta_respaldo.replace(carpeta_destino)
            raise

        shutil.rmtree(carpeta_respaldo, ignore_errors=True)
        xmls = list(carpeta_destino.rglob("*.xml"))
        return carpeta_destino, xmls
    except Exception:
        shutil.rmtree(carpeta_temporal, ignore_errors=True)
        raise
