import html
import smtplib
import ssl
from datetime import datetime
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
    documentos = "\n".join(f"- {nombre}" for _, nombre in adjuntos)
    return (
        f"Hola {nombre_cliente},\n\n"
        "Se adjuntan los comprobantes electrónicos XML procesados "
        "por el bot de facturas.\n\n"
        f"Cantidad de XML adjuntos: {len(adjuntos)}\n\n"
        f"Documentos:\n{documentos}\n\n"
        "Este correo fue generado automáticamente. "
        "Por favor, no responda a este mensaje.\n\n"
        "Saludos,\n"
        "Bot de Facturas"
    )


def crear_contenido_html(nombre_cliente, adjuntos):
    filas = "".join(
        "<tr>"
        f"<td style='padding:8px;border-bottom:1px solid #e5e7eb'>{indice}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #e5e7eb'>{html.escape(nombre)}</td>"
        "</tr>"
        for indice, (_, nombre) in enumerate(adjuntos, start=1)
    )
    fecha = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M")

    return (
        "<html><body style='font-family:Arial,sans-serif;color:#1f2937'>"
        "<div style='max-width:680px;margin:auto;border:1px solid #e5e7eb;"
        "border-radius:8px;overflow:hidden'>"
        "<div style='background:#17365d;color:white;padding:20px'>"
        "<h2 style='margin:0'>Entrega de comprobantes XML</h2>"
        "</div>"
        "<div style='padding:24px'>"
        f"<p>Hola <strong>{html.escape(nombre_cliente)}</strong>,</p>"
        "<p>Se adjuntan los comprobantes electrónicos XML procesados "
        "por el bot de facturas.</p>"
        "<div style='background:#f3f4f6;padding:14px;border-radius:6px;margin:20px 0'>"
        f"<strong>XML adjuntos:</strong> {len(adjuntos)}<br>"
        f"<strong>Fecha de procesamiento:</strong> {fecha}"
        "</div>"
        "<table style='width:100%;border-collapse:collapse'>"
        "<thead><tr style='background:#f9fafb'>"
        "<th style='padding:8px;text-align:left'>#</th>"
        "<th style='padding:8px;text-align:left'>Documento XML</th>"
        "</tr></thead>"
        f"<tbody>{filas}</tbody>"
        "</table>"
        "<p style='margin-top:24px;font-size:12px;color:#6b7280'>"
        "Este correo fue generado automáticamente. "
        "Por favor, no responda a este mensaje."
        "</p>"
        "<p>Saludos,<br><strong>Bot de Facturas</strong></p>"
        "</div></div></body></html>"
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
