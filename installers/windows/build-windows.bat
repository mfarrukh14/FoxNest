@echo off
REM Build script for FoxNest Windows installer

echo ========================================
echo Building FoxNest Windows installer...
echo ========================================

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6+ from https://python.org
    pause
    exit /b 1
)

echo ✓ Python found

REM Check if PyInstaller is installed
echo Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo ✓ PyInstaller ready

REM Install dependencies
echo Installing dependencies...
pip install requests flask
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Build the executables with PyInstaller
echo Building executables...
pyinstaller --clean foxnest.spec

if errorlevel 1 (
    echo Error: Failed to build executables
    echo Check the output above for details
    pause
    exit /b 1
)

echo ✓ Executables built successfully

REM Verify executables were created
if not exist "dist\foxnest\fox.exe" (
    echo Error: fox.exe was not created
    pause
    exit /b 1
)

if not exist "dist\foxnest\fox-server.exe" (
    echo Error: fox-server.exe was not created
    pause
    exit /b 1
)

echo ✓ Executables verified

REM Check if NSIS is available
echo Checking NSIS installation...
where makensis >nul 2>&1
if errorlevel 1 (
    echo Warning: NSIS not found. 
    echo To create an installer, please:
    echo 1. Download NSIS from: https://nsis.sourceforge.io/
    echo 2. Install NSIS and add it to your PATH
    echo 3. Run this script again
    echo.
    echo The executables are available in: dist\foxnest\
    echo You can copy fox.exe and fox-server.exe to a folder in your PATH
    pause
    exit /b 0
)

echo ✓ NSIS found

REM Create the installer
echo Creating installer...
makensis foxnest-installer.nsi

if errorlevel 1 (
    echo Error: Failed to create installer
    echo Check the NSIS output above for details
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ Build completed successfully!
echo ========================================
echo.
echo Files created:
echo   - dist\foxnest\fox.exe
echo   - dist\foxnest\fox-server.exe
echo   - foxnest-installer-v1.0.0.exe
echo.
echo To install FoxNest system-wide:
echo   1. Right-click foxnest-installer-v1.0.0.exe
echo   2. Select "Run as administrator"
echo   3. Follow the installation wizard
echo.
echo For portable use:
echo   Copy dist\foxnest\*.exe to your desired location
echo.
pause
