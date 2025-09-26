# FoxNest Installers

This directory contains platform-specific installers for FoxNest Version Control System.

## 🦊 What is FoxNest?

FoxNest is a distributed version control system with simple, Git-like commands. It provides:
- Local repository management
- Remote server synchronization
- File staging and commits
- Distributed collaboration features

## 📦 Available Installers

### Linux (.deb package)
**Location**: `linux/`
**Supports**: Ubuntu, Debian, and derivatives
**Installation**: System-wide via package manager

Features:
- ✅ Automatic dependency resolution
- ✅ System-wide `fox` command
- ✅ Easy uninstallation
- ✅ Follows Linux package standards

### Windows (.exe installer)
**Location**: `windows/`
**Supports**: Windows 10/11
**Installation**: System-wide executable installer

Features:
- ✅ Self-contained executable
- ✅ No Python installation required
- ✅ Start Menu integration
- ✅ Automatic PATH configuration
- ✅ Professional uninstaller

## 🚀 Quick Start

### Linux Installation
```bash
cd linux/
chmod +x build-deb.sh
./build-deb.sh
sudo dpkg -i foxnest_1.0.0_all.deb
fox --version
```

### Windows Installation
```cmd
cd windows\
build-windows.bat
# Then run the generated foxnest-installer-v1.0.0.exe as administrator
```

## 🛠️ Building Requirements

### Linux
- Ubuntu/Debian system
- `dpkg-deb` utility
- Python 3.6+
- `pip3` for dependencies

### Windows
- Windows 10/11
- Python 3.6+ (for building)
- PyInstaller: `pip install pyinstaller`
- NSIS (for installer creation)

## 📋 Installation Verification

After installation on either platform:

```bash
# Check installation
fox --version
fox help

# Initialize a test repository
mkdir test-repo
cd test-repo
fox init --username testuser --repo-name test

# Test basic functionality
echo "Hello FoxNest" > test.txt
fox add test.txt
fox commit -m "Initial commit"
fox status
```

## 🗂️ Installed Components

Both installers provide:

1. **`fox` command** - Main version control client
2. **`fox-server` command** - Repository server
3. **Documentation** - README and help files
4. **Dependencies** - All required libraries

## 🔧 Customization

### Linux Package Customization
Edit `linux/foxnest-1.0.0/DEBIAN/control` to modify:
- Package dependencies
- Description
- Maintainer information
- Version numbers

### Windows Installer Customization
Edit `windows/foxnest-installer.nsi` to modify:
- Installation directory
- Start Menu shortcuts
- Registry entries
- Bundled components

## 🐛 Troubleshooting

### Common Issues

**Command not found after installation:**
- Linux: Check if `/usr/local/bin` is in PATH
- Windows: Restart Command Prompt, check PATH environment

**Permission errors:**
- Linux: Ensure installation with `sudo`
- Windows: Run installer as administrator

**Python import errors:**
- Linux: Install with `sudo apt-get install -f`
- Windows: Use the bundled executable version

### Getting Help

1. Check the platform-specific README files
2. Run `fox help` for command documentation
3. Test with `fox --version` to verify installation

## 📄 License

FoxNest is distributed under the MIT License. See the main project README for details.

## 🤝 Contributing

To contribute to the installers:

1. Fork the repository
2. Create your feature branch
3. Test on the target platform
4. Submit a pull request

## 📞 Support

For installation issues:
- Linux: Check `linux/README.md`
- Windows: Check `windows/README.md`
- General: Open an issue on GitHub

---

**Happy version controlling with FoxNest! 🦊**
