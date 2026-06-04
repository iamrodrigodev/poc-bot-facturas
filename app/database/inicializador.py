from app.database.base import Base
from app.database.sesion import motor
from app.models import archivo_bitacora, archivo_tipo, cliente, pagina_fuente


def crear_tablas():
    Base.metadata.create_all(bind=motor)
