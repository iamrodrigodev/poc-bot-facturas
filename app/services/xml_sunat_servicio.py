import hashlib
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from defusedxml import ElementTree


ESPACIOS_NOMBRE = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def obtener_texto(raiz, ruta):
    elemento = raiz.find(ruta, ESPACIOS_NOMBRE)
    return elemento.text.strip() if elemento is not None and elemento.text else None


def obtener_ruc(raiz, parte):
    ruta = (
        f"cac:{parte}/cac:Party/cac:PartyIdentification/"
        "cbc:ID[@schemeID='6']"
    )
    return obtener_texto(raiz, ruta)


def calcular_hash(ruta_xml):
    calculador = hashlib.sha256()

    with Path(ruta_xml).open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            calculador.update(bloque)

    return calculador.hexdigest()


def convertir_fecha(valor):
    return date.fromisoformat(valor) if valor else None


def convertir_decimal(valor):
    try:
        return Decimal(valor) if valor else None
    except InvalidOperation:
        return None


def analizar_xml_sunat(ruta_xml):
    ruta_xml = Path(ruta_xml)
    datos = {
        "xml_hash_sha256": calcular_hash(ruta_xml),
        "xml_numero_documento": None,
        "xml_tipo_documento": None,
        "xml_fecha_emision": None,
        "xml_moneda": None,
        "xml_importe_total": None,
        "xml_ruc_emisor": None,
        "xml_ruc_receptor": None,
        "xml_ruta_fisica": str(ruta_xml.resolve()),
        "xml_procesado_ok": False,
        "xml_detalle": None,
    }

    try:
        raiz = ElementTree.parse(ruta_xml).getroot()
        datos.update(
            {
                "xml_numero_documento": obtener_texto(raiz, "cbc:ID"),
                "xml_tipo_documento": obtener_texto(raiz, "cbc:InvoiceTypeCode"),
                "xml_fecha_emision": convertir_fecha(
                    obtener_texto(raiz, "cbc:IssueDate"),
                ),
                "xml_moneda": obtener_texto(raiz, "cbc:DocumentCurrencyCode"),
                "xml_importe_total": convertir_decimal(
                    obtener_texto(
                        raiz,
                        "cac:LegalMonetaryTotal/cbc:PayableAmount",
                    ),
                ),
                "xml_ruc_emisor": obtener_ruc(raiz, "AccountingSupplierParty"),
                "xml_ruc_receptor": obtener_ruc(raiz, "AccountingCustomerParty"),
            },
        )
        datos["xml_procesado_ok"] = bool(
            datos["xml_numero_documento"]
            and datos["xml_ruc_emisor"]
            and datos["xml_ruc_receptor"],
        )
        datos["xml_detalle"] = (
            "XML UBL SUNAT procesado correctamente"
            if datos["xml_procesado_ok"]
            else "XML sin datos SUNAT obligatorios"
        )
    except Exception as error:
        datos["xml_detalle"] = str(error)

    return datos
