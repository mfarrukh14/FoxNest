@echo off
REM Test script for FoxNest executables

echo Testing FoxNest executables...
echo.

if not exist "dist\foxnest\fox.exe" (
    echo Error: fox.exe not found. Please build first using build-windows.bat
    pause
    exit /b 1
)

if not exist "dist\foxnest\fox-server.exe" (
    echo Error: fox-server.exe not found. Please build first using build-windows.bat
    pause
    exit /b 1
)

echo Testing fox.exe...
"dist\foxnest\fox.exe" --version
if errorlevel 1 (
    echo Error: fox.exe failed to run
    pause
    exit /b 1
)

echo.
echo Testing fox.exe help...
"dist\foxnest\fox.exe" help
if errorlevel 1 (
    echo Error: fox.exe help failed
    pause
    exit /b 1
)

echo.
echo ✓ All tests passed!
echo.
echo You can now:
echo 1. Copy the executables to a folder in your PATH for portable use
echo 2. Run build-windows.bat to create a full installer
echo.
pause
