"""
DLL search path setup for Windows.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def setup_windows_dll_search_paths():
    """Set up DLL search paths on Windows."""
    if sys.platform != "win32":
        return

    # PyInstaller: SDL2.dll next to exe
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        try:
            os.add_dll_directory(str(exe_dir))
        except FileNotFoundError:
            pass

    # vcpkg fallback
    vcpkg_root = os.environ.get("VCPKG_ROOT")
    if vcpkg_root:
        sdl_bin = Path(vcpkg_root) / "installed" / "x64-windows" / "bin"
        if sdl_bin.is_dir():
            try:
                os.add_dll_directory(str(sdl_bin))
            except FileNotFoundError:
                pass
