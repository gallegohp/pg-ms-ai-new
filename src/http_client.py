"""
Cliente HTTP hacia el backend de PulseGym: auto-login contra pg-ms-auth,
renovación automática del JWT, y el helper `request()` que usan todas
las tools para llamar a los microservicios (operation, reports, ...).
"""

import asyncio
import base64
import json
import time
from typing import Optional

import httpx

from .config import (
    API_BASE,
    AUTH_LOGIN_PATH,
    HTTP_TIMEOUT,
    MAX_LIST_ITEMS,
    MAX_STRING_CHARS,
    MCP_SERVICE_EMAIL,
    MCP_SERVICE_PASSWORD,
)


# -------------------------------------------------------------
# Truncado
# -------------------------------------------------------------
def truncate(data, depth: int = 0):
    if depth > 5:
        return "..."
    if isinstance(data, list):
        if len(data) > MAX_LIST_ITEMS:
            return {
                "_truncated": True,
                "_total": len(data),
                "items": [truncate(i, depth + 1) for i in data[:MAX_LIST_ITEMS]],
            }
        return [truncate(i, depth + 1) for i in data]
    if isinstance(data, dict):
        return {k: truncate(v, depth + 1) for k, v in data.items()}
    if isinstance(data, str) and len(data) > MAX_STRING_CHARS:
        return data[:MAX_STRING_CHARS] + "..."
    return data


# -------------------------------------------------------------
# TokenManager: auto-login y renovación automática del JWT
# -------------------------------------------------------------
class TokenManager:
    """
    Gestiona el JWT de servicio contra pg-ms-auth.
    - Login inicial con email/password.
    - Renueva cuando faltan < 30s para expirar.
    - Reintenta con re-login forzado si un request devuelve 401.
    """

    def __init__(self):
        self._token: Optional[str] = None
        self._exp: int = 0
        self._lock = asyncio.Lock()

    @staticmethod
    def _decode_exp(jwt: str) -> int:
        """Lee `exp` del payload del JWT sin verificar firma."""
        try:
            payload_b64 = jwt.split(".")[1]
            padding = "=" * (-len(payload_b64) % 4)
            data = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
            return int(data.get("exp", 0))
        except Exception:
            return 0

    async def _do_login(self) -> str:
        if not MCP_SERVICE_EMAIL or not MCP_SERVICE_PASSWORD:
            raise RuntimeError(
                "Faltan MCP_SERVICE_EMAIL / MCP_SERVICE_PASSWORD en el entorno."
            )

        url = f"{API_BASE}{AUTH_LOGIN_PATH}"
        body = {"email": MCP_SERVICE_EMAIL, "password": MCP_SERVICE_PASSWORD}

        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.post(url, json=body)

        if resp.status_code >= 400:
            raise RuntimeError(
                f"Login falló ({resp.status_code}): {resp.text[:300]}"
            )

        data = resp.json()

        token = (
            (data.get("data") or {}).get("jwt")
            or data.get("jwt")
            or data.get("token")
            or data.get("accessToken")
            or data.get("access_token")
        )
        if not token:
            raise RuntimeError(
                f"Login OK pero no se encontró el JWT. Keys: {list(data.keys())}"
            )

        self._token = token
        self._exp = self._decode_exp(token)

        exp_str = (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._exp))
            if self._exp else "desconocido"
        )
        print(f"🔐 Login OK. Token expira: {exp_str}")
        return token

    async def get_token(self, force_refresh: bool = False) -> str:
        async with self._lock:
            now = int(time.time())
            needs_refresh = (
                force_refresh
                or not self._token
                or (self._exp and now >= (self._exp - 30))
            )
            if needs_refresh:
                await self._do_login()
            return self._token


TOKEN_MGR = TokenManager()


# -------------------------------------------------------------
# Cliente HTTP
# -------------------------------------------------------------
async def request(method: str, path: str, **kwargs) -> dict:
    url = f"{API_BASE}{path}"

    # 1. Obtener token (login automático si hace falta)
    try:
        token = await TOKEN_MGR.get_token()
    except Exception as exc:
        return {"success": False, "error": f"Error de autenticación: {exc}"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # 2. Primer intento
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
    except httpx.RequestError as exc:
        return {"success": False, "error": f"Error de conexión: {exc}"}

    # 3. Si 401 → re-login forzado y reintentar UNA vez
    if response.status_code == 401:
        try:
            token = await TOKEN_MGR.get_token(force_refresh=True)
            headers["Authorization"] = f"Bearer {token}"
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.request(method, url, headers=headers, **kwargs)
        except Exception as exc:
            return {"success": False, "error": f"Re-login falló: {exc}"}

    # 4. Manejo normal
    if response.status_code >= 400:
        return {
            "success": False,
            "status": response.status_code,
            "error": response.text[:MAX_STRING_CHARS],
        }

    if not response.content:
        return {"success": True, "status": response.status_code}

    try:
        return truncate(response.json())
    except ValueError:
        return {
            "success": True,
            "status": response.status_code,
            "raw": response.text[:MAX_STRING_CHARS],
        }
