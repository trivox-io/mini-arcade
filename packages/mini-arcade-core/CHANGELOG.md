# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.3.4] - 2026-02-06

### Added
- add Animation class for frame-based animations

## [1.3.3] - 2026-02-06

### Added
- enhance rendering capabilities with texture management methods

### Other
- Merge branch 'release/1.3' of https://github.com/alexsc6955/mini-arcade-core into release/1.3

## [1.3.2] - 2026-02-05

### Changed
- refactor menu and simulation scene systems to use base classes for improved structure

## [1.3.1] - 2026-02-05

### Added
- add configuration utilities for backend components

## [1.3.0] - 2026-02-04

### Added
- add video recording and encoding functionality with capture service

### Other
- Merge release/1.2 into develop

## [1.2.2] - 2026-02-03

### Added
- implement capture service for screenshots and replays

## [1.2.1] - 2026-02-03

### Added
- implement asynchronous screenshot capturing with worker thread

## [1.2.0] - 2026-02-03

### Other
- Merge release/1.1 into develop

## [1.1.2] - 2026-02-03

### Changed
- Remove duplicate draw_groups variable from RenderStats class
- Update render_frame method to use FramePacket instead of RenderPacket
- Enable post-processing effects and improve viewport handling in menu
- Update viewport handling and rendering logic across multiple modules
- Update imports for SimScene and improve logging and profiler formatting
- Improve code structure and apply separation of concerns.

### Other
- Merge branch 'release/1.1' of https://github.com/alexsc6955/mini-arcade-core into release/1.1

## [1.1.1] - 2026-01-23

### Added
- implement post-processing effects system with CRT and vignette effects

### Other
- Merge branch 'release/1.1' of https://github.com/alexsc6955/mini-arcade-core into release/1.1

## [1.1.0] - 2026-01-23

### Added
- enhance rendering system with FramePacket and RenderService integration
- integrate rendering pipeline into game loop
- implement render pipeline with multiple processing passes

### Fixed
- add justification comments for duplicate code in render pipeline
- disable pylint warnings for unused arguments in render pass classes

### Changed
- enhance rendering system with detailed docstrings and new render service port

### Other
- Merge release/1.0 into develop

## [1.0.2] - 2026-01-23

### Added
- Add debug overlay scene to display FPS and window information
- Implement viewport management and window resizing functionality
- Introduce WindowSettings and enhance audio adapter functionality

### Changed
- Improve documentation and type hints in backend and viewport modules
- Enhance documentation and type hints across multiple modules

### Other
- Merge branch 'release/1.0' of https://github.com/alexsc6955/mini-arcade-core into release/1.0

## [1.0.1] - 2026-01-23

### Added
- Implement viewport management and window resizing functionality
- Introduce WindowSettings and enhance audio adapter functionality

### Changed
- Improve documentation and type hints in backend and viewport modules
- Enhance documentation and type hints across multiple modules

## [1.0.0] - 2026-01-21

### Added
- Add FrameTimer class for performance measurement and reporting in Game loop
- Implement menu systems and context for enhanced menu interactions and rendering
- Introduce CommandContext for structured command execution and update related command classes
- Enhance command execution by adding settings parameter and refactor menu command handling
- Implement RenderPipeline and RenderPacket for enhanced rendering capabilities
- Integrate CheatManager for enhanced cheat code functionality and scene management
- Introduce Command protocol and CommandQueue for structured command execution
- Implement InputAdapter and InputFrame for enhanced input handling
- Introduce CaptureAdapter and CapturePort for enhanced screenshot functionality
- Refactor runtime services by introducing adapters for window and scene management
- Implement scene cleanup functionality in SceneManager and ScenePort
- Add window title management to backend and enhance scene management interfaces
- Add window title setting and enhance service interface documentation
- Enhance runtime services with window management and logging utilities
- Add runtime configuration, logging utilities and deprecated wrapper

### Fixed
- Update _bmp_to_image method signature to include out_path parameter

### Changed
- Remove temporary development files from .gitignore
- Enhance docstrings across multiple modules for clarity and maintainability
- Remove Entity base classes to streamline architecture
- Clean up and reorganize scene and manager modules; remove unused classes and improve imports
- Simplify collision detection logic and enhance Collider2D abstraction
- Update CheatManager registration to improve clarity and consistency in parameter handling
- Rename cheats to cheat_manager in Game class for clarity and remove duplicate input declaration in RuntimeServices
- Replace _commands with command_queue in Game class and related components
- Remove unused _bmp_to_image method and update screenshot return type to file path
- Remove unused TYPE_CHECKING imports and simplify SceneAdapter initialization
- Update run method to use scene ID instead of SceneOrId type

### Other
- Refactor input and rendering modules; migrate to engine structure
- Refactor runtime components and reorganize adapters
- Merge release/0.10 into develop

## [0.10.0] - 2025-12-26

### Added
- Implement command and cheat management system
- Add Overlay and BaseOverlay classes with update and draw methods for enhanced overlay management

### Other
- Merge release/0.9 into develop
- Merge branch 'release/0.9' of https://github.com/alexsc6955/mini-arcade-core into release/0.9

