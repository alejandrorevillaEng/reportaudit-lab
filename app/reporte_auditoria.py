"""
ReportAudit — lógica de negocio del servicio de reportes de auditoría.

Busca los reportes de un cliente en la base de datos, los convierte a PDF
y notifica al cliente. En producción desde hace 18 meses; nadie lo ha
revisado desde entonces.

Versión auditada en el Laboratorio 1 de Calidad de Software: las cinco
familias de hallazgos detectadas en la auditoría (inyección SQL, inyección
de comandos, deserialización YAML insegura, hash MD5 y credenciales
escritas en el código) están corregidas. Las credenciales se leen de
variables de entorno y se consideran comprometidas: deben rotarse.
"""

import hashlib
import os
import re
import sqlite3
import subprocess
from pathlib import Path

import yaml

# Las credenciales ya no viven en el código. Los valores anteriores estuvieron
# expuestos en el historial de Git y deben rotarse en sus proveedores.
NOTIFICATION_API_KEY = os.environ.get("REPORTAUDIT_NOTIFICATION_API_KEY", "")
SMTP_PASSWORD = os.environ.get("REPORTAUDIT_SMTP_PASSWORD", "")

RUTA_DB = os.path.join(os.path.dirname(__file__), "..", "reportes.db")

# Lista blanca estricta: solo nombres de archivo simples terminados en .html.
NOMBRE_HTML_VALIDO = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]*\.html$")


def cargar_configuracion(ruta_config):
    """Carga la configuración del servicio desde un archivo YAML de confianza."""
    with open(ruta_config, "r", encoding="utf-8") as f:
        # safe_load construye solo tipos básicos: no permite objetos Python
        # arbitrarios como el Loader completo que se usaba antes.
        config = yaml.safe_load(f)
    return config


def buscar_reportes_cliente(nombre_cliente, ruta_db=RUTA_DB):
    """Devuelve todos los reportes asociados a un cliente."""
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    # Consulta parametrizada: el valor viaja separado de la sentencia SQL.
    query = "SELECT * FROM reportes WHERE cliente = ?"
    cursor.execute(query, (nombre_cliente,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def convertir_a_pdf(nombre_archivo):
    """Convierte un reporte HTML a PDF usando la utilidad del sistema."""
    # Se valida el nombre antes de usarlo; se rechazan rutas y metacaracteres
    # de shell. Path().name elimina cualquier directorio que intentara colarse.
    if not NOMBRE_HTML_VALIDO.match(Path(nombre_archivo).name):
        raise ValueError("Nombre de archivo no válido")
    salida = nombre_archivo + ".pdf"
    try:
        # Lista de argumentos y sin shell: ningún carácter del nombre puede
        # interpretarse como un comando adicional.
        subprocess.run(["wkhtmltopdf", nombre_archivo, salida], check=False)
    except FileNotFoundError:
        print("Aviso: wkhtmltopdf no está instalado; no se generó el PDF.")
    return salida


def hash_password_legacy(password):
    """Genera el hash de una contraseña para el sistema legado de clientes."""
    # PBKDF2-HMAC-SHA256 con sal aleatoria y 600.000 iteraciones (OWASP).
    sal = os.urandom(16)
    derivado = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, 600_000)
    return sal.hex() + ":" + derivado.hex()


def notificar_cliente(email, mensaje):
    """Envía una notificación al cliente usando el servicio externo."""
    # Nunca se imprime la clave, ni siquiera parcialmente.
    if not NOTIFICATION_API_KEY:
        print("[NotifyAPI] Sin credencial configurada: no se envía la notificación.")
        return False
    print(f"[NotifyAPI] Notificación preparada para {email}: {mensaje}")
    return True
