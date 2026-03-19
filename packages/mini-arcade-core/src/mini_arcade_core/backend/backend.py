"""
Backend interface for rendering and input.
This is the only part of the code that talks to SDL/pygame directly.
"""

from __future__ import annotations

from typing import Iterable, Protocol

from .events import Event

# Justification: Many positional and keyword arguments needed for some backend methods.
# Might be refactored later.
# pylint: disable=too-many-positional-arguments,too-many-arguments


class WindowProtocol(Protocol):
    """
    Represents a game window.
    """

    width: int
    height: int

    def set_title(self, title: str):
        """
        Set the window title.

        :param title: New window title.
        :type title: str
        """

    def resize(self, width: int, height: int):
        """
        Resize the window.

        :param width: New width in pixels.
        :type width: int
        :param height: New height in pixels.
        :type height: int
        """

    def size(self) -> tuple[int, int]:
        """
        Get the window size.

        :return: Tuple of (width, height) in pixels.
        :rtype: tuple[int, int]
        """

    def drawable_size(self) -> tuple[int, int]:
        """
        Get the drawable size of the window.

        :return: Tuple of (width, height) in pixels.
        :rtype: tuple[int, int]
        """


class InputProtocol(Protocol):
    """
    Interface for input operations.
    """

    def poll(self) -> Iterable[Event]:
        """
        Get the list of input events since the last call.

        :return: Iterable of Event instances.
        :rtype: Iterable[Event]
        """


class RenderProtocol(Protocol):
    """
    Interface for rendering operations.
    """

    def set_clear_color(self, r: int, g: int, b: int):
        """
        Set the clear color for the renderer.

        :param r: Red component (0-255).
        :type r: int
        :param g: Green component (0-255).
        :type g: int
        :param b: Blue component (0-255).
        :type b: int
        """

    def begin_frame(self):
        """Begin a new rendering frame."""

    def end_frame(self):
        """End the current rendering frame."""

    def draw_rect(self, x: int, y: int, w: int, h: int, color=(255, 255, 255)):
        """
        Draw a filled rectangle.

        :param x: The x-coordinate of the rectangle.
        :type x: int
        :param y: The y-coordinate of the rectangle.
        :type y: int
        :param w: The width of the rectangle.
        :type w: int
        :param h: The height of the rectangle.
        :type h: int
        :param color: The color of the rectangle as an (R, G, B) or (R, G, B, A) tuple.
        :type color: tuple[int, int, int] | tuple[int, int, int, int]
        """

    def draw_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color=(255, 255, 255),
        thickness: int = 1,
    ):
        """
        Draw a line between two points.

        :param x1: The x-coordinate of the start point.
        :type x1: int
        :param y1: The y-coordinate of the start point.
        :type y1: int
        :param x2: The x-coordinate of the end point.
        :type x2: int
        :param y2: The y-coordinate of the end point.
        :type y2: int
        :param color: The color of the line as an (R, G, B) or (R, G, B, A) tuple.
        :type color: tuple[int, int, int] | tuple[int, int, int, int]
        """

    def set_clip_rect(self, x: int, y: int, w: int, h: int):
        """
        Set the clipping rectangle.

        :param x: The x-coordinate of the clipping rectangle.
        :type x: int
        :param y: The y-coordinate of the clipping rectangle.
        :type y: int
        :param w: The width of the clipping rectangle.
        :type w: int
        :param h: The height of the clipping rectangle.
        :type h: int
        """

    def clear_clip_rect(self):
        """Clear the clipping rectangle."""

    def create_texture_rgba(
        self, w: int, h: int, pixels: bytes, pitch: int | None = None
    ) -> int:
        """
        Create a texture from RGBA pixel data.

        :param w: The width of the texture.
        :type w: int
        :param h: The height of the texture.
        :type h: int
        :param pixels: The pixel data in RGBA format.
        :type pixels: bytes
        :param pitch: The number of bytes in a row of pixel data. If None, defaults to w * 4.
        :type pitch: int | None
        """

    def destroy_texture(self, tex: int) -> None:
        """
        Destroy a texture.

        :param tex: The texture ID to destroy.
        :type tex: int
        """

    def draw_texture(
        self,
        tex: int,
        x: int,
        y: int,
        w: int,
        h: int,
        angle_deg: float = 0.0,
    ):
        """
        Draw a texture at the specified position and size.

        :param tex: The texture ID.
        :type tex: int
        :param x: The x-coordinate to draw the texture.
        :type x: int
        :param y: The y-coordinate to draw the texture.
        :type y: int
        :param w: The width to draw the texture.
        :type w: int
        :param h: The height to draw the texture.
        :type h: int
        :param angle_deg: Clockwise rotation angle in degrees around texture center.
        :type angle_deg: float
        """

    def draw_texture_tiled_y(
        self, tex_id: int, x: int, y: int, w: int, h: int
    ):
        """
        Draw a texture repeated vertically to fill (w,h).
        Assumes you can resolve tex_id -> pygame.Surface, and supports scaling width.

        :param tex_id: The texture ID.
        :type tex_id: int
        :param x: The x-coordinate to draw the texture.
        :type x: int
        :param y: The y-coordinate to draw the texture.
        :type y: int
        :param w: The width to draw the texture.
        :type w: int
        :param h: The height to draw the texture.
        :type h: int
        """

    def draw_circle(self, x: int, y: int, radius: int, color=(255, 255, 255)):
        """
        Draw a filled circle.

        :param x: Center x
        :param y: Center y
        :param radius: Radius in pixels
        :param color: (R,G,B) or (R,G,B,A)
        """

    def draw_poly(
        self,
        points: list[tuple[int, int]],
        color=(255, 255, 255),
        filled: bool = True,
    ):
        """
        Draw a polygon defined by a list of points.

        :param points: List of (x, y) tuples defining the vertices of the polygon.
        :type points: list[tuple[int, int]]
        :param color: The color of the polygon as an (R, G, B) or (R, G, B, A) tuple.
        :type color: tuple[int, int, int] | tuple[int, int, int, int]
        :param filled: Whether to draw a filled polygon or just the outline.
        :type filled: bool
        """


