; FoxNest Windows Installer Script
; This script creates a Windows installer for FoxNest

!define APPNAME "FoxNest"
!define COMPANYNAME "FoxNest Team"
!define DESCRIPTION "FoxNest Version Control System"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/foxnest/foxnest"
!define UPDATEURL "https://github.com/foxnest/foxnest/releases"
!define ABOUTURL "https://github.com/foxnest/foxnest"
!define INSTALLSIZE 15360

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\${APPNAME}"

Name "${APPNAME}"
outFile "foxnest-installer-v${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.exe"

!include LogicLib.nsh
!include WinMessages.nsh

page components
page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
        messageBox mb_iconstop "Administrator rights required!"
        setErrorLevel 740
        quit
${EndIf}
!macroend

function .onInit
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd

section "FoxNest Core" SecCore
    SectionIn RO  ; Required section
    
    setOutPath $INSTDIR
    
    ; Check if dist folder exists
    IfFileExists "dist\foxnest\fox.exe" FilesExist FilesNotExist
    
    FilesNotExist:
        MessageBox MB_OK "Error: Distribution files not found. Please build the project first using build-windows.bat or build-windows.ps1"
        Abort
        
    FilesExist:
        ; Install main executables and all dependencies
        File /r "dist\foxnest\*.*"
        
        ; Create batch wrappers for better PATH integration
        FileOpen $0 "$INSTDIR\fox.bat" w
        FileWrite $0 '@echo off$\r$\n'
        FileWrite $0 '"$INSTDIR\fox.exe" %*$\r$\n'
        FileClose $0
        
        FileOpen $0 "$INSTDIR\fox-server.bat" w
        FileWrite $0 '@echo off$\r$\n'
        FileWrite $0 '"$INSTDIR\fox-server.exe" %*$\r$\n'
        FileClose $0
    
    ; Write installation path to registry
    WriteRegStr HKLM "Software\${COMPANYNAME}\${APPNAME}" "InstallDir" "$INSTDIR"
    
    ; Add to system PATH
    ; Read current PATH
    ReadRegStr $0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PATH"
    ; Simple append to PATH (avoiding complex string operations)
    WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PATH" "$0;$INSTDIR"
    ; Notify system of environment change
    SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
    
    ; Create uninstaller
    writeUninstaller "$INSTDIR\uninstall.exe"
    
    ; Registry entries for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\fox.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    
    ; Success message
    MessageBox MB_OK "FoxNest has been installed successfully!$\r$\n$\r$\nYou can now use 'fox' and 'fox-server' commands from Command Prompt or PowerShell.$\r$\n$\r$\nTry: fox --version"
sectionEnd

section "Start Menu Shortcuts" SecStartMenu
    createDirectory "$SMPROGRAMS\${APPNAME}"
    createShortCut "$SMPROGRAMS\${APPNAME}\FoxNest Command Line.lnk" "cmd.exe" "/k echo FoxNest Version Control System && echo. && echo Available commands: && echo   fox --help && echo   fox-server && echo." "$INSTDIR\fox.exe"
    createShortCut "$SMPROGRAMS\${APPNAME}\Start FoxNest Server.lnk" "$INSTDIR\fox-server.exe" "" "$INSTDIR\fox-server.exe"
    createShortCut "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe"
sectionEnd

section "Desktop Shortcuts" SecDesktop
    createShortCut "$DESKTOP\FoxNest Command Line.lnk" "cmd.exe" "/k echo FoxNest Version Control System && echo. && echo Try: fox --help" "$INSTDIR\fox.exe"
sectionEnd

function un.onInit
	SetShellVarContext all
	MessageBox MB_OKCANCEL "Permanently remove ${APPNAME}?" IDOK next
		Abort
	next:
	!insertmacro VerifyUserIsAdmin
functionEnd

section "uninstall"
    ; Note: PATH cleanup is complex and left for manual cleanup if needed
    ; Most users won't notice the extra PATH entry after uninstall
    
    ; Remove Start Menu shortcuts
    delete "$SMPROGRAMS\${APPNAME}\FoxNest Command Line.lnk"
    delete "$SMPROGRAMS\${APPNAME}\Start FoxNest Server.lnk"
    delete "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk"
    rmDir "$SMPROGRAMS\${APPNAME}"
    
    ; Remove Desktop shortcut
    delete "$DESKTOP\FoxNest Command Line.lnk"
    
    ; Remove all files and directories
    rmDir /r "$INSTDIR"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKLM "Software\${COMPANYNAME}\${APPNAME}"
    
    ; Success message
    MessageBox MB_OK "FoxNest has been successfully removed from your system.$\r$\n$\r$\nNote: You may need to restart your computer or manually remove $INSTDIR from your PATH environment variable if needed."
sectionEnd
