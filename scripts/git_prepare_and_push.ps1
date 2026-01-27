# Safe Git prepare and push script for cloud deployment
# Usage: PowerShell -> .\scripts\git_prepare_and_push.ps1

function Ask-YesNo($msg) {
    $r = Read-Host "$msg (Y/n)"
    if ($r -eq '' -or $r -eq 'Y' -or $r -eq 'y') { return $true }
    return $false
}

Write-Host "== Git prepare & push helper =="

# 1) Check git installed
try {
    git --version > $null 2>&1
} catch {
    Write-Error "git no está disponible en este entorno. Instala Git y vuelve a ejecutar este script."
    exit 1
}

# 2) Ensure inside a git repo
$inside = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "No parece ser un repositorio git (no inside-work-tree). Ejecuta 'git init' o usa un repo correcto."
    exit 1
}

# 3) Scan for tracked sensitive files
Write-Host "Buscando archivos sensibles ya rastreados..."
$patterns = "secrets","secrets.toml","service_account","service-account","credentials","GCP","private_key",".env",".pem",".key",".json"
$matches = @()
$ls = git ls-files
foreach ($p in $patterns) {
    $m = $ls | Select-String -Pattern $p -SimpleMatch | ForEach-Object { $_.Line }
    if ($m) { $matches += $m }
}
$matches = $matches | Sort-Object -Unique
if ($matches.Count -gt 0) {
    Write-Warning "Se encontraron archivos rastreados potencialmente sensibles:"
    $matches | ForEach-Object { Write-Host "  $_" }
    if (-not (Ask-YesNo "¿Deseas removerlos del índice (git rm --cached) antes de continuar?")) {
        Write-Error "Abortando por seguridad. Revisa los archivos listados y remuévelos manualmente si es necesario."
        exit 1
    }
    foreach ($f in $matches) {
        Write-Host "Ejecutando: git rm --cached --quiet -- "$f""
        git rm --cached -- "$f" 2>$null
    }
    git add -A
    git commit -m "chore: remove sensitive files from index" 2>$null
    Write-Host "Archivos sensibles removidos del índice y commit creado."
} else {
    Write-Host "No hay archivos sensibles rastreados."
}

# 4) Ensure .gitignore contains recommended patterns (idempotente)
$repoRoot = git rev-parse --show-toplevel
$gitignore = Join-Path $repoRoot ".gitignore"
$addPatterns = @(
    "*service_account*.json",
    "*service-account*.json",
    "credentials.json",
    "secrets.toml",
    "*.key",
    "*.pem",
    "secrets/",
    ".env",
    ".streamlit/secrets.toml"
)
$changed = $false
if (-not (Test-Path $gitignore)) {
    "# Auto-generated .gitignore additions`n" | Out-File -FilePath $gitignore -Encoding utf8
}
$existing = Get-Content $gitignore -ErrorAction SilentlyContinue
foreach ($p in $addPatterns) {
    if ($existing -notcontains $p) {
        Add-Content -Path $gitignore -Value $p
        $changed = $true
        Write-Host "Añadido a .gitignore: $p"
    }
}
if ($changed) {
    git add .gitignore
    git commit -m "chore: update .gitignore with credential patterns" 2>$null
    Write-Host ".gitignore actualizado y commiteado."
} else {
    Write-Host ".gitignore ya contenía los patrones recomendados."
}

# 5) Create branch
$branchName = "fix/cloud-deployment"
Write-Host "Creando y cambiando a rama: $branchName"
git checkout -b $branchName

# 6) Add & commit all changes
Write-Host "Staging all changes..."
git add -A

$commitMsg = 'Final: QA verificado, dependencias sincronizadas y rutas normalizadas para despliegue en la nube'
if (git commit -m "$commitMsg") {
    Write-Host "Commit creado: $commitMsg"
} else {
    Write-Host "No se crearon nuevos commits (probablemente no hay cambios)."
}

# 7) Push if origin exists
try {
    $originUrl = git remote get-url origin 2>$null
    if ($LASTEXITCODE -eq 0 -and $originUrl) {
        Write-Host "Remote 'origin' detectado: $originUrl"
        if (Ask-YesNo "¿Deseas hacer push de la rama $branchName a origin ahora?") {
            git push -u origin $branchName
            Write-Host "Push realizado: origin/$branchName"
        } else {
            Write-Host "No se realizó push. Puedes usar: git push -u origin $branchName"
        }
    } else {
        Write-Warning "No se detectó remote 'origin'. Para subir, añade el remoto y ejecuta: git push -u origin $branchName"
    }
} catch {
    Write-Warning "Error comprobando remote origin. Comprueba manualmente."
}

Write-Host "== Script finalizado =="
