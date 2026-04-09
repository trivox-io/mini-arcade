from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import sys


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
            if "DaVinciResolveScript" in sys.modules:
                del sys.modules["DaVinciResolveScript"]
            return importlib.import_module("DaVinciResolveScript")
        except ImportError:
            continue
    raise RuntimeError("Could not import DaVinciResolveScript from fuscript.")


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
        raise RuntimeError("Could not connect to DaVinci Resolve from fuscript.")
    return resolve


def _slugify(text: str) -> str:
    cleaned = "".join(
        char.lower() if char.isalnum() else "-" for char in str(text).strip()
    )
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "ballistic"


def _clip_name(match: dict[str, object]) -> str:
    winner_name = str(match.get("winner_name") or "winner").strip() or "winner"
    label = (
        f"{match.get('round_label') or ''}-"
        f"{match.get('left_name') or ''}-vs-"
        f"{match.get('right_name') or ''}-{winner_name}"
    )
    slug = _slugify(label)
    match_id = str(match.get("match_id") or "match").strip() or "match"
    return f"{match_id}_{slug}" if slug else match_id


def _project_root_for_manifest(manifest_path: Path) -> Path:
    return manifest_path.resolve().parents[2]


def _resolve_path_from_manifest(
    manifest_path: Path,
    raw_path: str | None,
) -> Path | None:
    text = str(raw_path or "").strip()
    if not text:
        return None
    candidate = Path(text)
    if candidate.is_absolute():
        return candidate
    return (_project_root_for_manifest(manifest_path) / candidate).resolve()


def _load_manifest(manifest_path: Path) -> dict[str, object]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _build_plan(manifest_path: Path, project_name: str | None) -> dict[str, object]:
    payload = _load_manifest(manifest_path)
    capture_sessions = payload.get("capture_sessions") or []
    matches = payload.get("matches") or []
    session_video_paths: dict[str, Path] = {}
    capture_videos: list[Path] = []
    for raw_session in capture_sessions:
        if not isinstance(raw_session, dict):
            continue
        session_id = str(raw_session.get("session_id") or "").strip()
        video_path = _resolve_path_from_manifest(
            manifest_path,
            str(raw_session.get("video_path") or "").strip() or None,
        )
        if not session_id or video_path is None or not video_path.is_file():
            continue
        session_video_paths[session_id] = video_path
        capture_videos.append(video_path)

    plan_matches: list[dict[str, object]] = []
    for raw_match in matches:
        if not isinstance(raw_match, dict):
            continue
        segments: list[dict[str, object]] = []
        for raw_segment in raw_match.get("source_segments") or []:
            if not isinstance(raw_segment, dict):
                continue
            session_id = str(raw_segment.get("session_id") or "").strip()
            video_path = session_video_paths.get(session_id)
            end_seconds = raw_segment.get("end_seconds")
            if video_path is None or end_seconds is None:
                continue
            start_seconds = float(raw_segment.get("start_seconds") or 0.0)
            end_seconds_value = float(end_seconds)
            if end_seconds_value <= start_seconds:
                continue
            segments.append(
                {
                    "session_id": session_id,
                    "video_path": video_path,
                    "start_seconds": start_seconds,
                    "end_seconds": end_seconds_value,
                }
            )
        if not segments:
            media = raw_match.get("media") or {}
            video_path = (
                _resolve_path_from_manifest(
                    manifest_path,
                    str(media.get("video_path") or "").strip() or None,
                )
                if isinstance(media, dict)
                else None
            )
            duration_seconds = float(raw_match.get("duration_seconds") or 0.0)
            if video_path is not None and video_path.is_file() and duration_seconds > 0.0:
                capture_videos.append(video_path)
                segments.append(
                    {
                        "session_id": str(raw_match.get("match_id") or "").strip() or "match",
                        "video_path": video_path,
                        "start_seconds": 0.0,
                        "end_seconds": duration_seconds,
                    }
                )
        if not segments:
            continue
        plan_matches.append(
            {
                "match_id": str(raw_match.get("match_id") or "").strip(),
                "timeline_name": _clip_name(raw_match),
                "segments": segments,
            }
        )
    resolved_project_name = str(project_name or "").strip() or _slugify(
        str(payload.get("cup_title") or payload.get("run_id") or "ballistic")
    )
    return {
        "manifest_path": manifest_path,
        "csv_path": manifest_path.with_suffix(".csv"),
        "run_id": str(payload.get("run_id") or manifest_path.stem),
        "project_name": resolved_project_name,
        "render_root": str(
            _resolve_path_from_manifest(
                manifest_path,
                str(payload.get("render_root") or "").strip() or None,
            )
            or ""
        ).strip()
        or None,
        "source_timeline_name": f"{str(payload.get('run_id') or manifest_path.stem)}__source",
        "capture_videos": list(dict.fromkeys(capture_videos)),
        "matches": plan_matches,
    }


