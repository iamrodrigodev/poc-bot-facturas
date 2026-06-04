import re

from sqlalchemy import text

from app.config.ajustes import ajustes
from app.database.base import Base
from app.database.sesion import motor
from app.models import archivo_bitacora, archivo_tipo, cliente, pagina_fuente


def crear_esquema():
    with motor.begin() as conexion:
        for esquema in (
            ajustes.sql_schema_configuracion,
            ajustes.sql_schema_operacion,
        ):
            if not re.fullmatch(r"[a-z][a-z0-9_]*", esquema):
                raise ValueError("Los esquemas SQL deben utilizar snake_case")

            sentencia = (
                f"IF SCHEMA_ID(N'{esquema}') IS NULL "
                f"EXEC(N'CREATE SCHEMA [{esquema}]')"
            )
            conexion.execute(text(sentencia))


def crear_tablas():
    crear_esquema()
    Base.metadata.create_all(bind=motor)
