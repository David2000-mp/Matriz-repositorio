param(
    [Parameter(Mandatory=$true)]
    [string]$ServiceAccountJsonPath,

    [Parameter(Mandatory=$true)]
    [string]$GoogleSheetsId
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ServiceAccountJsonPath)) {
    throw "No existe el archivo JSON en: $ServiceAccountJsonPath"
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (-not (Test-Path ".venv\\Scripts\\python.exe")) {
    throw "No se encontro .venv. Crea el entorno primero."
}

$credsJson = Get-Content $ServiceAccountJsonPath -Raw
$env:GOOGLE_SHEETS_CREDS = $credsJson
$env:GOOGLE_SHEETS_ID = $GoogleSheetsId

Write-Output "GOOGLE_SHEETS_ID configurado para la sesion actual."
Write-Output "Ejecutando verificacion de Google Sheets..."

.\.venv\Scripts\python.exe .\verify_sheets_connection.py
