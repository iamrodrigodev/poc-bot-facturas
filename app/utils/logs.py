import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from uuid import uuid4

from app.config.ajustes import ajustes


IDENTIFICADOR_EJECUCION = str(uuid4())
ATRIBUTOS_LOG = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
}


class FormateadorJson(logging.Formatter):
    def format(self, registro):
        datos = {
            "fecha_hora": datetime.fromtimestamp(
                registro.created,
                tz=timezone.utc,
            ).astimezone().isoformat(),
            "nivel": registro.levelname,
            "ejecucion_id": IDENTIFICADOR_EJECUCION,
            "modulo": registro.name,
            "mensaje": registro.getMessage(),
        }
        contexto = {
            clave: valor
            for clave, valor in registro.__dict__.items()
            if clave not in ATRIBUTOS_LOG and not clave.startswith("_")
        }

        if contexto:
            datos["contexto"] = contexto

        if registro.exc_info:
            datos["excepcion"] = self.formatException(registro.exc_info)

        return json.dumps(datos, ensure_ascii=False, default=str)


def configurar_logs():
    registrador_raiz = logging.getLogger()

    if registrador_raiz.handlers:
        return

    ajustes.carpeta_logs.mkdir(parents=True, exist_ok=True)
    registrador_raiz.setLevel(logging.INFO)

    manejador_archivo = RotatingFileHandler(
        ajustes.carpeta_logs / "bot_facturas.jsonl",
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    manejador_archivo.setFormatter(FormateadorJson())

    manejador_consola = logging.StreamHandler()
    manejador_consola.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
    )

    registrador_raiz.addHandler(manejador_archivo)
    registrador_raiz.addHandler(manejador_consola)


def obtener_registrador(nombre):
    configurar_logs()
    return logging.getLogger(nombre)
