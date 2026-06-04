from app.database.inicializador import crear_tablas
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("script.crear_tablas")


if __name__ == "__main__":
    crear_tablas()
    registrador.info("Tablas creadas correctamente")
