from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config.ajustes import ajustes


motor = create_engine(
    ajustes.crear_url_sqlalchemy(),
    pool_pre_ping=True,
    use_setinputsizes=False,
)


@event.listens_for(motor, "connect")
def configurar_conexion(conexion_dbapi, registro_conexion):
    cursor = conexion_dbapi.cursor()
    cursor.execute("SET XACT_ABORT ON")
    cursor.execute("SET NOCOUNT ON")
    cursor.close()

crear_sesion = sessionmaker(
    bind=motor,
    autoflush=False,
    expire_on_commit=False,
)
