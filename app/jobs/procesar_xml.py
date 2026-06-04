import xml.etree.ElementTree as ET
from pathlib import Path

from app.database.transacciones import unidad_trabajo
from app.repositories.archivo_bitacora_repositorio import ArchivoBitacoraRepositorio
from app.repositories.archivo_xml_repositorio import ArchivoXmlRepositorio
from app.utils.logs import obtener_registrador


registrador = obtener_registrador("job.procesar_xml")

def extraer_datos_xml(ruta_xml):
    try:
        arbol = ET.parse(ruta_xml)
        raiz = arbol.getroot()
        
        rfc_emisor = None
        rfc_receptor = None
        uuid = None
        
        
        for elemento in raiz.iter():
            tag = elemento.tag.split("}")[-1] if "}" in elemento.tag else elemento.tag
            
            if tag == "Emisor":
                rfc_emisor = elemento.attrib.get("Rfc", rfc_emisor)
            elif tag == "Receptor":
                rfc_receptor = elemento.attrib.get("Rfc", rfc_receptor)
            elif tag == "TimbreFiscalDigital":
                uuid = elemento.attrib.get("UUID", uuid)
                
        return uuid, rfc_emisor, rfc_receptor
    except Exception as e:
        registrador.error(f"Error parseando XML {ruta_xml}: {e}")
        return None, None, None


def ejecutar():
    with unidad_trabajo() as sesion:
        bitacoras = ArchivoBitacoraRepositorio(sesion).listar_extraidos_sin_enviar()
        
    for bitacora in bitacoras:
        ruta_extraccion = Path(bitacora.archivo_bitacora_ruta_extraccion)
        if not ruta_extraccion.exists():
            continue
            
        xmls_procesados = 0
        with unidad_trabajo() as sesion:
            repositorio_xml = ArchivoXmlRepositorio(sesion)
            
            for ruta_xml in ruta_extraccion.rglob("*.xml"):
                ruta_fisica = str(ruta_xml)
                
                
                existente = repositorio_xml.obtener_por_ruta(ruta_fisica)
                if existente:
                    continue
                    
                uuid, rfc_emisor, rfc_receptor = extraer_datos_xml(ruta_xml)
                
                
                repositorio_xml.crear(
                    archivo_bitacora_id=bitacora.archivo_bitacora_id,
                    xml_uuid=uuid,
                    xml_rfc_emisor=rfc_emisor,
                    xml_rfc_receptor=rfc_receptor,
                    xml_ruta_fisica=ruta_fisica,
                    xml_procesado_ok=True
                )
                xmls_procesados += 1
                
        if xmls_procesados > 0:
            registrador.info(
                f"Procesados {xmls_procesados} XMLs para la bitácora {bitacora.archivo_bitacora_id}"
            )
