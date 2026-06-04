from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.envio_bitacora import EnvioBitacora


class EnvioBitacoraRepositorio:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar_ids_enviados(self, cliente_id):
        sentencia = select(EnvioBitacora.xml_id).where(
            EnvioBitacora.cliente_id == cliente_id,
            EnvioBitacora.envio_bitacora_estado == "enviado",
        )
        return set(self.sesion.scalars(sentencia))

    def listar_todos_ids_enviados(self):
        sentencia = select(EnvioBitacora.xml_id).where(
            EnvioBitacora.envio_bitacora_estado == "enviado",
        )
        return set(self.sesion.scalars(sentencia))

    def registrar_resultado(self, xml_id, cliente_id, estado, detalle):
        envio = EnvioBitacora(
            xml_id=xml_id,
            cliente_id=cliente_id,
            envio_bitacora_estado=estado,
            envio_bitacora_detalle=detalle,
        )
        self.sesion.add(envio)
        self.sesion.flush()
        return envio
