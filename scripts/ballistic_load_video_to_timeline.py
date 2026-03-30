from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

DEFAULT_PROJECT_NAME = "Ballistic Content"
DEFAULT_RECORDINGS_DIR = Path(
    "C:/Users/USUARIO/work/mini-arcade/originals/ball-vs-ball-cup/recordings"
)
DEFAULT_TIMELINE_WIDTH = 1080
DEFAULT_TIMELINE_HEIGHT = 1920


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
            "Tkinter is not available. Run this script with --video."
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


def _import_video(resolve, project, video_path: Path):
    media_pool = project.GetMediaPool()
    root_folder = media_pool.GetRootFolder()
    media_pool.SetCurrentFolder(root_folder)
    media_storage = resolve.GetMediaStorage()
    clips = media_storage.AddItemListToMediaPool([str(video_path)])
    if not clips:
        raise RuntimeError(f"Could not import video '{video_path}'.")
    return clips


def _configure_vertical_timeline(project) -> None:
    project.SetSetting("timelineResolutionWidth", str(DEFAULT_TIMELINE_WIDTH))
    project.SetSetting("timelineResolutionHeight", str(DEFAULT_TIMELINE_HEIGHT))
    project.SetSetting("timelineOutputResolutionWidth", str(DEFAULT_TIMELINE_WIDTH))
    project.SetSetting("timelineOutputResolutionHeight", str(DEFAULT_TIMELINE_HEIGHT))


def _configure_vertical_timeline_instance(timeline) -> None:
    if timeline is None:
        return
    timeline.SetSetting("timelineResolutionWidth", str(DEFAULT_TIMELINE_WIDTH))
    timeline.SetSetting("timelineResolutionHeight", str(DEFAULT_TIMELINE_HEIGHT))
    timeline.SetSetting(
        "timelineOutputResolutionWidth", str(DEFAULT_TIMELINE_WIDTH)
    )
    timeline.SetSetting(
        "timelineOutputResolutionHeight", str(DEFAULT_TIMELINE_HEIGHT)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load a Ballistic recording into a new DaVinci Resolve timeline."
    )
    parser.add_argument("--video", required=False, help="Path to the source video.")
    parser.add_argument(
        "--project-name",
        default=None,
        help="Resolve project to create or reuse.",
    )
    parser.add_argument(
        "--timeline-name",
        default=None,
        help="Timeline name. Defaults to the video filename stem.",
    )
    args = parser.parse_args()

    video_path = (
        Path(args.video).expanduser().resolve()
        if args.video
        else _choose_file(
            title="Select Ballistic recording",
            initial_dir=DEFAULT_RECORDINGS_DIR,
            filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")),
        )
    )
    if video_path is None:
        print("No video selected.")
        return 0
    if not video_path.is_file():
        raise FileNotFoundError(f"Video not found: {video_path}")

    timeline_name = args.timeline_name or video_path.stem
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

    _configure_vertical_timeline(project)

    existing = _timeline_by_name(project, timeline_name)
    if existing is not None:
        _configure_vertical_timeline_instance(existing)
        project.SetCurrentTimeline(existing)
        print(f"Timeline already exists and is now active: {timeline_name}")
        return 0

    clips = _import_video(resolve, project, video_path)
    media_pool = project.GetMediaPool()
    timeline = media_pool.CreateTimelineFromClips(timeline_name, clips)
    if timeline is None:
        raise RuntimeError(f"Could not create timeline '{timeline_name}'.")
    _configure_vertical_timeline_instance(timeline)
    project.SetCurrentTimeline(timeline)
    print(f"Created timeline '{timeline_name}' from '{video_path.name}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
