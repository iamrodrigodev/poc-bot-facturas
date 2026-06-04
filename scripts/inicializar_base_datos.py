import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.models
from app.config.ajustes import ajustes
from app.database.base import Base
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("script.inicializar_base_datos")


def validar_identificador(valor, nombre):
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", valor):
        raise ValueError(f"{nombre} contiene caracteres no permitidos")


def escapar_literal(valor):
    return valor.replace("'", "''")


def crear_url(database, usuario, contrasena):
    parametros = [
        f"DRIVER={{{ajustes.sql_driver}}}",
        f"SERVER={ajustes.sql_server}",
        f"DATABASE={database}",
        "TrustServerCertificate="
        f"{'yes' if ajustes.sql_trust_server_certificate else 'no'}",
    ]

    if usuario:
        parametros.extend([f"UID={usuario}", f"PWD={contrasena}"])
    else:
        parametros.append("Trusted_Connection=yes")

    return f"mssql+pyodbc:///?odbc_connect={quote_plus(';'.join(parametros))}"


def crear_motor(database, autocommit=False):
    usuario = ajustes.sql_admin_username
    contrasena = ajustes.sql_admin_password

    if not usuario and not ajustes.sql_trusted_connection:
        raise ValueError("Debe configurarse sql_admin_username")

    if usuario and not contrasena:
        raise ValueError("Debe configurarse sql_admin_password")

    motor = create_engine(
        crear_url(database, usuario, contrasena),
        pool_pre_ping=True,
        use_setinputsizes=False,
    )

    if autocommit:
        return motor.execution_options(isolation_level="AUTOCOMMIT")

    return motor


def crear_base_datos():
    validar_identificador(ajustes.sql_database, "sql_database")
    motor_master = crear_motor("master", autocommit=True)

    with motor_master.connect() as conexion:
        conexion.execute(
            text(
                f"IF DB_ID(N'{ajustes.sql_database}') IS NULL "
                f"CREATE DATABASE [{ajustes.sql_database}]",
            ),
        )

    motor_master.dispose()


def crear_esquemas_y_tablas(motor):
    with motor.begin() as conexion:
        conexion.execute(text("SET ANSI_NULLS ON"))
        conexion.execute(text("SET QUOTED_IDENTIFIER ON"))

        for esquema in (
            ajustes.sql_schema_configuracion,
            ajustes.sql_schema_operacion,
        ):
            validar_identificador(esquema, "esquema SQL")
            conexion.execute(
                text(
                    f"IF SCHEMA_ID(N'{esquema}') IS NULL "
                    f"EXEC(N'CREATE SCHEMA [{esquema}]')",
                ),
            )

        Base.metadata.create_all(bind=conexion)


def aplicar_integridad(motor):
    esquema = ajustes.sql_schema_operacion
    sentencias = [
        (
            "ck_archivo_bitacora_descarga_consistente",
            f"ALTER TABLE [{esquema}].[archivo_bitacora] ADD CONSTRAINT "
            "ck_archivo_bitacora_descarga_consistente CHECK ("
            "archivo_bitacora_descarga_ok = 0 OR "
            "(archivo_bitacora_nombre_fisico IS NOT NULL AND "
            "archivo_bitacora_ruta_descarga IS NOT NULL))",
        ),
        (
            "ck_archivo_bitacora_descompresion_consistente",
            f"ALTER TABLE [{esquema}].[archivo_bitacora] ADD CONSTRAINT "
            "ck_archivo_bitacora_descompresion_consistente CHECK ("
            "archivo_bitacora_descompresion_ok = 0 OR "
            "(archivo_bitacora_descarga_ok = 1 AND "
            "archivo_bitacora_ruta_extraccion IS NOT NULL))",
        ),
        (
            "ck_archivo_bitacora_envio_consistente",
            f"ALTER TABLE [{esquema}].[archivo_bitacora] ADD CONSTRAINT "
            "ck_archivo_bitacora_envio_consistente CHECK ("
            "archivo_bitacora_envio_ok = 0 OR "
            "archivo_bitacora_descompresion_ok = 1)",
        ),
    ]

    with motor.begin() as conexion:
        for nombre, sentencia in sentencias:
            conexion.execute(
                text(
                    "IF NOT EXISTS (SELECT 1 FROM sys.check_constraints "
                    f"WHERE name = '{nombre}') {sentencia}",
                ),
            )

        conexion.execute(
            text(
                "IF NOT EXISTS (SELECT 1 FROM sys.indexes "
                "WHERE name = 'uq_archivo_bitacora_descarga_exitosa') "
                "CREATE UNIQUE INDEX uq_archivo_bitacora_descarga_exitosa "
                f"ON [{esquema}].[archivo_bitacora] (archivo_tipo_id) "
                "WHERE archivo_bitacora_descarga_ok = 1",
            ),
        )


