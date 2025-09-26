#!/bin/bash
# Build script for FoxNest Linux .deb package

set -e

echo "Building FoxNest .deb package..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$SCRIPT_DIR/foxnest-1.0.0"

# Ensure we're in the right directory
cd "$SCRIPT_DIR"

# Set proper permissions
echo "Setting permissions..."
chmod 755 "$PACKAGE_DIR/DEBIAN/postinst"
chmod 755 "$PACKAGE_DIR/DEBIAN/prerm"
chmod 755 "$PACKAGE_DIR/usr/local/bin/fox"
chmod 755 "$PACKAGE_DIR/usr/local/bin/fox-server"
chmod 644 "$PACKAGE_DIR/usr/local/lib/foxnest/fox_client.py"
chmod 644 "$PACKAGE_DIR/usr/local/lib/foxnest/foxnest_server.py"
chmod 644 "$PACKAGE_DIR/usr/share/doc/foxnest/README.md"

# Build the .deb package
echo "Building package..."
dpkg-deb --build foxnest-1.0.0

# Move and rename the package
mv foxnest-1.0.0.deb foxnest_1.0.0_all.deb

echo "✓ Package built successfully: foxnest_1.0.0_all.deb"
echo ""
echo "To install, run:"
echo "  sudo dpkg -i foxnest_1.0.0_all.deb"
echo "  sudo apt-get install -f  # if there are dependency issues"
echo ""
echo "To uninstall, run:"
echo "  sudo dpkg -r foxnest"
