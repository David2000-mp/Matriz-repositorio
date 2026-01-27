# Script para configurar variables de entorno de Google Sheets de forma persistente
# Ejecutar como administrador para que sean permanentes

param(
    [string]$SheetsId,
    [string]$PrivateKey,
    [string]$ClientEmail,
    [string]$ProjectId,
    [string]$PrivateKeyId
)

if (-not $SheetsId) {
    Write-Host "Uso: .\configure_env.ps1 -SheetsId 'TU_SHEETS_ID' -PrivateKey 'TU_PRIVATE_KEY' -ClientEmail 'tu@email.com' -ProjectId 'tu-project' -PrivateKeyId 'tu-key-id'"
    exit 1
}

# Configurar variables de entorno persistentes
[Environment]::SetEnvironmentVariable("GOOGLE_SHEETS_ID", $SheetsId, "Machine")
[Environment]::SetEnvironmentVariable("GCP_PRIVATE_KEY", $PrivateKey, "Machine")
[Environment]::SetEnvironmentVariable("GCP_CLIENT_EMAIL", $ClientEmail, "Machine")
[Environment]::SetEnvironmentVariable("GCP_PROJECT_ID", $ProjectId, "Machine")
[Environment]::SetEnvironmentVariable("GCP_PRIVATE_KEY_ID", $PrivateKeyId, "Machine")

Write-Host "Variables de entorno configuradas permanentemente."
Write-Host "Reinicia la aplicación para que tome efecto."