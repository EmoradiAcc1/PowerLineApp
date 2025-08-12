[Setup]
AppName=PowerLineApp
AppVersion=9.99
DefaultDirName={pf}\PowerLineApp
DefaultGroupName=PowerLineApp
OutputDir=dist
OutputBaseFilename=PowerLineAppSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "fonts\*"; DestDir: "{app}\fonts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Resources\*"; DestDir: "{app}\Resources"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PowerLineApp"; Filename: "{app}\main.exe"

[Run]
Filename: "{app}\main.exe"; Description: "اجرای PowerLineApp"; Flags: nowait postinstall skipifsilent
