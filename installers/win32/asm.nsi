;NSIS Setup Script
;--------------------------------

!define VER_DISPLAY "ZZZasmversionZZZ"

;--------------------------------
;Configuration

OutFile sheltermanager3_win32.exe
SetCompressor lzma

InstType "Full"

InstallDir $PROGRAMFILES\ASM3
InstallDirRegKey HKLM Software\ASM3 ""

;--------------------------------

;--------------------------------
;Configuration

;Names
Name "Animal Shelter Manager"
Caption "Animal Shelter Manager ${VER_DISPLAY} Setup"
LicenseData license.txt

;Interface Settings
!define MUI_ABORTWARNING
!define MUI_HEADERIMAGE
!define MUI_COMPONENTSPAGE_SMALLDESC

;Pages
Page license
Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

; Variables
Var FH

;--------------------------------
;Installer Sections

Section "Animal Shelter Manager" Main

  SetDetailsPrint textonly
  DetailPrint "Installing ASM..."
  SetDetailsPrint listonly

  SectionIn 1 RO
  SetOverwrite on

  ; Python 2.7
  IfFileExists c:\Python27\python.exe skipPython installPython
  installPython:
      MessageBox MB_OK "Your system does not have Python installed.$\nClick OK to install it."
      SetOutPath $INSTDIR
      File python-2.7.3.msi
      ExecWait '"msiexec" /i "$INSTDIR\python-2.7.3.msi"'
      Delete "$INSTDIR\python-2.7.3.msi"
  skipPython:

  ; Setuptools 6.11
  IfFileExists c:\Python27\Scripts\easy_install.exe skipSetupTools installSetupTools
  installSetupTools:
      MessageBox MB_OK "Your system does not have Python easy_install.$\nClick OK to install it."
      SetOutPath $INSTDIR
      File setuptools-0.6c11.win32-py2.7.exe
      ExecWait '$INSTDIR\setuptools-0.6c11.win32-py2.7.exe'
      Delete "$INSTDIR\setuptools-0.6c11.win32-py2.7.exe"
  skipSetupTools:

  ; web.py 0.36
  IfFileExists c:\Python27\Lib\site-packages\web.py-0.36-py2.7.egg\EGG-INFO\PKG-INFO skipWebPy installWebPy
  installWebPy:
      SetOutPath $INSTDIR
      File web.py-0.36.zip
      nsisunz::UnzipToLog "$INSTDIR\web.py-0.36.zip" "$INSTDIR"
      GetFullPathName /SHORT $1 "$INSTDIR\web.py-0.36\setup.py"
      ExecWait '"c:\Python27\python.exe" $1 install'
      Delete "$INSTDIR\web.py-0.36.zip"
  skipWebPy:

  ; PIL 1.1.7
  IfFileExists c:\Python27\Lib\site-packages\PIL-1.1.7-py2.7-win32.egg\EGG-INFO\PKG-INFO skipPIL installPIL
  installPIL:
      MessageBox MB_OK "Your system does not have the Python imaging library.$\nClick OK to install it."
      SetOutPath $INSTDIR
      File PIL-1.1.7.win32-py2.7.exe
      ExecWait '$INSTDIR\PIL-1.1.7.win32-py2.7.exe'
      Delete "$INSTDIR\PIL-1.1.7.win32-py2.7.exe"
  skipPIL:

  ; MySQLdb 1.2.3
  IfFileExists c:\Python27\Lib\site-packages\MySQLdb\connections.py skipMySQL installMySQL
  installMySQL:
      MessageBox MB_OK "Your system does not have the MySQL client library.$\nClick OK to install it."
      SetOutPath $INSTDIR
      File MySQL-python-1.2.3.win32-py2.7.exe
      ExecWait '$INSTDIR\MySQL-python-1.2.3.win32-py2.7.exe'
      Delete "$INSTDIR\MySQL-python-1.2.3.win32-py2.7.exe"
  skipMySQL:

  ; Pisa (optional via easy_install if we have internet access - will fail if we don't)
  IfFileExists c:\Python27\Scripts\pisa.exe skipPisa installPisa
  installPisa:
      MessageBox MB_OK "Your system does not have the Pisa PDF library.$\nClick OK to install it."
      ExecWait '"c:\Python27\Scripts\easy_install.exe" pisa'
  skipPisa:
 
  ; Logo icon
  SetOutPath $INSTDIR
  File ..\..\logo\asm2009\asm.ico
 
  ; ASM bundle
  CreateDirectory $INSTDIR\asm
  SetOutPath $INSTDIR\asm
  File asm.zip
  nsisunz::UnzipToLog "$INSTDIR\asm\asm.zip" "$INSTDIR\asm"
  Delete "$INSTDIR\asm\asm.zip"

  ; This retrieves the short name to the user's home folder
  GetFullPathName /SHORT $0 $PROFILE

  ; Create the Start Server batch file
  FileOpen $FH "$INSTDIR\asm\run.bat" w
  FileWrite $FH 'SET ASM3_DBTYPE=SQLITE$\r$\n'
  FileWrite $FH 'SET ASM3_DBNAME=$0\asm.db$\r$\n'
  FileWrite $FH '"C:\Python27\python.exe" code.py 5000$\r$\n'
  FileWrite $FH 'pause$\r$\n'
  FileClose $FH 

  ; Create the Daily Tasks batch file
  FileOpen $FH "$INSTDIR\asm\daily.bat" w
  FileWrite $FH 'SET ASM3_DBTYPE=SQLITE$\r$\n'
  FileWrite $FH 'SET ASM3_DBNAME=$0\asm.db$\r$\n'
  FileWrite $FH '"C:\Python27\python.exe" cron.py all$\r$\n'
  FileClose $FH

  ; Create the scheduled task to run the daily batch
  ExecWait 'at 6:00 /every:M,T,W,Th,F,S,Su "$INSTDIR\asm\daily.bat"'

  ; Write the uninstaller, since the installer always insists on
  ; installing a client
  WriteUninstaller $INSTDIR\uninst-asm.exe

  ; Create shortcut to main program on start menu
  CreateDirectory "$SMPROGRAMS\Animal Shelter Manager 3"
  
  ; ======== START MENU ===============
  CreateShortCut "$SMPROGRAMS\Animal Shelter Manager 3\Start ASM3 Server.lnk" "$INSTDIR\asm\run.bat"
  CreateShortCut "$SMPROGRAMS\Animal Shelter Manager 3\Run Daily Tasks.lnk" "$INSTDIR\asm\daily.bat"
  CreateShortCut "$SMPROGRAMS\Animal Shelter Manager 3\Uninstall.lnk" "$INSTDIR\uninst-asm.exe" ""
  CreateShortCut "$SMPROGRAMS\Animal Shelter Manager 3\ASM3.lnk" "http://127.0.0.1:5000" "" "$INSTDIR\asm.ico"

  ; ============= DESKTOP ===============
  
  ; Start application
  CreateShortCut "$DESKTOP\Start ASM3 Server.lnk" "$INSTDIR\asm\run.bat"
  CreateShortCut "$DESKTOP\ASM3.lnk" "http://127.0.0.1:5000" "" "$INSTDIR\asm.ico"

  SetDetailsPrint textonly
  DetailPrint "Installation Complete."
  SetDetailsPrint listonly

SectionEnd


;--------------------------------
;Uninstaller Section

Section Uninstall

  SetDetailsPrint textonly
  DetailPrint "Deleting Registry Keys..."
  SetDetailsPrint listonly

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ASM3"
  DeleteRegKey HKLM "Software\ASM3"

  SetDetailsPrint textonly
  DetailPrint "Deleting Scheduled Task..."
  SetDetailsPrint listonly

  ExecWait 'at /delete /yes'

  SetDetailsPrint textonly
  DetailPrint "Deleting Files..."
  SetDetailsPrint listonly

  Delete "$DESKTOP\Start ASM3 Server.lnk"
  Delete "$DESKTOP\ASM3.lnk"
  RMDir /r "$SMPROGRAMS\Animal Shelter Manager 3"
  RMDir /r "$INSTDIR"

  SetDetailsPrint both

SectionEnd
