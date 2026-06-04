from pathlib import Path

from app.database.transacciones import unidad_trabajo
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.repositories.archivo_xml_repositorio import ArchivoXmlRepositorio
from app.repositories.cliente_repositorio import ClienteRepositorio
from app.repositories.envio_bitacora_repositorio import EnvioBitacoraRepositorio
from app.services.correo_servicio import enviar_xmls
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("job.enviar_xml_cliente")


def enviar_pendientes_cliente(cliente):
    if not cliente.cliente_ruc:
        registrador.warning(
            "Cliente sin RUC configurado",
            extra={"cliente_id": cliente.cliente_id},
        )
        return

    with unidad_trabajo() as sesion:
        ids_enviados = EnvioBitacoraRepositorio(sesion).listar_ids_enviados(
            cliente.cliente_id,
        )
        pendientes = ArchivoXmlRepositorio(sesion).listar_no_enviados_por_ruc(
            cliente.cliente_ruc,
            ids_enviados,
        )

    if not pendientes:
        return

    enviar_xmls(
        cliente.cliente_email,
        cliente.cliente_nombre,
        [Path(xml.xml_ruta_fisica) for xml in pendientes],
    )

    with unidad_trabajo() as sesion:
        repositorio = EnvioBitacoraRepositorio(sesion)

        for archivo_xml in pendientes:
            repositorio.registrar_resultado(
                archivo_xml.xml_id,
                cliente.cliente_id,
                "enviado",
                "Correo aceptado por el servidor SMTP",
            )

    registrador.info(
        "XML enviados al cliente",
        extra={
            "cliente_id": cliente.cliente_id,
            "cliente_ruc": cliente.cliente_ruc,
            "xml_enviados": len(pendientes),
        },
    )


def actualizar_bitacoras_completas():
    with unidad_trabajo() as sesion:
        bitacoras = ArchivoBitacoraRepositorio(sesion).listar_extraidos()
        ids_enviados = EnvioBitacoraRepositorio(sesion).listar_todos_ids_enviados()
        repositorio_xml = ArchivoXmlRepositorio(sesion)

        for bitacora in bitacoras:
            archivos_xml = repositorio_xml.listar_por_bitacora(
                bitacora.archivo_bitacora_id,
            )
            bitacora.archivo_bitacora_envio_ok = bool(archivos_xml) and all(
                archivo_xml.xml_procesado_ok and archivo_xml.xml_id in ids_enviados
                for archivo_xml in archivos_xml
            )


def ejecutar():
    with unidad_trabajo() as sesion:
        clientes = ClienteRepositorio(sesion).listar_activos()

    if not clientes:
        registrador.warning("No existen clientes activos para enviar los XML")
        return

    for cliente in clientes:
        try:
            enviar_pendientes_cliente(cliente)
        except Exception as error:
            with unidad_trabajo() as sesion:
                ids_enviados = EnvioBitacoraRepositorio(sesion).listar_ids_enviados(
                    cliente.cliente_id,
                )
                pendientes = ArchivoXmlRepositorio(sesion).listar_no_enviados_por_ruc(
                    cliente.cliente_ruc,
                    ids_enviados,
                )
                repositorio = EnvioBitacoraRepositorio(sesion)

                for archivo_xml in pendientes:
                    repositorio.registrar_resultado(
                        archivo_xml.xml_id,
                        cliente.cliente_id,
                        "error",
                        str(error),
                    )

            registrador.exception(
                "Error enviando XML al cliente",
                extra={"cliente_id": cliente.cliente_id},
            )

    actualizar_bitacoras_completas()
