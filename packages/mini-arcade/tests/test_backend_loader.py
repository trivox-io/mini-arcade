from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mini_arcade.common.backend_loader import BackendLoader


def test_backend_loader_raises_when_explicit_native_backend_fails(
    monkeypatch,
) -> None:
    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "mini_arcade_native_backend":
            raise ImportError("native backend unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    try:
        BackendLoader.load_backend({"provider": "native"})
    except ImportError as exc:
        assert "native backend unavailable" in str(exc)
    else:
        raise AssertionError(
            "Expected ImportError for explicit native backend"
        )
