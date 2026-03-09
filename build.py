"""
VoxControl -- Build script.

Creates a distributable Windows application using PyInstaller.

Usage:
  python build.py              # Build the .exe (onedir)
  python build.py --clean      # Clean previous builds first
  python build.py --installer  # Build .exe then create Inno Setup installer

Requirements:
  pip install pyinstaller
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.absolute()
# Avoid UNC paths on mapped drives — PyInstaller doesn't handle them well
if str(ROOT).startswith("\\\\"):
    import os
    cwd = os.getcwd()
    if not cwd.startswith("\\\\"):
        ROOT = Path(cwd)

# Directories
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"
SPEC_FILE = ROOT / "VoxControl.spec"
INSTALLER_DIR = ROOT / "installer"


def check_pyinstaller():
    """Verify PyInstaller is installed."""
    try:
        import PyInstaller  # noqa: F401
        print(f"  PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("ERROR: PyInstaller not installed.")
        print("  Install with:  pip install pyinstaller")
        return False


def clean():
    """Remove previous build artifacts."""
    print("\n-- Cleaning previous builds --")
    for d in [BUILD_DIR, DIST_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"  Removed {d}")
    print("  Clean done.\n")


def ensure_assets():
    """Create a default icon if none exists."""
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    icon_path = assets / "icon.ico"

    if not icon_path.exists():
        print("  Generating default icon...")
        try:
            from PIL import Image, ImageDraw

            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # Purple circle
            draw.ellipse([16, 16, 240, 240], fill=(108, 99, 255, 255))
            # Mic body
            draw.rounded_rectangle([96, 56, 160, 152], radius=32, fill=(255, 255, 255, 255))
            # Mic arc
            draw.arc([72, 112, 184, 192], start=0, end=180, fill=(255, 255, 255, 255), width=8)
            # Stand
            draw.line([128, 192, 128, 216], fill=(255, 255, 255, 255), width=8)
            draw.line([100, 216, 156, 216], fill=(255, 255, 255, 255), width=8)

            # Save as .ico with multiple sizes
            img.save(str(icon_path), format="ICO",
                     sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
            print(f"  Created {icon_path}")
        except ImportError:
            print("  Pillow not available — skipping icon generation")


def create_version_info():
    """Create a Windows version info file for the .exe."""
    version_file = INSTALLER_DIR / "version_info.txt"
    if version_file.exists():
        return

    INSTALLER_DIR.mkdir(exist_ok=True)
    version_file.write_text(r"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    fileVers=(1, 1, 0, 0),
    prodVers=(1, 1, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'VoxControl'),
            StringStruct(u'FileDescription', u'VoxControl - Voice Control for Windows'),
            StringStruct(u'FileVersion', u'1.1.0.0'),
            StringStruct(u'InternalName', u'VoxControl'),
            StringStruct(u'OriginalFilename', u'VoxControl.exe'),
            StringStruct(u'ProductName', u'VoxControl'),
            StringStruct(u'ProductVersion', u'1.1.0'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
""", encoding="utf-8")
    print(f"  Created {version_file}")


def build_exe():
    """Run PyInstaller with the spec file."""
    print("\n-- Building VoxControl.exe --")

    ensure_assets()
    create_version_info()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        str(SPEC_FILE),
    ]

    print(f"  Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(ROOT))

    if result.returncode != 0:
        print("\nERROR: PyInstaller build failed.")
        sys.exit(1)

    exe_path = DIST_DIR / "VoxControl" / "VoxControl.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n  BUILD SUCCESSFUL")
        print(f"  Output: {DIST_DIR / 'VoxControl'}")
        print(f"  Exe:    {exe_path} ({size_mb:.1f} MB)")
    else:
        print("\nERROR: VoxControl.exe not found after build.")
        sys.exit(1)

    return exe_path


def build_installer():
    """Build Inno Setup installer (requires Inno Setup installed)."""
    print("\n-- Building Windows Installer --")

    iss_file = INSTALLER_DIR / "setup.iss"
    if not iss_file.exists():
        print(f"ERROR: {iss_file} not found.")
        sys.exit(1)

    # Try common Inno Setup paths
    iscc_paths = [
        Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Inno Setup 6" / "ISCC.exe",
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
    ]

    iscc = None
    for p in iscc_paths:
        if p.exists():
            iscc = p
            break

    if not iscc:
        print("WARNING: Inno Setup 6 not found.")
        print("  Download from: https://jrsoftware.org/isdl.php")
        print("  The .exe was built successfully — you can distribute the dist/VoxControl/ folder directly.")
        return

    cmd = [str(iscc), str(iss_file)]
    print(f"  Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(ROOT))

    if result.returncode != 0:
        print("\nERROR: Inno Setup build failed.")
        sys.exit(1)

    print("\n  INSTALLER BUILT SUCCESSFULLY")
    print(f"  Output: {DIST_DIR / 'VoxControlSetup.exe'}")


def main():
    parser = argparse.ArgumentParser(description="Build VoxControl distribution")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts first")
    parser.add_argument("--installer", action="store_true", help="Also build Inno Setup installer")
    args = parser.parse_args()

    print("=" * 56)
    print("  VoxControl Build System")
    print("=" * 56)

    if not check_pyinstaller():
        sys.exit(1)

    if args.clean:
        clean()

    build_exe()

    if args.installer:
        build_installer()

    print("\n" + "=" * 56)
    print("  Build complete!")
    print("=" * 56)


if __name__ == "__main__":
    main()
