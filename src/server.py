"""
Servidor MCP para PulseGym IA - herramientas de operación del gimnasio.

Expone como herramientas MCP los endpoints del microservicio pg-ms-operation:
equipos, asistencias y proveedores.

Optimizado para minimizar el consumo de tokens del LLM.
"""

import os
import sys

from typing import Optional   # añade esto arriba del archivo
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# -------------------------------------------------------------
# Configuración
# -------------------------------------------------------------
load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")   
TRANSPORT = os.getenv("TRANSPORT", "sse").lower().strip()
API_BASE = os.getenv("PULSEGYM_API_BASE", "https://api.pulsegym.uk").rstrip("/")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "15"))

MAX_LIST_ITEMS = int(os.getenv("MAX_LIST_ITEMS", "20"))
MAX_STRING_CHARS = int(os.getenv("MAX_STRING_CHARS", "500"))

# Enums reales del backend (EnumEstado y EnumUrgencia)
ESTADOS_EQUIPO = {"OPERATIVO", "MANTENIMIENTO", "FUERA_DE_SERVICIO", "RETIRADO"}
URGENCIAS_FALLA = {"BAJA", "MEDIA", "ALTA", "CRITICA"}
TIPOS_ACCESO = {"APP", "QR", "MANUAL"}

# Texto de enums para meter en las descripciones de las tools
_ENUM_ESTADOS = ", ".join(sorted(ESTADOS_EQUIPO))
_ENUM_URGENCIAS = ", ".join(sorted(URGENCIAS_FALLA))
_ENUM_ACCESOS = ", ".join(sorted(TIPOS_ACCESO))

BASE_HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
}


# -------------------------------------------------------------
# Truncado
# -------------------------------------------------------------
def _truncate(data, depth: int = 0):
    if depth > 5:
        return "..."
    if isinstance(data, list):
        if len(data) > MAX_LIST_ITEMS:
            return {
                "_truncated": True,
                "_total": len(data),
                "items": [_truncate(i, depth + 1) for i in data[:MAX_LIST_ITEMS]],
            }
        return [_truncate(i, depth + 1) for i in data]
    if isinstance(data, dict):
        return {k: _truncate(v, depth + 1) for k, v in data.items()}
    if isinstance(data, str) and len(data) > MAX_STRING_CHARS:
        return data[:MAX_STRING_CHARS] + "..."
    return data


# -------------------------------------------------------------
# Cliente HTTP
# -------------------------------------------------------------
async def _request(method: str, path: str, **kwargs) -> dict:
    url = f"{API_BASE}{path}"
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.request(
                method, url, headers=BASE_HEADERS, **kwargs
            )
    except httpx.RequestError as exc:
        return {"success": False, "error": f"Error de conexión: {exc}"}

    if response.status_code >= 400:
        return {
            "success": False,
            "status": response.status_code,
            "error": response.text[:MAX_STRING_CHARS],
        }

    if not response.content:
        return {"success": True, "status": response.status_code}

    try:
        return _truncate(response.json())
    except ValueError:
        return {
            "success": True,
            "status": response.status_code,
            "raw": response.text[:MAX_STRING_CHARS],
        }


