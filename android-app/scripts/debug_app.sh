#!/bin/bash

cd "$(dirname $0)/../"

./gradlw assembleDebug

# install app on phone
adb install app/build/outputs/apk/debug/app-debug.apk 

# launch the app
adb shell am start -n com.kabilan108.myapplication/.MainActivity

