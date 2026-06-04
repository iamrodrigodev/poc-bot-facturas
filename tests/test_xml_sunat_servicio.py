import tempfile
import unittest
from pathlib import Path

from app.services.xml_sunat_servicio import analizar_xml_sunat


XML_SUNAT = """<?xml version="1.0" encoding="utf-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
 <cbc:ID>F001-00001234</cbc:ID>
 <cbc:IssueDate>2026-06-03</cbc:IssueDate>
 <cbc:InvoiceTypeCode>01</cbc:InvoiceTypeCode>
 <cbc:DocumentCurrencyCode>PEN</cbc:DocumentCurrencyCode>
 <cac:AccountingSupplierParty><cac:Party><cac:PartyIdentification>
 <cbc:ID schemeID="6">20123456789</cbc:ID>
 </cac:PartyIdentification></cac:Party></cac:AccountingSupplierParty>
 <cac:AccountingCustomerParty><cac:Party><cac:PartyIdentification>
 <cbc:ID schemeID="6">20987654321</cbc:ID>
 </cac:PartyIdentification></cac:Party></cac:AccountingCustomerParty>
 <cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="PEN">118.00</cbc:PayableAmount>
 </cac:LegalMonetaryTotal>
</Invoice>"""


class XmlSunatServicioPruebas(unittest.TestCase):
    def test_extrae_datos_de_factura_ubl_sunat(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "factura.xml"
            ruta.write_text(XML_SUNAT, encoding="utf-8")

            datos = analizar_xml_sunat(ruta)

        self.assertTrue(datos["xml_procesado_ok"])
        self.assertEqual(datos["xml_numero_documento"], "F001-00001234")
        self.assertEqual(datos["xml_ruc_emisor"], "20123456789")
        self.assertEqual(datos["xml_ruc_receptor"], "20987654321")
        self.assertEqual(str(datos["xml_importe_total"]), "118.00")

    def test_xml_invalido_no_se_marca_procesado(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "invalido.xml"
            ruta.write_text("<xml />", encoding="utf-8")

            datos = analizar_xml_sunat(ruta)

        self.assertFalse(datos["xml_procesado_ok"])
        self.assertEqual(datos["xml_detalle"], "XML sin datos SUNAT obligatorios")


if __name__ == "__main__":
    unittest.main()
