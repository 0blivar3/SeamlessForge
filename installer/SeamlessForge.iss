#define AppName "SeamlessForge"
#define AppVersion "0.1.0"
#define AppPublisher "SeamlessForge"
#define AppExeName "SeamlessForge.exe"

[Setup]
AppId={{9A5E3D47-5F4C-4C9D-A4E8-8F4DCC2C31A8}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\SeamlessForge
DefaultGroupName={#AppName}
OutputDir=..\dist\installer
OutputBaseFilename=SeamlessForge-Setup
SetupIconFile=
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#AppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\dist\SeamlessForge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SeamlessForge"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\SeamlessForge"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch SeamlessForge"; Flags: postinstall nowait skipifsilent
