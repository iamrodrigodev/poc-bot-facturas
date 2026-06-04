from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.config.ajustes import ajustes
from app.database.base import Base


class EnvioBitacora(Base):
    __tablename__ = "envio_bitacora"
    __table_args__ = (
        UniqueConstraint(
            "archivo_bitacora_id",
            "cliente_id",
            name="uq_envio_bitacora_archivo_cliente",
        ),
        CheckConstraint(
            "envio_bitacora_estado IN ('enviado')",
            name="ck_envio_bitacora_estado",
        ),
        {"schema": ajustes.sql_schema_operacion},
    )

    envio_bitacora_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    archivo_bitacora_id: Mapped[int] = mapped_column(
        ForeignKey(
            f"{ajustes.sql_schema_operacion}.archivo_bitacora.archivo_bitacora_id",
        ),
    )
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey(f"{ajustes.sql_schema_configuracion}.cliente.cliente_id"),
    )
    envio_bitacora_estado: Mapped[str] = mapped_column(String(30))
    envio_bitacora_detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    envio_bitacora_fecha_hora: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )
