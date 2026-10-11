# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../bindery.py'],
    pathex=[],
    binaries=[],
    datas=[('../Book', 'Book'), ('../Bindery.icns', '.')],
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
    [],
    exclude_binaries=True,
    name='Bindery',
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
    icon=['../Bindery.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Bindery',
)
app = BUNDLE(
    coll,
    name='Bindery.app',
    icon='../Bindery.icns',
    bundle_identifier=None,
)
