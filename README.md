# PoC Bot de facturas con SQL Server

Prototipo modular en Python para identificar archivos ZIP, seleccionar descargas, registrar resultados, descomprimir archivos e identificar XML.

La persistencia utiliza SQL Server mediante SQLAlchemy ORM. Las tablas, columnas y atributos persistidos utilizan `snake_case`.

## Arquitectura

```text
poc-bot-facturas-sqlserver/
├── main.py
├── 01_descargar_listado.py
├── 02_descargar_archivos.py
├── 03_descomprimir_archivos.py
├── 04_enviar_xml_cliente.py
├── app/
│   ├── config/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── jobs/
│   └── utils/
├── scripts/
└── storage/
    ├── downloads/
    ├── extracted/
    └── logs/
```

## Capas

| Capa | Responsabilidad |
|---|---|
| `models` | Entidades ORM y definición de tablas SQL Server. |
| `repositories` | Consultas y persistencia de datos. |
| `services` | Selenium, descarga HTTP, extracción ZIP y correo. |
| `jobs` | Casos de uso ejecutables de forma independiente. |
| `database` | Motor, sesiones y creación de tablas. |
| `config` | Variables de entorno y rutas locales. |

## Modelo de datos

### `pagina_fuente`

Registra las páginas web que el bot debe procesar.

### `archivo_tipo`

Registra los archivos ZIP encontrados. El campo `archivo_tipo_requerido` permite seleccionar manualmente qué archivos deben descargarse.

### `archivo_bitacora`

Registra el resultado de descarga, descompresión y envío de cada archivo.

### `cliente`

Registra los destinatarios activos para el envío de XML.

## Configuración

Crear el entorno:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copiar las variables:

```powershell
Copy-Item .env.example .env
```

Ejemplo con autenticación integrada:

```env
sql_server=localhost\SQLEXPRESS
sql_database=poc_bot_facturas
sql_driver=SQL Server
sql_trusted_connection=true
sql_trust_server_certificate=true
```

Crear la base de datos ejecutando `scripts/crear_base_datos.sql` en SQL Server.

El valor de `sql_driver` debe coincidir con un controlador instalado. Se puede consultar con:

```powershell
.\.venv\Scripts\python.exe -c "import pyodbc; print(pyodbc.drivers())"
```

Crear las tablas ORM:

```powershell
python scripts/crear_tablas.py
```

Cargar la página de prueba:

```text
scripts/cargar_datos_iniciales.sql
```

## Ejecución por jobs

### Job 1: obtener catálogo

```powershell
python 01_descargar_listado.py
```

Usa Selenium para recorrer las páginas activas y registrar ZIPs nuevos en `archivo_tipo`.

### Selección manual

Antes de descargar, marcar los archivos requeridos:

```sql
UPDATE archivo_tipo
SET archivo_tipo_requerido = 1
WHERE archivo_tipo_id IN (1, 2, 3);
```

### Job 2: descargar seleccionados

```powershell
python 02_descargar_archivos.py
```

Consulta `archivo_tipo_requerido = 1`, descarga los ZIPs y registra el resultado en `archivo_bitacora`.

### Job 3: descomprimir

```powershell
python 03_descomprimir_archivos.py
```

Consulta descargas exitosas pendientes de extracción, descomprime los ZIPs e identifica archivos XML.

### Job 4: enviar XML

```powershell
python 04_enviar_xml_cliente.py
```

Envía los XML encontrados a clientes activos y actualiza `archivo_bitacora_envio_ok`.

## Ejecución mediante `main.py`

```powershell
python main.py 01_descargar_listado
python main.py 02_descargar_archivos
python main.py 03_descomprimir_archivos
python main.py 04_enviar_xml_cliente
python main.py todos
```

## Consideraciones

- Las credenciales se almacenan en `.env` y no se versionan.
- Selenium se utiliza para páginas que requieren navegación mediante navegador.
- Requests se utiliza para descargar archivos mediante URL directa.
- `zipfile` se utiliza para extracción segura.
- SQLAlchemy centraliza la persistencia y evita SQL embebido en los jobs.
- El envío SMTP debe reemplazarse por Microsoft Graph en una versión productiva.
