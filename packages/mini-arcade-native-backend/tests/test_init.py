from __future__ import annotations

import importlib
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"


def test_editable_loader_exposes_compiled_native_symbols(monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(SRC_ROOT))

    for module_name in (
        "mini_arcade_native_backend._native",
        "mini_arcade_native_backend",
    ):
        sys.modules.pop(module_name, None)

    package = importlib.import_module("mini_arcade_native_backend")
    native = importlib.import_module("mini_arcade_native_backend._native")

    assert Path(package.__file__).resolve().is_relative_to(SRC_ROOT.resolve())
    assert hasattr(native, "RenderAPI")
    assert hasattr(native, "BackendConfig")
    assert hasattr(native, "Backend")
