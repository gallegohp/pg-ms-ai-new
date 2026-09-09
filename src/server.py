"""
Servidor MCP para PulseGym IA - herramientas de rutina y plan nutricional
"""
import sys
from src.main import HOST, PORT
from src.tools.nutricion import generar_plan_simulado
from src.tools.rutina import generar_rutina_simulada
from src.main import TRANSPORT
from starlette.responses import JSONResponse
from mcp_types import Request
from ast import Dict
from typing import Any
from mcp.server import MCPServer

from dotenv import load_dotenv

#Cargar variables de entorno
load_dotenv()



def create_server() -> MCPServer:
    server = MCPServer(
        name = "PulseGymAISimulator",
        version = "1.0.0",
        description = "Servidor MCP simulador de la IA para pruebas con antigravity",
        instructions = "Este servidor devuelve datos simulados. Pruebas de integracion"
    )

    # Herramientas: generar_rutinas
    @server.tool(
        name="generar_rutina",
        description=(
            "generar una rutina de entretenimiento simulada "
            "Recibe un contexto con datos del socio y devuelve una rutina de ejemplo"
        ),
    )
    async def generar_rutina(contexto: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[MCP tool] generar_rutina llamado para {contexto.get('nombre', 'socio')}")
        return generar_rutina_simulada(contexto)

    # Herramienta: generar plan nutricional 
    @server.tool(
        name="generar_rutina",
        description=(
            "generar un plan nutricinal simulado"
            "recibe un contexto con los datos del socio y devuelve un plan de ejemplo"
        ),
    )
    async def generar_rutina_nutricional(contexto: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[MCP tool] generar_plan_nutricional llamado para {contexto.get('nombre', 'socio')}")
        return generar_plan_simulado(contexto)

    #ruta de la raiz informativa del servidor
    @server.custom_route("/", methods=["GET"])
    async def root_handler(request:Request) -> JSONResponse:
        return JSONResponse({
            "name" : server.name,
            "version" : server.version,
            "status" : "online",
            "transport" : TRANSPORT,
            "endpoints" : {
                "sse" : "/sse",
                "messages" : "/messages/",
                "streamable_http" : "/mcp"
            },
            "available_tools": ["generar_rutina", "generar_plan_nutricional"],
        })
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
    
