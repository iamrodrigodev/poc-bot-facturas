from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cliente import Cliente


class ClienteRepositorio:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar_activos(self):
        sentencia = select(Cliente).where(Cliente.cliente_activo == True)
        return list(self.sesion.scalars(sentencia))
