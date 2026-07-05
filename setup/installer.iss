; DevTrack - Development Activity Tracker
; Copyright (c) 2026 Ivan Timov. All rights reserved.

#define MyAppName "DevTrack"
#define MyAppVersion "1.0"
#define MyAppPublisher "Ivan Timov"
#define MyAppURL "https://github.com/WhatisevenCalc/devtrack"
#define MyAppExeName "DevTrack.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=DevTrack_Installer_v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\resources\clock.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UsePreviousAppDir=yes
UsePreviousGroup=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
Source: "files\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "files\INSTRUCTIONS.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\resources\branding\logo_256.png"; DestDir: "{app}\resources"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch DevTrack"; Flags: postinstall nowait skipifsilent shellexec

[UninstallRun]
Filename: "{cmd}"; Parameters: "/C taskkill /IM DevTrack.exe /F /T"; Flags: runhidden

[Code]
var
  IsUpgrade: Boolean;

function GetUninstallString: string;
var
  sUnInstPath, sUnInstallString: String;
begin
  Result := '';
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgradeAvailable: Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

procedure KillDevTrack;
var
  ResultCode: Integer;
begin
  Exec(ExpandConstant('{cmd}'), '/C taskkill /IM DevTrack.exe /F /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  ResultCode: Integer;
  uninstallString: string;
begin
  Result := True;
  if CurPageID = wpSelectDir then
  begin
    if IsUpgradeAvailable then
    begin
      if MsgBox('DevTrack is already installed. Uninstall the previous version first?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        KillDevTrack;
        uninstallString := RemoveQuotes(GetUninstallString());
        if Exec(ExpandConstant(uninstallString), '/SILENT', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
        begin
          IsUpgrade := True;
          Sleep(500);
        end;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    if IsUpgradeAvailable and not IsUpgrade then
      KillDevTrack;
  end;
end;

procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel1.Caption := 'Welcome to DevTrack Setup';
  WizardForm.WelcomeLabel2.Caption := 'Installs DevTrack on your computer.'#13#10#13#10 +
    'DevTrack tracks your focused work time by monitoring your selected application.'#13#10#13#10 +
    'Copyright (c) 2026 Ivan Timov. All rights reserved.';
end;
