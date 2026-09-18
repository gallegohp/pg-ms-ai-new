"""
Servidor MCP para PulseGym IA - herramientas de operación y analítica del gimnasio.

Expone como herramientas MCP los endpoints de:
- pg-ms-operation: equipos, asistencias y proveedores (ver tools/equipos.py,
  tools/asistencias.py, tools/proveedores.py).
- pg-ms-reports: ingresos (dinero), mora y afluencia, entradas físicas
  (ver tools/reportes.py).

Optimizado para minimizar el consumo de tokens del LLM.

Autenticación (ver http_client.py):
- Auto-login contra pg-ms-auth usando MCP_SERVICE_EMAIL / MCP_SERVICE_PASSWORD.
- El JWT se renueva automáticamente cuando está por expirar (o al recibir 401).
"""

import sys

from mcp.server.fastmcp import FastMCP

from .config import API_BASE, AUTH_LOGIN_PATH, HOST, MCP_SERVICE_EMAIL, MCP_SERVICE_PASSWORD, PORT, TRANSPORT
from .tools import register_all


def create_server() -> FastMCP:
    server = FastMCP(
        name="PulseGymAISimulator",
        instructions="Herramientas para gestionar equipos, asistencias y proveedores de PulseGym.",
        host=HOST,
        port=PORT,
    )
    register_all(server)
    return server


# -------------------------------------------------------------
# Entry point
# -------------------------------------------------------------
def main():
    if not MCP_SERVICE_EMAIL or not MCP_SERVICE_PASSWORD:
        print("⚠️  MCP_SERVICE_EMAIL / MCP_SERVICE_PASSWORD vacíos: el auto-login fallará.")
    print(f"🌐 Backend PulseGym: {API_BASE}")
    print(f"🔑 Login endpoint: {API_BASE}{AUTH_LOGIN_PATH}")

    server = create_server()
    print(f"Iniciando servidor MCP '{server.name}' en http://{HOST}:{PORT} (transporte: {TRANSPORT})...")

    if TRANSPORT == "sse":
        server.run(transport="sse")
    elif TRANSPORT == "streamable-http":
        server.run(transport="streamable-http")
    elif TRANSPORT == "stdio":
        server.run(transport="stdio")
    else:
        print(f"_____Transporte '{TRANSPORT}' no válido. Opciones: sse, streamable-http, stdio_____")
        sys.exit(1)


if __name__ == "__main__":
    main()
