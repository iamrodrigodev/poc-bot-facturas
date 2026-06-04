from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.ajustes import ajustes
from app.database.base import Base


class ArchivoTipo(Base):
    __tablename__ = "archivo_tipo"
    __table_args__ = (
        UniqueConstraint(
            "pagina_fuente_id",
            "archivo_tipo_url",
            name="uq_archivo_tipo_pagina_url",
        ),
        {"schema": ajustes.sql_schema_operacion},
    )

    archivo_tipo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pagina_fuente_id: Mapped[int] = mapped_column(
        ForeignKey(
            f"{ajustes.sql_schema_configuracion}.pagina_fuente.pagina_fuente_id",
        ),
    )
    archivo_tipo_nombre: Mapped[str] = mapped_column(String(500))
    archivo_tipo_url: Mapped[str] = mapped_column(String(2000))
    archivo_tipo_requerido: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    pagina_fuente = relationship("PaginaFuente", back_populates="archivos_tipo")
    bitacoras = relationship("ArchivoBitacora", back_populates="archivo_tipo")
