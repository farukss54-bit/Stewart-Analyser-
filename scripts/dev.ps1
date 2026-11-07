# Yerel geliştirme: API (8000) ve web (3000) birlikte başlar.
# Depo kökünden çalıştırın:  .\scripts\dev.ps1
# Yalnızca ön kontrolleri yapmak için:  .\scripts\dev.ps1 -Check
# Durdurmak için Ctrl+C. Önce bir kez: pip install -r api/requirements.txt ve (web klasöründe) npm install

param([switch]$Check)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$webDir = Join-Path $root "web"
$apiPort = 8000
$webPort = 3000

function Test-PortFree([int]$port) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
    try { $listener.Start(); return $true }
    catch { return $false }
    finally { $listener.Stop() }
}

# Ön kontroller: eksikleri başlamadan önce, anlaşılır bir mesajla bildir
$sorunlar = @()
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    $sorunlar += "python bulunamadı. Python kurulu ve PATH içinde olmalı."
}
else {
    & python -c "import uvicorn, fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $sorunlar += "API bağımlılıkları kurulu değil. Çalıştırın: pip install -r api/requirements.txt"
    }
}
if (-not (Test-Path (Join-Path $webDir "node_modules"))) {
    $sorunlar += "web bağımlılıkları kurulu değil. Çalıştırın: cd web; npm install"
}
if (-not (Test-PortFree $apiPort)) { $sorunlar += "Port $apiPort dolu. API başlatılamaz." }
if (-not (Test-PortFree $webPort)) { $sorunlar += "Port $webPort dolu. Web başlatılamaz." }

if ($sorunlar.Count -gt 0) {
    Write-Host "Başlatılamadı:" -ForegroundColor Red
    $sorunlar | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

if ($Check) {
    Write-Host "Ön kontroller geçti. Sunucular başlatılmadı (-Check)."
    exit 0
}

$api = Start-Process -FilePath "python" `
    -ArgumentList "-m", "uvicorn", "api.main:app", "--port", "$apiPort" `
    -WorkingDirectory $root -PassThru -NoNewWindow

$webaldi = $false
try {
    Push-Location $webDir
    $webaldi = $true
    npm run dev
}
finally {
    if ($webaldi) { Pop-Location }
    if ($api -and -not $api.HasExited) { Stop-Process -Id $api.Id }
}
