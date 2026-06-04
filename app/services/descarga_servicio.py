import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin
from zipfile import is_zipfile

import requests

from app.config.ajustes import ajustes
from app.services.url_servicio import validar_url_publica


def obtener_respuesta_segura(url):
    sesion = requests.Session()

    try:
        url_actual = validar_url_publica(url)

        for _ in range(6):
            respuesta = sesion.get(
                url_actual,
                timeout=(10, 120),
                stream=True,
                allow_redirects=False,
            )

            if respuesta.is_redirect or respuesta.is_permanent_redirect:
                ubicacion = respuesta.headers.get("location")
                respuesta.close()

                if not ubicacion:
                    raise ValueError("La redirección no contiene una ubicación")

                url_actual = validar_url_publica(urljoin(url_actual, ubicacion))
                continue

            respuesta.raise_for_status()
            return sesion, respuesta

        raise ValueError("La descarga supera el máximo de redirecciones")
    except Exception:
        sesion.close()
        raise


def descargar_archivo(url, carpeta_destino, nombre_archivo):
    carpeta_destino = Path(carpeta_destino)
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    ruta_archivo = carpeta_destino / nombre_archivo
    tamanio_maximo = ajustes.descarga_tamanio_maximo_mb * 1024 * 1024

    sesion, respuesta = obtener_respuesta_segura(url)

    try:
        tamanio_declarado = int(respuesta.headers.get("content-length", "0"))

        if tamanio_declarado > tamanio_maximo:
            raise ValueError("El archivo supera el tamaño máximo permitido")

        with NamedTemporaryFile(
            dir=carpeta_destino,
            prefix=f".{nombre_archivo}.",
            suffix=".parcial",
            delete=False,
        ) as archivo_temporal:
            ruta_temporal = Path(archivo_temporal.name)
            tamanio_descargado = 0

            try:
                for bloque in respuesta.iter_content(chunk_size=1024 * 1024):
                    if not bloque:
                        continue

                    tamanio_descargado += len(bloque)

                    if tamanio_descargado > tamanio_maximo:
                        raise ValueError(
                            "El archivo supera el tamaño máximo permitido",
                        )

                    archivo_temporal.write(bloque)

                archivo_temporal.flush()
                os.fsync(archivo_temporal.fileno())

                if not is_zipfile(ruta_temporal):
                    raise ValueError("El archivo descargado no es un ZIP válido")

                ruta_temporal.replace(ruta_archivo)
                return ruta_archivo
            except Exception:
                ruta_temporal.unlink(missing_ok=True)
                raise
    finally:
        respuesta.close()
        sesion.close()
