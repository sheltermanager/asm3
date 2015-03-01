all: debug
targets:
	android list targets

project:
	android update project -p . -t 1

debug:
	ant debug 

test:
	ant debug install

release:
	ant release

log:
	$(HOME)/usr/android-sdk-linux/platform-tools/adb logcat

restart:
	adb kill-server
	adb start-server