class TextProtocol(Protocol):
    """
    Interface for text rendering operations.
    """

    def measure(
        self,
        text: str,
        font_size: int | None = None,
        font_name: str | None = None,
    ) -> tuple[int, int]:
        """
        Measure the width and height of the given text.

        :param text: The text to measure.
        :type text: str
        :param font_size: The font size to use for measurement.
        :type font_size: int | None
        :param font_name: Optional named font configured by the backend.
        :type font_name: str | None
        :return: A tuple containing the width and height of the text.
        :rtype: tuple[int, int]
        """

    def draw(
        self,
        x: int,
        y: int,
        text: str,
        color=(255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
    ):
        """
        Draw the given text at the specified position.

        :param x: The x-coordinate to draw the text.
        :type x: int
        :param y: The y-coordinate to draw the text.
        :type y: int
        :param text: The text to draw.
        :type text: str
        :param color: The color of the text as an (R, G, B) or (R, G, B, A) tuple.
        :type color: tuple[int, int, int] | tuple[int, int, int, int]
        :param font_size: The font size to use for drawing.
        :type font_size: int | None
        :param font_name: Optional named font configured by the backend.
        :type font_name: str | None
        """


class AudioProtocol(Protocol):
    """
    Interface for audio operations.
    """

    def init(
        self, frequency: int = 44100, channels: int = 2, chunk_size: int = 2048
    ):
        """
        Initialize audio subsystem.

        :param frequency: Audio frequency in Hz.
        :type frequency: int
        :param channels: Number of audio channels (1=mono, 2=stereo).
        :type channels: int
        :param chunk_size: Size of audio chunks.
        :type chunk_size: int
        """

    def shutdown(self):
        """
        Shutdown the audio subsystem.
        """

    def load_sound(self, sound_id: str, path: str):
        """
        Load a sound file.

        :param sound_id: Unique identifier for the sound.
        :type sound_id: str
        :param path: File path to the sound.
        :type path: str
        """

    def play_sound(self, sound_id: str, loops: int = 0):
        """
        Play a loaded sound.

        :param sound_id: Unique identifier for the sound.
        :type sound_id: str
        :param loops: Number of times to loop the sound.
        :type loops: int
        """

    def set_master_volume(self, volume: int):
        """
        Set the master volume.

        :param volume: Volume level (0-128).
        :type volume: int
        """

    def set_sound_volume(self, sound_id: str, volume: int):
        """
        Set volume for a specific sound.

        :param sound_id: Unique identifier for the sound.
        :type sound_id: str
        :param volume: Volume level (0-128).
        :type volume: int
        """

    def stop_all(self):
        """
        Stop all currently playing sounds.
        """


class CaptureProtocol(Protocol):
    """
    Interface for frame capture operations.
    """

    def bmp(self, path: str | None = None) -> bool:
        """
        Capture the current frame as a BMP file.

        :param path: Optional file path to save the BMP. If None, returns bytes.
        :type path: str | None
        :return: Whether the capture was successful.
        :rtype: bool
        """

    def argb8888_bytes(self) -> tuple[int, int, bytes]:
        """
        Capture the current frame as raw ARGB8888 bytes.

        :return: A tuple of (width, height, bytes).
        :rtype: tuple[int, int, bytes]
        """


# Justification: Many public methods needed for backend interface
# pylint: disable=too-many-public-methods
class Backend(Protocol):
    """
    Interface that any rendering/input backend must implement.
    mini-arcade-core only talks to this protocol, never to SDL/pygame directly.

    Each sub-capability is exposed as a typed protocol attribute so that
    systems or draw helpers can accept only the slice they need (e.g.
    ``RenderProtocol`` or ``TextProtocol``) instead of the full backend.

    :ivar window (WindowProtocol): Window management interface.
    :ivar audio (AudioProtocol): Audio management interface.
    :ivar input (InputProtocol): Input management interface.
    :ivar render (RenderProtocol): Rendering interface.
    :ivar text (TextProtocol): Text rendering interface.
    :ivar capture (CaptureProtocol): Frame capture interface.
    """

    window: WindowProtocol
    audio: AudioProtocol
    input: InputProtocol
    render: RenderProtocol
    text: TextProtocol
    capture: CaptureProtocol

    def init(self):
        """
        Initialize the backend and open a window.
        Should be called once before the main loop.
        """

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

    def clear_viewport_transform(self):
        """
        Clear the viewport transformation (reset to defaults).
        """
