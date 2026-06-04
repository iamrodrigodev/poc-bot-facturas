from app.config.ajustes import ajustes
from app.database.sesion import crear_sesion
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.repositories.archivo_tipo_repositorio import ArchivoTipoRepositorio
from app.services.descarga_servicio import descargar_archivo
from app.utils.nombres import crear_nombre_archivo, crear_nombre_carpeta


def ejecutar():
    with crear_sesion() as sesion:
        archivos = ArchivoTipoRepositorio(sesion).listar_requeridos()
        repositorio_bitacora = ArchivoBitacoraRepositorio(sesion)

        for archivo in archivos:
            nombre_fisico = crear_nombre_archivo(archivo.archivo_tipo_url)
            carpeta = crear_nombre_carpeta(
                archivo.pagina_fuente.pagina_fuente_nombre,
            )

            try:
                ruta = descargar_archivo(
                    archivo.archivo_tipo_url,
                    ajustes.carpeta_downloads / carpeta,
                    nombre_fisico,
                )
                repositorio_bitacora.crear(
                    archivo.archivo_tipo_id,
                    archivo_bitacora_descarga_ok=True,
                    archivo_bitacora_nombre_fisico=nombre_fisico,
                    archivo_bitacora_ruta_descarga=str(ruta),
                    archivo_bitacora_detalle="Descarga completada",
                )
                print(f"[DESCARGADO] {ruta}")
            except Exception as error:
                repositorio_bitacora.crear(
                    archivo.archivo_tipo_id,
                    archivo_bitacora_detalle=str(error),
                )
                print(f"[ERROR] {archivo.archivo_tipo_nombre}: {error}")

        sesion.commit()