## [0.9.9] - 2025-12-22

### Added
- Implement scene services and managers for enhanced entity and overlay handling

### Other
- Merge branch 'release/0.9' of https://github.com/alexsc6955/mini-arcade-core into release/0.9

## [0.9.8] - 2025-12-22

### Added
- Add cheats module with CheatCode and CheatManager classes

### Changed
- Remove logging statements from CheatManager for cleaner code

## [0.9.7] - 2025-12-19

### Changed
- Refactor run_game function to support flexible scene initialization and improve documentation

## [0.9.6] - 2025-12-18

### Added
- Add GameSettings dataclass for adjustable gameplay difficulty

### Other
- Merge branch 'release/0.9' of https://github.com/alexsc6955/mini-arcade-core into release/0.9

## [0.9.5] - 2025-12-16

### Added
- Enhance MenuStyle with font size attributes and update text rendering

## [0.9.4] - 2025-12-16

### Added
- Implement scene registration and discovery utilities

### Changed
- Remove redundant return types from method signatures in registry, menu, and test files

## [0.9.3] - 2025-12-16

### Added
- Add SceneRegistry for managing scene creation and registration

## [0.9.2] - 2025-12-16

### Added
- Enhance MenuStyle with additional attributes for improved styling options
- Add text measurement functionality and enhance menu styling options

### Other
- Merge branch 'release/0.9' of https://github.com/alexsc6955/mini-arcade-core into release/0.9

## [0.9.1] - 2025-12-16

### Added
- Add key definitions and SDL keymap for improved input handling

## [0.9.0] - 2025-12-15

### Added
- Enhance Event and EventType classes with additional event types and optional attributes

### Other
- Merge release/0.8 into develop

## [0.8.1] - 2025-12-15

### Added
- Add docstring to current_scene method for clarity on active scene retrieval
- Enhance menu system with detailed docstrings for better clarity
- Implement scene stack management and menu system with pause/resume functionality

## [0.8.0] - 2025-12-12

### Added
- Add docstring, format code and solve pylint warnings
- update imports and improve type annotations across multiple modules
- refactor color type handling in backend and kinematics2d modules
- enhance game configuration validation and update imports in __init__.py
- add VerticalBounce class for vertical collision handling and integrate Bounds2D
- add movement control methods to Velocity2D class
- add RectCollider class for 2D collision detection and integrate into entity system
- implement entity management methods in Scene class
- add Size2D import and define scene size in Scene class
- add Entity import and define entities list in Scene class
- add 2D geometry, physics, and kinematics classes for improved entity handling

### Changed
- clean up import statements in test files
- remove deprecated properties from SpriteEntity and KinematicEntity

### Other
- Refactor tests and implement new test cases for game backend, scene management, and 2D physics
- Merge release/0.7 into develop

## [0.7.5] - 2025-12-05

### Fixed
- handle exceptions in image saving process in Game class

## [0.7.4] - 2025-12-05

### Added
- add BMP to image conversion method in Game class and update dependencies
- enhance documentation with type hints and parameter descriptions across multiple modules

### Other
- Merge branch 'release/0.7' of https://github.com/alexsc6955/mini-arcade-core into release/0.7
- Merge branch 'release/0.7' of https://github.com/alexsc6955/mini-arcade-core into release/0.7

## [0.7.3] - 2025-12-05

### Added
- enhance documentation with type hints and parameter descriptions across multiple modules

### Other
- Merge branch 'release/0.7' of https://github.com/alexsc6955/mini-arcade-core into release/0.7

## [0.7.2] - 2025-12-05

### Added
- implement overlay management methods in Scene class

## [0.7.1] - 2025-12-05

### Added
- add capture_frame method to Backend protocol and implement screenshot method in Game class

## [0.7.0] - 2025-12-05

### Added
- add set_clear_color method to Backend protocol and update Game to use background_color
- add draw_text method to Backend protocol for rendering text

### Other
- Merge pull request #6 from alexsc6955/develop
- Merge pull request #5 from alexsc6955/feature/text_support
- Merge release/0.6 into develop

## [0.6.1] - 2025-12-04

### Added
- implement game loop and scene management in Game class

### Other
- Merge pull request #4 from alexsc6955/feature/game_loop
- Merge release/0.5 into develop
- Merge release/0.5 into main

## [0.5.3] - 2025-12-04

### Changed
- simplify version retrieval logic in __init__.py

### Other
- Merge branch 'release/0.5' of https://github.com/alexsc6955/mini-arcade-core into release/0.5

## [0.5.2] - 2025-12-04

### Changed
- enhance logging in get_version function and add logging configuration

### Other
- Merge branch 'release/0.5' of https://github.com/alexsc6955/mini-arcade-core into release/0.5

## [0.5.1] - 2025-12-04

### Fixed
- add print statement to indicate package not found in get_version function

## [0.5.0] - 2025-12-03

### Added

- add version retrieval function and handle exceptions gracefully

### Fixed

- improve docstring for get_version function to clarify return type and exceptions

## [0.4.0] - 2025-12-03

### Added

- Initial documented release. Earlier versions (0.1.0–0.3.0) are not listed here.
