# Windows security and trust

EcoTally is an offline desktop tool. It reads local tabular files, performs
calculations locally, and writes reports chosen by the user. The application
does not open listening ports, contact a server, download updates, or send
analysis data over the network.

## Firewall versus SmartScreen

Windows Defender Firewall filters network traffic. EcoTally does not require a
firewall exception because it has no network feature.

The “Windows protected your PC” or “unknown publisher” screen is Microsoft
Defender SmartScreen, not a firewall prompt. SmartScreen evaluates the
reputation of the downloaded file and its code-signing publisher. A new or
unsigned executable can show a warning even when it contains no networking
code.

Do not disable Windows security features to run EcoTally. Download releases
only from the official GitHub repository and verify the published SHA-256
checksum. A valid Authenticode signature should be checked before a release is
described as signed.

## Verify a downloaded release

In PowerShell, from the download directory:

```powershell
Get-FileHash .\EcoTally.exe -Algorithm SHA256
Get-AuthenticodeSignature .\EcoTally.exe |
    Select-Object Status, StatusMessage, SignerCertificate
```

Compare the hash with `EcoTally.exe.sha256` from the same GitHub Release.

## Trusted release path

The build accepts an optional `ECOTALLY_SIGNING_CERT_THUMBPRINT` environment
variable. When configured with a trusted code-signing certificate, the build
uses SignTool with SHA-256 and RFC 3161 timestamping, then fails unless Windows
reports a valid Authenticode signature.

The GitHub Windows workflow also contains an opt-in Microsoft Artifact Signing
step. It stays disabled until the repository has a verified Artifact Signing
account and GitHub OpenID Connect configuration. Self-signed certificates are
not used because they do not establish public trust or remove SmartScreen
warnings.
