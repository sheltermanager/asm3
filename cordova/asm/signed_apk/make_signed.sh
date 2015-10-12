#!/bin/sh
cd ..
cordova build android --release
cd signed_apk
cp ../platforms/android/build/outputs/apk/android-release-unsigned.apk asm.apk
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore asm-release-key.keystore asm.apk asm
~/usr/android-sdk-linux/build-tools/23.0.1/zipalign -f 4 asm.apk sheltermanager.apk
rm asm.apk