def _project_exists(project_manager, project_name: str) -> bool:
    list_projects = getattr(project_manager, "GetProjectListInCurrentFolder", None)
    if callable(list_projects):
        try:
            projects = list_projects() or ()
        except Exception:
            projects = ()
        if isinstance(projects, dict):
            values = projects.values()
        else:
            values = projects
        return any(str(value or "") == project_name for value in values)
    try:
        return project_manager.LoadProject(project_name) is not None
    except Exception:
        return False


def _unique_project_name(project_manager, base_name: str) -> str:
    normalized = str(base_name or "").strip() or "ballistic"
    if not _project_exists(project_manager, normalized):
        return normalized
    suffix = 2
    while True:
        candidate = f"{normalized}__{suffix}"
        if not _project_exists(project_manager, candidate):
            return candidate
        suffix += 1


def _get_or_create_project(project_manager, project_name: str):
    project = project_manager.LoadProject(project_name)
    if project is not None:
        return project
    project = project_manager.CreateProject(project_name)
    if project is not None:
        return project
    current_project = getattr(project_manager, "GetCurrentProject", lambda: None)()
    current_name = (
        getattr(current_project, "GetName", lambda: "")()
        if current_project is not None
        else ""
    )
    if current_project is not None and current_name == project_name:
        return current_project
    raise RuntimeError(f"Could not create or load project '{project_name}'.")


def _timeline_by_name(project, timeline_name: str):
    count = int(project.GetTimelineCount() or 0)
    for index in range(1, count + 1):
        timeline = project.GetTimelineByIndex(index)
        if timeline is not None and timeline.GetName() == timeline_name:
            return timeline
    return None


def _delete_timeline_if_present(project, media_pool, timeline_name: str) -> None:
    timeline = _timeline_by_name(project, timeline_name)
    if timeline is None:
        return
    delete_timelines = getattr(media_pool, "DeleteTimelines", None)
    if callable(delete_timelines):
        try:
            delete_timelines([timeline])
            return
        except Exception:
            pass


def _get_or_create_subfolder(media_pool, parent_folder, name: str):
    subfolders = getattr(parent_folder, "GetSubFolderList", lambda: [])() or []
    for folder in subfolders:
        if folder is not None and getattr(folder, "GetName", lambda: "")() == name:
            return folder
    add_subfolder = getattr(media_pool, "AddSubFolder", None)
    if callable(add_subfolder):
        created = add_subfolder(parent_folder, name)
        if created is not None:
            return created
    return parent_folder


def _import_videos(resolve, project, plan: dict[str, object]):
    media_pool = project.GetMediaPool()
    if media_pool is None:
        raise RuntimeError("Resolve project did not provide a media pool.")
    root_folder = media_pool.GetRootFolder()
    run_folder = _get_or_create_subfolder(
        media_pool,
        root_folder,
        f"run-{plan['run_id']}",
    )
    media_pool.SetCurrentFolder(run_folder)
    media_storage = resolve.GetMediaStorage()
    capture_videos = [str(path) for path in plan["capture_videos"]]
    imported = media_storage.AddItemListToMediaPool(capture_videos)
    items_by_path: dict[Path, object] = {}
    if imported:
        for item, path in zip(imported, plan["capture_videos"]):
            items_by_path[path] = item
    media_pool.SetCurrentFolder(root_folder)
    return media_pool, items_by_path


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


