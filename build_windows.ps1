param(
    [string]$Python = "python",
    [string]$SigningCertificateThumbprint = $env:ECOTALLY_SIGNING_CERT_THUMBPRINT,
    [string]$TimestampUrl = "http://timestamp.acs.microsoft.com"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ProjectRoot
try {
    & $Python -m pip install --disable-pip-version-check pyinstaller
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to install PyInstaller."
    }
    $PythonRoot = & $Python -c "import sys; print(sys.base_prefix)"
    $env:TCL_LIBRARY = Join-Path $PythonRoot "tcl\tcl8.6"
    $env:TK_LIBRARY = Join-Path $PythonRoot "tcl\tk8.6"
    $VersionFile = Join-Path $ProjectRoot "packaging\windows_version_info.txt"
    $Executable = Join-Path $ProjectRoot "dist\EcoTally.exe"
    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --windowed `
        --name EcoTally `
        --paths src `
        --version-file $VersionFile `
        --exclude-module socket `
        --exclude-module _socket `
        --exclude-module ssl `
        --exclude-module http `
        --exclude-module webbrowser `
        desktop_entry.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }

    if ($SigningCertificateThumbprint) {
        $SignTool = (Get-Command signtool.exe -ErrorAction Stop).Source
        & $SignTool sign `
            /sha1 $SigningCertificateThumbprint `
            /fd SHA256 `
            /tr $TimestampUrl `
            /td SHA256 `
            /d "EcoTally community ecology toolkit" `
            /du "https://github.com/B2N06/ecotally-tool--" `
            $Executable
        if ($LASTEXITCODE -ne 0) {
            throw "Authenticode signing failed."
        }
        $Signature = Get-AuthenticodeSignature -LiteralPath $Executable
        if ($Signature.Status -ne "Valid") {
            throw "Signature verification failed: $($Signature.Status)"
        }
        Write-Host "Authenticode signature: valid"
    }
    else {
        Write-Warning (
            "Built without Authenticode signing. Configure " +
            "ECOTALLY_SIGNING_CERT_THUMBPRINT for trusted releases."
        )
    }

    $Hash = Get-FileHash -LiteralPath $Executable -Algorithm SHA256
    $HashLine = "$($Hash.Hash.ToLowerInvariant())  EcoTally.exe"
    Set-Content `
        -LiteralPath (Join-Path $ProjectRoot "dist\EcoTally.exe.sha256") `
        -Value $HashLine `
        -Encoding ascii
    Write-Host "Built: $Executable"
    Write-Host "SHA-256: $($Hash.Hash)"
}
finally {
    Pop-Location
}
