#!/bin/bash
# Workaround script for PyInstaller PyQt5 symlink issue

echo "🔧 Applying workaround for PyInstaller symlink issue..."

# Clean and build
rm -rf build/ dist/
source venv/bin/activate

# Build until it fails at COLLECT stage
echo "Building (will stop at symlink error)..."
pyinstaller --clean --noconfirm "CSV SQL Engine Pro.spec" 2>&1 | tee /tmp/pyinstaller_workaround.log

# Check if we got to the COLLECT stage
if [ -d "dist/CSV SQL Engine Pro/_internal" ]; then
    echo "✅ Partial build created. Fixing symlinks..."
    
    # Fix the problematic symlink
    cd "dist/CSV SQL Engine Pro/_internal/PyQt5/Qt5/lib/QtBluetooth.framework"
    if [ -L "Versions/Current/Resources" ] && [ ! -e "Versions/Current/Resources" ]; then
        rm "Versions/Current/Resources"
        ln -s "../Resources" "Versions/Current/Resources"
        echo "✅ Fixed QtBluetooth framework symlink"
    fi
    cd - > /dev/null
    
    # Try to complete the build manually
    echo "Attempting to complete build..."
    cd "dist/CSV SQL Engine Pro"
    # Create the app bundle structure
    mkdir -p "CSV SQL Engine Pro.app/Contents/MacOS"
    mkdir -p "CSV SQL Engine Pro.app/Contents/Resources"
    
    # Copy the executable
    if [ -f "CSV SQL Engine Pro" ]; then
        cp "CSV SQL Engine Pro" "CSV SQL Engine Pro.app/Contents/MacOS/"
        chmod +x "CSV SQL Engine Pro.app/Contents/MacOS/CSV SQL Engine Pro"
        echo "✅ App bundle structure created"
    fi
    
    cd - > /dev/null
    echo "⚠️  Manual fix applied. App may need additional testing."
else
    echo "❌ Build didn't reach COLLECT stage"
fi
