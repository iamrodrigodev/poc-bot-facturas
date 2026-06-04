from contextlib import contextmanager

from app.database.sesion import crear_sesion


@contextmanager
def unidad_trabajo():
    sesion = crear_sesion()

    try:
        with sesion.begin():
            yield sesion
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()
