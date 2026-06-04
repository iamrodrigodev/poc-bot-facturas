import argparse

from app.database.inicializador import crear_tablas
from app.jobs import (
    descargar_archivos,
    descargar_listado,
    descomprimir_archivos,
    enviar_xml_cliente,
)
from app.utils.logs import obtener_registrador


JOBS = {
    "01_descargar_listado": descargar_listado.ejecutar,
    "02_descargar_archivos": descargar_archivos.ejecutar,
    "03_descomprimir_archivos": descomprimir_archivos.ejecutar,
    "04_enviar_xml_cliente": enviar_xml_cliente.ejecutar,
}
registrador = obtener_registrador("ejecutor")


def ejecutar_job(nombre):
    registrador.info("Inicio de job", extra={"job": nombre})

    try:
        JOBS[nombre]()
        registrador.info("Fin de job", extra={"job": nombre, "resultado": "correcto"})
    except Exception:
        registrador.exception(
            "Error durante la ejecución del job",
            extra={"job": nombre, "resultado": "error"},
        )
        raise


def ejecutar_jobs():
    analizador = argparse.ArgumentParser()
    analizador.add_argument("job", choices=[*JOBS.keys(), "todos"])
    argumentos = analizador.parse_args()

    crear_tablas()
    registrador.info("Inicio de ejecución", extra={"job_solicitado": argumentos.job})

    if argumentos.job == "todos":
        for nombre in JOBS:
            ejecutar_job(nombre)
        registrador.info("Fin de ejecución", extra={"job_solicitado": argumentos.job})
        return

    ejecutar_job(argumentos.job)
    registrador.info("Fin de ejecución", extra={"job_solicitado": argumentos.job})
