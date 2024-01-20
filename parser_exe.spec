# -*- mode: python ; coding: utf-8 -*-
import os
import scipy

os.chdir(os.path.dirname(scipy.__file__))

os.chdir(os.path.normpath(os.getcwd() + os.sep + os.pardir))

newpath = os.path.join(os.getcwd(),"scipy.libs")

a = Analysis(
    ['parser_exe.py'],
    pathex=['C:\\Python310\\lib\\site-packages\\scipy.libs'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='parser_exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='parser_exe',
)
