from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
CORE_SRC_ROOT = PACKAGE_ROOT.parent / "mini-arcade-core" / "src"


def test_render_port_draw_texture_falls_back_to_legacy_signature(
    monkeypatch,
) -> None:
    monkeypatch.syspath_prepend(str(CORE_SRC_ROOT))
    monkeypatch.syspath_prepend(str(SRC_ROOT))

    from mini_arcade_core.backend.viewport import ViewportTransform
    from mini_arcade_native_backend.ports.render import RenderPort

    calls: list[tuple[int, int, int, int, int]] = []

    class _LegacyBackend:
        def draw_texture(
            self,
            texture_id: int,
            x: int,
            y: int,
            width: int,
            height: int,
        ) -> None:
            calls.append((texture_id, x, y, width, height))

    port = RenderPort(_LegacyBackend(), ViewportTransform())

    port.draw_texture(5, 380, 530, 40, 20, 15.0)

    assert calls == [(5, 380, 530, 40, 20)]
