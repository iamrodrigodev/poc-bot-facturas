from app.database.inicializador import crear_tablas
from app.jobs.descargar_archivos import ejecutar


if __name__ == "__main__":
    crear_tablas()
    ejecutar()
