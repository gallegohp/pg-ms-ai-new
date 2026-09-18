"""Registro de todas las tools MCP, agrupadas por dominio."""

from mcp.server.fastmcp import FastMCP

from . import asistencias, equipos, proveedores, reportes


def register_all(server: FastMCP) -> None:
    equipos.register(server)
    asistencias.register(server)
    proveedores.register(server)
    reportes.register(server)
