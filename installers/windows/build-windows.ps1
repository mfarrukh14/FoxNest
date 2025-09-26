# PowerShell build script for FoxNest Windows installer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building FoxNest Windows installer..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.6+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if PyInstaller is installed
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
try {
    pip show pyinstaller | Out-Null
    Write-Host "✓ PyInstaller is already installed" -ForegroundColor Green
} catch {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Error: Failed to install PyInstaller" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✓ PyInstaller installed" -ForegroundColor Green
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install requests flask
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Error: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
Write-Host "✓ Previous builds cleaned" -ForegroundColor Green

# Build the executables with PyInstaller
Write-Host "Building executables..." -ForegroundColor Yellow
pyinstaller --clean foxnest.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Error: Failed to build executables" -ForegroundColor Red
    Write-Host "Check the output above for details" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Verify executables were created
if (-not (Test-Path "dist\foxnest\fox.exe")) {
    Write-Host "✗ Error: fox.exe was not created" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "dist\foxnest\fox-server.exe")) {
    Write-Host "✗ Error: fox-server.exe was not created" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Executables built and verified" -ForegroundColor Green

# Check if NSIS is available
Write-Host "Checking NSIS installation..." -ForegroundColor Yellow
$nsisPath = Get-Command makensis -ErrorAction SilentlyContinue
if (-not $nsisPath) {
    Write-Host "⚠ Warning: NSIS not found." -ForegroundColor Yellow
    Write-Host "To create an installer, please:" -ForegroundColor White
    Write-Host "1. Download NSIS from: https://nsis.sourceforge.io/" -ForegroundColor White
    Write-Host "2. Install NSIS and add it to your PATH" -ForegroundColor White
    Write-Host "3. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "The executables are available in: dist\foxnest\" -ForegroundColor Cyan
    Write-Host "You can copy fox.exe and fox-server.exe to a folder in your PATH" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host "✓ NSIS found" -ForegroundColor Green

# Create the installer
Write-Host "Creating installer..." -ForegroundColor Yellow
& makensis foxnest-installer.nsi

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Error: Failed to create installer" -ForegroundColor Red
    Write-Host "Check the NSIS output above for details" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files created:" -ForegroundColor Cyan
Write-Host "  - dist\foxnest\fox.exe" -ForegroundColor White
Write-Host "  - dist\foxnest\fox-server.exe" -ForegroundColor White
Write-Host "  - foxnest-installer-v1.0.0.exe" -ForegroundColor White
Write-Host ""
Write-Host "To install FoxNest system-wide:" -ForegroundColor Yellow
Write-Host "  1. Right-click foxnest-installer-v1.0.0.exe" -ForegroundColor White
Write-Host "  2. Select 'Run as administrator'" -ForegroundColor White
Write-Host "  3. Follow the installation wizard" -ForegroundColor White
Write-Host ""
Write-Host "For portable use:" -ForegroundColor Yellow
Write-Host "  Copy dist\foxnest\*.exe to your desired location" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
