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
        (Join-Path $Root "src\hearthstone_text_control\gui.py")

    Copy-Item (Join-Path $DistRoot "HearthstoneTextControl.exe") $ReleaseRoot
    Copy-Item (Join-Path $Root "config\example_profile.json") (Join-Path $ReleaseRoot "profile.json")

    Set-Content -Encoding UTF8 -Path (Join-Path $ReleaseRoot "run-dry-run.cmd") -Value @"
@echo off
cd /d "%~dp0"
HearthstoneTextControl.exe --profile "%~dp0profile.json"
"@

    Set-Content -Encoding UTF8 -Path (Join-Path $ReleaseRoot "run-live.cmd") -Value @"
@echo off
cd /d "%~dp0"
HearthstoneTextControl.exe --profile "%~dp0profile.json" --live
"@

    Set-Content -Encoding UTF8 -Path (Join-Path $ReleaseRoot "sample-commands.txt") -Value @"
选择卡组 法师
开始游戏
出牌 1 目标 对方英雄
打脸 1
结束回合
"@

    Set-Content -Encoding UTF8 -Path (Join-Path $ReleaseRoot "README_RELEASE.txt") -Value @"
Hearthstone Text Control Windows 图形界面版

最终用户要求：
- Windows
- 不需要安装 Python
- 不需要安装 pip
- 不需要安装 pyautogui
- 不需要打开 PowerShell

文件说明：
- HearthstoneTextControl.exe：图形界面主程序
- profile.json：可编辑的坐标配置文件
- run-dry-run.cmd：以安全 dry-run 模式打开图形界面
- run-live.cmd：以 live 鼠标控制模式打开图形界面
- sample-commands.txt：示例文字命令

推荐使用：
1. 打开炉石传说，并保持窗口位置固定。
2. 从桌面或开始菜单打开 Hearthstone Text Control。
3. 先不要勾选 live 模式，用 dry-run 日志确认命令。
4. 根据屏幕校准 profile.json 坐标。
5. 坐标正确后，在图形界面里勾选 live 模式。

紧急停止：
把鼠标移动到屏幕角落，触发 pyautogui fail-safe。
"@

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
        Copy-Item (Join-Path $Root "WINDOWS_INSTALL.md") (Join-Path $InstallerPackageRoot "使用说明.md")
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