def cargar_datos_iniciales(motor):
    esquema = ajustes.sql_schema_configuracion

    with motor.begin() as conexion:
        conexion.execute(
            text(
                f"IF NOT EXISTS (SELECT 1 FROM [{esquema}].[pagina_fuente] "
                "WHERE pagina_fuente_url = :url) "
                f"INSERT INTO [{esquema}].[pagina_fuente] ("
                "pagina_fuente_nombre, pagina_fuente_url, "
                "pagina_fuente_activa, fecha_creacion) "
                "VALUES (:nombre, :url, 1, GETDATE())",
            ),
            {
                "nombre": "samplelib",
                "url": "https://samplelib.com/sample-zip.html",
            },
        )


def crear_usuario_aplicacion(motor):
    usuario = ajustes.sql_username
    contrasena = ajustes.sql_password

    if not usuario or not contrasena:
        raise ValueError("Debe configurarse sql_username y sql_password")

    if usuario.lower() in {"sa", ajustes.sql_admin_username.lower()}:
        raise ValueError("El usuario de aplicación no puede ser administrador")

    validar_identificador(usuario, "sql_username")
    usuario_literal = escapar_literal(usuario)
    contrasena_literal = escapar_literal(contrasena)
    motor_master = crear_motor("master", autocommit=True)

    with motor_master.connect() as conexion:
        conexion.execute(
            text(
                f"IF NOT EXISTS (SELECT 1 FROM sys.sql_logins WHERE name = "
                f"N'{usuario_literal}') CREATE LOGIN [{usuario}] "
                f"WITH PASSWORD = N'{contrasena_literal}'",
            ),
        )

    motor_master.dispose()

    with motor.begin() as conexion:
        conexion.execute(
            text(
                "IF NOT EXISTS (SELECT 1 FROM sys.database_principals "
                f"WHERE name = N'{usuario_literal}') "
                f"CREATE USER [{usuario}] FOR LOGIN [{usuario}]",
            ),
        )
        conexion.execute(
            text(
                f"REVOKE INSERT, UPDATE, DELETE ON SCHEMA::"
                f"[{ajustes.sql_schema_configuracion}] FROM [{usuario}]",
            ),
        )
        conexion.execute(
            text(
                f"REVOKE DELETE ON SCHEMA::[{ajustes.sql_schema_operacion}] "
                f"FROM [{usuario}]",
            ),
        )
        conexion.execute(
            text(
                f"GRANT SELECT ON SCHEMA::[{ajustes.sql_schema_configuracion}] "
                f"TO [{usuario}]",
            ),
        )
        conexion.execute(
            text(
                f"GRANT SELECT, INSERT, UPDATE ON SCHEMA::"
                f"[{ajustes.sql_schema_operacion}] TO [{usuario}]",
            ),
        )


def ejecutar():
    registrador.info("Inicio de inicialización de base de datos")
    crear_base_datos()
    motor = crear_motor(ajustes.sql_database)
    crear_esquemas_y_tablas(motor)
    aplicar_integridad(motor)
    cargar_datos_iniciales(motor)
    crear_usuario_aplicacion(motor)
    motor.dispose()
    registrador.info("Base de datos inicializada correctamente")


if __name__ == "__main__":
    ejecutar()
