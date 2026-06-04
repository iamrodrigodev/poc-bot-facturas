from app.database.inicializador import crear_tablas
from app.jobs.enviar_xml_cliente import ejecutar


if __name__ == "__main__":
    crear_tablas()
    ejecutar()
