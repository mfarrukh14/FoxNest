# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Analysis for fox client
fox_a = Analysis(
    ['foxnest/fox_client.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'requests', 'json', 'hashlib', 'shutil', 'argparse', 
        'base64', 'datetime', 'pathlib', 'os', 'sys'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Analysis for fox server
server_a = Analysis(
    ['foxnest/server.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'flask', 'requests', 'json', 'hashlib', 'shutil', 
        'datetime', 'pathlib', 'base64', 'os', 'sys'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Create PYZ archives
fox_pyz = PYZ(fox_a.pure, fox_a.zipped_data, cipher=block_cipher)
server_pyz = PYZ(server_a.pure, server_a.zipped_data, cipher=block_cipher)

# Create executables
fox_exe = EXE(
    fox_pyz,
    fox_a.scripts,
    [],
    exclude_binaries=True,
    name='fox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add 'foxnest.ico' here when available
)

server_exe = EXE(
    server_pyz,
    server_a.scripts,
    [],
    exclude_binaries=True,
    name='fox-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add 'foxnest.ico' here when available
)

# Collect all files into distribution directory
coll = COLLECT(
    fox_exe,
    fox_a.binaries,
    fox_a.zipfiles,
    fox_a.datas,
    server_exe,
    server_a.binaries,
    server_a.zipfiles,
    server_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='foxnest',
)
