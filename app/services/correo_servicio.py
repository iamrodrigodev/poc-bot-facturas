import smtplib
import ssl
from email.message import EmailMessage

from app.config.ajustes import ajustes


def enviar_xmls(destinatario, nombre_cliente, rutas_xml):
    if not ajustes.smtp_username or not ajustes.smtp_password:
        raise ValueError("Las credenciales SMTP no están configuradas")

    mensaje = EmailMessage()
    mensaje["From"] = ajustes.smtp_username
    mensaje["To"] = destinatario
    mensaje["Subject"] = "PoC Bot - XML procesados"
    mensaje.set_content(
        f"Hola {nombre_cliente},\n\n"
        f"Se adjuntan {len(rutas_xml)} archivos XML procesados.\n",
    )

    for ruta_xml in rutas_xml:
        mensaje.add_attachment(
            ruta_xml.read_bytes(),
            maintype="application",
            subtype="xml",
            filename=ruta_xml.name,
        )

    with smtplib.SMTP(ajustes.smtp_server, ajustes.smtp_port, timeout=60) as servidor:
        servidor.starttls(context=ssl.create_default_context())
        servidor.login(ajustes.smtp_username, ajustes.smtp_password)
        servidor.send_message(mensaje)
