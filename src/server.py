"""
Servidor MCP en Python con transporte HTTP (SSE) y herramientas matemáticas básicas.
La lógica de las herramientas y la configuración residen directamente en este archivo.
"""

import json
import os
import sys
import httpx
from typing import Any

from dotenv import load_dotenv
from mcp.server import MCPServer
from starlette.requests import Request
from starlette.responses import JSONResponse

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración leída desde variables de entorno (.env)
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
TRANSPORT = os.getenv("TRANSPORT", "sse").lower().strip()


BASE_HEADERS = {
    "Authorization": f"Bearer {os.getenv('AUTH_TOKEN')}",
    "Content-Type": "application/json",
}

# Creacion y configuración del servidor MCP 
def create_server() -> MCPServer:
    """Crea y configura el servidor MCP con herramientas de PulseGym."""
    server = MCPServer(
        name="PulseGymServer",
        version="1.0.0",
        description="Servidor MCP para consultar equipos e historial de accesos de PulseGym.",
        instructions="Este servidor permite obtener informacion operativa del proyecto PulseGym",
    )

    # -------------------------------------------------------------
    # 1. Obtener equipos
    # -------------------------------------------------------------
    @server.tool(
        name="obtener_equipos",
        description="Obtener la lista de todos los equipos del gimnasio y su estado operativo (Operativo, Mantenimiento, etc.).",
    )
    async def obtener_equipos() -> dict[str, Any]:
        """Consulta el endpoint /api/equipos/todos."""
        url = "https://api.pulsegym.uk/pg-ms-operation/api/equipos/todos"
        print(f"👉 [MCP Tool] Ejecutando obtener_equipos")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=BASE_HEADERS, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return {
                    "success" : False,
                    "error" : f"Error Http {response.status_code}: {response.text}",
                }
            except Exception as exc:
                return {"success": False, "error": f"Error de conexion: {str(exc)}"}
    # -------------------------------------------------------------
    # 2. Obtener historial de accesos
    # -------------------------------------------------------------
    @server.tool(
        name="obtener_historial_accesos",
        description="Obtener el historial de accesos de usuarios al gimnasio (entradas por APP, sede).",
    )
    async def obtener_historial_accesos() -> dict[str, Any]:
        """Consulta el endpoint /api/historial-accesos."""
        url = "https://api.pulsegym.uk/pg-ms-operation/api/historial-accesos"
        print(f"👉 [MCP Tool] Ejecutando obtener_historial_accesos")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=BASE_HEADERS, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return {
                    "success": False,
                    "error": f"Error HTTP {response.status_code}: {response.text}",
                }
            except Exception as exc:
                return {"success": False, "error": f"Error de conexión: {str(exc)}"}


    # -------------------------------------------------------------
    # RECURSO DE ESTADO (MCP Resource)
    # -------------------------------------------------------------
    @server.resource(
        "system://status",
        name="server_status",
        description="Estado y herramientas disponibles en el servidor MCP",
        mime_type="application/json",
    )
    def server_status() -> str:
        """Retorna un recurso JSON informativo."""
        return json.dumps(
            {
                "status": "healthy",
                "server": "PulseGymServer",
                "version": "1.0.0",
                "transport": TRANSPORT,
                "tools": ["obtener_equipos", "obtener_historial_accesos"],
            },
            indent=2,
        )

    # -------------------------------------------------------------
    # RUTA HTTP PERSONALIZADA PARA INFO/HEALTH
    # -------------------------------------------------------------
    @server.custom_route("/", methods=["GET"])
    async def root_handler(request: Request) -> JSONResponse:
        """Endpoint HTTP informativo en la raíz."""
        return JSONResponse(
            {
                "name": "MathToolsServer",
                "version": "1.0.0",
                "protocol": "Model Context Protocol (MCP)",
                "status": "online",
                "transport": TRANSPORT,
                "endpoints": {
                    "sse": "/sse",
                    "messages": "/messages/",
                    "streamable_http": "/mcp",
                },
                "available_tools": [
                    "obtener_equipos",
                    "obtener_historial_accesos",
                ],
            }
        )

    return server


def main() -> None:
    """Punto de entrada principal para ejecutar el servidor MCP."""
    server = create_server()
    print(f"🚀 Iniciando servidor MCP '{server.name}' v{server.version} en http://{HOST}:{PORT} (transporte: {TRANSPORT})...")

    if TRANSPORT == "sse":
        server.run(transport="sse", host=HOST, port=PORT)
    elif TRANSPORT == "streamable-http":
        server.run(transport="streamable-http", host=HOST, port=PORT)
    elif TRANSPORT == "stdio":
        server.run(transport="stdio")
    else:
        print(f"❌ Transporte '{TRANSPORT}' no válido. Opciones: sse, streamable-http, stdio")
        sys.exit(1)


if __name__ == "__main__":
    main()
