from app.config.ajustes import ajustes
from app.database.transacciones import unidad_trabajo
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.repositories.archivo_tipo_repositorio import ArchivoTipoRepositorio
from app.services.descarga_servicio import descargar_archivo
from app.utils.logs import obtener_registrador
from app.utils.nombres import crear_nombre_archivo, crear_nombre_carpeta


registrador = obtener_registrador("job.descargar_archivos")


def ejecutar():
    with unidad_trabajo() as sesion:
        archivos = ArchivoTipoRepositorio(sesion).listar_requeridos()

    registrador.info(
        "Archivos requeridos obtenidos",
        extra={"cantidad": len(archivos)},
    )

    for archivo in archivos:
        nombre_fisico = crear_nombre_archivo(archivo.archivo_tipo_url)
        carpeta = crear_nombre_carpeta(archivo.pagina_fuente.pagina_fuente_nombre)

        try:
            ruta = descargar_archivo(
                archivo.archivo_tipo_url,
                ajustes.carpeta_downloads / carpeta,
                nombre_fisico,
            )

            with unidad_trabajo() as sesion:
                ArchivoBitacoraRepositorio(sesion).crear(
                    archivo.archivo_tipo_id,
                    archivo_bitacora_descarga_ok=True,
                    archivo_bitacora_nombre_fisico=nombre_fisico,
                    archivo_bitacora_ruta_descarga=str(ruta),
                    archivo_bitacora_detalle="Descarga completada",
                )

            registrador.info(
                "Archivo descargado",
                extra={
                    "archivo_tipo_id": archivo.archivo_tipo_id,
                    "ruta_descarga": str(ruta),
                },
            )
        except Exception as error:
            with unidad_trabajo() as sesion:
                ArchivoBitacoraRepositorio(sesion).crear(
                    archivo.archivo_tipo_id,
                    archivo_bitacora_detalle=str(error),
                )

            registrador.exception(
                "Error al descargar archivo",
                extra={
                    "archivo_tipo_id": archivo.archivo_tipo_id,
                    "archivo_nombre": archivo.archivo_tipo_nombre,
                },
            )
