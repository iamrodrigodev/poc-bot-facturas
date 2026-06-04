from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pagina_fuente import PaginaFuente


class PaginaFuenteRepositorio:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar_activas(self):
        sentencia = select(PaginaFuente).where(
            PaginaFuente.pagina_fuente_activa.is_(True),
        )
        return list(self.sesion.scalars(sentencia))

    def obtener_por_url(self, url):
        sentencia = select(PaginaFuente).where(PaginaFuente.pagina_fuente_url == url)
        return self.sesion.scalar(sentencia)

    def crear(self, nombre, url):
        pagina_fuente = PaginaFuente(
            pagina_fuente_nombre=nombre,
            pagina_fuente_url=url,
        )
        self.sesion.add(pagina_fuente)
        self.sesion.flush()
        return pagina_fuente
