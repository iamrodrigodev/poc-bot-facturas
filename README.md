# PoC Bot de facturas con SQL Server

Prototipo modular en Python para identificar archivos ZIP, seleccionar descargas, registrar resultados, descomprimir archivos e identificar XML.

La persistencia utiliza SQL Server mediante SQLAlchemy ORM. Las tablas, columnas y atributos persistidos utilizan `snake_case`.

## Arquitectura

```text
poc-bot-facturas/
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
├── logs/
└── storage/
    ├── downloads/
    └── extracted/
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

## Logs

Cada ejecución muestra mensajes legibles en consola y almacena eventos estructurados en:

```text
logs/bot_facturas.jsonl
```

Cada línea es un objeto JSON independiente con fecha, nivel, identificador de ejecución, módulo, mensaje y contexto:

```json
{"fecha_hora":"2026-06-04T10:30:00-05:00","nivel":"INFO","ejecucion_id":"...","modulo":"job.descargar_archivos","mensaje":"Archivo descargado","contexto":{"archivo_tipo_id":1,"ruta_descarga":"..."}}
```

El archivo rota automáticamente al alcanzar aproximadamente 5 MB y conserva hasta cinco respaldos.

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

Ejemplo para el contenedor Docker:

```env
sql_server=localhost,1433
sql_database=poc_bot_facturas
sql_schema_configuracion=configuracion
sql_schema_operacion=operacion
sql_username=bot_facturas_app
sql_password=Cambiar_Esta_Clave_2026!
sql_driver=SQL Server
sql_trusted_connection=false
sql_trust_server_certificate=true
```

Crear la base de datos ejecutando `scripts/crear_base_datos.sql` en SQL Server.

Las tablas se separan por responsabilidad en dos esquemas:

```text
poc_bot_facturas
├── configuracion
│   ├── pagina_fuente
│   └── cliente
└── operacion
    ├── archivo_tipo
    └── archivo_bitacora
```

El valor de `sql_driver` debe coincidir con un controlador instalado. Se puede consultar con:

```powershell
.\.venv\Scripts\python.exe -c "import pyodbc; print(pyodbc.drivers())"
```

Crear las tablas ORM:

```powershell
python -m scripts.crear_tablas
```

Aplicar restricciones de integridad y crear el usuario de ejecución:

```text
scripts/endurecer_integridad.sql
scripts/crear_usuario_aplicacion.sql
```

La creación inicial debe ejecutarse con una cuenta administrativa. Los jobs deben utilizar `bot_facturas_app`, que solo posee permisos de lectura y escritura sobre los esquemas.

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
UPDATE operacion.archivo_tipo
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
- Los jobs no crean ni modifican la estructura de la base de datos.
- Cada operación SQL confirma o revierte sus cambios mediante una unidad de trabajo.
- SQL Server impide ejecutar simultáneamente dos instancias del mismo job.
- Selenium se utiliza para páginas que requieren navegación mediante navegador.
- Requests se utiliza para descargar archivos mediante URL directa.
- `zipfile` se utiliza para extracción segura.
- SQLAlchemy centraliza la persistencia y evita SQL embebido en los jobs.
- El envío SMTP debe reemplazarse por Microsoft Graph en una versión productiva.

## Seguridad y recuperación

La auditoría técnica, controles implementados y riesgos residuales están documentados en `AUDITORIA_SEGURIDAD.md`.

Ejecutar las pruebas de integración:

```powershell
python -m unittest tests.test_seguridad_integracion -v
```

Generar un respaldo fuera del contenedor:

```powershell
$env:SQLSERVER_SA_PASSWORD="clave_administrativa"
.\scripts\respaldar_base_datos.ps1
```
