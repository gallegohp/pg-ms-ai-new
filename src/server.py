"""
Servidor MCP para PulseGym IA - herramientas de rutina y plan nutricional
"""
import sys
import httpx
import os

from src.main import HOST, PORT
# pyrefly: ignore [missing-import]
from src.main import TRANSPORT
from starlette.responses import JSONResponse
from mcp_types import Request
from ast import Dict
from typing import Any
from mcp.server import MCPServer

from dotenv import load_dotenv

#Cargar variables de entorno
load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
TRANSPORT = os.getenv("TRANSPORT", "sse").lower().strip()

BASE_HEADERS = {
    "Authorization": f"Bearer {os.getenv('AUTH_TOKEN')}",
    "Content-Type": "application/json",
}


def create_server() -> MCPServer:
    server = MCPServer(
        name = "PulseGymAISimulator",
        version = "1.0.0",
        description = "Servidor MCP simulador de la IA para pruebas con antigravity0''0",
        instructions = "Este servidor devuelve datos simulados. Pruebas de integracion"
    )

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
    return server

    

def main():
    server = create_server()
    print(f"Iniciando servidor MCP '{server.name}' v{server.version} en http://{HOST}:{PORT} (transporte: {TRANSPORT})...")

    if TRANSPORT == "sse":
        server.run(transport="sse", host=HOST, port=PORT)
    elif TRANSPORT == "streamable-http":
        server.run(transport="streamable-http", host=HOST, port=PORT)
    elif TRANSPORT == "stdio":
        server.run(transport="stdio")
    else:
        print(f"_____Transporte '{TRANSPORT}' no válido. Opciones: sse, streamable-http, stdio_____")
        sys.exit(1)

if __name__ == "__main__":
    main()  
    
