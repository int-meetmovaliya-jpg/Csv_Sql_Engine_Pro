#!/bin/bash

# Rebuild DMG script for CSV SQL Engine Pro with all latest changes

set -e  # Exit on error

echo "🔨 Rebuilding CSV SQL Engine Pro DMG with latest changes..."
echo ""

# Check if PyQt5 is installed
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "⚠️  Warning: PyQt5 not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/

# Build with PyInstaller
echo "📦 Building application with PyInstaller..."
echo "   (This may take a few minutes...)"

pyinstaller "CSV SQL Engine Pro.spec"

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Check if app was created
if [ ! -d "dist/CSV SQL Engine Pro.app" ]; then
    echo "❌ Application bundle not found in dist/"
    exit 1
fi

echo "✅ Build completed successfully!"
echo ""

# Create DMG
echo "💿 Creating DMG..."
DMG_NAME="CSV_SQL_Engine_Pro.dmg"

# Remove old DMG if exists
if [ -f "$DMG_NAME" ]; then
    rm "$DMG_NAME"
    echo "   Removed old DMG"
fi

# Create new DMG
hdiutil create -volname "CSV SQL Engine Pro" \
  -srcfolder "dist/CSV SQL Engine Pro.app" \
  -ov -format UDZO \
  "$DMG_NAME"

if [ $? -eq 0 ]; then
    DMG_SIZE=$(du -h "$DMG_NAME" | cut -f1)
    echo ""
    echo "✅ DMG created successfully!"
    echo "   File: $DMG_NAME"
    echo "   Size: $DMG_SIZE"
    echo ""
    echo "📦 DMG includes:"
    echo "   ✅ Native macOS window (PyQt5)"
    echo "   ✅ App icon"
    echo "   ✅ 10GB file support"
    echo "   ✅ Query result caching"
    echo "   ✅ Pagination for large results"
    echo "   ✅ All performance optimizations"
    echo "   ✅ Security improvements"
    echo ""
else
    echo "❌ Failed to create DMG"
    exit 1
fi

