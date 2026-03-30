"""
Default capture event handlers.
"""

from __future__ import annotations

from mini_arcade_core.bus import event_bus
from mini_arcade_core.runtime.capture import events
from mini_arcade_core.utils import logger

_REGISTERED = False


# Justification: This is a momentary global for idempotent registration of event handlers.
# pylint: disable=global-statement
def register_default_capture_event_handlers() -> None:
    """
    Register logging handlers for capture events once per process.
    """
    global _REGISTERED
    if _REGISTERED:
        return

    event_bus.on(
        events.SCREENSHOT_DONE,
        lambda path, **_: logger.info(f"[capture] screenshot saved: {path}"),
    )
    event_bus.on(
        events.SCREENSHOT_FAILED,
        lambda error, **_: logger.warning(
            f"[capture] screenshot failed: {error}"
        ),
    )
    event_bus.on(
        events.VIDEO_STARTED,
        lambda path, **_: logger.info(
            f"[capture] video recording started: {path}"
        ),
    )
    event_bus.on(
        events.VIDEO_STATE_CHANGED,
        lambda state, message, **_: logger.info(
            f"[capture] video state -> {state}: {message}"
        ),
    )
    event_bus.on(
        events.VIDEO_FINALIZING,
        lambda path, **_: logger.info(f"[capture] video finalizing: {path}"),
    )
    event_bus.on(
        events.VIDEO_STOPPED,
        lambda path, **_: logger.info(
            f"[capture] video recording stopped: {path}"
        ),
    )
    event_bus.on(
        events.VIDEO_ENCODE_STARTED,
        lambda path, **_: logger.info(
            f"[capture] video encoding started: {path}"
        ),
    )
    event_bus.on(
        events.VIDEO_ENCODE_DONE,
        lambda path, **_: logger.info(f"[capture] video encoded: {path}"),
    )
    event_bus.on(
        events.VIDEO_ENCODE_FAILED,
        lambda error, **_: logger.warning(
            f"[capture] video encode failed: {error}"
        ),
    )
    event_bus.on(
        events.VIDEO_QUIT_BLOCKED,
        lambda message, **_: logger.info(
            f"[capture] quit deferred: {message}"
        ),
    )
    event_bus.on(
        events.REPLAY_RECORD_STARTED,
        lambda path, **_: logger.info(
            f"[capture] replay recording started: {path}"
        ),
    )
    event_bus.on(
        events.REPLAY_RECORD_STOPPED,
        lambda path, **_: logger.info(
            f"[capture] replay recording stopped: {path}"
        ),
    )
    event_bus.on(
        events.REPLAY_PLAY_STARTED,
        lambda path, **_: logger.info(
            f"[capture] replay playback started: {path}"
        ),
    )
    event_bus.on(
        events.REPLAY_PLAY_STOPPED,
        lambda **_: logger.info("[capture] replay playback stopped"),
    )
    event_bus.on(
        events.REPLAY_PLAY_FINISHED,
        lambda **_: logger.info("[capture] replay playback finished"),
    )

    _REGISTERED = True
