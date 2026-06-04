from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.archivo_xml import ArchivoXml


class ArchivoXmlRepositorio:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear(self, archivo_bitacora_id, xml_uuid, xml_rfc_emisor, xml_rfc_receptor, xml_ruta_fisica, xml_procesado_ok=True):
        xml = ArchivoXml(
            archivo_bitacora_id=archivo_bitacora_id,
            xml_uuid=xml_uuid,
            xml_rfc_emisor=xml_rfc_emisor,
            xml_rfc_receptor=xml_rfc_receptor,
            xml_ruta_fisica=xml_ruta_fisica,
            xml_procesado_ok=xml_procesado_ok,
        )
        self.sesion.add(xml)
        self.sesion.flush()
        return xml

    def obtener_por_ruta(self, xml_ruta_fisica):
        sentencia = select(ArchivoXml).where(ArchivoXml.xml_ruta_fisica == xml_ruta_fisica)
        return self.sesion.scalars(sentencia).first()

    def listar_no_enviados_por_rfc(self, rfc: str, ids_enviados: set):
        sentencia = select(ArchivoXml).where(
            ArchivoXml.xml_rfc_receptor == rfc,
            ArchivoXml.xml_id.notin_(ids_enviados) if ids_enviados else True,
        )
        return list(self.sesion.scalars(sentencia))
