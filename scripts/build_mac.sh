#!/bin/bash
# Compilacion en macOS sin CMake
set -e
cd "$(dirname "$0")/.."
mkdir -p build
CXX=${CXX:-g++}
$CXX -std=c++17 -I include -c src/parking_core.cpp -o build/parking_core.o
$CXX -std=c++17 -I include -c src/socket_platform.cpp -o build/socket_platform.o
$CXX -std=c++17 -I include -o build/parking_server src/socket_server.cpp build/parking_core.o build/socket_platform.o
$CXX -std=c++17 -I include -o build/parking_generator src/generator_main.cpp build/parking_core.o build/socket_platform.o
echo "OK: build/parking_server build/parking_generator"
