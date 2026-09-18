"""
Configuración del servidor MCP: variables de entorno, timeouts y los
enums reales del backend (EnumEstado, EnumUrgencia, tipos de acceso).
"""

import os

from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
TRANSPORT = os.getenv("TRANSPORT", "sse").lower().strip()
API_BASE = os.getenv("PULSEGYM_API_BASE", "https://api.pulsegym.uk").rstrip("/")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "15"))

MAX_LIST_ITEMS = int(os.getenv("MAX_LIST_ITEMS", "20"))
MAX_STRING_CHARS = int(os.getenv("MAX_STRING_CHARS", "500"))

# -------------------------------------------------------------
# Credenciales de servicio (auto-login)
# -------------------------------------------------------------
MCP_SERVICE_EMAIL = os.getenv("MCP_SERVICE_EMAIL", "")
MCP_SERVICE_PASSWORD = os.getenv("MCP_SERVICE_PASSWORD", "")
AUTH_LOGIN_PATH = os.getenv("AUTH_LOGIN_PATH", "/pg-ms-auth/auth/login")

# Enums reales del backend (EnumEstado y EnumUrgencia)
ESTADOS_EQUIPO = {"OPERATIVO", "MANTENIMIENTO", "FUERA_DE_SERVICIO", "RETIRADO"}
URGENCIAS_FALLA = {"BAJA", "MEDIA", "ALTA", "CRITICA"}
TIPOS_ACCESO = {"APP", "QR", "MANUAL"}

# Texto de enums para meter en las descripciones de las tools
ENUM_ESTADOS = ", ".join(sorted(ESTADOS_EQUIPO))
ENUM_URGENCIAS = ", ".join(sorted(URGENCIAS_FALLA))
ENUM_ACCESOS = ", ".join(sorted(TIPOS_ACCESO))
