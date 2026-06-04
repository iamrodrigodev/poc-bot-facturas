from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import requests

from app.services.url_servicio import validar_url_publica


class ZipLinkParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.archivos = []
        self.in_a = False
        self.current_href = None
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href" and value and value.lower().endswith(".zip"):
                    self.in_a = True
                    self.current_href = urljoin(self.base_url, value)
                    self.current_text = ""

    def handle_data(self, data):
        if self.in_a:
            self.current_text += data

    def handle_endtag(self, tag):
        if tag == "a" and self.in_a:
            nombre_texto = self.current_text.strip()
            if not nombre_texto or len(nombre_texto) < 5 or not any(c.isalpha() for c in nombre_texto):
                nombre = Path(self.current_href.split("?")[0]).name
            else:
                nombre = nombre_texto

            self.archivos.append({
                "nombre": nombre[:500],
                "url": self.current_href,
            })
            self.in_a = False
            self.current_href = None


def obtener_archivos_zip(url):
    validar_url_publica(url)
    
    respuesta = requests.get(url, timeout=30)
    respuesta.encoding = "utf-8"
    respuesta.raise_for_status()
    
    parser = ZipLinkParser(base_url=url)
    parser.feed(respuesta.text)
    
    for archivo in parser.archivos:
        validar_url_publica(archivo["url"])
        
    return parser.archivos
