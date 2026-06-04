# Instalación del prototipo

Esta guía explica cómo preparar y ejecutar el prototipo por primera vez.

## 1. Requisitos

- Python 3.11 o superior
- Docker Desktop
- SQL Server Management Studio, DataGrip o `sqlcmd`
- ODBC Driver para SQL Server

## 2. Preparar el entorno Python

Abrir PowerShell dentro de la carpeta del proyecto:

```powershell
cd C:\ruta\poc-bot-facturas

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
Copy-Item .env.example .env
```

Completar el archivo `.env` con las credenciales locales de SQL Server y, si se probará el envío de correos, las credenciales SMTP.

## 3. Levantar SQL Server

```powershell
docker run -d `
  --name poc-sql-server `
  -e "ACCEPT_EULA=Y" `
  -e "MSSQL_SA_PASSWORD=ContraseñaSegura123!" `
  -p 1433:1433 `
  mcr.microsoft.com/mssql/server:2022-latest
```

La contraseña debe cumplir los requisitos de seguridad de SQL Server.

## 4. Preparar una base de datos nueva

Para una instalación nueva no debe ejecutarse ninguna migración.

Ejecutar los siguientes pasos en orden:

### 4.1 Crear la base de datos y los esquemas

Ejecutar como administrador:

```text
scripts/crear_base_datos.sql
```

### 4.2 Crear las tablas

Configurar temporalmente `.env` con el usuario administrador:

```env
sql_username=sa
sql_password=ContraseñaSegura123!
```

Ejecutar:

```powershell
python scripts/crear_tablas.py
```

### 4.3 Aplicar restricciones de integridad

Ejecutar:

```text
scripts/endurecer_integridad.sql
```

### 4.4 Cargar los datos iniciales

Ejecutar:

```text
scripts/cargar_datos_iniciales.sql
```

### 4.5 Crear el usuario de la aplicación

Ejecutar:

```text
scripts/crear_usuario_aplicacion.sql
```

El valor `$(BOT_FACTURAS_PASSWORD)` debe proporcionarse mediante SQLCMD o reemplazarse por una contraseña segura durante la ejecución local.

Después de crear el usuario, actualizar `.env`:

```env
sql_username=bot_facturas_app
sql_password=contraseña_del_usuario
```

## 5. Migraciones

El archivo siguiente se utiliza solamente para actualizar una instalación antigua que todavía utiliza RFC:

```text
scripts/migrar_modelo_xml_sunat.sql
```

No debe ejecutarse en una instalación nueva.

Antes de ejecutar cualquier migración debe realizarse un respaldo de la base de datos.

## 6. Configurar los datos

Las páginas utilizadas para encontrar archivos ZIP se registran en:

```text
configuracion.pagina_fuente
```

Los clientes se registran en:

```text
configuracion.cliente
```

Cada cliente debe tener:

- Nombre
- Correo electrónico
- RUC de 11 dígitos
- Estado activo

## 7. Ejecutar el prototipo

Para ejecutar todo el flujo:

```powershell
python main.py todos
```

Para ejecutar y revisar cada job por separado:

```powershell
python main.py 01_descargar_listado
python main.py 02_descargar_archivos
python main.py 03_descomprimir_archivos
python main.py 04_procesar_xml
python main.py 05_enviar_xml_cliente
```

## 8. Flujo de ejecución

```text
Página fuente configurada
    |
    v
Detección y registro de enlaces ZIP
    |
    v
Selección de archivos para descargar
    |
    v
Descarga de archivos ZIP
    |
    v
Descompresión segura
    |
    v
Procesamiento individual de XML SUNAT
    |
    v
Asignación de XML al cliente por RUC receptor
    |
    v
Envío por correo y registro del resultado
```

Antes de ejecutar `02_descargar_archivos`, debe seleccionarse en la base de datos qué archivos encontrados deben descargarse.

## 9. Validar la instalación

Ejecutar las pruebas automatizadas:

```powershell
python -m unittest discover -s tests -v
```

Revisar los archivos generados en:

```text
logs/
storage/downloads/
storage/extracted/
```

