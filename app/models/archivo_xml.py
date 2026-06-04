from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.ajustes import ajustes
from app.database.base import Base


class ArchivoXml(Base):
    __tablename__ = "archivo_xml"
    __table_args__ = {"schema": ajustes.sql_schema_operacion}

    xml_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    archivo_bitacora_id: Mapped[int] = mapped_column(
        ForeignKey(f"{ajustes.sql_schema_operacion}.archivo_bitacora.archivo_bitacora_id"),
    )
    xml_uuid: Mapped[str | None] = mapped_column(String(36), nullable=True)
    xml_rfc_emisor: Mapped[str | None] = mapped_column(String(13), nullable=True)
    xml_rfc_receptor: Mapped[str | None] = mapped_column(String(13), nullable=True)
    xml_ruta_fisica: Mapped[str] = mapped_column(String(2000))
    xml_procesado_ok: Mapped[bool] = mapped_column(Boolean, default=False)
