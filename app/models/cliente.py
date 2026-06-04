from sqlalchemy import Boolean, CheckConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.ajustes import ajustes
from app.database.base import Base


class Cliente(Base):
    __tablename__ = "cliente"
    __table_args__ = (
        Index(
            "uq_cliente_ruc",
            "cliente_ruc",
            unique=True,
            mssql_where="cliente_ruc IS NOT NULL",
        ),
        CheckConstraint(
            "cliente_ruc IS NULL OR LEN(cliente_ruc) = 11",
            name="ck_cliente_ruc_longitud",
        ),
        {"schema": ajustes.sql_schema_configuracion},
    )

    cliente_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_nombre: Mapped[str] = mapped_column(String(1000))
    cliente_email: Mapped[str] = mapped_column(String(1000))
    cliente_ruc: Mapped[str | None] = mapped_column(String(11), nullable=True)
    cliente_activo: Mapped[bool] = mapped_column(Boolean, default=True)
