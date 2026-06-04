from pathlib import Path

from selenium.webdriver.common.by import By

from app.services.navegador_servicio import crear_navegador


def obtener_archivos_zip(url):
    navegador = crear_navegador()

    try:
        navegador.get(url)
        enlaces = navegador.find_elements(By.XPATH, "//a[contains(@href,'.zip')]")
        archivos = []

        for enlace in enlaces:
            url_zip = enlace.get_attribute("href")

            if not url_zip:
                continue

            nombre = enlace.text.strip() or Path(url_zip.split("?")[0]).name
            archivos.append({
                "nombre": nombre[:500],
                "url": url_zip,
            })

        return archivos
    finally:
        navegador.quit()
