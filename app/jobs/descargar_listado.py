from app.database.sesion import crear_sesion
from app.repositories.archivo_tipo_repositorio import ArchivoTipoRepositorio
from app.repositories.pagina_fuente_repositorio import PaginaFuenteRepositorio
from app.services.catalogo_servicio import obtener_archivos_zip
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("job.descargar_listado")


def ejecutar():
    with crear_sesion() as sesion:
        paginas = PaginaFuenteRepositorio(sesion).listar_activas()
        repositorio_archivos = ArchivoTipoRepositorio(sesion)
        registrador.info("Páginas activas obtenidas", extra={"cantidad": len(paginas)})

        for pagina in paginas:
            registrador.info(
                "Procesando página fuente",
                extra={
                    "pagina_fuente_id": pagina.pagina_fuente_id,
                    "pagina_fuente_url": pagina.pagina_fuente_url,
                },
            )
            archivos = obtener_archivos_zip(pagina.pagina_fuente_url)
            registrador.info(
                "Archivos ZIP detectados",
                extra={
                    "pagina_fuente_id": pagina.pagina_fuente_id,
                    "cantidad": len(archivos),
                },
            )

            for archivo in archivos:
                existente = repositorio_archivos.obtener_por_url(
                    pagina.pagina_fuente_id,
                    archivo["url"],
                )

                if existente:
                    registrador.info(
                        "Archivo ya registrado",
                        extra={
                            "archivo_nombre": archivo["nombre"],
                            "archivo_url": archivo["url"],
                        },
                    )
                    continue

                repositorio_archivos.crear(
                    pagina.pagina_fuente_id,
                    archivo["nombre"],
                    archivo["url"],
                )
                registrador.info(
                    "Archivo registrado",
                    extra={
                        "archivo_nombre": archivo["nombre"],
                        "archivo_url": archivo["url"],
                    },
                )

        sesion.commit()
