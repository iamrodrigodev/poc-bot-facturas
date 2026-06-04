from pathlib import Path

from app.config.ajustes import ajustes
from app.database.sesion import crear_sesion
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.services.extraccion_servicio import extraer_archivo_zip
from app.utils.nombres import crear_nombre_carpeta


def ejecutar():
    with crear_sesion() as sesion:
        repositorio = ArchivoBitacoraRepositorio(sesion)

        for bitacora in repositorio.listar_descargados_sin_extraer():
            carpeta = crear_nombre_carpeta(
                bitacora.archivo_tipo.pagina_fuente.pagina_fuente_nombre,
            )

            try:
                ruta, xmls = extraer_archivo_zip(
                    Path(bitacora.archivo_bitacora_ruta_descarga),
                    ajustes.carpeta_extracted / carpeta,
                )
                bitacora.archivo_bitacora_descompresion_ok = True
                bitacora.archivo_bitacora_ruta_extraccion = str(ruta)
                bitacora.archivo_bitacora_detalle = (
                    f"Extraccion completada. XML encontrados: {len(xmls)}"
                )
                print(f"[EXTRAIDO] {ruta}")
            except Exception as error:
                bitacora.archivo_bitacora_detalle = str(error)
                print(f"[ERROR] {error}")

        sesion.commit()
