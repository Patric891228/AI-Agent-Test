# PyInstaller build spec for bundling the app with a portable Tesseract folder.

from pathlib import Path

project_root = Path.cwd()
datas = [(str(project_root / "config.yaml"), ".")]

vendor_tesseract = project_root / "vendor" / "tesseract"
if vendor_tesseract.exists():
    datas.append((str(vendor_tesseract), "vendor/tesseract"))


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
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
    name="AI-Agent-Test",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
