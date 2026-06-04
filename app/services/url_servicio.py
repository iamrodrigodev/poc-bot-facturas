import ipaddress
import socket
from urllib.parse import urlsplit, urlunsplit


def validar_url_publica(url):
    partes = urlsplit(url)

    if partes.scheme not in {"http", "https"} or not partes.hostname:
        raise ValueError("La URL debe utilizar HTTP o HTTPS")

    for resultado in socket.getaddrinfo(partes.hostname, partes.port):
        direccion = ipaddress.ip_address(resultado[4][0])

        if not direccion.is_global:
            raise ValueError("La URL apunta a una red privada o reservada")

    return url


def ocultar_parametros_url(url):
    partes = urlsplit(url)
    return urlunsplit((partes.scheme, partes.netloc, partes.path, "", ""))
