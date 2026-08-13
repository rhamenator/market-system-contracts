[CmdletBinding()]
param(
    [string]$InstallDir = $(if ($env:MARKET_SYSTEM_CONTRACTS_HOME) {
        $env:MARKET_SYSTEM_CONTRACTS_HOME
    } else {
        Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'MarketSystemContracts'
    })
)

$sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Recurse -Force -Path (Join-Path $sourceDir 'schemas'), (Join-Path $sourceDir 'docs'), (Join-Path $sourceDir 'testdata') -Destination $InstallDir
Write-Host "Market System Contracts installed in $InstallDir"
