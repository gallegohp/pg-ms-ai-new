"""
Servidor MCP para PulseGym IA - herramientas de operación del gimnasio.

Expone como herramientas MCP los endpoints del microservicio pg-ms-operation:
equipos, asistencias y proveedores.
"""

import os
import sys

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# -------------------------------------------------------------
# Configuración
# -------------------------------------------------------------
load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
TRANSPORT = os.getenv("TRANSPORT", "sse").lower().strip()
API_BASE = os.getenv("PULSEGYM_API_BASE", "https://api.pulsegym.uk").rstrip("/")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "15"))

BASE_HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
}


# -------------------------------------------------------------
# Cliente HTTP con manejo de errores uniforme
# -------------------------------------------------------------
async def _request(method: str, path: str, **kwargs) -> dict:
    """Ejecuta una petición al backend y normaliza la respuesta."""
    url = f"{API_BASE}{path}"
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.request(
                method, url, headers=BASE_HEADERS, **kwargs
            )
    except httpx.RequestError as exc:
        return {
            "success": False,
            "error": f"Error de conexión: {exc}",
            "url": url,
        }

    if response.status_code >= 400:
        return {
            "success": False,
            "status": response.status_code,
            "error": response.text,
            "url": url,
        }

    if not response.content:
        return {"success": True, "status": response.status_code}

    try:
        return response.json()
    except ValueError:
        return {"success": True, "status": response.status_code, "raw": response.text}


