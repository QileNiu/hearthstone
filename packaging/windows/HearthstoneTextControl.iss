#define MyAppName "Hearthstone Text Control"
#define MyAppExeName "HearthstoneTextControl.exe"
#define MyAppVersion "0.1.0"

#ifndef SourceDir
#define SourceDir "..\..\release\HearthstoneTextControl"
#endif

#ifndef OutputDir
#define OutputDir "..\..\release"
#endif

[Setup]
AppId={{6DBB6733-3769-495E-B661-09D1D8E37F46}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Hearthstone Text Control
DefaultDirName={localappdata}\Programs\HearthstoneTextControl
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename=Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}
UsePreviousAppDir=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#SourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceDir}\profile.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "{#SourceDir}\run-dry-run.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceDir}\run-live.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceDir}\sample-commands.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceDir}\README_RELEASE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Hearthstone Text Control"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--profile ""{app}\profile.json"""; WorkingDir: "{app}"
Name: "{group}\Hearthstone Text Control Live"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--profile ""{app}\profile.json"" --live"; WorkingDir: "{app}"
Name: "{group}\Edit Coordinate Profile"; Filename: "notepad.exe"; Parameters: """{app}\profile.json"""; WorkingDir: "{app}"
Name: "{userdesktop}\Hearthstone Text Control"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--profile ""{app}\profile.json"""; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--profile ""{app}\profile.json"""; WorkingDir: "{app}"; Flags: nowait skipifsilent runasoriginaluser
