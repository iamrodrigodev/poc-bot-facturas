import tempfile
import unittest
from pathlib import Path

from app.services.correo_servicio import crear_contenido_html, preparar_xmls


class CorreoServicioPruebas(unittest.TestCase):
    def test_prepara_nombres_unicos_por_origen(self):
        with tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            primero = carpeta / "zip-uno" / "factura.xml"
            segundo = carpeta / "zip-dos" / "factura.xml"
            primero.parent.mkdir()
            segundo.parent.mkdir()
            primero.write_text("<xml />", encoding="utf-8")
            segundo.write_text("<xml />", encoding="utf-8")

            adjuntos = preparar_xmls([primero, segundo])
            nombres = [nombre for _, nombre in adjuntos]

            self.assertEqual(
                nombres,
                ["zip-dos_factura.xml", "zip-uno_factura.xml"],
            )

    def test_html_incluye_cliente_y_cantidad(self):
        adjuntos = [(Path("factura.xml"), "zip_factura.xml")]
        contenido = crear_contenido_html("Practicante GTI 22", adjuntos)

        self.assertIn("Practicante GTI 22", contenido)
        self.assertIn("XML adjuntos:</strong> 1", contenido)
        self.assertIn("zip_factura.xml", contenido)


if __name__ == "__main__":
    unittest.main()