# -------------------------------------------------------------
# Servidor MCP
# -------------------------------------------------------------
def create_server() -> FastMCP:
    server = FastMCP(
        name="PulseGymAISimulator",
        instructions=(
            "Servidor MCP con herramientas para gestionar equipos, asistencias "
            "y proveedores del gimnasio PulseGym. Usa estas herramientas cuando "
            "el usuario pregunte por equipos, fallas, asistencias o proveedores."
        ),
        host=HOST,      # ← host va aquí
        port=PORT,      # ← port va aquí
    )

    # =====================================================================
    # EQUIPOS
    # =====================================================================
    @server.tool(
        name="listar_equipos",
        description="Lista todos los equipos del gimnasio con su estado operativo.",
    )
    async def listar_equipos() -> dict:
        print("👉 [MCP Tool] listar_equipos")
        return await _request("GET", "/pg-ms-operation/api/equipos/todos")

    @server.tool(
        name="consultar_equipos",
        description=(
            "Consulta el inventario de equipos filtrando por estado. "
            "Estados válidos: OPERATIVO, MANTENIMIENTO, FUERA_SERVICIO."
        ),
    )
    async def consultar_equipos(estado: str) -> dict:
        print(f"👉 [MCP Tool] consultar_equipos(estado={estado})")
        return await _request(
            "POST",
            "/pg-ms-operation/api/equipos/consultar",
            json={"estado": estado},
        )

    @server.tool(
        name="actualizar_equipo",
        description=(
            "Actualiza todos los datos de un equipo existente. "
            "Requiere enviar el objeto completo del equipo."
        ),
    )
    async def actualizar_equipo(
        id: int,
        idProveedor: int,
        idSede: int,
        nombre: str,
        marca: str,
        modelo: str,
        numeroSerie: str,
        fechaAdquisicion: str,
        fechaGarantia: str,
        ubicacion: str,
        estado: str,
    ) -> dict:
        print(f"👉 [MCP Tool] actualizar_equipo(id={id})")
        body = {
            "idProveedor": idProveedor,
            "idSede": idSede,
            "nombre": nombre,
            "marca": marca,
            "modelo": modelo,
            "numeroSerie": numeroSerie,
            "fechaAdquisicion": fechaAdquisicion,
            "fechaGarantia": fechaGarantia,
            "ubicacion": ubicacion,
            "estado": estado,
        }
        return await _request(
            "PUT", f"/pg-ms-operation/api/equipos/{id}", json=body
        )

    @server.tool(
        name="reportar_falla_equipo",
        description=(
            "Reporta una falla en un equipo. "
            "Urgencias válidas: BAJA, MEDIA, ALTA."
        ),
    )
    async def reportar_falla_equipo(
        idEquipo: int,
        urgencia: str,
        descripcion: str,
    ) -> dict:
        print(f"👉 [MCP Tool] reportar_falla_equipo(idEquipo={idEquipo})")
        body = {"urgencia": urgencia, "descripcion": descripcion}
        return await _request(
            "POST",
            f"/pg-ms-operation/api/equipos/{idEquipo}/reportar-falla",
            json=body,
        )

    @server.tool(
        name="listar_reportes_falla",
        description="Consulta todas las fallas reportadas en los equipos.",
    )
    async def listar_reportes_falla() -> dict:
        print("👉 [MCP Tool] listar_reportes_falla")
        return await _request(
            "GET", "/pg-ms-operation/api/equipos/reportes-falla"
        )

    # =====================================================================
    # ASISTENCIAS
    # =====================================================================
    @server.tool(
        name="registrar_entrada",
        description=(
            "Registra la entrada de un usuario al gimnasio. "
            "Tipos de acceso válidos: APP, QR, MANUAL."
        ),
    )
    async def registrar_entrada(
        idUsuario: int,
        idSede: int,
        tipoAcceso: str,
    ) -> dict:
        print(f"👉 [MCP Tool] registrar_entrada(idUsuario={idUsuario})")
        body = {
            "idUsuario": idUsuario,
            "idSede": idSede,
            "tipoAcceso": tipoAcceso,
        }
        return await _request(
            "POST", "/pg-ms-operation/api/asistencias/entrada", json=body
        )

    @server.tool(
        name="historial_asistencia_usuario",
        description="Consulta el historial de asistencias de un usuario por su ID.",
    )
    async def historial_asistencia_usuario(idUsuario: int) -> dict:
        print(f"👉 [MCP Tool] historial_asistencia_usuario(idUsuario={idUsuario})")
        return await _request(
            "GET",
            f"/pg-ms-operation/api/asistencias/historial/usuario/{idUsuario}",
        )

    @server.tool(
        name="asistencia_por_sede",
        description="Consulta las asistencias registradas en una sede específica.",
    )
    async def asistencia_por_sede(idSede: int) -> dict:
        print(f"👉 [MCP Tool] asistencia_por_sede(idSede={idSede})")
        return await _request(
            "GET", f"/pg-ms-operation/api/asistencias/sede/{idSede}"
        )

    @server.tool(
        name="asistencia_hoy",
        description="Consulta las asistencias registradas hoy.",
    )
    async def asistencia_hoy() -> dict:
        print("👉 [MCP Tool] asistencia_hoy")
        return await _request("GET", "/pg-ms-operation/api/asistencias/hoy")

    # =====================================================================
    # PROVEEDORES
    # =====================================================================
    @server.tool(
        name="registrar_proveedor",
        description="Registra un nuevo proveedor en el sistema.",
    )
    async def registrar_proveedor(
        nombreEmpresa: str,
        contactoNombre: str,
        telefono: str,
        email: str,
    ) -> dict:
        print(f"👉 [MCP Tool] registrar_proveedor({nombreEmpresa})")
        body = {
            "nombreEmpresa": nombreEmpresa,
            "contactoNombre": contactoNombre,
            "telefono": telefono,
            "email": email,
        }
        return await _request(
            "POST", "/pg-ms-operation/api/proveedores/registrar", json=body
        )

    @server.tool(
        name="listar_proveedores",
        description="Lista todos los proveedores registrados.",
    )
    async def listar_proveedores() -> dict:
        print("👉 [MCP Tool] listar_proveedores")
        return await _request("GET", "/pg-ms-operation/api/proveedores/todos")

    @server.tool(
        name="obtener_proveedor",
        description="Obtiene los datos de un proveedor por su ID.",
    )
    async def obtener_proveedor(id: int) -> dict:
        print(f"👉 [MCP Tool] obtener_proveedor(id={id})")
        return await _request("GET", f"/pg-ms-operation/api/proveedores/{id}")

    @server.tool(
        name="actualizar_proveedor",
        description="Actualiza los datos de un proveedor existente.",
    )
    async def actualizar_proveedor(
        id: int,
        nombreEmpresa: str,
        contactoNombre: str,
        telefono: str,
        email: str,
    ) -> dict:
        print(f"👉 [MCP Tool] actualizar_proveedor(id={id})")
        body = {
            "nombreEmpresa": nombreEmpresa,
            "contactoNombre": contactoNombre,
            "telefono": telefono,
            "email": email,
        }
        return await _request(
            "PUT", f"/pg-ms-operation/api/proveedores/{id}", json=body
        )

    @server.tool(
        name="eliminar_proveedor",
        description="Elimina un proveedor por su ID.",
    )
    async def eliminar_proveedor(id: int) -> dict:
        print(f"👉 [MCP Tool] eliminar_proveedor(id={id})")
        return await _request("DELETE", f"/pg-ms-operation/api/proveedores/{id}")

    return server


# -------------------------------------------------------------
# Entry point
# -------------------------------------------------------------
def main():
    if not AUTH_TOKEN:
        print("⚠️  AUTH_TOKEN vacío: las llamadas al backend fallarán con 401.")
    print(f"🌐 Backend PulseGym: {API_BASE}")

    server = create_server()
    print(
        f"Iniciando servidor MCP '{server.name}' en "
        f"http://{HOST}:{PORT} (transporte: {TRANSPORT})..."
    )

    if TRANSPORT == "sse":
        server.run(transport="sse")
    elif TRANSPORT == "streamable-http":
        server.run(transport="streamable-http")
    elif TRANSPORT == "stdio":
        server.run(transport="stdio")
    else:
        print(
            f"_____Transporte '{TRANSPORT}' no válido. "
            f"Opciones: sse, streamable-http, stdio_____"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()