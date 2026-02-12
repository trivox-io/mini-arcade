"""
Video encoding utilities.
"""

from __future__ import annotations

import subprocess
import traceback
from dataclasses import dataclass
from pathlib import Path

from mini_arcade_core.utils import logger


@dataclass(frozen=True)
class EncodeResult:
    """
    Result of an encoding operation.

    :ivar ok (bool): Whether the encoding was successful.
    :ivar output_path (Path | None): Path to the encoded video file if successful.
    :ivar error (str | None): Error message if the encoding failed.
    """

    ok: bool
    output_path: Path | None = None
    error: str | None = None


# pylint: disable=too-many-arguments
def encode_png_sequence_to_mp4(
    *,
    ffmpeg_path: str,
    frames_dir: Path,
    output_path: Path,
    input_fps: int,  # <-- capture_fps
    output_fps: (
        int | None
    ) = None,  # <-- optional container fps (e.g. 60)video_interpolate: bool = False
    video_interpolate: bool = False,
    pattern: str = "frame_%08d.png",
    codec: str = "libx264",
    crf: int = 18,
    preset: str = "veryfast",
) -> EncodeResult:
    """
    Encodes frames_dir/frame_%08d.png into output_path (mp4).
    Assumes contiguous numbering starting at 0.

    :param ffmpeg_path: Path to the ffmpeg executable.
    :type ffmpeg_path: str
    :param frames_dir: Directory containing the PNG frames to encode.
    :type frames_dir: Path
    :param output_path: Destination path for the encoded video file.
    :type output_path: Path
    :param input_fps: Frames per second of the input PNG sequence.
    :type input_fps: int
    :param output_fps: Frames per second for the output video file.
    :type output_fps: int | None
    :param video_interpolate: Whether to use motion interpolation for output fps.
    :type video_interpolate: bool
    :param pattern: Filename pattern for input frames.
    :type pattern: str
    :param codec: Video codec to use for encoding.
    :type codec: str
    :param crf: Constant Rate Factor for video quality.
    :type crf: int
    :param preset: Preset for video encoding speed/quality tradeoff.
    :type preset: str
    :return: Result of the encoding operation.
    :rtype: EncodeResult
    """
    frames_glob = frames_dir / pattern
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg_path,
        "-y",
        "-framerate",
        str(input_fps),  # <-- IMPORTANT
        "-i",
        str(frames_glob),
    ]

    if output_fps is not None and output_fps > 0:
        if video_interpolate:
            cmd += [
                "-vf",
                f"minterpolate=fps={output_fps}:mi_mode=mci:mc_mode=aobmc:vsbmc=1",
            ]
        cmd += ["-r", str(output_fps)]

    cmd += [
        "-c:v",
        codec,
        "-pix_fmt",
        "yuv420p",
        "-crf",
        str(crf),
        "-preset",
        preset,
        str(output_path),
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            return EncodeResult(
                ok=False,
                error=(proc.stderr or proc.stdout or "ffmpeg failed").strip(),
            )
        return EncodeResult(ok=True, output_path=output_path)
    except FileNotFoundError as exc:
        logger.error(f"ffmpeg not found: {exc}")
        return EncodeResult(ok=False, error=f"ffmpeg not found: {exc}")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        tb_str = traceback.format_exc()
        logger.error(f"ffmpeg encoding error: {exc}\n{tb_str}")
        return EncodeResult(ok=False, error=f"ffmpeg encoding error: {exc}")
