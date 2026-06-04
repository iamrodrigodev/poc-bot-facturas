import argparse

from app.database.inicializador import crear_tablas
from app.jobs import (
    descargar_archivos,
    descargar_listado,
    descomprimir_archivos,
    enviar_xml_cliente,
)


JOBS = {
    "01_descargar_listado": descargar_listado.ejecutar,
    "02_descargar_archivos": descargar_archivos.ejecutar,
    "03_descomprimir_archivos": descomprimir_archivos.ejecutar,
    "04_enviar_xml_cliente": enviar_xml_cliente.ejecutar,
}


def ejecutar_jobs():
    analizador = argparse.ArgumentParser()
    analizador.add_argument("job", choices=[*JOBS.keys(), "todos"])
    argumentos = analizador.parse_args()

    crear_tablas()

    if argumentos.job == "todos":
        for nombre, ejecutar in JOBS.items():
            print(f"\n{'=' * 70}\n{nombre}\n{'=' * 70}")
            ejecutar()
        return

    JOBS[argumentos.job]()
