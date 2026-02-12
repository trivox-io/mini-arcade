"""
Type stubs for the native backend module.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Dict, Tuple

# Justification: Some methods have many arguments for configuration purposes.
# pylint: disable=too-many-positional-arguments,too-many-arguments

# Justification: 'id' and 'type' are commonly used names in this context.
# pylint: disable=redefined-builtin

# Justification: Enum members use PascalCase by convention.
# pylint: disable=invalid-name

class EventType(IntEnum):
    """Enumeration of event types."""

    Unknown = 0
    Quit = 1
    KeyDown = 2
    KeyUp = 3
    MouseMotion = 4
    MouseButtonDown = 5
    MouseButtonUp = 6
    MouseWheel = 7
    WindowResized = 8
    TextInput = 9

class RenderAPI(IntEnum):
    """Enumeration of rendering APIs."""

    SDL2 = 0
    OpenGL = 1

class Event:
    """
    Representation of a native event.

    :ivar type (EventType): The type of the event.
    :ivar key (int): Key code for keyboard events.
    :ivar scancode (int): Scancode for keyboard events.
    :ivar mod (int): Modifier keys state.
    :ivar repeat (int): Repeat count for keyboard events.
    :ivar x (int): X coordinate for mouse events.
    :ivar y (int): Y coordinate for mouse events.
    :ivar dx (int): Change in X for mouse motion events.
    :ivar dy (int): Change in Y
    :ivar button (int): Mouse button for mouse button events.
    :ivar wheel_x (int): Wheel movement in X direction.
    :ivar wheel_y (int): Wheel movement in Y direction.
    :ivar width (int): Width for window resize events.
    :ivar height (int): Height for window resize events.
    :ivar text (str): Text input for text input events.
    """

    type: EventType
    key: int
    scancode: int
    mod: int
    repeat: int
    x: int
    y: int
    dx: int
    dy: int
    button: int
    wheel_x: int
    wheel_y: int
    width: int
    height: int
    text: str

class ColorRGBA:
    """
    Representation of an RGBA color.

    :ivar r (int): Red component (0-255).
    :ivar g (int): Green component (0-255).
    :ivar b (int): Blue component (0-255).
    :ivar a (int): Alpha component (0-255).
    """

    r: int
    g: int
    b: int
    a: int

class WindowConfig:
    """
    Configuration for the application window.

    :ivar width (int): Width of the window.
    :ivar height (int): Height of the window.
    :ivar title (str): Title of the window.
    :ivar resizable (bool): Whether the window is resizable.
    :ivar high_dpi (bool): Whether to enable high DPI support.
    """

    width: int
    height: int
    title: str
    resizable: bool
    high_dpi: bool

class RenderConfig:
    """
    Configuration for the rendering system.

    :ivar api (RenderAPI): The rendering API to use.
    """

    api: RenderAPI
    clear_color: ColorRGBA

class TextConfig:
    """
    Configuration for the text rendering system.

    :ivar default_font_path (str): Path to the default font.
    :ivar default_font_size (int): Size of the default font.
    """

    default_font_path: str
    default_font_size: int

class AudioConfig:
    """
    Configuration for the audio system.

    :ivar enabled (bool): Whether audio is enabled.
    :ivar frequency (int): Audio frequency.
    :ivar channels (int): Number of audio channels.
    :ivar chunk_size (int): Size of audio chunks.
    """

    enabled: bool
    frequency: int
    channels: int
    chunk_size: int

class BackendConfig:
    """
    Configuration for the native backend.

    :ivar window (WindowConfig): Window configuration.
    :ivar render (RenderConfig): Render configuration.
    :ivar text (TextConfig): Text configuration.
    :ivar audio (AudioConfig): Audio configuration.
    :ivar sounds (Dict[str, str]): Mapping of sound IDs to file paths.
    """

    window: WindowConfig
    render: RenderConfig
    text: TextConfig
    audio: AudioConfig
    sounds: Dict[str, str]

class Window:
    """
    Window management class.
    """

    def set_title(self, title: str):
        """
        Set the window title.

        :param title: The new title for the window.
        :type title: str
        """

    def resize(self, w: int, h: int):
        """
        Resize the window.

        :param w: New width of the window.
        :type w: int
        :param h: New height of the window.
        :type h: int
        """

    def size(self) -> Tuple[int, int]:
        """
        Get the current size of the window.

        :return: A tuple containing the width and height of the window.
        :rtype: Tuple[int, int]
        """

    def drawable_size(self) -> Tuple[int, int]:
        """
        Get the drawable size of the window.

        :return: A tuple containing the drawable width and height of the window.
        :rtype: Tuple[int, int]
        """

class Audio:
    """
    Audio management class.
    """

    def init(
        self, frequency: int = 44100, channels: int = 2, chunk_size: int = 2048
    ):
        """
        :param frequency: Audio frequency (default is 44100).
        :type frequency: int
        :param channels: Number of audio channels (default is 2).
        :type channels: int
        :param chunk_size: Size of audio chunks (default is 2048).
        :type chunk_size: int
        """

    def shutdown(self):
        """Shutdown the audio system."""

    def load_sound(self, id: str, path: str):
        """
        Load a sound from the given file path.

        :param id: Identifier for the sound.
        :type id: str
        :param path: File path to the sound.
        :type path: str
        """

    def play_sound(self, id: str, loops: int = 0):
        """
        Play a sound by its identifier.

        :param id: Identifier of the sound to play.
        :type id: str
        :param loops: Number of times to loop the sound (default is 0).
        :type loops: int
        """

    def set_master_volume(self, volume: int):
        """
        Set the master volume for audio playback.

        :param volume: Volume level (0-100).
        :type volume: int
        """

    def set_sound_volume(self, id: str, volume: int):
        """
        Set the volume for a specific sound.

        :param id: Identifier of the sound.
        :type id: str
        :param volume: Volume level (0-100).
        :type volume: int
        """

    def stop_all(self):
        """Stop all currently playing sounds."""

class Backend:
    """
    Native backend class.

    :ivar window (Window): Window management instance.
    :ivar audio (Audio): Audio management instance.
    """

    window: Window
    audio: Audio

    def __init__(self, config: BackendConfig):
        """
        :param config: Configuration for the backend.
        :type config: BackendConfig
        """

    def set_clear_color(self, r: int, g: int, b: int):
        """
        Set the clear color for rendering.

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

    def draw_rect(
        self, x: int, y: int, w: int, h: int, r: int, g: int, b: int, a: int
    ):
        """
        Draw a rectangle.

        :param x: X coordinate of the rectangle.
        :type x: int
        :param y: Y coordinate of the rectangle.
        :type y: int
        :param w: Width of the rectangle.
        :type w: int
        :param h: Height of the rectangle.
        :type h: int
        :param r: Red component (0-255).
        :type r: int
        :param g: Green component (0-255).
        :type g: int
        :param b: Blue component (0-255).
        :type b: int
        :param a: Alpha component (0-255).
        :type a: int
        """

    def draw_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        r: int,
        g: int,
        b: int,
        a: int,
    ):
        """
        Draw a line.

        :param x1: X coordinate of the start point.
        :type x1: int
        :param y1: Y coordinate of the start point.
        :type y1: int
        :param x2: X coordinate of the end point.
        :type x2: int
        :param y2: Y coordinate of the end point.
        :type y2: int
        :param r: Red component (0-255).
        :type r: int
        :param g: Green component (0-255).
        :type g: int
        :param b: Blue component (0-255).
        :type b: int
        :param a: Alpha component (0-255).
        :type a: int
        """

    def set_clip_rect(self, x: int, y: int, w: int, h: int):
        """
        Set the clipping rectangle for rendering.

        :param x: X coordinate of the clipping rectangle.
        :type x: int
        :param y: Y coordinate of the clipping rectangle.
        :type y: int
        :param w: Width of the clipping rectangle.
        :type w: int
        :param h: Height of the clipping rectangle.
        :type h: int
        """

    def clear_clip_rect(self):
        """Clear the clipping rectangle."""

    def load_font(self, path: str, pt: int) -> int:
        """
        Load a font from the given file path.

        :param path: File path to the font.
        :type path: str
        :param pt: Point size of the font.
        :type pt: int
        :return: Font identifier.
        :rtype: int
        """

    def measure_text(self, text: str, font_id: int = -1) -> Tuple[int, int]:
        """
        Measure the dimensions of the given text.

        :param text: The text to measure.
        :type text: str
        :param font_id: Identifier of the font to use (default is -1 for default font).
        :type font_id: int
        :return: A tuple containing the width and height of the text.
        :rtype: Tuple[int, int]
        """

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        r: int,
        g: int,
        b: int,
        a: int,
        font_id: int = -1,
    ):
        """
        Draw text at the specified position.

        :param text: The text to draw.
        :type text: str
        :param x: X coordinate for the text.
        :type x: int
        :param y: Y coordinate for the text.
        :type y: int
        :param r: Red component (0-255).
        :type r: int
        :param g: Green component (0-255).
        :type g: int
        :param b: Blue component (0-255).
        :type b: int
        :param a: Alpha component (0-255).
        :type a: int
        :param font_id: Identifier of the font to use (default is -1 for default font).
        :type font_id: int
        """

    def poll_events(self) -> list[Event]:
        """
        Poll for native events.

        :return: A list of polled events.
        :rtype: list[Event]
        """

    def capture_bmp(self, path: str) -> bool:
        """
        Capture the current frame buffer to a BMP file.

        :param path: File path to save the BMP image.
        :type path: str
        :return: True if the capture was successful, False otherwise.
        :rtype: bool
        """

    def capture_argb8888_bytes(self) -> tuple[int, int, bytes]:
        """
        Capture the current frame buffer and return pixel data in ARGB8888 format.

        :return: A tuple containing the width, height, and pixel data in ARGB8888 format.
        :rtype: tuple[int, int, bytes]
        """

    def create_texture_rgba(
        self, width: int, height: int, data: bytes, pitch: int = -1
    ) -> int:
        """
        Create a texture from RGBA pixel data.

        :param width: Width of the texture.
        :type width: int
        :param height: Height of the texture.
        :type height: int
        :param data: Pixel data in RGBA format.
        :type data: bytes
        :param pitch: Number of bytes per row (default is -1 for tightly packed).
        :type pitch: int
        :return: Texture identifier.
        :rtype: int
        """

    def draw_texture(
        self, texture_id: int, x: int, y: int, width: int, height: int
    ) -> None:
        """
        Draw a texture at the specified position and size.

        :param texture_id: Identifier of the texture to draw.
        :type texture_id: int
        :param x: X coordinate for the texture.
        :type x: int
        :param y: Y coordinate for the texture.
        :type y: int
        :param width: Width of the texture.
        :type width: int
        :param height: Height of the texture.
        :type height: int
        """

    def destroy_texture(self, texture_id: int) -> None:
        """
        Destroy a texture by its identifier.

        :param texture_id: Identifier of the texture to destroy.
        :type texture_id: int
        """

    def draw_texture_tiled_y(
        self, texture_id: int, x: int, y: int, width: int, height: int
    ) -> None:
        """
        Draw a texture repeated vertically to fill (width, height).

        :param texture_id: Identifier of the texture to draw.
        :type texture_id: int
        :param x: X coordinate for the texture.
        :type x: int
        :param y: Y coordinate for the texture.
        :type y: int
        :param width: Width of the area to fill with the texture.
        :type width: int
        :param height: Height of the area to fill with the texture.
        :type height: int
        """
