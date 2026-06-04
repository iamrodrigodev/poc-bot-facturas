from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from app.config.ajustes import ajustes


def crear_navegador():
    opciones = Options()

    if ajustes.selenium_headless:
        opciones.add_argument("--headless=new")

    opciones.add_argument("--start-maximized")
    navegador = webdriver.Chrome(options=opciones)
    navegador.set_page_load_timeout(60)
    return navegador
