from app.database.sesion import crear_sesion
from app.repositories.archivo_tipo_repositorio import ArchivoTipoRepositorio
from app.repositories.pagina_fuente_repositorio import PaginaFuenteRepositorio
from app.services.catalogo_servicio import obtener_archivos_zip


def ejecutar():
    with crear_sesion() as sesion:
        paginas = PaginaFuenteRepositorio(sesion).listar_activas()
        repositorio_archivos = ArchivoTipoRepositorio(sesion)

        for pagina in paginas:
            archivos = obtener_archivos_zip(pagina.pagina_fuente_url)

            for archivo in archivos:
                existente = repositorio_archivos.obtener_por_url(
                    pagina.pagina_fuente_id,
                    archivo["url"],
                )

                if existente:
                    print(f"[EXISTE] {archivo['nombre']}")
                    continue

                repositorio_archivos.crear(
                    pagina.pagina_fuente_id,
                    archivo["nombre"],
                    archivo["url"],
                )
                print(f"[INSERTADO] {archivo['nombre']}")

        sesion.commit()
