#!/bin/bash

# start listening on 5555
adb tcpip 5555

# connect phone
adb connect 10.0.0.153:5555

