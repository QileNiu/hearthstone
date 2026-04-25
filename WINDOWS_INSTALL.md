# Windows 图形界面安装和使用说明

这份文档面向最终用户。正常使用时，你会拿到一个安装包，解压后双击里面的 `Setup.exe` 安装，然后双击桌面或开始菜单里的快捷方式打开图形界面。

最终用户不需要安装 Python、pip、pyautogui、PyInstaller、Inno Setup，也不需要打开 PowerShell 执行命令。

如果你的 Windows 电脑只有鼠标键盘操作能力，不想使用命令行，那么它只需要用来安装和运行软件，不应该用来构建安装包。发布者应该提前给你一个类似这样的文件：

```text
HearthstoneTextControl-Installer.zip
```

## 1. 最终用户安装步骤

你会拿到一个压缩包：

```text
HearthstoneTextControl-Installer.zip
```

解压后里面应该有：

```text
Setup.exe
使用说明.md
```

安装步骤：

1. 解压 `HearthstoneTextControl-Installer.zip`。
2. 双击解压出来的 `Setup.exe`。
3. 按安装器提示继续。
4. 如果希望桌面上有快捷方式，保留桌面快捷方式选项。
5. 点击 Finish 完成安装。
6. 安装完成后，程序会自动打开图形界面。

程序默认安装到：

```text
%LOCALAPPDATA%\Programs\HearthstoneTextControl
```

这个位置是当前用户自己的程序目录，通常不需要管理员权限。

## 2. 如何打开程序

安装后可以从这些位置打开：

- 桌面快捷方式：`Hearthstone Text Control`
- 开始菜单：`Hearthstone Text Control`

双击快捷方式后，会打开一个中文图形界面窗口，标题是：

```text
炉石文字控制器
```

你可以在这个窗口里输入文字命令，也可以点击常用按钮，例如：

- 选择卡组
- 开始游戏
- 出牌
- 出牌到目标
- 打脸
- 攻击目标
- 结束回合
- 点击英雄技能

## 3. 第一次使用建议

第一次打开时，建议先不要启用 live 模式。

界面右上角有：

```text
live 模式：真实控制鼠标
```

如果这个选项没有勾选，程序处于 dry-run 模式。

dry-run 模式只会在右侧日志里显示将要点击的位置，不会真的移动鼠标。你可以先用它确认命令是否正确。

建议第一次输入：

```text
帮助
```

然后试一下：

```text
选择卡组 法师
开始游戏
结束回合
```

如果右侧日志出现模拟点击记录，说明程序正常。

## 4. live 模式使用方法

确认 dry-run 没问题后，再启用 live 模式。

使用 live 模式前建议：

1. 打开炉石传说。
2. 把炉石窗口放在固定位置。
3. 推荐使用窗口化或无边框窗口模式。
4. 每次尽量使用相同的屏幕分辨率。
5. 确认坐标配置已经适配你的屏幕。

然后在图形界面右上角勾选：

```text
live 模式：真实控制鼠标
```

勾选后，你在 UI 里输入的命令或点击的按钮会变成真实鼠标点击。

## 5. 图形界面各区域说明

顶部区域：

- `坐标配置`：当前使用的 `profile.json`
- `选择配置`：选择另一个坐标配置文件
- `编辑配置`：用记事本打开当前坐标配置
- `live 模式：真实控制鼠标`：切换 dry-run 和真实控制模式

命令输入区域：

- 输入一行命令
- 点击 `执行命令`
- 或按 Enter 执行

左侧按钮区域：

- `卡组和对局`：选择卡组、开始游戏、结束回合
- `出牌`：选择手牌编号并出牌
- `攻击`：选择我方随从编号并攻击
- `快捷点击`：点击对方英雄、我方英雄、英雄技能、确认

右侧日志区域：

- 显示执行过的命令
- 显示模拟点击或真实点击坐标
- 显示错误信息

## 6. 常用文字命令

通用命令：

```text
帮助
退出
等待 1
```

卡组和对局：

```text
选择卡组 法师
开始游戏
结束回合
```

出牌：

```text
出牌 1
出牌 2 目标 对方英雄
出牌 3 目标 我方英雄
```

