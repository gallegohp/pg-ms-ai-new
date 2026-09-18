"""Tools MCP de proveedores (pg-ms-operation)."""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from ..http_client import request


def register(server: FastMCP) -> None:
    @server.tool(name="registrar_proveedor", description="Registra proveedor.")
    async def registrar_proveedor(nombreEmpresa: str, contactoNombre: str, telefono: str, email: str) -> dict:
        body = {"nombreEmpresa": nombreEmpresa, "contactoNombre": contactoNombre, "telefono": telefono, "email": email}
        return await request("POST", "/pg-ms-operation/api/proveedores/registrar", json=body)

    @server.tool(name="listar_proveedores", description="Lista proveedores.")
    async def listar_proveedores(dummy: str = "") -> dict:
        return await request("GET", "/pg-ms-operation/api/proveedores/todos")

    @server.tool(
        name="consultar_proveedores",
        description="Consulta proveedores por nombre de empresa (búsqueda parcial). Sin filtro, devuelve todos.",
    )
    async def consultar_proveedores(nombreEmpresa: Optional[str] = None) -> dict:
        if nombreEmpresa:
            return await request(
                "GET", "/pg-ms-operation/api/proveedores/buscar", params={"nombre": nombreEmpresa}
            )
        return await request("GET", "/pg-ms-operation/api/proveedores/todos")

    @server.tool(name="obtener_proveedor", description="Obtiene proveedor por ID.")
    async def obtener_proveedor(id: int) -> dict:
        return await request("GET", f"/pg-ms-operation/api/proveedores/{id}")

    @server.tool(name="actualizar_proveedor", description="Actualiza proveedor.")
    async def actualizar_proveedor(id: int, nombreEmpresa: str, contactoNombre: str, telefono: str, email: str) -> dict:
        body = {"nombreEmpresa": nombreEmpresa, "contactoNombre": contactoNombre, "telefono": telefono, "email": email}
        return await request("PUT", f"/pg-ms-operation/api/proveedores/{id}", json=body)

    @server.tool(name="eliminar_proveedor", description="Elimina proveedor por ID.")
    async def eliminar_proveedor(id: int) -> dict:
        return await request("DELETE", f"/pg-ms-operation/api/proveedores/{id}")
