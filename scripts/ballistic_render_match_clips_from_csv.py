from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import time

DEFAULT_PROJECT_NAME = "Ballistic Content"
DEFAULT_CONTENT_DIR = Path(
    "C:/Users/USUARIO/work/mini-arcade/games/ballistic/.mini-arcade/content"
)


def _resolve_api_module():
    candidates: list[Path] = []
    env_root = os.getenv("RESOLVE_SCRIPT_API")
    if env_root:
        candidates.append(Path(env_root) / "Modules")
    program_data = Path(os.getenv("PROGRAMDATA", "C:/ProgramData"))
    candidates.append(
        program_data
        / "Blackmagic Design"
        / "DaVinci Resolve"
        / "Support"
        / "Developer"
        / "Scripting"
        / "Modules"
    )
    for module_dir in candidates:
        if not module_dir.exists():
            continue
        module_str = str(module_dir)
        if module_str not in sys.path:
            sys.path.append(module_str)
        try:
            import DaVinciResolveScript as bmd  # type: ignore

            return bmd
        except ImportError:
            continue
    raise RuntimeError(
        "Could not import DaVinciResolveScript. Set RESOLVE_SCRIPT_API or run from Resolve."
    )


def _get_resolve():
    existing_resolve = globals().get("resolve")
    if existing_resolve is not None:
        return existing_resolve

    app_obj = globals().get("app")
    if app_obj is not None and hasattr(app_obj, "GetResolve"):
        resolve = app_obj.GetResolve()
        if resolve is not None:
            return resolve

    fusion_obj = globals().get("fusion")
    if fusion_obj is not None and hasattr(fusion_obj, "GetResolve"):
        resolve = fusion_obj.GetResolve()
        if resolve is not None:
            return resolve

    bmd = _resolve_api_module()
    resolve = bmd.scriptapp("Resolve")
    if resolve is None:
        raise RuntimeError(
            "Could not connect to DaVinci Resolve. Run this from Workspace -> Scripts inside Resolve."
        )
    return resolve


def _choose_file(*, title: str, initial_dir: Path, filetypes):
    try:
        from tkinter import Tk, filedialog
    except ImportError as exc:
        raise RuntimeError(
            "Tkinter is not available. Run this script with --csv."
        ) from exc
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askopenfilename(
            title=title,
            initialdir=str(initial_dir),
            filetypes=filetypes,
        )
    finally:
        root.destroy()
    return Path(selected).resolve() if selected else None


def _get_or_create_project(project_manager, project_name: str):
    project = project_manager.LoadProject(project_name)
    if project is not None:
        return project
    project = project_manager.CreateProject(project_name)
    if project is None:
        raise RuntimeError(f"Could not create or load project '{project_name}'.")
    return project


def _timeline_by_name(project, timeline_name: str):
    count = int(project.GetTimelineCount() or 0)
    for index in range(1, count + 1):
        timeline = project.GetTimelineByIndex(index)
        if timeline is not None and timeline.GetName() == timeline_name:
            return timeline
    return None


@dataclass(frozen=True)
class MatchClip:
    match_id: str
    round_label: str
    left_name: str
    right_name: str
    winner_name: str
    start_seconds: float
    end_seconds: float

    @property
    def clip_name(self) -> str:
        slug = f"{self.round_label}-{self.left_name}-vs-{self.right_name}-{self.winner_name}"
        cleaned = "".join(
            char.lower() if char.isalnum() else "-" for char in slug
        )
        while "--" in cleaned:
            cleaned = cleaned.replace("--", "-")
        cleaned = cleaned.strip("-")
        return f"{self.match_id}_{cleaned}"


def _load_match_clips(csv_path: Path) -> list[MatchClip]:
    clips: list[MatchClip] = []
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            start_seconds = float(row["start_seconds"])
            end_text = str(row.get("end_seconds", "")).strip()
            if not end_text:
                continue
            end_seconds = float(end_text)
            if end_seconds <= start_seconds:
                continue
            clips.append(
                MatchClip(
                    match_id=str(row.get("match_id", "")).strip(),
                    round_label=str(row.get("round_label", "")).strip(),
                    left_name=str(row.get("left_name", "")).strip(),
                    right_name=str(row.get("right_name", "")).strip(),
                    winner_name=str(row.get("winner_name", "")).strip() or "winner",
                    start_seconds=start_seconds,
                    end_seconds=end_seconds,
                )
            )
    if not clips:
        raise RuntimeError(f"No complete match rows found in '{csv_path}'.")
    return clips


def _timeline_fps(project) -> float:
    fps_value = project.GetSetting("timelineFrameRate") or project.GetSetting(
        "timelinePlaybackFrameRate"
    )
    try:
        return max(1.0, float(fps_value))
    except (TypeError, ValueError):
        return 60.0


def _seconds_to_frame(seconds: float, fps: float) -> int:
    return max(0, int(round(float(seconds) * float(fps))))


