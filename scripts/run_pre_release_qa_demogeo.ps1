param(
    [switch]$WithSheets
)

$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$scriptPath = "scripts\run_pre_release_qa_demogeo.py"
if ($WithSheets) {
    & $python $scriptPath --with-sheets
} else {
    & $python $scriptPath
}

exit $LASTEXITCODE
