"""Tools MCP de asistencias (pg-ms-operation)."""

from mcp.server.fastmcp import FastMCP

from ..config import ENUM_ACCESOS, TIPOS_ACCESO
from ..http_client import request


def register(server: FastMCP) -> None:
    @server.tool(
        name="registrar_entrada",
        description=f"Registra entrada de usuario. Tipos de acceso: {ENUM_ACCESOS}.",
    )
    async def registrar_entrada(idUsuario: int, idSede: int, tipoAcceso: str) -> dict:
        tipo_up = tipoAcceso.upper()
        if tipo_up not in TIPOS_ACCESO:
            return {"success": False, "error": f"TipoAcceso inválido. Válidos: {sorted(TIPOS_ACCESO)}"}
        body = {"idUsuario": idUsuario, "idSede": idSede, "tipoAcceso": tipo_up}
        return await request("POST", "/pg-ms-operation/api/asistencias/entrada", json=body)

    @server.tool(name="historial_asistencia_usuario", description="Historial de asistencias de un usuario.")
    async def historial_asistencia_usuario(idUsuario: int) -> dict:
        return await request("GET", f"/pg-ms-operation/api/asistencias/historial/usuario/{idUsuario}")

    @server.tool(name="asistencia_por_sede", description="Asistencias de una sede.")
    async def asistencia_por_sede(idSede: int) -> dict:
        return await request("GET", f"/pg-ms-operation/api/asistencias/sede/{idSede}")

    @server.tool(name="asistencia_hoy", description="Asistencias de hoy.")
    async def asistencia_hoy(dummy: str = "") -> dict:
        return await request("GET", "/pg-ms-operation/api/asistencias/hoy")

    @server.tool(
        name="consultar_asistencias",
        description=(
            "Consulta asistencias filtrando por usuario o por sede. "
            "Sin filtros, devuelve las asistencias de hoy."
        ),
    )
    async def consultar_asistencias(
        idUsuario: int = 0,
        idSede: int = 0,
    ) -> dict:
        if idUsuario:
            return await request("GET", f"/pg-ms-operation/api/asistencias/historial/usuario/{idUsuario}")
        if idSede:
            return await request("GET", f"/pg-ms-operation/api/asistencias/sede/{idSede}")
        return await request("GET", "/pg-ms-operation/api/asistencias/hoy")

    @server.tool(
        name="contar_asistencias_por_fecha",
        description=(
            "Cuenta asistencias registradas hoy, opcionalmente filtradas por sede. "
            "Limitación actual del backend: solo soporta el conteo del día de hoy, "
            "no rangos de fecha arbitrarios."
        ),
    )
    async def contar_asistencias_por_fecha(idSede: int = 0) -> dict:
        path = (
            f"/pg-ms-operation/api/asistencias/sede/{idSede}"
            if idSede
            else "/pg-ms-operation/api/asistencias/hoy"
        )
        data = await request("GET", path)
        if isinstance(data, dict) and "_total" in data:
            return {"total": data["_total"]}
        if isinstance(data, list):
            return {"total": len(data)}
        return data
