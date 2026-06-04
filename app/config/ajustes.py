from dataclasses import dataclass
from os import getenv
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


CARPETA_BASE = Path(__file__).resolve().parents[2]
load_dotenv(CARPETA_BASE / ".env")


def obtener_booleano(nombre, valor_predeterminado=False):
    valor = getenv(nombre)

    if valor is None:
        return valor_predeterminado

    return valor.lower() in {"1", "true", "si", "yes"}


@dataclass(frozen=True)
class Ajustes:
    sql_server: str = getenv("sql_server", "localhost\\SQLEXPRESS")
    sql_database: str = getenv("sql_database", "poc_bot_facturas")
    sql_username: str = getenv("sql_username", "")
    sql_password: str = getenv("sql_password", "")
    sql_driver: str = getenv("sql_driver", "SQL Server")
    sql_trusted_connection: bool = obtener_booleano("sql_trusted_connection", True)
    sql_trust_server_certificate: bool = obtener_booleano(
        "sql_trust_server_certificate",
        True,
    )
    selenium_headless: bool = obtener_booleano("selenium_headless", False)
    smtp_server: str = getenv("smtp_server", "smtp.gmail.com")
    smtp_port: int = int(getenv("smtp_port", "587"))
    smtp_username: str = getenv("smtp_username", "")
    smtp_password: str = getenv("smtp_password", "")
    carpeta_downloads: Path = CARPETA_BASE / "storage" / "downloads"
    carpeta_extracted: Path = CARPETA_BASE / "storage" / "extracted"
    carpeta_logs: Path = CARPETA_BASE / "logs"

    def crear_url_sqlalchemy(self):
        parametros = [
            f"DRIVER={{{self.sql_driver}}}",
            f"SERVER={self.sql_server}",
            f"DATABASE={self.sql_database}",
            "TrustServerCertificate="
            f"{'yes' if self.sql_trust_server_certificate else 'no'}",
        ]

        if self.sql_trusted_connection:
            parametros.append("Trusted_Connection=yes")
        else:
            parametros.extend([
                f"UID={self.sql_username}",
                f"PWD={self.sql_password}",
            ])

        cadena_odbc = ";".join(parametros)
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(cadena_odbc)}"


ajustes = Ajustes()
