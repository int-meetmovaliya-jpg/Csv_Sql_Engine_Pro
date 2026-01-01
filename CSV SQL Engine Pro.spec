# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('ui_streamlit.py', '.'), ('versioning.py', '.'), ('macros.py', '.'), ('version.json', '.'), ('engine.py', '.'), ('ingestion.py', '.'), ('completer.py', '.'), ('native_window.py', '.'), ('utils.py', '.')]
binaries = []
hiddenimports = ['PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtGui']
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('duckdb')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PyQt5')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Exclude problematic PyQt5 modules that cause symlink issues
exclude_modules = ['PyQt5.QtBluetooth', 'PyQt5.QtNfc', 'PyQt5.Qt3D', 'PyQt5.QtGamepad', 'PyQt5.Qt3DCore', 'PyQt5.Qt3DRender', 'PyQt5.Qt3DInput', 'PyQt5.Qt3DLogic', 'PyQt5.Qt3DAnimation', 'PyQt5.Qt3DExtras', 'PyQt5.Qt3DQuick', 'PyQt5.Qt3DQuickScene2D', 'PyQt5.QtPdf', 'PyQt5.QtBodymovin']


a = Analysis(
    ['bootstrap.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=exclude_modules,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CSV SQL Engine Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CSV SQL Engine Pro',
)
app = BUNDLE(
    coll,
    name='CSV SQL Engine Pro.app',
    icon='app_icon.icns',
    bundle_identifier='com.csvsql.engine.pro',
)
