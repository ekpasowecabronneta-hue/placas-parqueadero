@echo off
setlocal
cd /d "%~dp0"

if not exist build mkdir build
cd build

cmake .. -G "Visual Studio 17 2022" -A x64
if errorlevel 1 (
    cmake .. -G "Visual Studio 16 2019" -A x64
)
if errorlevel 1 (
    echo Error: instale CMake y Visual Studio con C++.
    exit /b 1
)

cmake --build . --config Release
if errorlevel 1 exit /b 1

echo.
echo Binarios en build\Release\
echo   parking_server.exe
echo   parking_generator.exe
echo   parking_core_shared.dll
echo.
echo Python: pip install -r python\requirements.txt
echo         streamlit run python\app.py
endlocal
