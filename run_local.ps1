param(
	[string]$SheetsId = "1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY",
	[string]$CredsPath = "",
	[int]$Port = 8501
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

Write-Output "========================================"
Write-Output "  CHAMPILEAKS - Local Runner"
Write-Output "========================================"

$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
	throw "No se encontro .venv en el repo. Crea el entorno primero."
}

if ([string]::IsNullOrWhiteSpace($CredsPath)) {
	$defaultCreds = Join-Path $repoRoot "secrets\gcp-service-account.json"
	if (Test-Path $defaultCreds) {
		$CredsPath = $defaultCreds
	}
}

if (-not [string]::IsNullOrWhiteSpace($CredsPath)) {
	if (-not (Test-Path $CredsPath)) {
		throw "No existe el archivo de credenciales: $CredsPath"
	}

	$credsJson = Get-Content $CredsPath -Raw
	$env:GCP_SERVICE_ACCOUNT_JSON = $credsJson
	Write-Output "Credenciales cargadas desde: $CredsPath"
} else {
	Write-Output "Aviso: no se cargo archivo de credenciales."
	Write-Output "La app intentara usar st.secrets u otras variables ya definidas."
}

if (-not [string]::IsNullOrWhiteSpace($SheetsId)) {
	$env:GOOGLE_SHEETS_ID = $SheetsId
	Write-Output "GOOGLE_SHEETS_ID configurado."
}

Write-Output "Iniciando app_refactored.py en puerto $Port ..."
& $pythonExe -m streamlit run app_refactored.py --server.port $Port --server.headless true
