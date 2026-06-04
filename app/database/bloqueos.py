from contextlib import contextmanager

from sqlalchemy import text

from app.database.sesion import motor


@contextmanager
def bloquear_job(nombre):
    conexion = motor.connect()
    bloqueo_obtenido = False

    try:
        resultado = conexion.execute(
            text(
                "DECLARE @resultado int; "
                "EXEC @resultado = sp_getapplock "
                "@Resource = :recurso, "
                "@LockMode = 'Exclusive', "
                "@LockOwner = 'Session', "
                "@LockTimeout = 0; "
                "SELECT @resultado;"
            ),
            {"recurso": f"poc_bot_facturas:{nombre}"},
        ).scalar_one()

        if resultado < 0:
            raise RuntimeError(f"El job {nombre} ya se encuentra en ejecución")

        bloqueo_obtenido = True
        yield
    finally:
        if bloqueo_obtenido:
            conexion.execute(
                text(
                    "EXEC sp_releaseapplock "
                    "@Resource = :recurso, "
                    "@LockOwner = 'Session';"
                ),
                {"recurso": f"poc_bot_facturas:{nombre}"},
            )

        conexion.close()
