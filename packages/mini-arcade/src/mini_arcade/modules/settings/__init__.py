"""
Settings module for mini-arcade.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml


class Settings:
    """
    Settings reader with optional profile scoping.

    Supported sources:
    - explicit config_path
    - MINI_ARCADE_CONFIG_PATH env var
    - monorepo game-local settings under `games/<game_id>/settings/`
    - monorepo example settings under `examples/settings/`
    - repo-level defaults under `settings/settings.yml|yaml`

    Profile convention under monorepo root:
    - games: `games/<game_id>/settings/settings.yml|yaml`
    - examples: `examples/settings/<example_id>.yml|yaml`
    - shared examples: `examples/settings/settings.yml|yaml`
    - default: `settings/settings.yml|yaml`
    """

    _instances: dict[tuple[str | None, str | None, str | None], "Settings"] = (
        {}
    )
    _settings: dict[str, Any]
    _config_path: Path | None
    _scope: str | None
    _name: str | None
    _TOKEN_RE = re.compile(r"\$\{([A-Za-z0-9_.-]+)\}")

    def __new__(
        cls,
        config_path: str | Path | None = None,
        *,
        scope: str | None = None,
        name: str | None = None,
        required: bool = True,
        force_reload: bool = False,
    ):
        key = (
            str(config_path) if config_path is not None else None,
            scope,
            name,
        )

        if force_reload or key not in cls._instances:
            inst = super().__new__(cls)
            inst._settings = {}
            inst._config_path = None
            inst._scope = scope
            inst._name = name
            inst._load_settings(
                config_path=config_path,
                scope=scope,
                name=name,
                required=required,
            )
            cls._instances[key] = inst

        return cls._instances[key]

    @staticmethod
    def _is_repo_root(path: Path) -> bool:
        return (
            (path / "pyproject.toml").exists()
            and (path / "packages").exists()
            and (path / "examples").exists()
        )

    @classmethod
    def _find_repo_root(cls) -> Path | None:
        starts = [Path.cwd().resolve(), Path(__file__).resolve()]
        for start in starts:
            current = start if start.is_dir() else start.parent
            for candidate in (current, *current.parents):
                if cls._is_repo_root(candidate):
                    return candidate
        return None

    @staticmethod
    def _name_path(name: str | None) -> Path:
        if not name:
            return Path("shared")
        clean = str(name).strip("/\\")
        if not clean:
            return Path("shared")
        return Path(*clean.replace("\\", "/").split("/"))

    @classmethod
    def _profile_candidates(
        cls,
        *,
        repo_root: Path,
        scope: str | None,
        name: str | None,
    ) -> list[Path]:
        if scope == "game":
            if not name:
                return []
            base = (
                repo_root
                / "games"
                / cls._name_path(name)
                / "settings"
                / "settings"
            )
            return [base.with_suffix(".yml"), base.with_suffix(".yaml")]

        if scope == "example":
            settings_root = repo_root / "examples" / "settings"
            if name is None:
                base = settings_root / "settings"
            else:
                base = settings_root / cls._name_path(name)
            return [base.with_suffix(".yml"), base.with_suffix(".yaml")]

        # default repo-level settings file
        base = repo_root / "settings" / "settings"
        return [
            base.with_suffix(".yml"),
            base.with_suffix(".yaml"),
        ]

    @classmethod
    def _default_candidates(
        cls,
        *,
        scope: str | None = None,
        name: str | None = None,
    ) -> list[Path]:
        candidates: list[Path] = []

        env_path = os.getenv("MINI_ARCADE_CONFIG_PATH")
        if env_path:
            candidates.append(Path(env_path).expanduser())

        repo_root = cls._find_repo_root()
        if repo_root is not None:
            # examples can load shared defaults and overlay one specific profile.
            if scope == "example" and name is not None:
                candidates.extend(
                    cls._profile_candidates(
                        repo_root=repo_root,
                        scope="example",
                        name=None,
                    )
                )
                candidates.extend(
                    cls._profile_candidates(
                        repo_root=repo_root,
                        scope="example",
                        name=name,
                    )
                )
            elif scope == "game" and name is not None:
                candidates.extend(
                    cls._profile_candidates(
                        repo_root=repo_root,
                        scope="game",
                        name=name,
                    )
                )
            else:
                candidates.extend(
                    cls._profile_candidates(
                        repo_root=repo_root,
                        scope=scope,
                        name=None,
                    )
                )
        return candidates

    @staticmethod
    def _first_existing(candidates: list[Path]) -> Path | None:
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return None

    def _resolve_config_paths(
        self,
        config_path: str | Path | None = None,
        *,
        scope: str | None = None,
        name: str | None = None,
    ) -> list[Path]:
        if config_path is not None:
            resolved = Path(config_path).expanduser()
            if not resolved.is_absolute():
                resolved = (Path.cwd() / resolved).resolve()
            return [resolved]

        env_path = os.getenv("MINI_ARCADE_CONFIG_PATH")
        if env_path:
            return [Path(env_path).expanduser().resolve()]

        repo_root = self._find_repo_root()
        if repo_root is None:
            return []

        if scope == "example":
            shared = self._first_existing(
                self._profile_candidates(
                    repo_root=repo_root,
                    scope="example",
                    name=None,
                )
            )
            if name is None:
                return [shared] if shared is not None else []

            specific = self._first_existing(
                self._profile_candidates(
                    repo_root=repo_root,
                    scope="example",
                    name=name,
                )
            )
            paths: list[Path] = []
            if shared is not None:
                paths.append(shared)
            if specific is not None:
                paths.append(specific)
            return paths

        target = self._first_existing(
            self._profile_candidates(
                repo_root=repo_root,
                scope=scope,
                name=name,
            )
        )
        return [target] if target is not None else []

    def _load_settings(
        self,
        *,
        config_path: str | Path | None = None,
        scope: str | None = None,
        name: str | None = None,
        required: bool = True,
    ) -> None:
        resolved_paths = self._resolve_config_paths(
            config_path,
            scope=scope,
            name=name,
        )
        if not resolved_paths:
            searched = "\n".join(
                f"- {p}"
                for p in self._default_candidates(scope=scope, name=name)
            )
            if required:
                raise FileNotFoundError(
                    "No settings file found. Searched:\n" f"{searched}"
                )
            self._settings = {}
            self._config_path = None
            return

        merged: dict[str, Any] = {}
        for resolved in resolved_paths:
            if not resolved.exists():
                if required:
                    raise FileNotFoundError(
                        f"Config file not found at {resolved}"
                    )
                self._settings = {}
                self._config_path = None
                return

            with open(resolved, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
                if not isinstance(data, dict):
                    raise ValueError(
                        f"Config at {resolved} must be a mapping/dict at root."
                    )
                merged = self._deep_merge_dicts(merged, data)

        self._settings = merged
        self._config_path = resolved_paths[-1]

    @classmethod
    def for_game(
        cls,
        game_id: str,
        *,
        required: bool = False,
        force_reload: bool = False,
    ) -> "Settings":
        """
        Load settings profile for one game.
        """
        return cls(
            scope="game",
            name=game_id,
            required=required,
            force_reload=force_reload,
        )

    @classmethod
    def for_example(
        cls,
        example_id: str | None = None,
        *,
        required: bool = False,
        force_reload: bool = False,
    ) -> "Settings":
        """
        Load settings profile for one example.

        If example_id is None, loads shared example settings profile.
        """
        return cls(
            scope="example",
            name=example_id,
            required=required,
            force_reload=force_reload,
        )

    @property
    def config_path(self) -> Path | None:
        """
        Path to currently loaded settings file.
        """
        return self._config_path

    def get(self, key_: str, default: Any = None) -> Any:
        """
        Get nested key using dot notation.
        """
        data: Any = self._settings
        for part in key_.split("."):
            if not isinstance(data, dict):
                return default
            data = data.get(part, default)
            if data is default:
                return default
        return data

    def section(self, key_: str) -> dict[str, Any]:
        """
        Return one section as dict.
        """
        data = self.get(key_, {})
        return data if isinstance(data, dict) else {}

    def project_root(self) -> Path:
        """
        Resolve project root for this settings profile.

        Priority:
        1) project.root / paths.project_root key in yaml
        2) inferred from scope/name:
           - game -> <repo>/games/<game_id>
           - example -> <repo>/examples/catalog/<example_id>
        3) repo root
        4) cwd
        """
        configured = self.get("project.root") or self.get("paths.project_root")
        if configured:
            raw = str(configured).strip()
            expanded = self._expand_tokens(
                raw, tokens=self._base_token_values()
            )
            p = Path(expanded)
            if p.is_absolute():
                return p.resolve()
            repo_root = self._find_repo_root()
            if repo_root is not None:
                return (repo_root / p).resolve()
            return (Path.cwd() / p).resolve()

        return self._inferred_project_root()

    def assets_root(self) -> Path:
        """
        Resolve assets root for this settings profile.
        """
        configured = self.get("project.assets_root") or self.get(
            "paths.assets_root"
        )
        if configured:
            raw = str(configured).strip()
            expanded = self._expand_tokens(
                raw,
                tokens=self._project_token_values(),
            )
            p = Path(expanded)
            if p.is_absolute():
                return p.resolve()
            return (self.project_root() / p).resolve()
        return (self.project_root() / "assets").resolve()

    def _token_values(self) -> dict[str, str]:
        tokens = self._base_token_values()
        tokens["project_root"] = str(self.project_root())
        tokens["assets_root"] = str(self.assets_root())
        return tokens

    def _base_token_values(self) -> dict[str, str]:
        repo = self._find_repo_root()
        settings_dir = (
            self._config_path.parent if self._config_path else Path.cwd()
        )
        tokens = {
            "cwd": str(Path.cwd().resolve()),
            "settings_dir": str(settings_dir.resolve()),
        }
        if repo is not None:
            tokens["repo_root"] = str(repo.resolve())
        return tokens

    def _project_token_values(self) -> dict[str, str]:
        tokens = self._base_token_values()
        tokens["project_root"] = str(self.project_root())
        return tokens

    def _inferred_project_root(self) -> Path:
        repo_root = self._find_repo_root()
        if repo_root is None:
            return Path.cwd().resolve()

        if self._scope == "game" and self._name:
            return (repo_root / "games" / str(self._name)).resolve()
        if self._scope == "example" and self._name:
            rel = str(self._name).replace("\\", "/").strip("/")
            return (repo_root / "examples" / "catalog" / rel).resolve()

        return repo_root.resolve()

    def _expand_tokens(
        self, value: str, *, tokens: dict[str, str] | None = None
    ) -> str:
        if tokens is None:
            tokens = self._token_values()

        def _replace(match: re.Match[str]) -> str:
            token = match.group(1)
            return tokens.get(token, match.group(0))

        expanded = self._TOKEN_RE.sub(_replace, value)
        return os.path.expandvars(os.path.expanduser(expanded))

    def resolve_path(
        self, path_value: str | Path, *, default_to_cwd: bool = False
    ) -> Path:
        """
        Resolve one path using token/env expansion and project-root defaults.

        Supported placeholders:
        - ${repo_root}
        - ${project_root}
        - ${assets_root}
        - ${settings_dir}
        - ${cwd}
        """
        raw = str(path_value).strip()
        expanded = self._expand_tokens(raw)
        p = Path(expanded)
        if p.is_absolute():
            return p.resolve()
        if default_to_cwd:
            return (Path.cwd() / p).resolve()
        return (self.project_root() / p).resolve()

    def resolve_asset_path(self, path_value: str | Path) -> Path:
        """
        Resolve one asset path relative to assets root when not absolute.
        """
        raw = str(path_value).strip()
        expanded = self._expand_tokens(raw)
        p = Path(expanded)
        if p.is_absolute():
            return p.resolve()
        return (self.assets_root() / p).resolve()

    @staticmethod
    def _deep_copy_dict(data: dict[str, Any]) -> dict[str, Any]:
        copied: dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                copied[key] = Settings._deep_copy_dict(value)
            elif isinstance(value, list):
                copied[key] = [
                    (
                        Settings._deep_copy_dict(item)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in value
                ]
            else:
                copied[key] = value
        return copied

    @staticmethod
    def _deep_merge_dicts(
        base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        out = Settings._deep_copy_dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(out.get(key), dict):
                out[key] = Settings._deep_merge_dicts(
                    out[key], value
                )
            elif isinstance(value, dict):
                out[key] = Settings._deep_copy_dict(value)
            elif isinstance(value, list):
                out[key] = [
                    Settings._deep_copy_dict(item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                out[key] = value
        return out

    def engine_config_defaults(self) -> dict[str, Any]:
        """
        Engine settings defaults aligned to
        `mini_arcade_core.engine.game_config.EngineConfig`.
        """
        src = self.section("engine_config")

        virtual = src.get("virtual_resolution", (800, 600))
        if isinstance(virtual, (list, tuple)) and len(virtual) == 2:
            virtual_resolution = (int(virtual[0]), int(virtual[1]))
        else:
            virtual_resolution = (800, 600)

        postfx_src = src.get("postfx", {}) if isinstance(src, dict) else {}
        if not isinstance(postfx_src, dict):
            postfx_src = {}

        active = postfx_src.get("active", [])
        if not isinstance(active, list):
            active = []

        return {
            "fps": int(src.get("fps", 60)),
            "virtual_resolution": virtual_resolution,
            "enable_profiler": bool(src.get("enable_profiler", False)),
            "postfx": {
                "enabled": bool(postfx_src.get("enabled", True)),
                "active": [str(item) for item in active],
            },
        }

    def scene_defaults(self) -> dict[str, Any]:
        """
        Scene bootstrap defaults aligned to
        `mini_arcade_core.engine.game_config.SceneConfig`.
        """
        src = self.section("scene")

        if not isinstance(src, dict):
            src = {}

        scene_registry = src.get("scene_registry", {})
        if not isinstance(scene_registry, dict):
            scene_registry = {}

        discover_packages = scene_registry.get("discover_packages", [])
        if not isinstance(discover_packages, list):
            discover_packages = []

        initial_scene = src.get("initial_scene", "main")

        return {
            "initial_scene": str(initial_scene),
            "discover_packages": [
                str(item) for item in discover_packages if isinstance(item, str)
            ],
        }

    def gameplay_defaults(self) -> dict[str, Any]:
        """
        Gameplay settings defaults consumed by runtime gameplay settings.
        """
        src = self.section("gameplay")
        if not isinstance(src, dict):
            return {}

        out: dict[str, Any] = {}
        difficulty = src.get("difficulty")
        if isinstance(difficulty, str):
            out["difficulty"] = {"level": difficulty}
            return out

        if not isinstance(difficulty, dict):
            return out

        level = difficulty.get("level", difficulty.get("default"))
        if level is not None:
            out["difficulty"] = {"level": str(level)}
        return out

    def backend_defaults(
        self, *, resolve_paths: bool = False
    ) -> dict[str, Any]:
        """
        Backend settings defaults for backend-specific settings builders.
        """
        backend = self.section("backend")
        if not resolve_paths:
            return backend

        out = self._deep_copy_dict(backend)

        fonts = out.get("fonts")
        if isinstance(fonts, dict):
            path_ = fonts.get("path")
            if isinstance(path_, str):
                fonts["path"] = str(self.resolve_path(path_))
        elif isinstance(fonts, list):
            for item in fonts:
                if not isinstance(item, dict):
                    continue
                path_ = item.get("path")
                if isinstance(path_, str):
                    item["path"] = str(self.resolve_path(path_))

        audio = out.get("audio")
        if isinstance(audio, dict):
            sounds = audio.get("sounds")
            if isinstance(sounds, dict):
                for sound_id, sound_path in list(sounds.items()):
                    if isinstance(sound_path, str):
                        sounds[sound_id] = str(
                            self.resolve_asset_path(sound_path)
                        )

        return out

    def as_dict(self) -> dict[str, Any]:
        """
        Return full settings dictionary.
        """
        return dict(self._settings)


# Lazy-by-default global settings object (no exception if file is missing).
settings = Settings(required=False)

if __name__ == "__main__":
    # Example usage
    print("Loaded settings:")
    shared = Settings.for_example()
    print(shared.as_dict())
    engine_config_basics = settings.for_example("config/engine_config_basics")
    print(engine_config_basics.as_dict())
    backend_swap = settings.for_example("config/backend_swap")
    print(backend_swap.as_dict())
    s_asteroids = settings.for_game("asteroids")
    print(s_asteroids.as_dict())
    s_space = settings.for_game("space-invaders")
    print(s_space.as_dict())
    s_deja = settings.for_game("deja-bounce")
    print(s_deja.as_dict())
