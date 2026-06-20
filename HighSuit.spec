# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Collect all data files
added_files = [
    ('assets', 'assets'),       # music, icons
    ('scores.json', '.'),       # high scores file (if exists)
]

# Only include scores.json if it exists
if not os.path.exists('scores.json'):
    added_files = [('assets', 'assets')]

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'pygame',
        'pygame.mixer',
        'pygame.sndarray',
        'numpy',
        'src.card',
        'src.deck',
        'src.hand',
        'src.player',
        'src.game',
        'src.ui',
        'src.scores',
        'src.sound',
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HighSuit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # No black console window — GUI only
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,           # We'll add an icon in polish step
)