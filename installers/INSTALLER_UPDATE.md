# FoxNest Installer Update Guide

## Changes Included in This Update

### New Features
1. **Git-like Storage Optimization**
   - Zlib compression for all objects (~50% size reduction)
   - Subdirectory structure (objects/ab/cd...)
   - Pack files for efficient storage
   - Delta encoding infrastructure
   - Automatic garbage collection

2. **Archive Management**
   - `fox push` - Push to active repositories
   - `fox push --archive` - Push and archive repository
   - Proper error handling when pushing to archived repos

3. **New Commands**
   - `fox gc` - Garbage collection/optimization
   - Better error messages
   - "Everything up-to-date" when no commits to push

### Bug Fixes
- Fixed archived repository handling
- Improved error messages for HTTP errors
- Better handling of no-commit scenarios
- Repository filtering in frontend (Archive vs Repositories tabs)

## Linux Installation (✅ COMPLETED)

The Linux installer has been updated and installed system-wide:

```bash
# Already completed:
cd installers/linux
bash build-deb.sh
sudo dpkg -i foxnest_1.0.0_all.deb

# Verify installation:
fox --version
fox help | grep gc
```

### Linux Files Updated
- ✅ `installers/linux/foxnest-1.0.0/usr/local/lib/foxnest/fox_client.py`
- ✅ `installers/linux/foxnest_1.0.0_all.deb` (rebuilt)
- ✅ Installed system-wide

## Windows Installation (Instructions)

### Prerequisites
On a Windows machine, you need:
- Python 3.8+ installed
- PyInstaller: `pip install pyinstaller`
- NSIS (for creating installer): Download from https://nsis.sourceforge.io/

### Files Already Updated
✅ `installers/windows/foxnest/fox_client.py` - Already updated with latest code

### Step 1: Build Executables (Windows Only)

On Windows, open PowerShell or Command Prompt:

```powershell
cd installers\windows

# Build the executables
python build-windows.ps1
# OR
pyinstaller foxnest.spec

# This creates:
# - dist/fox.exe
# - dist/fox-server.exe
```

### Step 2: Create Installer (Windows Only)

```powershell
# Using NSIS
makensis foxnest-installer.nsi

# This creates:
# - FoxNest-1.0.0-Setup.exe
```

### Step 3: Install on Windows

```powershell
# Run the installer
.\FoxNest-1.0.0-Setup.exe

# Or manually copy files:
xcopy /E /I dist\* "C:\Program Files\FoxNest\"
setx PATH "%PATH%;C:\Program Files\FoxNest"
```

### Step 4: Verify Installation (Windows)

```cmd
fox --version
fox help
```

## Alternative: Manual Installation (Any Platform)

If you don't want to use installers, you can use the client directly:

### Linux/Mac
```bash
# Create alias or symlink
sudo ln -sf /path/to/FoxNest/client/fox.py /usr/local/bin/fox
sudo chmod +x /usr/local/bin/fox

# Or add to ~/.bashrc
echo 'alias fox="python3 /path/to/FoxNest/client/fox.py"' >> ~/.bashrc
source ~/.bashrc
```

### Windows
```cmd
# Add to PATH
setx PATH "%PATH%;C:\path\to\FoxNest\client"

# Or create batch file: C:\Windows\System32\fox.bat
@echo off
python C:\path\to\FoxNest\client\fox.py %*
```

## Testing the Update

After installation, test the new features:

```bash
# 1. Test version
fox --version

# 2. Test new gc command
cd /tmp
fox init --username test --repo-name test
echo "test" > test.txt
fox add test.txt
fox commit -m "test"
fox gc  # Should show garbage collection

# 3. Test archive feature
fox set origin 192.168.15.237:5000
fox push --archive  # Should archive
fox push            # Should show error about archived repo

# 4. Test optimization help
fox help | grep -E "(gc|archive|OPTIMIZATION)"
```

## What's Been Updated

### Client Code (fox.py)
- ✅ Compression methods (zlib)
- ✅ Pack file generation
- ✅ Delta encoding infrastructure
- ✅ Archive parameter handling
- ✅ Better error messages
- ✅ "Everything up-to-date" check

### Server Code (server.py)
- ✅ Archive/unarchive endpoints
- ✅ Repository status checking
- ✅ Proper HTTP error codes
- ✅ Detailed error messages

### Frontend (React)
- ✅ Archive tab filtering
- ✅ Repositories tab filtering
- ✅ Proper is_archived field handling

### Database (CRUD)
- ✅ archive_repository method
- ✅ unarchive_repository method
- ✅ Repository status fields

## Rollback (If Needed)

### Linux
```bash
sudo dpkg -r foxnest
# Then install old version if you have it
```

### Windows
```cmd
# Use Windows "Add/Remove Programs"
# Or delete: C:\Program Files\FoxNest
```

## Support

If you encounter issues:

1. Check Python version: `python --version` (need 3.8+)
2. Check dependencies: `pip list | grep requests`
3. Check logs: Look for error messages in terminal
4. Verify PATH: `which fox` (Linux/Mac) or `where fox` (Windows)

## Version History

- **v1.0.0** (Current)
  - Git-like storage optimization
  - Archive management
  - Garbage collection command
  - Improved error handling

## Next Steps

After successful installation:

1. ✅ Verify `fox --version` works
2. ✅ Test `fox gc` command
3. ✅ Test `fox push --archive`
4. ✅ Check frontend Archive/Repositories tabs
5. 📝 Document any issues
6. 🚀 Deploy to production

---

**Note**: The Linux installer has been successfully updated and installed. Windows users should follow the Windows installation steps above on a Windows machine.
