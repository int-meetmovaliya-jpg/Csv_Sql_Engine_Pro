#!/bin/bash

# Build script for CSV SQL Engine Pro
# This script builds the macOS DMG package

echo "Building CSV SQL Engine Pro..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/
rm -rf dist/

# Build with PyInstaller
echo "Building application with PyInstaller..."
pyinstaller "CSV SQL Engine Pro.spec"

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

# Check if app was created
if [ ! -d "dist/CSV SQL Engine Pro.app" ]; then
    echo "Application bundle not found in dist/"
    exit 1
fi

echo "Build completed successfully!"
echo "Application bundle: dist/CSV SQL Engine Pro.app"
echo ""
echo "To create a DMG:"
echo "1. Install dmgbuild: pip install dmgbuild"
echo "2. Use Disk Utility or dmgbuild to create the DMG"
echo "3. Or use: hdiutil create -volname 'CSV SQL Engine Pro' -srcfolder 'dist/CSV SQL Engine Pro.app' -ov -format UDZO 'CSV_SQL_Engine_Pro.dmg'"

