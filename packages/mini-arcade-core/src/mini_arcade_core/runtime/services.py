"""
Service container for runtime components.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.runtime.audio.audio_port import AudioPort
from mini_arcade_core.runtime.capture.capture_service_protocol import (
    CaptureServicePort,
)
from mini_arcade_core.runtime.file.file_port import FilePort
from mini_arcade_core.runtime.input.input_port import InputPort
from mini_arcade_core.runtime.render.render_port import RenderServicePort
from mini_arcade_core.runtime.scene.scene_query_port import SceneQueryPort
from mini_arcade_core.runtime.window.window_port import WindowPort


@dataclass
class RuntimeServices:
    """
    Container for runtime service ports.

    :ivar window (WindowPort): Window service port.
    :ivar scenes (ScenePort): Scene management service port.
    :ivar audio (AudioPort): Audio service port.
    :ivar files (FilePort): File service port.
    :ivar capture (CaptureServicePort): Capture service port.
    :ivar input (InputPort): Input handling service port.
    :ivar render (RenderServicePort): Rendering service port.
    """

    window: WindowPort
    audio: AudioPort
    files: FilePort
    capture: CaptureServicePort
    input: InputPort
    render: RenderServicePort
    scenes: SceneQueryPort