攻击：

```text
打脸
打脸 1
攻击 1 对方英雄
```

快捷点击：

```text
点击 结束回合
点击 对方英雄
点击 我方英雄
点击 英雄技能
点击 确认
```

## 7. 坐标配置文件

程序通过点击屏幕坐标控制炉石。

坐标配置文件是：

```text
%LOCALAPPDATA%\Programs\HearthstoneTextControl\profile.json
```

你可以在图形界面点击：

```text
编辑配置
```

它会用记事本打开 `profile.json`。

重要配置段如下。

常用按钮和目标：

```json
"points": {
  "play_button": [960, 860],
  "end_turn": [1575, 520],
  "enemy_hero": [960, 185]
}
```

卡组位置：

```json
"decks": {
  "法师": [530, 360]
}
```

手牌位置：

```json
"hand_slots": {
  "1": [650, 930],
  "2": [760, 930]
}
```

我方场上随从位置：

```json
"board_slots": {
  "1": [690, 575],
  "2": [810, 575]
}
```

如果点击位置不对，修改对应坐标，保存 `profile.json`，然后重新打开程序。

## 8. 紧急停止

live 模式使用 pyautogui 的 fail-safe 机制。

如果鼠标开始点错位置，可以这样停止：

```text
把鼠标移动到屏幕角落。
```

也可以直接关闭图形界面窗口。

## 9. 卸载

通过 Windows 设置卸载：

```text
Settings -> Apps -> Installed apps -> Hearthstone Text Control -> Uninstall
```

如果开始菜单里有卸载入口，也可以从开始菜单卸载。

## 10. 常见问题

如果 `Setup.exe` 打不开：

- 右键点击 `Setup.exe`。
- 选择 Properties。
- 如果看到 Unblock 选项，勾选它。
- 再次运行 `Setup.exe`。

如果 Windows SmartScreen 弹出警告：

- 这是因为当前安装器还没有代码签名。
- 如果你确认安装包来源可信，可以点击 More info，然后选择 Run anyway。

如果程序打开了，但点击位置不对：

- 先关闭 live 模式，用 dry-run 看日志。
- 检查 `profile.json`。
- 确保炉石每次都在相同分辨率和相同窗口位置。

如果 live 模式不移动鼠标：

- 确认 UI 右上角已经勾选 live 模式。
- 确认炉石窗口可见，没有最小化。
- 尝试先打开炉石，再打开本程序。

如果中文输入不稳定：

- 可以把命令复制粘贴到输入框。
- 每次只输入一行命令。

## 11. 最终用户检查清单

```text
[ ] 双击 Setup.exe 能完成安装
[ ] 桌面或开始菜单快捷方式能打开图形界面
[ ] 不勾选 live 模式时，命令只在日志里显示模拟点击
[ ] profile.json 坐标已经校准
[ ] 勾选 live 模式后，UI 按钮和文字命令能正确控制炉石
```

## 12. 发布者附录：如何生成最终安装包

这一节只给发布者或开发者看，最终用户不需要执行。

### 方式 A：GitHub 网页构建

如果项目已经放在 GitHub 仓库里，可以用网页构建，不需要在最终用户 Windows 电脑上打开命令行。

步骤：

1. 打开 GitHub 仓库网页。
2. 进入 Actions。
3. 选择 `Build Windows Installer`。
4. 点击 `Run workflow`。
5. 等待构建完成。
6. 打开完成的 workflow run。
7. 在 Artifacts 里下载 `HearthstoneTextControl-Setup`。
8. 解压下载的 artifact，得到 `HearthstoneTextControl-Installer.zip`。
9. 把 `HearthstoneTextControl-Installer.zip` 发给最终用户。

### 方式 B：Windows 构建机命令行构建

发布者需要在一台 Windows 构建机上安装：

- Python 3.9 或更新版本
- Inno Setup 6

然后在项目目录运行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\packaging\windows\build_release.ps1
```

构建成功后会生成最终安装包：

```text
release\HearthstoneTextControl-Installer.zip
```

把 `release\HearthstoneTextControl-Installer.zip` 发给最终用户即可。最终用户解压后双击 `Setup.exe` 安装。
