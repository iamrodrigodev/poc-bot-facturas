from pathlib import Path

from app.database.sesion import crear_sesion
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.repositories.cliente_repositorio import ClienteRepositorio
from app.services.correo_servicio import enviar_xmls


def ejecutar():
    with crear_sesion() as sesion:
        bitacoras = ArchivoBitacoraRepositorio(sesion).listar_extraidos_sin_enviar()
        clientes = ClienteRepositorio(sesion).listar_activos()
        xmls = []

        for bitacora in bitacoras:
            ruta = Path(bitacora.archivo_bitacora_ruta_extraccion)
            xmls.extend(ruta.rglob("*.xml"))

        if not xmls:
            print("No se encontraron archivos XML para enviar.")
            return

        if not clientes:
            print("No existen clientes activos para enviar los XML.")
            return

        for cliente in clientes:
            enviar_xmls(cliente.cliente_email, cliente.cliente_nombre, xmls)
            print(f"[ENVIADO] {cliente.cliente_email}")

        for bitacora in bitacoras:
            bitacora.archivo_bitacora_envio_ok = True

        sesion.commit()
