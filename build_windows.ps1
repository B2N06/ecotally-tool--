param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ProjectRoot
try {
    & $Python -m pip install --disable-pip-version-check pyinstaller
    $PythonRoot = & $Python -c "import sys; print(sys.base_prefix)"
    $env:TCL_LIBRARY = Join-Path $PythonRoot "tcl\tcl8.6"
    $env:TK_LIBRARY = Join-Path $PythonRoot "tcl\tk8.6"
    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --windowed `
        --name EcoTally `
        --paths src `
        desktop_entry.py
    Write-Host "Built: $ProjectRoot\dist\EcoTally.exe"
}
finally {
    Pop-Location
}
