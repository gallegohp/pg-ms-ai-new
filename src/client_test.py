import asyncio
import os
import sys

from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

DEFAULT_HOST = os.getenv("HOST", "127.0.0.1")
DEFAULT_PORT = os.getenv("PORT", "8000")
DEFAULT_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"


async def run_client_tests(base_url: str = DEFAULT_URL) -> bool:
    """Ejecuta pruebas sobre las herramientas de PulseGym en el servidor MCP."""
    mcp_endpoint = f"{base_url.rstrip('/')}/mcp"
    print(f"\n🚀 Conectando al servidor MCP en {mcp_endpoint}...")

    try:
        async with streamable_http_client(mcp_endpoint) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                print("🤝 Realizando handshake de inicialización...")
                init_result = await session.initialize()
                print(f"✅ Servidor conectado: {init_result.server_info.name} (v{init_result.server_info.version})")

                print("\n📋 Listando herramientas disponibles...")
                tools_response = await session.list_tools()
                for tool in tools_response.tools:
                    print(f"  - 🔧 {tool.name}: {tool.description}")

                print("\n🧪 Ejecutando pruebas sobre los endpoints de PulseGym...")

                # 1. Probar herramienta obtener_equipos
                print("\n1️⃣ Probando 'obtener_equipos'...")
                equipos_res = await session.call_tool("obtener_equipos", {})
                print("Resultado Equipos:")
                print(equipos_res.content[0].text if equipos_res.content else equipos_res)

                # 2. Probar herramienta obtener_historial_accesos
                print("\n2️⃣ Probando 'obtener_historial_accesos'...")
                accesos_res = await session.call_tool("obtener_historial_accesos", {})
                print("Resultado Historial Accesos:")
                print(accesos_res.content[0].text if accesos_res.content else accesos_res)

                print("\n🎉 ¡Pruebas finalizadas con éxito!")
                return True

    except Exception as exc:
        print(f"\n❌ Error durante la ejecución de las pruebas: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def main() -> None:
    server_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    success = asyncio.run(run_client_tests(server_url))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()