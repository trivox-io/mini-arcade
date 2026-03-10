from __future__ import annotations

from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mini_arcade_core.engine.gameplay_settings import GamePlaySettings
from mini_arcade_core.scenes.entity_blueprints import resolve_transform_layout


def test_resolve_transform_layout_supports_right_and_center_anchors():
    resolved = resolve_transform_layout(
        {
            "size": {"width": 20.0, "height": 100.0},
            "position": {
                "x": {"anchor": "right", "offset": 20.0},
                "y": {"anchor": "center"},
            },
        },
        viewport=(800.0, 600.0),
    )

    assert resolved["center"]["x"] == 760.0
    assert resolved["center"]["y"] == 250.0


def test_gameplay_settings_preserve_scene_specific_data():
    settings = GamePlaySettings.from_dict(
        {
            "scenes": {
                "pong": {
                    "escape": {"command": "change_scene", "scene_id": "menu"},
                    "entities": {
                        "right_paddle": {
                            "transform": {
                                "position": {
                                    "x": {"anchor": "right", "offset": 20.0}
                                }
                            }
                        }
                    },
                }
            }
        }
    )

    scene_cfg = settings.scene_settings("pong")

    assert scene_cfg is not None
    assert scene_cfg.escape is not None
    assert scene_cfg.escape.scene_id == "menu"
    assert scene_cfg.get("entities", {})["right_paddle"]["transform"]["position"][
        "x"
    ] == {"anchor": "right", "offset": 20.0}
