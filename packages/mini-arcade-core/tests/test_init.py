from __future__ import annotations

import pytest

import mini_arcade_core


def test_run_game_reraises_discovery_failures(monkeypatch) -> None:
    logged: list[str] = []
    debug_messages: list[str] = []

    class _BrokenRegistry:
        def __init__(self, _factories) -> None:
            self._factories = _factories

        def discover(self, *packages):
            del packages
            raise RuntimeError("discover boom")

    monkeypatch.setattr(mini_arcade_core, "SceneRegistry", _BrokenRegistry)
    monkeypatch.setattr(mini_arcade_core.logger, "exception", logged.append)
    monkeypatch.setattr(
        mini_arcade_core.logger, "debug", debug_messages.append
    )

    with pytest.raises(RuntimeError, match="discover boom"):
        mini_arcade_core.run_game(
            backend=object(),
            scene_config={"discover_packages": ["tests.fake_scene_pkg"]},
        )

    assert logged == ["Unhandled exception in game loop: discover boom"]
    assert any("discover boom" in msg for msg in debug_messages)


def test_run_game_reraises_engine_failures(monkeypatch) -> None:
    logged: list[str] = []
    debug_messages: list[str] = []

    class _Registry:
        listed_scene_ids = ["main"]

    class _RegistryFactory:
        def __init__(self, _factories) -> None:
            self._factories = _factories

        def discover(self, *packages):
            del packages
            return _Registry()

    class _BrokenEngine:
        def __init__(self, config, dependencies) -> None:
            del config, dependencies

        def run(self, initial_scene=None) -> None:
            del initial_scene
            raise RuntimeError("tick boom")

    monkeypatch.setattr(mini_arcade_core, "SceneRegistry", _RegistryFactory)
    monkeypatch.setattr(mini_arcade_core, "Engine", _BrokenEngine)
    monkeypatch.setattr(mini_arcade_core.logger, "exception", logged.append)
    monkeypatch.setattr(
        mini_arcade_core.logger, "debug", debug_messages.append
    )

    with pytest.raises(RuntimeError, match="tick boom"):
        mini_arcade_core.run_game(
            backend=object(),
            scene_config={"initial_scene": "main"},
        )

    assert logged == ["Unhandled exception in game loop: tick boom"]
    assert any("tick boom" in msg for msg in debug_messages)
