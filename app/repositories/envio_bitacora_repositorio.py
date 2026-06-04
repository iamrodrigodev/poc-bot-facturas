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

    def registrar_envio(self, xml_id, cliente_id):
        sentencia = select(EnvioBitacora).where(
            EnvioBitacora.xml_id == xml_id,
            EnvioBitacora.cliente_id == cliente_id,
        )
        envio = self.sesion.scalar(sentencia)

        if envio is None:
            envio = EnvioBitacora(
                xml_id=xml_id,
                cliente_id=cliente_id,
            )
            self.sesion.add(envio)

        envio.envio_bitacora_estado = "enviado"
        envio.envio_bitacora_detalle = "Correo aceptado por el servidor SMTP"
        return envio
