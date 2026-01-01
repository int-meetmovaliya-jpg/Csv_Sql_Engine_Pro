# Setting Up the App Icon

## Steps to Use Your Logo as the App Icon

1. **Save the logo image** as a PNG file (preferably 1024x1024px or larger, square format)
   - Save it in the project root directory
   - Name it something like `logo.png` or `app_icon.png`

2. **Convert to .icns format** (macOS icon format):
   ```bash
   ./create_icon.sh logo.png
   ```
   This will create `app_icon.icns` in the project root.

3. **Update the PyInstaller spec file**:
   - Open `CSV SQL Engine Pro.spec`
   - Find the line: `icon=None,`
   - Change it to: `icon='app_icon.icns',`

4. **Rebuild the app**:
   ```bash
   pyinstaller "CSV SQL Engine Pro.spec"
   ```

5. **Create the DMG**:
   ```bash
   hdiutil create -volname "CSV SQL Engine Pro" \
     -srcfolder "dist/CSV SQL Engine Pro.app" \
     -ov -format UDZO "CSV_SQL_Engine_Pro.dmg"
   ```

## Current Status

- ❌ DMG is **NOT** built with latest changes (native window support)
- ❌ No icon is currently set (icon=None in spec file)
- ✅ Icon conversion script is ready to use

## Quick Fix

If you have the logo image file:

1. Save it as `logo.png` in the project root
2. Run: `./create_icon.sh logo.png`
3. Update the spec file to use `icon='app_icon.icns'`
4. Rebuild everything

