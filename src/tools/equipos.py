"""Tools MCP de equipos (pg-ms-operation)."""

from mcp.server.fastmcp import FastMCP

from ..config import ENUM_ESTADOS, ENUM_URGENCIAS, ESTADOS_EQUIPO, URGENCIAS_FALLA
from ..http_client import request


def register(server: FastMCP) -> None:
    # NOTA: `dummy` no se usa. Existe para que el esquema JSON incluya
    # `properties`, que Groq exige en herramientas sin parámetros.
    #
    # NOTA: los parámetros opcionales usan sentinels ("" / 0) en vez de
    # `Optional[X] = None`. Groq valida el tipo de cada argumento contra
    # el schema, y si el modelo manda `null` en un campo declarado como
    # "string" (no nullable), la API entera devuelve 400 y el agente
    # termina sin poder usar ninguna tool. Con un tipo simple y no nulo,
    # el modelo manda "" en vez de null y todo el resto del código ya
    # trata ambos como "no viene" (`if nombre:` es falsy para "" y None).

    @server.tool(name="listar_equipos", description="Lista todos los equipos (id, nombre, estado).")
    async def listar_equipos(dummy: str = "") -> dict:
        return await request("GET", "/pg-ms-operation/api/equipos/todos")

    @server.tool(
        name="consultar_equipos",
        description=(
            "Filtra equipos por nombre, marca, ubicación, sede o estado. "
            f"Estados válidos: {ENUM_ESTADOS}."
        ),
    )
    async def consultar_equipos(
        nombre: str = "",
        marca: str = "",
        ubicacion: str = "",
        idSede: int = 0,
        estado: str = "",
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
        return await request("POST", "/pg-ms-operation/api/equipos/consultar", json=body)

    @server.tool(
        name="contar_equipos_por_estado",
        description=f"Cuenta equipos en un estado. Válidos: {ENUM_ESTADOS}.",
    )
    async def contar_equipos_por_estado(estado: str) -> dict:
        estado_up = estado.upper()
        if estado_up not in ESTADOS_EQUIPO:
            return {"success": False, "error": f"Estado inválido. Válidos: {sorted(ESTADOS_EQUIPO)}"}
        return await request("GET", f"/pg-ms-operation/api/equipos/conteo?estado={estado_up}")

    @server.tool(
        name="cambiar_estado_equipo",
        description=(
            "Cambia SOLO el estado de un equipo. Úsalo cuando el usuario quiera "
            f"cambiar únicamente el estado. Válidos: {ENUM_ESTADOS}."
        ),
    )
    async def cambiar_estado_equipo(id: int, estado: str) -> dict:
        estado_up = estado.upper()
        if estado_up not in ESTADOS_EQUIPO:
            return {"success": False, "error": f"Estado inválido. Válidos: {sorted(ESTADOS_EQUIPO)}"}
        return await request(
            "PATCH",
            f"/pg-ms-operation/api/equipos/{id}/estado",
            json={"estado": estado_up},
        )

    @server.tool(
        name="crear_equipo",
        description=(
            "Crea un nuevo equipo en el sistema. "
            "Fechas en formato YYYY-MM-DD. "
            f"El estado debe ser uno de: {ENUM_ESTADOS}."
        ),
    )
    async def crear_equipo(
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
        return await request("POST", "/pg-ms-operation/api/equipos", json=body)

    @server.tool(
        name="actualizar_equipo",
        description=(
            "Actualiza TODOS los campos de un equipo. Requiere enviar el objeto completo. "
            f"El estado debe ser uno de: {ENUM_ESTADOS}."
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
        return await request("PUT", f"/pg-ms-operation/api/equipos/{id}", json=body)

    @server.tool(
        name="reportar_falla_equipo",
        description=f"Reporta falla de un equipo. Urgencias válidas: {ENUM_URGENCIAS}.",
    )
    async def reportar_falla_equipo(idEquipo: int, urgencia: str, descripcion: str) -> dict:
        urgencia_up = urgencia.upper()
        if urgencia_up not in URGENCIAS_FALLA:
            return {"success": False, "error": f"Urgencia inválida. Válidas: {sorted(URGENCIAS_FALLA)}"}
        body = {"urgencia": urgencia_up, "descripcion": descripcion}
        return await request(
            "POST",
            f"/pg-ms-operation/api/equipos/{idEquipo}/reportar-falla",
            json=body,
        )

    @server.tool(name="listar_reportes_falla", description="Lista reportes de fallas.")
    async def listar_reportes_falla(dummy: str = "") -> dict:
        return await request("GET", "/pg-ms-operation/api/equipos/reportes-falla")
