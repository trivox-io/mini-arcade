from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mini_arcade.modules.settings import Settings, SettingsArgs


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
