"""
Capture event names emitted through the global bus.
"""

from __future__ import annotations

SCREENSHOT_QUEUED = "capture.screenshot.queued"
SCREENSHOT_DONE = "capture.screenshot.done"
SCREENSHOT_FAILED = "capture.screenshot.failed"

VIDEO_STARTED = "capture.video.started"
VIDEO_STATE_CHANGED = "capture.video.state.changed"
VIDEO_FINALIZING = "capture.video.finalizing"
VIDEO_STOPPED = "capture.video.stopped"
VIDEO_ENCODE_QUEUED = "capture.video.encode.queued"
VIDEO_ENCODE_STARTED = "capture.video.encode.started"
VIDEO_ENCODE_PROGRESS = "capture.video.encode.progress"
VIDEO_ENCODE_DONE = "capture.video.encode.done"
VIDEO_ENCODE_FAILED = "capture.video.encode.failed"
VIDEO_QUIT_BLOCKED = "capture.video.quit.blocked"

REPLAY_RECORD_STARTED = "capture.replay.record.started"
REPLAY_RECORD_STOPPED = "capture.replay.record.stopped"
REPLAY_PLAY_STARTED = "capture.replay.play.started"
REPLAY_PLAY_STOPPED = "capture.replay.play.stopped"
REPLAY_PLAY_FINISHED = "capture.replay.play.finished"
