# Configuración de variables de entorno para Google Sheets
# Reemplaza los valores con tus credenciales reales

# ID del Spreadsheet de Google Sheets
$env:GOOGLE_SHEETS_ID = "TU_GOOGLE_SHEETS_ID_AQUI"

# Credenciales de GCP (opción 1: variables individuales)
$env:GCP_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nTU_PRIVATE_KEY_AQUI\n-----END PRIVATE KEY-----\n"
$env:GCP_CLIENT_EMAIL = "tu-service-account@tu-project.iam.gserviceaccount.com"
$env:GCP_PROJECT_ID = "tu-project-id"
$env:GCP_PRIVATE_KEY_ID = "tu-private-key-id"

# O usa GCP_SERVICE_ACCOUNT_JSON si tienes el JSON completo
# $env:GCP_SERVICE_ACCOUNT_JSON = '{"type": "service_account", ... }'

Write-Host "Variables de entorno configuradas. Reemplaza los placeholders con tus valores reales."
Write-Host "Para hacer persistentes, ejecuta como administrador y usa [Environment]::SetEnvironmentVariable"