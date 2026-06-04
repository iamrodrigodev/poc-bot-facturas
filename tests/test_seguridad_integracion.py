import tempfile
import threading
import unittest
from pathlib import Path
from time import sleep
from zipfile import ZipFile

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.database.bloqueos import bloquear_job
from app.database.sesion import motor
from app.database.transacciones import unidad_trabajo
from app.models.cliente import Cliente
from app.repositories.cliente_repositorio import ClienteRepositorio
from app.services.extraccion_servicio import extraer_archivo_zip
from app.services.url_servicio import validar_url_publica


class SeguridadIntegracionPruebas(unittest.TestCase):
    def test_transaccion_revierte_cambios(self):
        nombre = "cliente_rollback_prueba"

        with self.assertRaises(RuntimeError):
            with unidad_trabajo() as sesion:
                sesion.add(
                    Cliente(
                        cliente_nombre=nombre,
                        cliente_email="rollback@example.com",
                    ),
                )
                sesion.flush()
                raise RuntimeError("fallo controlado")

        with unidad_trabajo() as sesion:
            encontrados = [
                cliente
                for cliente in ClienteRepositorio(sesion).listar_activos()
                if cliente.cliente_nombre == nombre
            ]

        self.assertEqual(encontrados, [])

    def test_base_rechaza_bitacora_inconsistente(self):
        with self.assertRaises(DBAPIError), motor.begin() as conexion:
            pagina_fuente_id = conexion.execute(
                text(
                    "SELECT TOP 1 pagina_fuente_id "
                    "FROM configuracion.pagina_fuente"
                ),
            ).scalar_one()
            archivo_tipo_id = conexion.execute(
                text(
                    "INSERT INTO operacion.archivo_tipo "
                    "(pagina_fuente_id, archivo_tipo_nombre, archivo_tipo_url, "
                    "archivo_tipo_requerido, fecha_creacion) "
                    "OUTPUT INSERTED.archivo_tipo_id "
                    "VALUES (:pagina, 'prueba', :url, 0, GETDATE())"
                ),
                {"pagina": pagina_fuente_id, "url": "https://example.com/prueba.zip"},
            ).scalar_one()
            conexion.execute(
                text(
                    "INSERT INTO operacion.archivo_bitacora "
                    "(archivo_tipo_id, archivo_bitacora_fecha_hora, "
                    "archivo_bitacora_descarga_ok, "
                    "archivo_bitacora_descompresion_ok, archivo_bitacora_envio_ok) "
                    "VALUES (:archivo, GETDATE(), 1, 0, 0)"
                ),
                {"archivo": archivo_tipo_id},
            )

    def test_bloqueo_impide_dos_ejecuciones(self):
        iniciado = threading.Event()
        resultados = []

        def primera_ejecucion():
            with bloquear_job("prueba_concurrencia"):
                resultados.append("primera")
                iniciado.set()
                sleep(1)

        def segunda_ejecucion():
            iniciado.wait()

            try:
                with bloquear_job("prueba_concurrencia"):
                    resultados.append("segunda")
            except RuntimeError:
                resultados.append("rechazada")

        primero = threading.Thread(target=primera_ejecucion)
        segundo = threading.Thread(target=segunda_ejecucion)
        primero.start()
        segundo.start()
        primero.join()
        segundo.join()

        self.assertEqual(sorted(resultados), ["primera", "rechazada"])

    def test_url_privada_es_rechazada(self):
        with self.assertRaises(ValueError):
            validar_url_publica("http://127.0.0.1/archivo.zip")

    def test_zip_con_ruta_peligrosa_es_rechazado(self):
        with tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            ruta_zip = carpeta / "peligroso.zip"

            with ZipFile(ruta_zip, "w") as archivo_zip:
                archivo_zip.writestr("../fuera.xml", "<xml />")

            with self.assertRaises(ValueError):
                extraer_archivo_zip(ruta_zip, carpeta / "destino")


if __name__ == "__main__":
    unittest.main()
