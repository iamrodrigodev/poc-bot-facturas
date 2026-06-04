from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Cliente(Base):
    __tablename__ = "cliente"

    cliente_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_nombre: Mapped[str] = mapped_column(String(1000))
    cliente_email: Mapped[str] = mapped_column(String(1000))
    cliente_activo: Mapped[bool] = mapped_column(Boolean, default=True)
