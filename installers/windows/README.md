# FoxNest Windows Installation

This directory contains the files needed to create and install FoxNest on Windows systems.

## 🎉 New in Version 1.0.0

**Git-like Storage Optimizations:**
- ✅ Zlib compression for all objects (~50% size reduction)
- ✅ Subdirectory structure for better performance
- ✅ Pack files for efficient storage
- ✅ New `fox gc` command for garbage collection
- ✅ Delta encoding infrastructure ready

See `OPTIMIZATION.md` in the root directory for details.

## Prerequisites

- Windows 10 or later
- Python 3.6 or higher (for building from source)
- Administrator privileges (for installation)

## Quick Installation

### Option 1: Using the Pre-built Installer (Recommended)

1. Download `foxnest-installer-v1.0.0.exe`
2. Right-click and select "Run as administrator"
3. Follow the installation wizard
4. FoxNest will be added to your system PATH automatically

### Option 2: Using the Portable Version

1. Extract the contents of `dist/foxnest/` to your desired location
2. Add the folder to your system PATH manually
3. You can now use `fox` and `fox-server` commands

## Building from Source

### Prerequisites for Building

- Windows 10/11
- Python 3.6+ (for building)
- pip package manager
- PyInstaller: `pip install pyinstaller`
- NSIS (Nullsoft Scriptable Install System) for creating the installer

### Build Steps

1. **Using Batch Script (Windows Command Prompt):**
   ```cmd
   build-windows.bat
   ```

2. **Using PowerShell:**
   ```powershell
   .\build-windows.ps1
   ```

3. **Manual Build:**
   ```cmd
   pip install pyinstaller requests flask
   pyinstaller --clean foxnest.spec
   makensis foxnest-installer.nsi
   ```

### Testing the Build

Before creating the installer, you can test the executables:
```cmd
test-executables.bat
```

This will verify that both `fox.exe` and `fox-server.exe` work correctly.

## What Gets Installed

- `fox.exe` - Main FoxNest command-line tool
- `fox-server.exe` - FoxNest server executable
- All required Python dependencies bundled
- Start Menu shortcuts
- Desktop shortcut (optional)
- Automatic PATH configuration

## Installation Locations

- **Program Files**: `C:\Program Files\FoxNest\`
- **Start Menu**: `Start Menu > FoxNest`
- **Desktop**: `FoxNest.lnk` (if selected during installation)

## Verifying Installation

After installation, open Command Prompt or PowerShell and run:
```cmd
fox --version
fox help
fox-server
```

Or use the verification script:
```cmd
verify-installation.bat
```

This script will check that all components are properly installed and working.

## Uninstalling

### Using Control Panel
1. Open "Programs and Features" or "Apps & Features"
2. Find "FoxNest" in the list
3. Click "Uninstall"

### Using Command Line
Run the uninstaller directly:
```cmd
"C:\Program Files\FoxNest\uninstall.exe"
```

## Troubleshooting

### Command not found
If you get "'fox' is not recognized as an internal or external command":
1. Restart Command Prompt/PowerShell
2. Check if `C:\Program Files\FoxNest` is in your PATH
3. Try running the full path: `"C:\Program Files\FoxNest\fox.exe"`

### Administrator privileges required
Some operations require administrator privileges:
1. Right-click Command Prompt/PowerShell
2. Select "Run as administrator"
3. Try the command again

### Antivirus warnings
Some antivirus software may flag the executables:
1. This is common with PyInstaller-built executables
2. Add an exception for the FoxNest installation folder
3. The source code is available for inspection

### Python runtime errors
If you encounter Python-related errors:
1. Ensure you're using the bundled executable, not a Python script
2. Try reinstalling FoxNest
3. Check Windows Event Viewer for detailed error messages

## Building Requirements

### For PyInstaller
- Windows 10/11
- Python 3.6-3.11 (3.12+ may have compatibility issues)
- At least 2GB free disk space during build

### For NSIS Installer
- Download NSIS from: https://nsis.sourceforge.io/
- Add NSIS to your PATH or update the script with the full path

## Advanced Configuration

### Custom Installation Directory
To install to a custom directory, modify the NSIS script:
```nsis
InstallDir "$PROGRAMFILES64\YourCustomPath\FoxNest"
```

### Silent Installation
For automated deployment:
```cmd
foxnest-installer-v1.0.0.exe /S
```

## File Structure

```
installers/windows/
├── build-windows.bat         # Windows batch build script
├── build-windows.ps1         # PowerShell build script
├── test-executables.bat      # Test script for built executables
├── verify-installation.bat   # Installation verification script
├── foxnest.spec              # PyInstaller specification
├── foxnest-installer.nsi     # NSIS installer script
├── foxnest/                  # Python package directory
│   ├── __init__.py
│   ├── fox_client.py         # Main client code
│   └── server.py             # Server code
├── setup.py                  # Python setuptools configuration
└── README.md                 # This file
```
