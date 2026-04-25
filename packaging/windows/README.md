# Windows 安装器发布说明

这个目录里的脚本用于发布者生成 `Setup.exe`。最终用户不需要阅读或执行这里的命令。

最终用户拿到 `release\HearthstoneTextControl-Installer.zip` 后，只需要解压并双击里面的 `Setup.exe`；安装完成后通过桌面或开始菜单快捷方式打开中文图形界面。

## 构建机要求

只在发布者的 Windows 构建机上安装：

- Python 3.9 或更新版本
- Inno Setup 6

最终用户不需要安装这些工具。

## 生成安装器

在 Windows 构建机的 PowerShell 里运行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\packaging\windows\build_release.ps1
```

脚本会生成：

```text
release\Setup.exe
release\HearthstoneTextControl-Installer.zip
release\HearthstoneTextControl.zip
release\HearthstoneTextControl\
  HearthstoneTextControl.exe
  profile.json
  run-dry-run.cmd
  run-live.cmd
  sample-commands.txt
  README_RELEASE.txt
```

给最终用户分发：

```text
release\HearthstoneTextControl-Installer.zip
```

## 最终用户体验

- 解压 `HearthstoneTextControl-Installer.zip`。
- 双击 `Setup.exe`。
- 安装到 `%LOCALAPPDATA%\Programs\HearthstoneTextControl`。
- 创建开始菜单快捷方式和可选桌面快捷方式。
- 安装完成后自动打开中文图形界面。
- 用户在 UI 里输入命令或点击按钮操作。
