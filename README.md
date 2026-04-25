# Hearthstone Text Control

This is a first prototype of a GUI-based text-command accessibility controller for Hearthstone on Windows.

It is designed for manual assistive control: the user types a command or clicks a UI button, and the program performs only that requested mouse action sequence. It does not play automatically, read game memory, inspect hidden state, or make gameplay decisions.

## Source Quick Start

The source CLI dry-run works on any system and only prints actions:

```bash
PYTHONPATH=src python -m hearthstone_text_control --command "选择卡组 法师" --command "开始游戏" --command "结束回合"
```

For GUI development from source:

```bash
PYTHONPATH=src python -m hearthstone_text_control.gui
```

## Commands

- `帮助`
- `选择卡组 <名称>`
- `开始游戏`
- `出牌 <手牌编号>`
- `出牌 <手牌编号> 目标 <目标>`
- `打脸`
- `打脸 <己方随从编号>`
- `攻击 <己方随从编号> <目标>`
- `结束回合`
- `点击 <配置点名称>`
- `等待 <秒数>`
- `退出`

Examples:

```text
选择卡组 法师
开始游戏
出牌 1
出牌 2 目标 对方英雄
打脸 1
结束回合
```

## Configuration

Coordinates live in JSON profiles under `config/`. Copy `config/example_profile.json` and adjust positions for your Windows resolution and Hearthstone layout.

The default profile contains placeholder 1920x1080 coordinates. Real positions must be calibrated on the target machine.

Important groups:

- `points`: named UI points such as `play_button`, `end_turn`, `enemy_hero`
- `decks`: deck names mapped to click coordinates
- `hand_slots`: hand card positions by number
- `board_slots`: friendly board minion positions by number
- `aliases`: user-facing names mapped to `points` keys

## Safety Notes

Keep Hearthstone in windowed or borderless mode and verify coordinates in dry-run before live mode. In live mode, `pyautogui` fail-safe is enabled, so moving the mouse to a screen corner should abort automation.

## Standalone Windows Installer

For final users who should not install Python or dependencies, build a standalone `Setup.exe` with GitHub Actions or on a Windows build machine.

GitHub Actions can build the installer from the web UI:

- Open Actions.
- Run `Build Windows Installer`.
- Download the `HearthstoneTextControl-Setup` artifact.
- Extract `HearthstoneTextControl-Installer.zip`.
- Give that zip to the final user.

Windows build-machine command:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\packaging\windows\build_release.ps1
```

The build machine needs Python 3.9+ and Inno Setup 6. The final user does not need either.

Give the final user:

- `release\HearthstoneTextControl-Installer.zip`

The final user extracts that package and double-clicks `Setup.exe`; it installs the app, creates shortcuts, and launches the Chinese GUI after installation. The final user does not need PowerShell or Python.

See `WINDOWS_INSTALL.md` for the full build, installation, usage, calibration, and troubleshooting guide.