def _create_source_timeline(project, media_pool, items_by_path, plan) -> None:
    _delete_timeline_if_present(project, media_pool, str(plan["source_timeline_name"]))
    clips = [
        items_by_path[path]
        for path in plan["capture_videos"]
        if path in items_by_path
    ]
    if not clips:
        return
    timeline = media_pool.CreateTimelineFromClips(
        str(plan["source_timeline_name"]),
        clips,
    )
    if timeline is not None:
        project.SetCurrentTimeline(timeline)


def _create_match_timelines(project, media_pool, items_by_path, plan) -> None:
    fps = _timeline_fps(project)
    for match_plan in plan["matches"]:
        timeline_name = str(match_plan["timeline_name"])
        _delete_timeline_if_present(project, media_pool, timeline_name)
        create_empty_timeline = getattr(media_pool, "CreateEmptyTimeline", None)
        if not callable(create_empty_timeline):
            continue
        timeline = create_empty_timeline(timeline_name)
        if timeline is None:
            continue
        project.SetCurrentTimeline(timeline)
        append_to_timeline = getattr(media_pool, "AppendToTimeline", None)
        if not callable(append_to_timeline):
            continue
        clip_infos: list[dict[str, object]] = []
        record_frame = 0
        for segment in match_plan["segments"]:
            video_path = segment["video_path"]
            item = items_by_path.get(video_path)
            if item is None:
                continue
            start_frame = _seconds_to_frame(segment["start_seconds"], fps)
            end_frame = _seconds_to_frame(segment["end_seconds"], fps)
            if end_frame <= start_frame:
                continue
            clip_infos.append(
                {
                    "mediaPoolItem": item,
                    "startFrame": start_frame,
                    "endFrame": max(start_frame, end_frame - 1),
                    "recordFrame": record_frame,
                }
            )
            record_frame += max(1, end_frame - start_frame)
        if clip_infos:
            append_to_timeline(clip_infos)


def _open_resolve_edit_page(resolve) -> None:
    open_page = getattr(resolve, "OpenPage", None)
    if not callable(open_page):
        return
    for page_name in ("edit", "media"):
        try:
            if open_page(page_name):
                return
        except Exception:
            continue


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a Ballistic manifest inside DaVinci Resolve."
    )
    parser.add_argument("--manifest-path", required=True)
    parser.add_argument("--project-name", required=False, default=None)
    parser.add_argument("--ensure-unique-project-name", action="store_true")
    args = parser.parse_args()

    manifest_path = Path(args.manifest_path).expanduser().resolve()
    plan = _build_plan(manifest_path, args.project_name)
    resolve = _get_resolve()
    project_manager = resolve.GetProjectManager()
    if project_manager is None:
        raise RuntimeError("Could not get Resolve project manager.")
    resolved_project_name = (
        _unique_project_name(project_manager, str(plan["project_name"]))
        if args.ensure_unique_project_name
        else str(plan["project_name"])
    )
    project = _get_or_create_project(project_manager, resolved_project_name)
    _open_resolve_edit_page(resolve)
    media_pool, items_by_path = _import_videos(resolve, project, plan)
    _create_source_timeline(project, media_pool, items_by_path, plan)
    _create_match_timelines(project, media_pool, items_by_path, plan)
    print(
        json.dumps(
            {
                "manifest_path": str(manifest_path),
                "csv_path": str(manifest_path.with_suffix(".csv")),
                "run_id": str(plan["run_id"]),
                "project_name": resolved_project_name,
                "render_root": plan["render_root"],
                "capture_videos": [str(path) for path in plan["capture_videos"]],
                "match_timelines": [
                    str(match["timeline_name"]) for match in plan["matches"]
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