# -------------------------------------------------------------
# Servidor MCP
# -------------------------------------------------------------
def create_server() -> FastMCP:
    server = FastMCP(
        name="PulseGymAISimulator",
        instructions="Herramientas para gestionar equipos, asistencias y proveedores de PulseGym.",
        host=HOST,
        port=PORT,
    )

    # =====================================================================
    # EQUIPOS
    # =====================================================================
    # NOTA: `dummy` no se usa. Existe para que el esquema JSON incluya
    # `properties`, que Groq exige en herramientas sin parámetros.

    @server.tool(name="listar_equipos", description="Lista todos los equipos (id, nombre, estado).")
    async def listar_equipos(dummy: str = "") -> dict:
        return await _request("GET", "/pg-ms-operation/api/equipos/todos")

    @server.tool(
    name="consultar_equipos",
    description=(
        "Filtra equipos por nombre, marca, ubicación, sede o estado. "
        f"Estados válidos: {_ENUM_ESTADOS}."
    ),
)
    async def consultar_equipos(
        nombre: Optional[str] = None,
        marca: Optional[str] = None,
        ubicacion: Optional[str] = None,
        idSede: Optional[int] = None,
        estado: Optional[str] = None,
    ) -> dict:
        body = {}
        if nombre:
            body["nombre"] = nombre
        if marca:
            body["marca"] = marca
        if ubicacion:
            body["ubicacion"] = ubicacion
        if idSede:
            body["idSede"] = idSede
        if estado:
            estado_up = estado.upper()
            if estado_up not in ESTADOS_EQUIPO:
                return {"success": False, "error": f"Estado inválido. Válidos: {sorted(ESTADOS_EQUIPO)}"}
            body["estado"] = estado_up
        return await _request("POST", "/pg-ms-operation/api/equipos/consultar", json=body)

    @server.tool(
        name="contar_equipos_por_estado",
        description=f"Cuenta equipos en un estado. Válidos: {_ENUM_ESTADOS}.",
    )
    async def contar_equipos_por_estado(estado: str) -> dict:
        estado_up = estado.upper()
        if estado_up not in ESTADOS_EQUIPO:
            return {"success": False, "error": f"Estado inválido. Válidos: {sorted(ESTADOS_EQUIPO)}"}
        return await _request("GET", f"/pg-ms-operation/api/equipos/conteo?estado={estado_up}")

    @server.tool(
        name="cambiar_estado_equipo",
        description=(
            "Cambia SOLO el estado de un equipo. Úsalo cuando el usuario quiera "
            f"cambiar únicamente el estado. Válidos: {_ENUM_ESTADOS}."
        ),
    )
    async def cambiar_estado_equipo(id: int, estado: str) -> dict:
        estado_up = estado.upper()
        if estado_up not in ESTADOS_EQUIPO:
            return {"success": False, "error": f"Estado inválido. Válidos: {sorted(ESTADOS_EQUIPO)}"}
        return await _request(
            "PATCH",
            f"/pg-ms-operation/api/equipos/{id}/estado",
            json={"estado": estado_up},
        )

    @server.tool(
        name="actualizar_equipo",
        description=(
            "Actualiza TODOS los campos de un equipo. Requiere enviar el objeto completo. "
            f"El estado debe ser uno de: {_ENUM_ESTADOS}."
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
        estado_up = estado.upper()
        if estado_up not in ESTADOS_EQUIPO:
            return {"success": False, "error": f"Estado inválido. Válidos: {sorted(ESTADOS_EQUIPO)}"}
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
            "estado": estado_up,
        }
        return await _request("PUT", f"/pg-ms-operation/api/equipos/{id}", json=body)

    @server.tool(
        name="reportar_falla_equipo",
        description=f"Reporta falla de un equipo. Urgencias válidas: {_ENUM_URGENCIAS}.",
    )
    async def reportar_falla_equipo(idEquipo: int, urgencia: str, descripcion: str) -> dict:
        urgencia_up = urgencia.upper()
        if urgencia_up not in URGENCIAS_FALLA:
            return {"success": False, "error": f"Urgencia inválida. Válidas: {sorted(URGENCIAS_FALLA)}"}
        body = {"urgencia": urgencia_up, "descripcion": descripcion}
        return await _request(
            "POST",
            f"/pg-ms-operation/api/equipos/{idEquipo}/reportar-falla",
            json=body,
        )

    @server.tool(name="listar_reportes_falla", description="Lista reportes de fallas.")
    async def listar_reportes_falla(dummy: str = "") -> dict:
        return await _request("GET", "/pg-ms-operation/api/equipos/reportes-falla")

    # =====================================================================
    # ASISTENCIAS
    # =====================================================================
    @server.tool(
        name="registrar_entrada",
        description=f"Registra entrada de usuario. Tipos de acceso: {_ENUM_ACCESOS}.",
    )
    async def registrar_entrada(idUsuario: int, idSede: int, tipoAcceso: str) -> dict:
        tipo_up = tipoAcceso.upper()
        if tipo_up not in TIPOS_ACCESO:
            return {"success": False, "error": f"TipoAcceso inválido. Válidos: {sorted(TIPOS_ACCESO)}"}
        body = {"idUsuario": idUsuario, "idSede": idSede, "tipoAcceso": tipo_up}
        return await _request("POST", "/pg-ms-operation/api/asistencias/entrada", json=body)

    @server.tool(name="historial_asistencia_usuario", description="Historial de asistencias de un usuario.")
    async def historial_asistencia_usuario(idUsuario: int) -> dict:
        return await _request("GET", f"/pg-ms-operation/api/asistencias/historial/usuario/{idUsuario}")

    @server.tool(name="asistencia_por_sede", description="Asistencias de una sede.")
    async def asistencia_por_sede(idSede: int) -> dict:
        return await _request("GET", f"/pg-ms-operation/api/asistencias/sede/{idSede}")

    @server.tool(name="asistencia_hoy", description="Asistencias de hoy.")
    async def asistencia_hoy(dummy: str = "") -> dict:
        return await _request("GET", "/pg-ms-operation/api/asistencias/hoy")

    # =====================================================================
    # PROVEEDORES
    # =====================================================================
    @server.tool(name="registrar_proveedor", description="Registra proveedor.")
    async def registrar_proveedor(nombreEmpresa: str, contactoNombre: str, telefono: str, email: str) -> dict:
        body = {"nombreEmpresa": nombreEmpresa, "contactoNombre": contactoNombre, "telefono": telefono, "email": email}
        return await _request("POST", "/pg-ms-operation/api/proveedores/registrar", json=body)

    @server.tool(name="listar_proveedores", description="Lista proveedores.")
    async def listar_proveedores(dummy: str = "") -> dict:
        return await _request("GET", "/pg-ms-operation/api/proveedores/todos")

    @server.tool(name="obtener_proveedor", description="Obtiene proveedor por ID.")
    async def obtener_proveedor(id: int) -> dict:
        return await _request("GET", f"/pg-ms-operation/api/proveedores/{id}")

    @server.tool(name="actualizar_proveedor", description="Actualiza proveedor.")
    async def actualizar_proveedor(id: int, nombreEmpresa: str, contactoNombre: str, telefono: str, email: str) -> dict:
        body = {"nombreEmpresa": nombreEmpresa, "contactoNombre": contactoNombre, "telefono": telefono, "email": email}
        return await _request("PUT", f"/pg-ms-operation/api/proveedores/{id}", json=body)

    @server.tool(name="eliminar_proveedor", description="Elimina proveedor por ID.")
    async def eliminar_proveedor(id: int) -> dict:
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