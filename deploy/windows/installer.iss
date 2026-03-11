#define MyAppName "Log Sentinel"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Aiknow"
#define MyAppExeName "sentinel.exe"
#define MyAppDirName "acc_log_sentinel"

[Setup]
AppId={{F4B9A4A3-44C8-4F4D-8A0C-C0D05D9237BE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Aiknow\{#MyAppDirName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\..\dist\installer
OutputBaseFilename=LogSentinelSetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
WizardStyle=modern

[Files]
Source: "..\..\dist\windows\acc_log_sentinel\sentinel.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\windows\acc_log_sentinel\setup.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\windows\acc_log_sentinel\sentinel.env.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\windows\acc_log_sentinel\INSTALL-WINDOWS.txt"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\data"

[Icons]
Name: "{group}\Log Sentinel Setup"; Filename: "{app}\setup.bat"
Name: "{group}\Log Sentinel Pasta"; Filename: "{app}"

[Run]
Filename: "{cmd}"; Parameters: "/C ""{app}\setup.bat"""; Description: "Executar configuracao inicial do Log Sentinel"; Flags: postinstall shellexec skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    if FileExists(ExpandConstant('{app}\sentinel.exe')) then
    begin
      Exec(ExpandConstant('{app}\sentinel.exe'), 'stop', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Exec(ExpandConstant('{app}\sentinel.exe'), 'uninstall', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
