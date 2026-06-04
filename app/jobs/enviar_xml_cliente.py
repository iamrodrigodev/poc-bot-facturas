from pathlib import Path

from app.database.transacciones import unidad_trabajo
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.repositories.cliente_repositorio import ClienteRepositorio
from app.repositories.envio_bitacora_repositorio import EnvioBitacoraRepositorio
from app.services.correo_servicio import enviar_xmls
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("job.enviar_xml_cliente")


def ejecutar():
    with unidad_trabajo() as sesion:
        bitacoras = ArchivoBitacoraRepositorio(sesion).listar_extraidos_sin_enviar()
        clientes = ClienteRepositorio(sesion).listar_activos()

    if not clientes:
        registrador.warning("No existen clientes activos para enviar los XML")
        return

    for cliente in clientes:
        with unidad_trabajo() as sesion:
            ids_enviados = EnvioBitacoraRepositorio(sesion).listar_ids_enviados(
                cliente.cliente_id,
            )

        pendientes = [
            bitacora
            for bitacora in bitacoras
            if bitacora.archivo_bitacora_id not in ids_enviados
        ]
        xmls = []

        for bitacora in pendientes:
            ruta = Path(bitacora.archivo_bitacora_ruta_extraccion)
            xmls.extend(ruta.rglob("*.xml"))

        if not xmls:
            continue

        enviar_xmls(cliente.cliente_email, cliente.cliente_nombre, xmls)

        with unidad_trabajo() as sesion:
            repositorio_envios = EnvioBitacoraRepositorio(sesion)

            for bitacora in pendientes:
                repositorio_envios.registrar_envio(
                    bitacora.archivo_bitacora_id,
                    cliente.cliente_id,
                )

        registrador.info(
            "XML enviados al cliente",
            extra={
                "cliente_id": cliente.cliente_id,
                "xml_enviados": len(xmls),
            },
        )

    ids_completos = {bitacora.archivo_bitacora_id for bitacora in bitacoras}

    for cliente in clientes:
        with unidad_trabajo() as sesion:
            ids_enviados = EnvioBitacoraRepositorio(sesion).listar_ids_enviados(
                cliente.cliente_id,
            )
        ids_completos &= ids_enviados

    with unidad_trabajo() as sesion:
        repositorio = ArchivoBitacoraRepositorio(sesion)

        for archivo_bitacora_id in ids_completos:
            bitacora_actual = repositorio.obtener_por_id(archivo_bitacora_id)
            bitacora_actual.archivo_bitacora_envio_ok = True
