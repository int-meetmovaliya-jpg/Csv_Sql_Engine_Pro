#!/bin/bash

# Script to convert logo image to macOS .icns format
# Usage: ./create_icon.sh logo.png

if [ $# -eq 0 ]; then
    echo "Usage: $0 <image_file>"
    echo "Example: $0 logo.png"
    echo ""
    echo "The image should be a high-resolution square image (1024x1024px or larger recommended)"
    exit 1
fi

INPUT_IMAGE="$1"
ICON_NAME="app_icon"
ICONSET_DIR="${ICON_NAME}.iconset"

# Check if input file exists
if [ ! -f "$INPUT_IMAGE" ]; then
    echo "Error: Image file '$INPUT_IMAGE' not found!"
    exit 1
fi

# Create iconset directory
echo "Creating iconset directory..."
rm -rf "$ICONSET_DIR"
mkdir "$ICONSET_DIR"

# Check if sips is available (macOS built-in tool)
if ! command -v sips &> /dev/null; then
    echo "Error: sips command not found. This script requires macOS."
    exit 1
fi

# Create all required icon sizes
echo "Generating icon sizes..."

# 16x16
sips -z 16 16 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_16x16.png"
cp "${ICONSET_DIR}/icon_16x16.png" "${ICONSET_DIR}/icon_16x16@2x.png"

# 32x32
sips -z 32 32 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_32x32.png"
cp "${ICONSET_DIR}/icon_32x32.png" "${ICONSET_DIR}/icon_32x32@2x.png"

# 64x64 (for @2x of 32x32)
sips -z 64 64 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_32x32@2x.png"

# 128x128
sips -z 128 128 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_128x128.png"
cp "${ICONSET_DIR}/icon_128x128.png" "${ICONSET_DIR}/icon_128x128@2x.png"

# 256x256 (for @2x of 128x128)
sips -z 256 256 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_128x128@2x.png"

# 256x256
sips -z 256 256 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_256x256.png"
cp "${ICONSET_DIR}/icon_256x256.png" "${ICONSET_DIR}/icon_256x256@2x.png"

# 512x512 (for @2x of 256x256)
sips -z 512 512 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_256x256@2x.png"

# 512x512
sips -z 512 512 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_512x512.png"
cp "${ICONSET_DIR}/icon_512x512.png" "${ICONSET_DIR}/icon_512x512@2x.png"

# 1024x1024 (for @2x of 512x512)
sips -z 1024 1024 "$INPUT_IMAGE" --out "${ICONSET_DIR}/icon_512x512@2x.png"

# Create .icns file
echo "Creating .icns file..."
iconutil -c icns "$ICONSET_DIR" -o "${ICON_NAME}.icns"

# Cleanup
rm -rf "$ICONSET_DIR"

if [ -f "${ICON_NAME}.icns" ]; then
    echo ""
    echo "✅ Success! Icon created: ${ICON_NAME}.icns"
    echo ""
    echo "Next steps:"
    echo "1. Update 'CSV SQL Engine Pro.spec' to use this icon"
    echo "2. Rebuild the app with: pyinstaller 'CSV SQL Engine Pro.spec'"
else
    echo "❌ Error: Failed to create .icns file"
    exit 1
fi

