from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.config.ajustes import ajustes
from app.database.base import Base


class ArchivoXml(Base):
    __tablename__ = "archivo_xml"
    __table_args__ = (
        UniqueConstraint("xml_hash_sha256", name="uq_archivo_xml_hash_sha256"),
        UniqueConstraint("xml_ruta_fisica", name="uq_archivo_xml_ruta_fisica"),
        CheckConstraint(
            "xml_ruc_emisor IS NULL OR LEN(xml_ruc_emisor) = 11",
            name="ck_archivo_xml_ruc_emisor_longitud",
        ),
        CheckConstraint(
            "xml_ruc_receptor IS NULL OR LEN(xml_ruc_receptor) = 11",
            name="ck_archivo_xml_ruc_receptor_longitud",
        ),
        {"schema": ajustes.sql_schema_operacion},
    )

    xml_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    archivo_bitacora_id: Mapped[int] = mapped_column(
        ForeignKey(
            f"{ajustes.sql_schema_operacion}.archivo_bitacora.archivo_bitacora_id",
        ),
    )
    xml_hash_sha256: Mapped[str] = mapped_column(String(64))
    xml_numero_documento: Mapped[str | None] = mapped_column(String(50), nullable=True)
    xml_tipo_documento: Mapped[str | None] = mapped_column(String(10), nullable=True)
    xml_fecha_emision: Mapped[date | None] = mapped_column(Date, nullable=True)
    xml_moneda: Mapped[str | None] = mapped_column(String(3), nullable=True)
    xml_importe_total: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )
    xml_ruc_emisor: Mapped[str | None] = mapped_column(String(11), nullable=True)
    xml_ruc_receptor: Mapped[str | None] = mapped_column(String(11), nullable=True)
    xml_ruta_fisica: Mapped[str] = mapped_column(String(2000))
    xml_procesado_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    xml_detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
