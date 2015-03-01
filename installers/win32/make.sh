#!/bin/sh
cd `dirname $0`

# Copy the nsisunz.dll file to the NSIS installation
cp -f nsisunz.dll "$HOME/.wine/drive_c/Program Files/NSIS/Plugins"

# Make a zip build of the application
cd ../../src
zip -r9 ../installers/win32/asm.zip *
cd ../installers/win32

# Make a copy of the asm.nsi file and set the version number on it
cat asm.nsi | sed "s/ZZZasmversionZZZ/`cat ../../VERSION`/g" > build.nsi
wine "$HOME/.wine/drive_c/Program Files/NSIS/makensis.exe" build.nsi
rm build.nsi
rm asm.zip
