# Rebuilding the DMG with Latest Changes

## Current Status

❌ **The DMG is NOT up to date** with the latest changes. It was built before:
- Native window support (PyQt5)
- App icon
- 10GB file support
- Performance optimizations
- Security improvements

## How to Rebuild

### Option 1: Using the Rebuild Script (Recommended)

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install/update dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the rebuild script:**
   ```bash
   ./REBUILD_DMG.sh
   ```

### Option 2: Manual Rebuild

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Clean old builds:**
   ```bash
   rm -rf build/ dist/
   ```

4. **Build the app:**
   ```bash
   pyinstaller "CSV SQL Engine Pro.spec"
   ```

5. **Create the DMG:**
   ```bash
   hdiutil create -volname "CSV SQL Engine Pro" \
     -srcfolder "dist/CSV SQL Engine Pro.app" \
     -ov -format UDZO "CSV_SQL_Engine_Pro.dmg"
   ```

## What's New in This Build

✅ Native macOS window (PyQt5) - No more browser mode!  
✅ App icon (professional logo)  
✅ 10GB file support  
✅ Query result caching (10-100x faster)  
✅ Pagination for large results  
✅ Security improvements (SQL injection prevention)  
✅ Performance optimizations  
✅ Better error handling  

## Estimated Build Time

- Building: 5-10 minutes (depending on system)
- DMG creation: 30 seconds
- **Total: ~10 minutes**

## Troubleshooting

If you get errors about PyQt5:
```bash
pip install PyQt5 PyQtWebEngine
```

If build fails, check:
- Virtual environment is activated
- All dependencies are installed
- Enough disk space (build needs ~2-3GB)
