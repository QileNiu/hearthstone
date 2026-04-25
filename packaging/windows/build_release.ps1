param(
    [switch]$SkipTests,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..\..")).Path
$BuildRoot = Join-Path $Root "build\windows"
$DistRoot = Join-Path $BuildRoot "dist"
$WorkRoot = Join-Path $BuildRoot "work"
$SpecRoot = Join-Path $BuildRoot "spec"
$ReleaseRoot = Join-Path $Root "release\HearthstoneTextControl"
$ReleaseDir = Join-Path $Root "release"
$SetupPath = Join-Path $ReleaseDir "Setup.exe"
$InstallerPackageRoot = Join-Path $ReleaseDir "HearthstoneTextControl-Installer"
$InstallerPackageZip = Join-Path $ReleaseDir "HearthstoneTextControl-Installer.zip"
$VenvDir = Join-Path $BuildRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

function Invoke-HostPython {
    param([string[]]$Arguments)

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        & py -3 @Arguments
        return
    }

    & python @Arguments
}

function Get-InnoSetupCompiler {
    $iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($iscc) {
        return $iscc.Source
    }

    $candidates = @()
    if (${env:ProgramFiles(x86)}) {
        $candidates += (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe")
    }
    if ($env:ProgramFiles) {
        $candidates += (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe")
    }

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    throw "Inno Setup compiler ISCC.exe was not found. Install Inno Setup 6 on the Windows build machine, or rerun with -SkipInstaller to build only the portable folder."
}

Push-Location $Root
try {
    New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null
    Invoke-HostPython @("-m", "venv", $VenvDir)

    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install ".[windows]" pyinstaller

    if (-not $SkipTests) {
        & $VenvPython -m unittest discover -s tests
    }

    Remove-Item -Recurse -Force $DistRoot, $WorkRoot, $SpecRoot, $ReleaseRoot, $InstallerPackageRoot -ErrorAction SilentlyContinue
    Remove-Item -Force (Join-Path $ReleaseDir "HearthstoneTextControl.zip"), $SetupPath, $InstallerPackageZip -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $ReleaseRoot | Out-Null

    & $VenvPython -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --windowed `
        --name HearthstoneTextControl `
        --paths (Join-Path $Root "src") `
        --collect-data hearthstone_text_control `
        --distpath $DistRoot `
        --workpath $WorkRoot `
        --specpath $SpecRoot `
        (Join-Path $Root "packaging\windows\gui_entry.py")

    Copy-Item (Join-Path $DistRoot "HearthstoneTextControl.exe") $ReleaseRoot
    Copy-Item (Join-Path $Root "config\example_profile.json") (Join-Path $ReleaseRoot "profile.json")

    Set-Content -Encoding UTF8 -Path (Join-Path $ReleaseRoot "run-dry-run.cmd") -Value @(
        '@echo off'
        'cd /d "%~dp0"'
        'HearthstoneTextControl.exe --profile "%~dp0profile.json"'
    )

    Set-Content -Encoding UTF8 -Path (Join-Path $ReleaseRoot "run-live.cmd") -Value @(
        '@echo off'
        'cd /d "%~dp0"'
        'HearthstoneTextControl.exe --profile "%~dp0profile.json" --live'
    )

    Set-Content -Encoding UTF8 -Path (Join-Path $ReleaseRoot "sample-commands.txt") -Value @(
        'help'
        'exit'
    )

    Set-Content -Encoding UTF8 -Path (Join-Path $ReleaseRoot "README_RELEASE.txt") -Value @(
        'Hearthstone Text Control Windows GUI'
        ''
        'Final user requirements:'
        '- Windows'
        '- No Python installation required'
        '- No pip installation required'
        '- No pyautogui installation required'
        '- No PowerShell usage required'
        ''
        'Files:'
        '- HearthstoneTextControl.exe: GUI application'
        '- profile.json: editable coordinate profile'
        '- run-dry-run.cmd: open GUI in dry-run mode'
        '- run-live.cmd: open GUI in live mouse-control mode'
        '- sample-commands.txt: sample text commands'
        ''
        'Recommended use:'
        '1. Open Hearthstone and keep the window position fixed.'
        '2. Open Hearthstone Text Control from the desktop or Start menu.'
        '3. First use dry-run mode to confirm command output.'
        '4. Calibrate coordinates in profile.json for the target screen.'
        '5. Enable live mode in the GUI only after coordinates are correct.'
        ''
        'Emergency stop:'
        'Move the mouse to a screen corner to trigger the pyautogui fail-safe.'
    )

    $ZipPath = Join-Path $Root "release\HearthstoneTextControl.zip"
    Remove-Item -Force $ZipPath -ErrorAction SilentlyContinue
    Compress-Archive -Path (Join-Path $ReleaseRoot "*") -DestinationPath $ZipPath

    if (-not $SkipInstaller) {
        $Iscc = Get-InnoSetupCompiler
        & $Iscc `
            "/DSourceDir=$ReleaseRoot" `
            "/DOutputDir=$ReleaseDir" `
            (Join-Path $ScriptDir "HearthstoneTextControl.iss")

        New-Item -ItemType Directory -Force -Path $InstallerPackageRoot | Out-Null
        Copy-Item $SetupPath (Join-Path $InstallerPackageRoot "Setup.exe")
        $InstructionsName = ([string][char]0x4F7F) + ([string][char]0x7528) + ([string][char]0x8BF4) + ([string][char]0x660E) + ".md"
        Copy-Item (Join-Path $Root "WINDOWS_INSTALL.md") (Join-Path $InstallerPackageRoot $InstructionsName)
        Compress-Archive -Path (Join-Path $InstallerPackageRoot "*") -DestinationPath $InstallerPackageZip
    }

    Write-Host "Release created:"
    Write-Host "  $ReleaseRoot"
    Write-Host "  $ZipPath"
    if (-not $SkipInstaller) {
        Write-Host "  $SetupPath"
        Write-Host "  $InstallerPackageZip"
    }
}
finally {
    Pop-Location
}
