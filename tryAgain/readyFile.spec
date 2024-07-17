# -*- mode: python ; coding: utf-8 -*-

import os

# Assuming the tkdnd library is in a folder named 'tkdnd' in the same directory as the script
tkdnd_path = 'C:\\Users\\User\\AppData\\Roaming\\Python\\Python38\\site-packages\\python_tkdnd-0.2.1.dist-info'

a = Analysis(
    ['readyFile.py'],
    pathex=[],
    binaries=[],
    datas=[
        (tkdnd_path, "tkdnd"),  # Include the tkdnd directory
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='readyFile',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
