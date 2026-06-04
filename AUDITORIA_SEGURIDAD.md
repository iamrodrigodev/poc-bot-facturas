# Auditoría de seguridad e integridad

## Alcance

La revisión cubre persistencia SQL Server, transacciones, concurrencia, descargas HTTP, extracción ZIP, envío SMTP, credenciales, logs y recuperación.

## Controles implementados

| Área | Control |
|---|---|
| Transacciones | Cada cambio SQL usa una unidad de trabajo con confirmación o rollback automático. |
| Concurrencia | SQL Server bloquea ejecuciones simultáneas del mismo job mediante `sp_getapplock`. |
| Integridad | Restricciones SQL rechazan estados imposibles y descargas exitosas duplicadas. |
| Privilegios | El usuario de ejecución solo puede leer configuración y leer/escribir operación sin borrar registros. |
| Descargas | Escritura temporal, límite de tamaño, validación ZIP y reemplazo atómico. |
| URLs | Solo HTTP/HTTPS públicos; redes privadas y redirecciones inseguras son rechazadas. |
| Extracción | Staging, rollback de carpeta, bloqueo de path traversal, symlinks y ZIP bombs. |
| Envíos | Bitácora independiente por cliente y archivo para reducir duplicados en reintentos. |
| SMTP | TLS verificado, timeout y validación previa de credenciales. |
| Recuperación | Script de backup con checksum y copia fuera del contenedor. |
| Verificación | Suite de integración con rollback, restricciones, concurrencia, SSRF y ZIP malicioso. |

## Riesgos residuales

### Envío exactamente una vez

SMTP no ofrece idempotencia transaccional. Si el servidor acepta un correo y el proceso se detiene antes de registrar el resultado, un reintento puede duplicarlo. Para eliminar este riesgo se necesita un proveedor con clave de idempotencia o una cola transaccional con confirmación externa.

### SQL Server y filesystem

Una transacción SQL no puede incluir de forma atómica el filesystem local. Las operaciones de archivo son atómicas individualmente y los jobs son reejecutables, pero producción debería incorporar un job de reconciliación entre rutas físicas y bitácoras.

### Web scraping

La validación bloquea URLs privadas conocidas, pero Selenium y DNS pueden presentar escenarios avanzados de redirección o DNS rebinding. Producción debería ejecutar el bot en una red aislada con reglas de salida permitidas.

### Malware

Los ZIP y XML se validan estructuralmente, pero no se analizan con antivirus. Producción debería incorporar análisis antimalware antes de procesar o enviar archivos.

### Secretos

El archivo `.env` está excluido de Git, pero producción debe usar un gestor de secretos y rotación periódica. `sql_trust_server_certificate=true` solo es apropiado para el entorno Docker local.

### Backups

El script genera backups verificables, pero deben copiarse a almacenamiento externo, cifrado y con política de retención. Una restauración debe probarse periódicamente.

## Verificación

```powershell
python -m unittest tests.test_seguridad_integracion -v
```

```powershell
$env:SQLSERVER_SA_PASSWORD="clave_administrativa"
.\scripts\respaldar_base_datos.ps1
```
