from pathlib import Path

from app.database.transacciones import unidad_trabajo
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.repositories.archivo_xml_repositorio import ArchivoXmlRepositorio
from app.services.xml_sunat_servicio import analizar_xml_sunat
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("job.procesar_xml")


def ejecutar():
    with unidad_trabajo() as sesion:
        bitacoras = ArchivoBitacoraRepositorio(sesion).listar_extraidos()

    for bitacora in bitacoras:
        ruta_extraccion = Path(bitacora.archivo_bitacora_ruta_extraccion)

        if not ruta_extraccion.is_dir():
            registrador.warning(
                "Ruta de extracción inexistente",
                extra={"archivo_bitacora_id": bitacora.archivo_bitacora_id},
            )
            continue

        cantidad = 0

        for ruta_xml in ruta_extraccion.rglob("*.xml"):
            datos = analizar_xml_sunat(ruta_xml)

            with unidad_trabajo() as sesion:
                repositorio = ArchivoXmlRepositorio(sesion)
                repositorio.guardar(bitacora.archivo_bitacora_id, **datos)
                cantidad += 1

        registrador.info(
            "XML procesados",
            extra={
                "archivo_bitacora_id": bitacora.archivo_bitacora_id,
                "cantidad": cantidad,
            },
        )
