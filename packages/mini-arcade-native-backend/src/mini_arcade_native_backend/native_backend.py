"""
Native backend façade.
"""

from __future__ import annotations

from pathlib import Path

from mini_arcade_core.backend.viewport import ViewportTransform
from mini_arcade_native_backend.config import NativeBackendSettings
from mini_arcade_native_backend.mapping.events import NativeEventMapper
from mini_arcade_native_backend.ports.audio import AudioPort
from mini_arcade_native_backend.ports.capture import CapturePort
from mini_arcade_native_backend.ports.input import InputPort
from mini_arcade_native_backend.ports.render import RenderPort
from mini_arcade_native_backend.ports.text import TextPort
from mini_arcade_native_backend.ports.window import WindowPort

# Justification: native is a compiled extension module.
# pylint: disable=no-name-in-module
from . import _native as native  # type: ignore


def _find_repo_root(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in (current.parent, *current.parents):
        if (
            (candidate / "packages").exists()
            and (candidate / "games").exists()
            and (candidate / "examples").exists()
        ):
            return candidate
    return None


def _default_font_candidates() -> list[Path]:
    """
    Candidate fonts used when no explicit font path is configured.
    """
    module_dir = Path(__file__).resolve().parent
    candidates: list[Path] = [
        module_dir / "assets" / "fonts" / "DejaVuSans.ttf",
        module_dir / "assets" / "fonts" / "default.ttf",
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]

    repo_root = _find_repo_root(module_dir)
    if repo_root is not None:
        candidates.append(
            repo_root
            / "games"
            / "deja-bounce"
            / "assets"
            / "fonts"
            / "deja_vu_dive"
            / "Deja-vu_dive.ttf"
        )

    return candidates


def _resolve_default_font_path() -> str | None:
    for candidate in _default_font_candidates():
        if candidate.exists():
            return str(candidate.resolve())
    return None


# Justification: We want to keep all ports as attributes of the backend.
# pylint: disable=too-many-instance-attributes
class NativeBackend:
    """
    Native backend façade.

    Intentionally small: expose ports as attributes.
    Core will be updated to depend on these sub-ports.

    :param settings: Backend settings.
    :type settings: NativeBackendSettings | None
    """

    def __init__(self, settings: NativeBackendSettings | None = None):
        self._settings = settings or NativeBackendSettings()
        self._vp = ViewportTransform()
        self._backend: native.Backend | None = None

        # Ports (created after init)
        self.window: WindowPort | None = None
        self.input: InputPort | None = None
        self.render: RenderPort | None = None
        self.text: TextPort | None = None
        self.audio: AudioPort | None = None
        self.capture: CapturePort | None = None

    def _initialize_window(self, cfg: native.BackendConfig):
        cfg.window.width = int(self._settings.core.window.width)
        cfg.window.height = int(self._settings.core.window.height)
        cfg.window.title = self._settings.core.window.title
        cfg.window.resizable = self._settings.core.window.resizable
        cfg.window.high_dpi = self._settings.core.window.high_dpi

    def _initialize_renderer(self, cfg: native.BackendConfig):
        cfg.render.api = self._settings.api

        r, g, b = self._settings.core.renderer.background_color
        cfg.render.clear_color.r = int(r)
        cfg.render.clear_color.g = int(g)
        cfg.render.clear_color.b = int(b)
        cfg.render.clear_color.a = 255

    def _initialize_fonts(self, cfg: native.BackendConfig) -> str | None:
        selected_path: str | None = None
        selected_size: int = 24

        if self._settings.core.fonts:
            selected_size = int(self._settings.core.fonts[0].size)
            for font in self._settings.core.fonts:
                if font.path:
                    selected_path = str(font.path)
                    selected_size = int(font.size)
                    break

        if not selected_path:
            selected_path = _resolve_default_font_path()

        if selected_path:
            cfg.text.default_font_path = selected_path
            cfg.text.default_font_size = max(8, int(selected_size))

        return selected_path

    def _initialize_audio(self, cfg: native.BackendConfig):
        cfg.audio.enabled = bool(self._settings.core.audio.enable)

        if self._settings.core.audio.sounds:
            cfg.sounds = dict(self._settings.core.audio.sounds)

    def init(self):
        """
        Initialize the native backend with the given window settings.
        """
        cfg = native.BackendConfig()
        self._initialize_window(cfg)
        self._initialize_renderer(cfg)
        resolved_font_path = self._initialize_fonts(
            cfg,
        )
        self._initialize_audio(cfg)

        self._backend = native.Backend(cfg)

        mapper = NativeEventMapper(native)

        # Build ports
        self.window = WindowPort(self._backend.window)
        self.audio = AudioPort(self._backend.audio)
        self.render = RenderPort(self._backend, self._vp)
        self.text = TextPort(
            self._backend,
            self._vp,
            resolved_font_path,
        )
        self.input = InputPort(self._backend, mapper)
        self.capture = CapturePort(self._backend)

    def set_viewport_transform(
        self, offset_x: int, offset_y: int, scale: float
    ):
        """
        Set the viewport transformation.

        :param offset_x: Horizontal offset.
        :type offset_x: int
        :param offset_y: Vertical offset.
        :type offset_y: int
        :param scale: Scaling factor.
        :type scale: float
        """
        self._vp.ox = int(offset_x)
        self._vp.oy = int(offset_y)
        self._vp.s = float(scale)

    def clear_viewport_transform(self):
        """
        Clear the viewport transformation (reset to defaults).
        """
        self._vp.ox = 0
        self._vp.oy = 0
        self._vp.s = 1.0
