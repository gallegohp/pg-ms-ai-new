# Servidor MCP en Python — PulseGym API (Transporte HTTP / SSE)

Este repositorio contiene una implementación de un servidor **MCP (Model Context Protocol)** desarrollado en Python utilizando la librería oficial de MCP (`mcp>=2.0.0`), enfocado en la integración con la API del gimnasio **PulseGym**.

Toda la lógica del servidor y sus herramientas reside en `src/server.py`, las pruebas de cliente en `src/client_test.py`, y la configuración se gestiona dinámicamente mediante el archivo `.env`.

---

## 🌟 Herramientas incluidas

| Herramienta | Parámetros | Descripción | Ejemplo de respuesta |
|---|---|---|---|
| `obtener_equipos` | *Ninguno* | Obtiene la lista completa de máquinas y equipos del gimnasio con su estado operativo (`OPERATIVO`, `MANTENIMIENTO`, etc.). | Lista de equipos y conteo total. |
| `obtener_historial_accesos` | Parámetros opcionales de paginación/filtro | Obtiene el historial de accesos registrados por los usuarios (entradas vía APP o en sedes). | Paginación con lista de accesos por usuario y sede. |

---

## 📁 Estructura del proyecto

```
proyecto_mcp/
├── .venv/                  # Entorno virtual de Python
├── .env                    # Variables de entorno (tokens, servidor, puerto)
├── .env.example             # Plantilla de variables de entorno
├── pyrightconfig.json       # Configuración del analizador estático (Pyright/Pyrefly)
├── README.md                # Documentación técnica del proyecto
└── src/
    ├── __init__.py
    ├── server.py             # Servidor MCP con los endpoints y cliente HTTP a PulseGym
    └── client_test.py        # Cliente de pruebas para verificar los endpoints MCP
```

---

## ⚙️ Configuración (`.env`)

Asegúrate de configurar el archivo `.env` en la raíz de tu proyecto con las credenciales necesarias:

```env
# Protocolo de transporte: 'streamable-http', 'sse' o 'stdio'
TRANSPORT=streamable-http

# Configuración del Servidor MCP
HOST=127.0.0.1
PORT=8000

# Credenciales de acceso a la API externa de PulseGym
PULSEGYM_API_TOKEN=tu_token_aqui
PULSEGYM_API_BASE_URL=https://api.pulsegym.com
```

---

## 🚀 Inicio rápido

### 1. Activar el entorno virtual e instalar dependencias

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Iniciar el servidor MCP

```bash
python3 src/server.py
```

Verás la confirmación de inicio en la consola:

```
🚀 Iniciando servidor MCP 'PulseGymServer' v1.0.0 en http://127.0.0.1:8000/mcp...
```

### 3. Ejecutar las pruebas con el cliente

Abre una segunda terminal, activa el entorno virtual y ejecuta:

```bash
source .venv/bin/activate
python3 src/client_test.py
```

---

## 🔌 Configuración en Antigravity / IDEs con MCP

Para conectar este servidor MCP con Antigravity o tu editor compatible, edita tu archivo de configuración de servidores MCP (`mcp_config.json`) agregando el bloque correspondiente:

**Conexión HTTP (`serverUrl`):**

```json
{
  "mcpServers": {
    "PulseGymServer": {
      "serverUrl": "http://127.0.0.1:8000/mcp"
    }
  }
}
```