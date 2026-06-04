from pathlib import Path

from app.database.sesion import crear_sesion
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.repositories.cliente_repositorio import ClienteRepositorio
from app.services.correo_servicio import enviar_xmls
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("job.enviar_xml_cliente")


def ejecutar():
    with crear_sesion() as sesion:
        bitacoras = ArchivoBitacoraRepositorio(sesion).listar_extraidos_sin_enviar()
        clientes = ClienteRepositorio(sesion).listar_activos()
        xmls = []

        for bitacora in bitacoras:
            ruta = Path(bitacora.archivo_bitacora_ruta_extraccion)
            xmls.extend(ruta.rglob("*.xml"))

        if not xmls:
            registrador.warning("No se encontraron archivos XML para enviar")
            return

        if not clientes:
            registrador.warning("No existen clientes activos para enviar los XML")
            return

        for cliente in clientes:
            enviar_xmls(cliente.cliente_email, cliente.cliente_nombre, xmls)
            registrador.info(
                "XML enviados al cliente",
                extra={
                    "cliente_id": cliente.cliente_id,
                    "cliente_email": cliente.cliente_email,
                    "xml_enviados": len(xmls),
                },
            )

        for bitacora in bitacoras:
            bitacora.archivo_bitacora_envio_ok = True

        sesion.commit()
