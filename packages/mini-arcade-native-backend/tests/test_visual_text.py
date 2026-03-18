from __future__ import annotations

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from PIL import Image

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
REPO_ROOT = PACKAGE_ROOT.parents[1]

# experiments/ is gitignored and unavailable in CI.
_experiments_available = (REPO_ROOT / "experiments").is_dir()
if not _experiments_available:
    pytest.skip(
        "experiments/ directory not available (gitignored)",
        allow_module_level=True,
    )

EXTRA_PATHS = (
    REPO_ROOT,
    REPO_ROOT / "packages" / "mini-arcade" / "src",
    REPO_ROOT / "packages" / "mini-arcade-core" / "src",
    REPO_ROOT / "packages" / "mini-arcade-pygame-backend" / "src",
    SRC_ROOT,
)
for path in reversed(EXTRA_PATHS):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from experiments.bouncing_balls.system_lab_case import (  # noqa: E402
    BouncingBallsContext,
    BouncingBallsRenderSystem,
    build_bouncing_balls_world,
)
from mini_arcade.modules.backend_loader import BackendLoader  # noqa: E402
from mini_arcade_core.engine.commands import CommandQueue  # noqa: E402
from mini_arcade_core.engine.render.context import RenderContext  # noqa: E402
from mini_arcade_core.engine.render.frame_packet import (  # noqa: E402
    FramePacket,
)
from mini_arcade_core.engine.render.pipeline import (  # noqa: E402
    RenderPipeline,
)
from mini_arcade_core.engine.render.viewport import (  # noqa: E402
    ViewportMode,
    ViewportState,
)
from mini_arcade_core.runtime.input_frame import InputFrame  # noqa: E402


def _render_packet_image(packet, *, width: int, height: int) -> Image.Image:
    try:
        backend = BackendLoader.load_backend(
            {
                "provider": "native",
                "window": {
                    "width": width,
                    "height": height,
                    "title": "native-text-test",
                    "resizable": False,
                },
                "renderer": {
                    "background_color": [10, 10, 14],
                },
                "audio": {
                    "enable": False,
                },
            }
        )
    except ImportError as exc:
        pytest.skip(f"native backend extension is unavailable: {exc}")
    backend.init()

    viewport = ViewportState(
        virtual_w=width,
        virtual_h=height,
        window_w=width,
        window_h=height,
        mode=ViewportMode.FIT,
        scale=1.0,
        viewport_w=width,
        viewport_h=height,
        offset_x=0,
        offset_y=0,
    )

    backend.render.begin_frame()
    try:
        RenderPipeline().render_frame(
            backend,
            RenderContext(viewport=viewport),
            [
                FramePacket(
                    scene_id="test_scene",
                    is_overlay=False,
                    packet=packet,
                )
            ],
        )
        with NamedTemporaryFile(suffix=".bmp", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        backend.capture.bmp(str(tmp_path))
    finally:
        backend.render.end_frame()
        native_backend = getattr(backend, "_backend", None)
        if native_backend is not None and hasattr(native_backend, "shutdown"):
            native_backend.shutdown()

    image = Image.open(tmp_path).convert("RGBA")
    out = image.copy()
    image.close()
    tmp_path.unlink(missing_ok=True)
    return out


def _count_non_background_pixels(
    image: Image.Image,
    *,
    rect: tuple[int, int, int, int],
    background: tuple[int, int, int],
) -> int:
    x0, y0, x1, y1 = rect
    count = 0
    for y in range(y0, min(y1, image.height)):
        for x in range(x0, min(x1, image.width)):
            if image.getpixel((x, y))[:3] != background:
                count += 1
    return count


def test_native_backend_renders_bouncing_balls_hud_text() -> None:
    ctx = BouncingBallsContext(
        input_frame=InputFrame(frame_index=0, dt=1.0 / 60.0),
        dt=1.0 / 60.0,
        world=build_bouncing_balls_world(viewport=(800.0, 600.0)),
        commands=CommandQueue(),
    )

    BouncingBallsRenderSystem().step(ctx)
    image = _render_packet_image(ctx.packet, width=800, height=600)

    # This region contains the HUD text only, not the moving balls.
    assert (
        _count_non_background_pixels(
            image,
            rect=(0, 0, 420, 180),
            background=(10, 10, 14),
        )
        > 4_000
    )
