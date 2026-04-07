from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mini_arcade.common.settings import Settings, SettingsArgs


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def test_settings_accepts_settings_args_for_direct_instantiation(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "engine_config:\n" "  fps: 75\n" "scene:\n" "  initial_scene: play\n",
        encoding="utf-8",
    )

    settings = Settings(
        SettingsArgs(
            config_path=config_path,
            required=True,
            force_reload=True,
        )
    )

    assert settings.config_path == config_path.resolve()
    assert settings.engine_config_defaults()["fps"] == 75
    assert settings.scene_defaults()["initial_scene"] == "play"


def test_settings_accepts_legacy_keyword_arguments(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "engine_config:\n" "  fps: 90\n",
        encoding="utf-8",
    )

    settings = Settings(
        config_path=config_path,
        required=True,
        force_reload=True,
    )

    assert settings.config_path == config_path.resolve()
    assert settings.engine_config_defaults()["fps"] == 90


def test_settings_for_game_prefers_local_game_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    game_dir = tmp_path / "games" / "orbit-garden"
    (game_dir / "settings").mkdir(parents=True)
    (game_dir / "pyproject.toml").write_text(
        "[tool.mini-arcade.game]\n"
        'id = "orbit-garden"\n'
        'entrypoint = "manage.py"\n',
        encoding="utf-8",
    )
    (game_dir / "settings" / "settings.yml").write_text(
        "engine_config:\n  fps: 72\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(game_dir)

    settings = Settings.for_game(
        "orbit-garden",
        required=True,
        force_reload=True,
    )

    assert (
        settings.config_path
        == (game_dir / "settings" / "settings.yml").resolve()
    )
    assert settings.project_root() == game_dir.resolve()


def test_gameplay_manifests_merge_and_inline_overrides(tmp_path: Path) -> None:
    project_root = tmp_path / "orbit"
    settings_path = project_root / "settings" / "settings.yml"
    _write_text(
        settings_path,
        """
        project:
          root: ${settings_dir}/..
          assets_root: ${project_root}/assets
        gameplay:
          manifests:
            - ${project_root}/data/base.yml
            - ${project_root}/data/override.yml
          controls:
            play:
              bindings:
                pause:
                  type: digital
                  keys: [ESCAPE]
          data:
            title: Inline Override
        """,
    )
    _write_text(
        project_root / "data" / "base.yml",
        """
        difficulty:
          level: easy
        controls:
          play:
            bindings:
              restart:
                type: digital
                keys: [SPACE]
        scenes:
          play:
            presentation:
              ready_message: READY
        data:
          title: Base Title
          presentation:
            hud:
              score_font: ${assets_root}/fonts/score.ttf
        """,
    )
    _write_text(
        project_root / "data" / "override.yml",
        """
        difficulty:
          level: hard
        data:
          title: Manifest Override
        """,
    )

    settings = Settings(
        config_path=settings_path,
        required=True,
        force_reload=True,
    )

    assert settings.get("gameplay.difficulty.level") == "hard"
    assert (
        settings.get("gameplay.controls.play.bindings.restart.type")
        == "digital"
    )
    assert settings.get("gameplay.data.title") == "Inline Override"
    assert (
        settings.section("gameplay")["scenes"]["play"]["presentation"][
            "ready_message"
        ]
        == "READY"
    )

    gameplay_defaults = settings.gameplay_defaults()

    assert gameplay_defaults["difficulty"]["level"] == "hard"
    assert gameplay_defaults["data"]["presentation"]["hud"][
        "score_font"
    ] == str((project_root / "assets" / "fonts" / "score.ttf").resolve())
    assert gameplay_defaults["data"]["title"] == "Inline Override"
    assert settings.as_dict()["gameplay"]["data"]["title"] == "Inline Override"


def test_gameplay_manifests_require_existing_files(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings" / "settings.yml"
    _write_text(
        settings_path,
        """
        project:
          root: ${settings_dir}/..
        gameplay:
          manifests:
            - ${project_root}/data/missing.yml
        """,
    )

    with pytest.raises(FileNotFoundError):
        Settings(
            config_path=settings_path,
            required=True,
            force_reload=True,
        )


def test_gameplay_manifest_root_must_be_mapping(tmp_path: Path) -> None:
    project_root = tmp_path / "orbit"
    settings_path = project_root / "settings" / "settings.yml"
    _write_text(
        settings_path,
        """
        project:
          root: ${settings_dir}/..
        gameplay:
          manifests:
            - ${project_root}/data/gameplay.yml
        """,
    )
    _write_text(project_root / "data" / "gameplay.yml", "- nope\n")

    with pytest.raises(ValueError, match="Gameplay manifest"):
        Settings(
            config_path=settings_path,
            required=True,
            force_reload=True,
        )
