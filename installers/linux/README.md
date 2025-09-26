# FoxNest Linux Installation

This directory contains the files needed to create and install FoxNest on Linux systems using .deb packages.

## Prerequisites

- Ubuntu/Debian-based Linux distribution
- `dpkg` package manager
- Python 3.6 or higher
- Internet connection for dependency installation

## Building the .deb Package

1. Run the build script:
   ```bash
   chmod +x build-deb.sh
   ./build-deb.sh
   ```

2. This will create `foxnest_1.0.0_all.deb` in the current directory.

## Installing FoxNest

1. Install the package:
   ```bash
   sudo dpkg -i foxnest_1.0.0_all.deb
   ```

2. If there are dependency issues, fix them with:
   ```bash
   sudo apt-get install -f
   ```

## What Gets Installed

- `/usr/local/bin/fox` - Main FoxNest command
- `/usr/local/bin/fox-server` - FoxNest server command
- `/usr/local/lib/foxnest/` - FoxNest library files
- `/usr/share/doc/foxnest/` - Documentation files

## Verifying Installation

After installation, you should be able to run:
```bash
fox --version
fox help
fox-server
```

## Uninstalling

To remove FoxNest:
```bash
sudo dpkg -r foxnest
```

## Troubleshooting

### Command not found
If you get "command not found" after installation:
1. Check if `/usr/local/bin` is in your PATH
2. Try running `/usr/local/bin/fox` directly
3. Restart your terminal or source your profile

### Permission issues
If you get permission errors:
1. Make sure you installed with `sudo`
2. Check file permissions: `ls -la /usr/local/bin/fox*`

### Python dependencies
If you get import errors:
1. Ensure Python 3.6+ is installed
2. Install missing packages: `pip3 install requests flask`

## Building from Source

If you want to build the package yourself:

1. Ensure the source files are in the correct locations:
   - `foxnest-1.0.0/usr/local/lib/foxnest/fox_client.py`
   - `foxnest-1.0.0/usr/local/lib/foxnest/foxnest_server.py`
   - `foxnest-1.0.0/usr/local/bin/fox`
   - `foxnest-1.0.0/usr/local/bin/fox-server`

2. Set proper permissions and build:
   ```bash
   chmod 755 foxnest-1.0.0/DEBIAN/postinst
   chmod 755 foxnest-1.0.0/DEBIAN/prerm
   dpkg-deb --build foxnest-1.0.0
   ```
