import html
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from app.config.ajustes import ajustes


def crear_nombre_adjunto(ruta_xml):
    origen = ruta_xml.parent.name
    return f"{origen}_{ruta_xml.name}"


def preparar_xmls(rutas_xml):
    adjuntos = []
    nombres = set()

    for ruta_xml in sorted({Path(ruta).resolve() for ruta in rutas_xml}):
        if not ruta_xml.is_file() or ruta_xml.suffix.lower() != ".xml":
            continue

        nombre = crear_nombre_adjunto(ruta_xml)

        if nombre in nombres:
            continue

        nombres.add(nombre)
        adjuntos.append((ruta_xml, nombre))

    return adjuntos


def crear_contenido_texto(nombre_cliente, adjuntos):
    return (
        "Aviso: Correo Electrónico Externo\n"
        "Verifica la dirección del remitente antes de acceder a enlaces o abrir archivos adjuntos. Si tienes dudas, notifica a Seguridad de la Información\n\n"
        f"Hola {nombre_cliente},\n\n"
        "Se adjuntan los archivos XML procesados por el bot de prueba.\n\n"
        f"Cantidad de XML adjuntos: {len(adjuntos)}\n\n"
        "Saludos,\n"
        "Bot de Facturas"
    )


def crear_contenido_html(nombre_cliente, adjuntos):
    return (
        "<html><body>"
        "<p><strong>[Aviso: Correo Electrónico Externo]</strong><br>"
        "Verifica la dirección del remitente antes de acceder a enlaces o abrir archivos adjuntos. Si tienes dudas, notifica a Seguridad de la Información</p>"
        f"<p>Hola {html.escape(nombre_cliente)},</p>"
        "<p>Se adjuntan los archivos XML procesados por el bot de prueba.</p>"
        f"<p>Cantidad de XML adjuntos: {len(adjuntos)}</p>"
        "<p>Saludos,<br>Bot de Facturas</p>"
        "</body></html>"
    )


def enviar_xmls(destinatario, nombre_cliente, rutas_xml):
    if not ajustes.smtp_username or not ajustes.smtp_password:
        raise ValueError("Las credenciales SMTP no están configuradas")

    adjuntos = preparar_xmls(rutas_xml)

    if not adjuntos:
        raise ValueError("No existen archivos XML válidos para enviar")

    mensaje = EmailMessage()
    mensaje["From"] = f"Bot de Facturas <{ajustes.smtp_username}>"
    mensaje["To"] = destinatario
    mensaje["Subject"] = f"Comprobantes XML procesados ({len(adjuntos)})"
    mensaje.set_content(crear_contenido_texto(nombre_cliente, adjuntos))
    mensaje.add_alternative(
        crear_contenido_html(nombre_cliente, adjuntos),
        subtype="html",
    )

    for ruta_xml, nombre_adjunto in adjuntos:
        mensaje.add_attachment(
            ruta_xml.read_bytes(),
            maintype="application",
            subtype="xml",
            filename=nombre_adjunto,
        )

    with smtplib.SMTP(ajustes.smtp_server, ajustes.smtp_port, timeout=60) as servidor:
        servidor.starttls(context=ssl.create_default_context())
        servidor.login(ajustes.smtp_username, ajustes.smtp_password)
        servidor.send_message(mensaje)
