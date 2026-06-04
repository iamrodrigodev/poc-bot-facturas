from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.archivo_xml import ArchivoXml


class ArchivoXmlRepositorio:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def obtener_por_hash(self, xml_hash_sha256):
        sentencia = select(ArchivoXml).where(
            ArchivoXml.xml_hash_sha256 == xml_hash_sha256,
        )
        return self.sesion.scalar(sentencia)

    def obtener_por_ruta(self, xml_ruta_fisica):
        sentencia = select(ArchivoXml).where(
            ArchivoXml.xml_ruta_fisica == xml_ruta_fisica,
        )
        return self.sesion.scalar(sentencia)

    def guardar(self, archivo_bitacora_id, **datos):
        archivo_xml = self.obtener_por_hash(datos["xml_hash_sha256"])

        if archivo_xml is None:
            archivo_xml = self.obtener_por_ruta(datos["xml_ruta_fisica"])

        if archivo_xml is None:
            archivo_xml = ArchivoXml(archivo_bitacora_id=archivo_bitacora_id)
            self.sesion.add(archivo_xml)

        archivo_xml.archivo_bitacora_id = archivo_bitacora_id

        for nombre, valor in datos.items():
            setattr(archivo_xml, nombre, valor)

        self.sesion.flush()
        return archivo_xml

    def listar_por_bitacora(self, archivo_bitacora_id):
        sentencia = select(ArchivoXml).where(
            ArchivoXml.archivo_bitacora_id == archivo_bitacora_id,
        )
        return list(self.sesion.scalars(sentencia))

    def listar_no_enviados_por_ruc(self, ruc, ids_enviados):
        sentencia = select(ArchivoXml).where(
            ArchivoXml.xml_procesado_ok == True,
            ArchivoXml.xml_ruc_receptor == ruc,
        )

        if ids_enviados:
            sentencia = sentencia.where(ArchivoXml.xml_id.notin_(ids_enviados))

        return list(self.sesion.scalars(sentencia))
