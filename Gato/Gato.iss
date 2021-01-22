; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{F8099CCA-6482-4114-9A3C-4A9BE6D68A95}
AppName=CATBox
AppVerName=CATBox 1.2.6
AppPublisher=Schliep & Hochstaettler
AppPublisherURL=http://schliep.org/CATBox
AppSupportURL=http://schliep.org/CATBox
AppUpdatesURL=http://schliep.org/CATBox
DefaultDirName={pf}\Gato
DefaultGroupName=CATBox
AllowNoIcons=true
LicenseFile=LGPL.txt
InfoBeforeFile=installer-before.txt
InfoAfterFile=installer-after.txt
OutputBaseFilename=CATBox-setup
Compression=lzma
SolidCompression=true
AppCopyright=� 2020 Alexander Schliep
ShowLanguageDialog=no

[Languages]
Name: english; MessagesFile: compiler:Default.isl

[Tasks]
Name: desktopicon; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: unchecked

[Files]
; order like in explorer
Source: dist\tcl\tcl8.5\*; DestDir: {app}\tcl\tcl8.5\
Source: dist\tcl\tcl8.5\encoding\*; DestDir: {app}\tcl\tcl8.5\encoding\
Source: dist\tcl\tcl8.5\http1.0\*; DestDir: {app}\tcl\tcl8.5\http1.0\
Source: dist\tcl\tcl8.5\msgs\*; DestDir: {app}\tcl\tcl8.5\msgs\
Source: dist\tcl\tcl8.5\opt0.4\*; DestDir: {app}\tcl\tcl8.5\opt0.4\
Source: dist\tcl\tcl8.5\tzdata\*; DestDir: {app}\tcl\tcl8.5\tzdata\
Source: dist\tcl\tk8.5\*; DestDir: {app}\tcl\tk8.5
Source: dist\tcl\tk8.5\demos\*; DestDir: {app}\tcl\tk8.5\demos\
Source: dist\tcl\tk8.5\images\*; DestDir: {app}\tcl\tk8.5\images\
Source: dist\tcl\tk8.5\msgs\*; DestDir: {app}\tcl\tk8.5\msgs\
Source: dist\tcl\tk8.5\demos\*; DestDir: {app}\tcl\tk8.5\demos\
Source: dist\tcl\tk8.5\ttk\*; DestDir: {app}\tcl\tk8.5\ttk\
Source: dist\_ctypes.pyd; DestDir: {app}
Source: dist\_hashlib.pyd; DestDir: {app}
Source: dist\_socket.pyd; DestDir: {app}
Source: dist\_ssl.pyd; DestDir: {app}
Source: dist\_tkinter.pyd; DestDir: {app}
Source: dist\bz2.pyd; DestDir: {app}
Source: dist\CRYPT32.dll; DestDir: {app}
Source: dist\Gato.exe; DestDir: {app}; Flags: ignoreversion
Source: dist\Gato.zip; DestDir: {app}
Source: dist\Gred.exe; DestDir: {app}; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files
Source: dist\pyexpat.pyd; DestDir: {app}
Source: dist\python27.dll; DestDir: {app}
Source: dist\select.pyd; DestDir: {app}
Source: dist\tcl85.dll; DestDir: {app}
Source: dist\tk85.dll; DestDir: {app}
Source: dist\unicodedata.pyd; DestDir: {app}
Source: sample.cat; DestDir: {userdocs}\CATBox; Tasks: ; Languages: 
Source: BFS.alg; DestDir: {userdocs}\CATBox
Source: BFS.pro; DestDir: {userdocs}\CATBox
Source: ..\CATBox\02-GraphsNetworks\*; DestDir: {userdocs}\CATBox\02-GraphsNetworks\
Source: ..\CATBox\03-MinimalSpanningTrees\*; DestDir: {userdocs}\CATBox\03-MinimalSpanningTrees\
Source: ..\CATBox\04-LPDuality\*; DestDir: {userdocs}\CATBox\04-LPDuality\
Source: ..\CATBox\05-ShortestPaths\*; DestDir: {userdocs}\CATBox\05-ShortestPaths\
Source: ..\CATBox\06-MaximalFlows\*; DestDir: {userdocs}\CATBox\06-MaximalFlows\
Source: ..\CATBox\07-MinimumCostFlows\*; DestDir: {userdocs}\CATBox\07-MinimumCostFlows\
Source: ..\CATBox\08-Matching\*; DestDir: {userdocs}\CATBox\08-Matching\
Source: ..\CATBox\09-WeightedMatching\*; DestDir: {userdocs}\CATBox\09-WeightedMatching\
Source: ..\CATBox\Appendix\*; DestDir: {userdocs}\CATBox\Appendix\


[Icons]
Name: {group}\CATBox; Filename: {app}\Gato.exe
Name: {commondesktop}\CATBox; Filename: {app}\Gato.exe; Tasks: desktopicon

[Run]
Filename: {app}\Gato.exe; Description: {cm:LaunchProgram,CATBox}; Flags: nowait postinstall skipifsilent

[Dirs]
Name: {app}\tcl
Name: {userdocs}\CATBox; Flags: uninsalwaysuninstall
Name: {userdocs}\CATBox\02-GraphsNetworks
Name: {userdocs}\CATBox\09-WeightedMatching
Name: {userdocs}\CATBox\03-MinimalSpanningTrees
Name: {userdocs}\CATBox\04-LPDuality
Name: {userdocs}\CATBox\05-ShortestPaths
Name: {userdocs}\CATBox\06-MaximalFlows
Name: {userdocs}\CATBox\07-MinimumCostFlows
Name: {userdocs}\CATBox\08-Matching
Name: {userdocs}\CATBox\Appendix
