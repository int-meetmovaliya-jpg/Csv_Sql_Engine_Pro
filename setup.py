"""
py2app setup file for CSV SQL Engine Pro
"""
from setuptools import setup

APP = ['bootstrap.py']
DATA_FILES = [
    ('', ['ui_streamlit.py', 'versioning.py', 'macros.py', 'version.json', 
          'engine.py', 'ingestion.py', 'completer.py', 'native_window.py', 
          'utils.py', 'app_icon.icns']),
    ('data', []),
    ('schemas', []),
]

OPTIONS = {
    'argv_emulation': False,
    'packages': ['streamlit', 'duckdb', 'pandas', 'PyQt5'],
    'includes': ['streamlit', 'duckdb', 'pandas', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 
                 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtGui', 'native_window', 'utils'],
    'excludes': ['PyInstaller', 'matplotlib', 'scipy'],
    'iconfile': 'app_icon.icns',
    'plist': {
        'CFBundleName': 'CSV SQL Engine Pro',
        'CFBundleDisplayName': 'CSV SQL Engine Pro',
        'CFBundleGetInfoString': 'CSV SQL Engine Pro - SQL Engine for CSV Files',
        'CFBundleIdentifier': 'com.csvsql.engine.pro',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
    'frameworks': [],
    'site_packages': True,
}

setup(
    app=APP,
    name='CSV SQL Engine Pro',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

