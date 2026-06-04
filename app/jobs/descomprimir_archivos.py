from pathlib import Path

from app.config.ajustes import ajustes
from app.database.sesion import crear_sesion
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.services.extraccion_servicio import extraer_archivo_zip
from app.utils.nombres import crear_nombre_carpeta
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("job.descomprimir_archivos")


def ejecutar():
    with crear_sesion() as sesion:
        repositorio = ArchivoBitacoraRepositorio(sesion)

        bitacoras = repositorio.listar_descargados_sin_extraer()
        registrador.info(
            "Descargas pendientes obtenidas",
            extra={"cantidad": len(bitacoras)},
        )

        for bitacora in bitacoras:
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
                registrador.info(
                    "Archivo descomprimido",
                    extra={
                        "archivo_bitacora_id": bitacora.archivo_bitacora_id,
                        "ruta_extraccion": str(ruta),
                        "xml_encontrados": len(xmls),
                    },
                )
            except Exception as error:
                bitacora.archivo_bitacora_detalle = str(error)
                registrador.exception(
                    "Error al descomprimir archivo",
                    extra={
                        "archivo_bitacora_id": bitacora.archivo_bitacora_id,
                        "ruta_descarga": bitacora.archivo_bitacora_ruta_descarga,
                    },
                )

        sesion.commit()
