from pathlib import Path

import requests


def descargar_archivo(url, carpeta_destino, nombre_archivo):
    carpeta_destino = Path(carpeta_destino)
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    ruta_archivo = carpeta_destino / nombre_archivo

    respuesta = requests.get(url, timeout=120, stream=True)
    respuesta.raise_for_status()

    with ruta_archivo.open("wb") as archivo:
        for bloque in respuesta.iter_content(chunk_size=1024 * 1024):
            if bloque:
                archivo.write(bloque)

    return ruta_archivo
