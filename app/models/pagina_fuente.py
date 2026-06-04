from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.ajustes import ajustes
from app.database.base import Base


class PaginaFuente(Base):
    __tablename__ = "pagina_fuente"
    __table_args__ = {"schema": ajustes.sql_schema_configuracion}

    pagina_fuente_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pagina_fuente_nombre: Mapped[str] = mapped_column(String(300))
    pagina_fuente_url: Mapped[str] = mapped_column(String(2000), unique=True)
    pagina_fuente_activa: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    archivos_tipo = relationship(
        "ArchivoTipo",
        back_populates="pagina_fuente",
        cascade="all, delete-orphan",
    )
