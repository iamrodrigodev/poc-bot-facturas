param(
    [string]$Contenedor = "poc-sql-server",
    [string]$BaseDatos = "poc_bot_facturas"
)

if (-not $env:SQLSERVER_SA_PASSWORD) {
    throw "Debe definir SQLSERVER_SA_PASSWORD"
}

$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
$nombre = "${BaseDatos}_${fecha}.bak"
$rutaContenedor = "/var/opt/mssql/backup/$nombre"
$carpetaLocal = Join-Path $PSScriptRoot "..\backups"
$rutaLocal = Join-Path $carpetaLocal $nombre

New-Item -ItemType Directory -Force -Path $carpetaLocal | Out-Null
docker exec $Contenedor mkdir -p /var/opt/mssql/backup
docker exec `
    -e "SQLCMDPASSWORD=$env:SQLSERVER_SA_PASSWORD" `
    $Contenedor `
    /opt/mssql-tools18/bin/sqlcmd `
    -S localhost `
    -U sa `
    -C `
    -Q "BACKUP DATABASE [$BaseDatos] TO DISK = N'$rutaContenedor' WITH COPY_ONLY, CHECKSUM, INIT"

if ($LASTEXITCODE -ne 0) {
    throw "No se pudo generar el respaldo"
}

docker cp "${Contenedor}:${rutaContenedor}" $rutaLocal

if ($LASTEXITCODE -ne 0) {
    throw "No se pudo copiar el respaldo fuera del contenedor"
}

Write-Output $rutaLocal
