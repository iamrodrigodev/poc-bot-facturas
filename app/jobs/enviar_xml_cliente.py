from pathlib import Path

from app.database.transacciones import unidad_trabajo
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.repositories.archivo_xml_repositorio import ArchivoXmlRepositorio
from app.repositories.cliente_repositorio import ClienteRepositorio
from app.repositories.envio_bitacora_repositorio import EnvioBitacoraRepositorio
from app.services.correo_servicio import enviar_xmls
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("job.enviar_xml_cliente")


def ejecutar():
    with unidad_trabajo() as sesion:
        clientes = ClienteRepositorio(sesion).listar_activos()
        bitacoras = ArchivoBitacoraRepositorio(sesion).listar_extraidos_sin_enviar()

    if not clientes:
        registrador.warning("No existen clientes activos para enviar los XML")
        return

    
    ids_completos = {bitacora.archivo_bitacora_id for bitacora in bitacoras}

    for cliente in clientes:
        if not cliente.cliente_rfc:
            registrador.warning(f"El cliente {cliente.cliente_id} no tiene RFC configurado. Se omitirá.")
            continue

        with unidad_trabajo() as sesion:
            ids_enviados = EnvioBitacoraRepositorio(sesion).listar_ids_enviados(
                cliente.cliente_id,
            )
            
            xmls_pendientes = ArchivoXmlRepositorio(sesion).listar_no_enviados_por_rfc(
                cliente.cliente_rfc, ids_enviados
            )

        if not xmls_pendientes:
            continue

        rutas_xmls = [Path(xml.xml_ruta_fisica) for xml in xmls_pendientes]

        try:
            enviar_xmls(cliente.cliente_email, cliente.cliente_nombre, rutas_xmls)
            
            with unidad_trabajo() as sesion:
                repositorio_envios = EnvioBitacoraRepositorio(sesion)
                for xml in xmls_pendientes:
                    repositorio_envios.registrar_envio(
                        xml.xml_id,
                        cliente.cliente_id,
                    )

            registrador.info(
                "XML enviados al cliente",
                extra={
                    "cliente_id": cliente.cliente_id,
                    "cliente_rfc": cliente.cliente_rfc,
                    "xml_enviados": len(xmls_pendientes),
                },
            )
        except Exception as e:
            registrador.error(f"Error enviando XMLs al cliente {cliente.cliente_id}: {e}")
            
            for xml in xmls_pendientes:
                ids_completos.discard(xml.archivo_bitacora_id)

    
    with unidad_trabajo() as sesion:
        repositorio_bitacora = ArchivoBitacoraRepositorio(sesion)
        for archivo_bitacora_id in ids_completos:
            bitacora_actual = repositorio_bitacora.obtener_por_id(archivo_bitacora_id)
            if bitacora_actual:
                bitacora_actual.archivo_bitacora_envio_ok = True
