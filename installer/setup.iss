; ============================================================
; VoxControl -- Inno Setup Installer Script
;
; Installs VoxControl to %LOCALAPPDATA%\Programs\VoxControl
; User data (config, logs)  → %APPDATA%\VoxControl
;
; Download Inno Setup 6: https://jrsoftware.org/isdl.php
; Build:  ISCC.exe installer\setup.iss
; ============================================================

#define MyAppName "VoxControl"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "VoxControl"
#define MyAppExeName "VoxControl.exe"
#define MyAppDescription "Voice Control for Windows"

[Setup]
AppId={{B4F2E8A1-5C3D-4E6F-A7B9-1D2E3F4A5B6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
; No admin rights required — installs to user directories
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=VoxControlSetup
SetupIconFile=..\assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Uninstall info
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
; Minimum Windows version (Windows 10)
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Start VoxControl with Windows"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
; Main application (PyInstaller output)
Source: "..\dist\VoxControl\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Default config files → %APPDATA%\VoxControl\config\
Source: "..\config\settings.yaml"; DestDir: "{userappdata}\{#MyAppName}\config"; Flags: onlyifdoesntexist
Source: "..\config\custom_commands.yaml"; DestDir: "{userappdata}\{#MyAppName}\config"; Flags: onlyifdoesntexist

[Dirs]
; Ensure user data directories exist
Name: "{userappdata}\{#MyAppName}\config"
Name: "{userappdata}\{#MyAppName}\logs"
Name: "{userappdata}\{#MyAppName}\models"

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\Configuration"; Filename: "{userappdata}\{#MyAppName}\config"; Comment: "Open configuration folder"
; Desktop shortcut (optional)
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "{#MyAppDescription}"
; Startup (optional)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon; Parameters: "--minimized"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up logs on uninstall (keep config for potential reinstall)
Type: filesandirs; Name: "{userappdata}\{#MyAppName}\logs"

[Code]
// Show a note about user data location after install
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Nothing extra needed — dirs are created by [Dirs] section
  end;
end;
