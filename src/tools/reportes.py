"""
Tools MCP de reportes (pg-ms-reports): ingresos, mora, afluencia.

NOTA: "ingresos" aquí es dinero (pagos/membresías), no confundir con
"afluencia" (entradas físicas al gimnasio, ex check-ins).
Estos endpoints exigen rol Admin (ingresos/mora) o Admin/Recepcionista
(afluencia) en la cuenta de servicio del MCP; si esa cuenta no tiene el
rol adecuado, el backend responde 403.
"""

from datetime import date
from typing import Optional

from mcp.server.fastmcp import FastMCP

from ..http_client import request


def register(server: FastMCP) -> None:
    @server.tool(
        name="reporte_ingresos_diarios",
        description="Total de ingresos (dinero) de un día. Sin fecha, usa hoy. Requiere rol Admin.",
    )
    async def reporte_ingresos_diarios(fecha: Optional[str] = None) -> dict:
        fecha_str = fecha or date.today().isoformat()
        return await request(
            "GET", "/pg-ms-reports/api/reportes/ingresos/diarios", params={"fecha": fecha_str}
        )

    @server.tool(
        name="reporte_ingresos_mensuales",
        description="Total de ingresos (dinero) de un mes/año específico (mes 1-12). Requiere rol Admin.",
    )
    async def reporte_ingresos_mensuales(mes: int, anio: int) -> dict:
        if mes < 1 or mes > 12:
            return {"success": False, "error": "El mes debe estar entre 1 y 12"}
        return await request(
            "GET",
            "/pg-ms-reports/api/reportes/ingresos/mensuales",
            params={"mes": mes, "anio": anio},
        )

    @server.tool(
        name="reporte_ingresos_por_membresia",
        description=(
            "Ingresos (dinero) agrupados por tipo de membresía entre dos "
            "fechas (YYYY-MM-DD). Requiere rol Admin."
        ),
    )
    async def reporte_ingresos_por_membresia(fechaInicio: str, fechaFin: str) -> dict:
        if fechaInicio > fechaFin:
            return {"success": False, "error": "fechaInicio no puede ser posterior a fechaFin"}
        return await request(
            "GET",
            "/pg-ms-reports/api/reportes/ingresos/por-membresia",
            params={"fechaInicio": fechaInicio, "fechaFin": fechaFin},
        )

    @server.tool(
        name="reporte_ingresos_ultimos_seis_meses",
        description="Ingresos (dinero) mensuales de los últimos 6 meses y su total acumulado. Requiere rol Admin.",
    )
    async def reporte_ingresos_ultimos_seis_meses(dummy: str = "") -> dict:
        return await request("GET", "/pg-ms-reports/api/reportes/ingresos/ultimos-seis-meses")

    @server.tool(
        name="reporte_mora",
        description=(
            "Lista de socios en mora (pagos atrasados), opcionalmente entre "
            "dos fechas (YYYY-MM-DD). Sin fechas, trae todos. Requiere rol Admin."
        ),
    )
    async def reporte_mora(fechaInicio: Optional[str] = None, fechaFin: Optional[str] = None) -> dict:
        params = {}
        if fechaInicio:
            params["fechaInicio"] = fechaInicio
        if fechaFin:
            params["fechaFin"] = fechaFin
        return await request("GET", "/pg-ms-reports/api/reportes/mora", params=params)

    @server.tool(
        name="reporte_afluencia_hoy",
        description=(
            "Total de socios que ingresaron FÍSICAMENTE hoy (check-ins, no "
            "dinero). Requiere rol Admin o Recepcionista."
        ),
    )
    async def reporte_afluencia_hoy(dummy: str = "") -> dict:
        return await request("GET", "/pg-ms-reports/api/reportes/afluencia/hoy")

    @server.tool(
        name="reporte_afluencia_por_dia",
        description=(
            "Total de socios que ingresaron FÍSICAMENTE en una fecha "
            "(check-ins, no dinero). Sin fecha, usa hoy. Requiere rol Admin "
            "o Recepcionista."
        ),
    )
    async def reporte_afluencia_por_dia(fecha: Optional[str] = None) -> dict:
        fecha_str = fecha or date.today().isoformat()
        return await request(
            "GET",
            "/pg-ms-reports/api/reportes/afluencia/socios-por-dia",
            params={"fecha": fecha_str},
        )
