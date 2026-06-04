from app.database.transacciones import unidad_trabajo
from app.repositories.archivo_tipo_repositorio import ArchivoTipoRepositorio
from app.repositories.pagina_fuente_repositorio import PaginaFuenteRepositorio
from app.services.catalogo_servicio import obtener_archivos_zip
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("job.descargar_listado")


def ejecutar():
    with unidad_trabajo() as sesion:
        paginas = PaginaFuenteRepositorio(sesion).listar_activas()

    registrador.info("Páginas activas obtenidas", extra={"cantidad": len(paginas)})

    for pagina in paginas:
        registrador.info(
            "Procesando página fuente",
            extra={"pagina_fuente_id": pagina.pagina_fuente_id},
        )
        archivos = obtener_archivos_zip(pagina.pagina_fuente_url)
        registrador.info(
            "Archivos ZIP detectados",
            extra={
                "pagina_fuente_id": pagina.pagina_fuente_id,
                "cantidad": len(archivos),
            },
        )

        with unidad_trabajo() as sesion:
            repositorio = ArchivoTipoRepositorio(sesion)

            for archivo in archivos:
                existente = repositorio.obtener_por_url(
                    pagina.pagina_fuente_id,
                    archivo["url"],
                )

                if existente:
                    registrador.info(
                        "Archivo ya registrado",
                        extra={"archivo_nombre": archivo["nombre"]},
                    )
                    continue

                repositorio.crear(
                    pagina.pagina_fuente_id,
                    archivo["nombre"],
                    archivo["url"],
                )
                registrador.info(
                    "Archivo registrado",
                    extra={"archivo_nombre": archivo["nombre"]},
                )
