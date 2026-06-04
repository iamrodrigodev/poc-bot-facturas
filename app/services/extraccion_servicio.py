from pathlib import Path
from zipfile import ZipFile


def extraer_archivo_zip(ruta_zip, carpeta_destino):
    ruta_zip = Path(ruta_zip)
    carpeta_destino = Path(carpeta_destino) / ruta_zip.stem
    carpeta_destino.mkdir(parents=True, exist_ok=True)

    with ZipFile(ruta_zip, "r") as archivo_zip:
        for nombre in archivo_zip.namelist():
            ruta_destino = (carpeta_destino / nombre).resolve()

            if not str(ruta_destino).startswith(str(carpeta_destino.resolve())):
                raise ValueError("El ZIP contiene rutas no permitidas")

        archivo_zip.extractall(carpeta_destino)

    xmls = list(carpeta_destino.rglob("*.xml"))
    return carpeta_destino, xmls
