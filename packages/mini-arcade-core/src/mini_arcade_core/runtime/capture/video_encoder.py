"""
Video encoding utilities.
"""

from __future__ import annotations

import subprocess
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import os

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
    audio_path: Path | None = None,
    input_fps: float,  # <-- effective capture fps
    output_fps: (
        int | None
    ) = None,  # <-- optional container fps (e.g. 60)
    video_interpolate: bool = False,
    expected_duration_seconds: float | None = None,
    frame_times_seconds: tuple[float, ...] | None = None,
    progress_callback: Callable[[float], None] | None = None,
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
    :type input_fps: float
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
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frame_paths = sorted(frames_dir.glob("frame_*.png"))
    concat_path: Path | None = None
    use_variable_timestamps = bool(
        frame_times_seconds
        and len(frame_paths) == len(frame_times_seconds)
        and len(frame_paths) >= 2
    )
    cmd = [
        ffmpeg_path,
        "-y",
        "-loglevel",
        "error",
        "-nostats",
        "-progress",
        "pipe:1",
    ]
    if use_variable_timestamps:
        concat_path = frames_dir / "__frames_concat.txt"
        _write_concat_manifest(
            concat_path=concat_path,
            frame_paths=frame_paths,
            frame_times_seconds=tuple(float(v) for v in frame_times_seconds or ()),
            expected_duration_seconds=expected_duration_seconds,
            fallback_frame_seconds=(
                1.0 / max(1.0, float(input_fps))
            ),
        )
        cmd += [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
        ]
    else:
        frames_glob = frames_dir / pattern
        cmd += [
            "-framerate",
            str(input_fps),
            "-i",
            str(frames_glob),
        ]
    if audio_path is not None and audio_path.is_file():
        cmd += [
            "-i",
            str(audio_path),
        ]

    should_interpolate = bool(
        video_interpolate
        and output_fps is not None
        and output_fps > 0
        and float(output_fps) > (float(input_fps) + 0.5)
    )
    if use_variable_timestamps:
        cmd += ["-vsync", "vfr"]
        if should_interpolate:
            cmd += [
                "-vf",
                f"minterpolate=fps={output_fps}:mi_mode=mci:mc_mode=aobmc:vsbmc=1",
            ]
    elif output_fps is not None and output_fps > 0:
        if should_interpolate:
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
    ]
    if audio_path is not None and audio_path.is_file():
        cmd += [
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
        ]
    cmd += [
        str(output_path),
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stderr_chunks: list[str] = []
        stdout_stream = proc.stdout
        if stdout_stream is not None:
            for raw_line in stdout_stream:
                line = raw_line.strip()
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if (
                    key in {"out_time_us", "out_time_ms"}
                    and expected_duration_seconds is not None
                    and expected_duration_seconds > 0.0
                ):
                    try:
                        raw = float(value)
                    except ValueError:
                        continue
                    seconds = raw / (
                        1_000_000.0 if key == "out_time_us" else 1_000.0
                    )
                    if progress_callback is not None:
                        progress_callback(
                            min(0.99, seconds / float(expected_duration_seconds))
                        )
        stderr_text = ""
        if proc.stderr is not None:
            stderr_text = proc.stderr.read()
            if stderr_text:
                stderr_chunks.append(stderr_text)
        return_code = proc.wait()
        if return_code != 0:
            return EncodeResult(
                ok=False,
                error=("".join(stderr_chunks) or "ffmpeg failed").strip(),
            )
        if progress_callback is not None:
            progress_callback(1.0)
        return EncodeResult(ok=True, output_path=output_path)
    except FileNotFoundError as exc:
        logger.error(f"ffmpeg not found: {exc}")
        return EncodeResult(ok=False, error=f"ffmpeg not found: {exc}")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        tb_str = traceback.format_exc()
        logger.error(f"ffmpeg encoding error: {exc}\n{tb_str}")
        return EncodeResult(ok=False, error=f"ffmpeg encoding error: {exc}")
    finally:
        if concat_path is not None:
            try:
                concat_path.unlink(missing_ok=True)
            except OSError:
                pass


def _write_concat_manifest(
    *,
    concat_path: Path,
    frame_paths: list[Path],
    frame_times_seconds: tuple[float, ...],
    expected_duration_seconds: float | None,
    fallback_frame_seconds: float,
) -> None:
    lines: list[str] = []
    last_time = max(0.0, float(frame_times_seconds[-1]))
    total_duration = (
        max(last_time, float(expected_duration_seconds))
        if expected_duration_seconds is not None
        else last_time + max(0.001, float(fallback_frame_seconds))
    )
    for index, frame_path in enumerate(frame_paths):
        lines.append(f"file '{_ffmpeg_escape_path(frame_path)}'")
        if index < len(frame_paths) - 1:
            duration = max(
                0.001,
                float(frame_times_seconds[index + 1]) - float(frame_times_seconds[index]),
            )
            lines.append(f"duration {duration:.9f}")
    final_duration = max(0.001, float(total_duration) - float(last_time))
    lines.append(f"duration {final_duration:.9f}")
    lines.append(f"file '{_ffmpeg_escape_path(frame_paths[-1])}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ffmpeg_escape_path(path: Path) -> str:
    absolute = path.resolve()
    text = os.fspath(absolute)
    return text.replace("\\", "/").replace("'", "'\\''")
