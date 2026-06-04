from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.archivo_tipo import ArchivoTipo


class ArchivoTipoRepositorio:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def obtener_por_url(self, pagina_fuente_id, url):
        sentencia = select(ArchivoTipo).where(
            ArchivoTipo.pagina_fuente_id == pagina_fuente_id,
            ArchivoTipo.archivo_tipo_url == url,
        )
        return self.sesion.scalar(sentencia)

    def crear(self, pagina_fuente_id, nombre, url):
        archivo_tipo = ArchivoTipo(
            pagina_fuente_id=pagina_fuente_id,
            archivo_tipo_nombre=nombre,
            archivo_tipo_url=url,
        )
        self.sesion.add(archivo_tipo)
        self.sesion.flush()
        return archivo_tipo

    def listar_requeridos(self):
        sentencia = (
            select(ArchivoTipo)
            .options(selectinload(ArchivoTipo.pagina_fuente))
            .where(ArchivoTipo.archivo_tipo_requerido.is_(True))
        )
        return list(self.sesion.scalars(sentencia))
