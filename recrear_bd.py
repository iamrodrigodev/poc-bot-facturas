from sqlalchemy import text
from app.database.sesion import motor
from app.database.inicializador import crear_tablas

def recrear():
    print("Borrando tablas...")
    with motor.begin() as conexion:
        try:
            conexion.execute(text("DROP TABLE operacion.envio_bitacora;"))
        except Exception:
            pass
        try:
            conexion.execute(text("DROP TABLE operacion.archivo_xml;"))
        except Exception:
            pass
        try:
            conexion.execute(text("DROP TABLE operacion.archivo_bitacora;"))
        except Exception:
            pass
        try:
            conexion.execute(text("DROP TABLE operacion.archivo_tipo;"))
        except Exception:
            pass
        try:
            conexion.execute(text("DROP TABLE configuracion.pagina_fuente;"))
        except Exception:
            pass
        try:
            conexion.execute(text("DROP TABLE configuracion.cliente;"))
        except Exception:
            pass

    print("Creando tablas...")
    crear_tablas()
    print("BD recreada correctamente.")

if __name__ == "__main__":
    recrear()
