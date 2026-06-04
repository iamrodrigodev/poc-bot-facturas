from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.archivo_bitacora import ArchivoBitacora
from app.models.archivo_tipo import ArchivoTipo


class ArchivoBitacoraRepositorio:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear(self, archivo_tipo_id, **valores):
        bitacora = ArchivoBitacora(
            archivo_tipo_id=archivo_tipo_id,
            **valores,
        )
        self.sesion.add(bitacora)
        self.sesion.flush()
        return bitacora

    def listar_descargados_sin_extraer(self):
        sentencia = (
            select(ArchivoBitacora)
            .options(
                selectinload(ArchivoBitacora.archivo_tipo).selectinload(
                    ArchivoTipo.pagina_fuente,
                ),
            )
            .where(
                ArchivoBitacora.archivo_bitacora_descarga_ok == True,
                ArchivoBitacora.archivo_bitacora_descompresion_ok == False,
            )
        )
        return list(self.sesion.scalars(sentencia))

    def listar_extraidos_sin_enviar(self):
        sentencia = (
            select(ArchivoBitacora)
            .options(selectinload(ArchivoBitacora.archivo_tipo))
            .where(
                ArchivoBitacora.archivo_bitacora_descompresion_ok == True,
                ArchivoBitacora.archivo_bitacora_envio_ok == False,
            )
        )
        return list(self.sesion.scalars(sentencia))