def _default_output_dir(csv_path: Path) -> Path:
    manifest_path = csv_path.with_suffix(".json")
    if manifest_path.is_file():
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            payload = {}
        render_root = str(payload.get("render_root") or "").strip()
        if render_root:
            candidate = Path(render_root)
            if candidate.is_absolute():
                return candidate
            return (csv_path.parent.parent.parent / candidate).resolve()
    run_name = csv_path.stem
    return csv_path.parent.parent / "renders" / run_name


def _configure_mp4_h264(project) -> None:
    formats = project.GetRenderFormats() or {}
    render_format = next(
        (
            str(format_name)
            for format_name, extension in formats.items()
            if str(format_name).lower() == "mp4"
            or str(extension).lower() == "mp4"
        ),
        None,
    )
    if render_format is None:
        raise RuntimeError("Resolve did not report an MP4 render format.")

    codecs = project.GetRenderCodecs(render_format) or {}
    render_codec = next(
        (
            str(codec_name)
            for description, codec_name in codecs.items()
            if str(codec_name).lower() == "h264"
            or "h.264" in str(description).lower()
            or "h264" in str(description).lower()
        ),
        None,
    )
    if render_codec is None:
        raise RuntimeError("Resolve did not report an H.264 codec for MP4.")

    if not project.SetCurrentRenderFormatAndCodec(render_format, render_codec):
        raise RuntimeError(
            f"Resolve refused render format/codec '{render_format}/{render_codec}'."
        )
    project.SetCurrentRenderMode(1)


def _queue_render_jobs(project, timeline, clips: list[MatchClip], output_dir: Path) -> int:
    fps = _timeline_fps(project)
    project.SetCurrentTimeline(timeline)
    timeline_start_frame = int(timeline.GetStartFrame() or 0)
    _configure_mp4_h264(project)
    queued = 0
    for clip in clips:
        start_frame = timeline_start_frame + _seconds_to_frame(
            clip.start_seconds, fps
        )
        end_frame = timeline_start_frame + _seconds_to_frame(
            clip.end_seconds, fps
        )
        if end_frame <= start_frame:
            continue
        mark_out = max(start_frame, end_frame - 1)
        timeline.SetMarkInOut(start_frame, mark_out, "all")
        settings = {
            "SelectAllFrames": False,
            "MarkIn": start_frame,
            "MarkOut": mark_out,
            "TargetDir": str(output_dir),
            "CustomName": clip.clip_name,
            "AudioCodec": "aac",
            "ExportVideo": True,
            "ExportAudio": True,
        }
        project.SetRenderSettings(settings)
        job_id = project.AddRenderJob()
        if job_id:
            queued += 1
    timeline.ClearMarkInOut("all")
    return queued


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Queue and render Ballistic match clips in DaVinci Resolve from a content CSV."
    )
    parser.add_argument("--csv", required=False, help="Path to the Ballistic content CSV.")
    parser.add_argument(
        "--project-name",
        default=None,
        help="Resolve project to create or reuse.",
    )
    parser.add_argument(
        "--timeline-name",
        default=None,
        help="Timeline name to render from. Defaults to the current timeline.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Defaults to the manifest render_root when available.",
    )
    parser.add_argument(
        "--queue-only",
        action="store_true",
        help="Queue render jobs but do not start rendering.",
    )
    args = parser.parse_args()

    csv_path = (
        Path(args.csv).expanduser().resolve()
        if args.csv
        else _choose_file(
            title="Select Ballistic content CSV",
            initial_dir=DEFAULT_CONTENT_DIR,
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
    )
    if csv_path is None:
        print("No CSV selected.")
        return 0
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    clips = _load_match_clips(csv_path)

    resolve = _get_resolve()
    project_manager = resolve.GetProjectManager()
    if project_manager is None:
        raise RuntimeError("Could not get Resolve project manager.")
    project = project_manager.GetCurrentProject()
    if args.project_name:
        if project is None or project.GetName() != args.project_name:
            project = _get_or_create_project(project_manager, args.project_name)
    elif project is None:
        project = _get_or_create_project(project_manager, DEFAULT_PROJECT_NAME)

    if args.timeline_name:
        timeline = _timeline_by_name(project, args.timeline_name)
        if timeline is None:
            raise RuntimeError(
                f"Timeline '{args.timeline_name}' was not found in project '{args.project_name}'."
            )
    else:
        timeline = project.GetCurrentTimeline()
        if timeline is None:
            raise RuntimeError(
                "No current timeline is active. Run ballistic_load_video_to_timeline.py first or pass --timeline-name."
            )

    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else _default_output_dir(csv_path)
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    queued = _queue_render_jobs(project, timeline, clips, output_dir)
    if queued <= 0:
        raise RuntimeError("No render jobs were queued.")

    print(f"Queued {queued} render jobs into '{output_dir}'.")
    if args.queue_only:
        return 0

    if not project.StartRendering():
        raise RuntimeError("Resolve refused to start rendering.")
    print("Rendering started...")
    while project.IsRenderingInProgress():
        time.sleep(1.0)
    print("Rendering finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
