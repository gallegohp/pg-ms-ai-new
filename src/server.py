"""
Servidor MCP para PulseGym IA - herramientas de rutina y plan nutricional
"""
import os

from dotenv import load_dotenv

#Cargar variables de entorno
load_dotenv()

#Configuracion del servidor
HOST = os.gatenv("MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_PORT", "8087"))
TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http").lower().strip()
