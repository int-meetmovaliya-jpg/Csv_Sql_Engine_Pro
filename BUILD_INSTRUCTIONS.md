# Building CSV SQL Engine Pro DMG

## Prerequisites

1. Python 3.9+ installed
2. All dependencies installed: `pip install -r requirements.txt`
   - This includes PyQt5 and PyQtWebEngine for native macOS window support
3. PyInstaller installed: `pip install pyinstaller`

## Build Steps

### Option 1: Using the Build Script

```bash
./build_dmg.sh
```

### Option 2: Manual Build

1. **Build the application:**
   ```bash
   pyinstaller "CSV SQL Engine Pro.spec"
   ```

2. **Create the DMG:**
   
   **Simple method (using hdiutil):**
   ```bash
   hdiutil create -volname "CSV SQL Engine Pro" \
     -srcfolder "dist/CSV SQL Engine Pro.app" \
     -ov -format UDZO "CSV_SQL_Engine_Pro.dmg"
   ```
   
   **Advanced method (using dmgbuild - for better appearance):**
   ```bash
   pip install dmgbuild
   # Create a dmg_settings.py file with DMG settings
   dmgbuild -s dmg_settings.py "CSV SQL Engine Pro" "CSV_SQL_Engine_Pro.dmg"
   ```

## Update Process

When you make changes to the code:

1. **Update version.json** with the new version number and changelog
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Version X.Y.Z: [description of changes]"
   git push
   ```
3. **Build a new DMG** using the steps above
4. **Distribute the DMG** to users

Users who have the app installed will:
- Be notified of the update when they launch the app
- Have the option to update, skip, or be reminded later
- Get the update automatically if they choose to update

## Notes

- The `bootstrap.py` file is the entry point for the application
- The app runs as a **native macOS application** using PyQt5, not as a browser-based localhost server
- Updates are downloaded from the GitHub repository's main branch
- User data and preferences are preserved during updates
- The update system checks `version.json` in the GitHub repository
- The app uses `native_window.py` to embed Streamlit in a native macOS window

