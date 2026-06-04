from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.ajustes import ajustes
from app.database.base import Base


class ArchivoBitacora(Base):
    __tablename__ = "archivo_bitacora"
    __table_args__ = (
        CheckConstraint(
            "archivo_bitacora_descarga_ok = 0 OR "
            "(archivo_bitacora_nombre_fisico IS NOT NULL AND "
            "archivo_bitacora_ruta_descarga IS NOT NULL)",
            name="ck_archivo_bitacora_descarga_consistente",
        ),
        CheckConstraint(
            "archivo_bitacora_descompresion_ok = 0 OR "
            "(archivo_bitacora_descarga_ok = 1 AND "
            "archivo_bitacora_ruta_extraccion IS NOT NULL)",
            name="ck_archivo_bitacora_descompresion_consistente",
        ),
        CheckConstraint(
            "archivo_bitacora_envio_ok = 0 OR archivo_bitacora_descompresion_ok = 1",
            name="ck_archivo_bitacora_envio_consistente",
        ),
        Index(
            "uq_archivo_bitacora_descarga_exitosa",
            "archivo_tipo_id",
            unique=True,
            mssql_where="archivo_bitacora_descarga_ok = 1",
        ),
        {"schema": ajustes.sql_schema_operacion},
    )

    archivo_bitacora_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    archivo_tipo_id: Mapped[int] = mapped_column(
        ForeignKey(f"{ajustes.sql_schema_operacion}.archivo_tipo.archivo_tipo_id"),
    )
    archivo_bitacora_fecha_hora: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )
    archivo_bitacora_descarga_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    archivo_bitacora_descompresion_ok: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    archivo_bitacora_envio_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    archivo_bitacora_nombre_fisico: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    archivo_bitacora_ruta_descarga: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    archivo_bitacora_ruta_extraccion: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    archivo_bitacora_detalle: Mapped[str | None] = mapped_column(Text, nullable=True)

    archivo_tipo = relationship("ArchivoTipo", back_populates="bitacoras")
