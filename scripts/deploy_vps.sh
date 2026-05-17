#!/bin/bash
# Despliegue en VPS Linux (servidor + generador)
set -e
cd "$(dirname "$0")/.."
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j"$(nproc)"
echo "Build OK: $(pwd)"
