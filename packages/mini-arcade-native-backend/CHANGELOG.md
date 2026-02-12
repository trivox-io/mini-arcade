# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.3] - 2026-02-06

### Added
- add texture management functions including creation, drawing, and destruction

## [1.0.2] - 2026-02-05

### Changed
- consolidate backend settings and remove unused viewport module

## [1.0.1] - 2026-02-04

### Added
- add ARGB8888 capture functionality and corresponding bindings

## [1.0.0] - 2026-02-03

### Changed
- Add separation of concerns

### Other
- Merge release/0.6 into develop
- Merge branch 'release/0.6' of https://github.com/alexsc6955/mini-arcade-native-backend into release/0.6

## [0.6.0] - 2026-01-23

### Added
- add draw_line method to Engine and bind it in Python

### Other
- Merge release/0.5 into develop

## [0.5.3] - 2026-01-23

- Internal changes only.

## [0.5.2] - 2026-01-23

### Added
- add window resizing and clipping functions to Engine and update bindings
- add audio management functions to Engine and integrate with NativeBackend

### Fixed
- update apt dependencies to include libsdl2-mixer-dev for CI and release workflows

### Changed
- add TODO for backend interface refactoring to improve structure

## [0.5.1] - 2026-01-23

### Added
- add window resizing and clipping functions to Engine and update bindings
- add audio management functions to Engine and integrate with NativeBackend

### Fixed
- update apt dependencies to include libsdl2-mixer-dev for CI and release workflows

### Changed
- add TODO for backend interface refactoring to improve structure

## [0.5.0] - 2026-01-21

### Added
- add set_window_title method to Engine and update init method to accept optional title

### Fixed
- Update dependencies and improve import handling for mini-arcade-core
- update import statements for Event and SDL_KEYCODE_TO_KEY to improve clarity

### Other
- Merge branch 'develop' into release/0.5

## [0.4.6] - 2025-12-26

### Fixed
- update mini-arcade-core dependency version and improve import statements

### Other
- Merge branch 'release/0.4' of https://github.com/alexsc6955/mini-arcade-native-backend into release/0.4

## [0.4.5] - 2025-12-16

### Added
- implement font caching and update draw_text and measure_text methods to support dynamic font sizes

## [0.4.4] - 2025-12-16

### Added
- add measure_text method to Engine and expose it in NativeBackend
- add alpha handling methods and refactor color extraction in NativeBackend
- update draw_rect and draw_text methods to support alpha channel in color

### Other
- Merge branch 'release/0.4' of https://github.com/alexsc6955/mini-arcade-native-backend into release/0.4
- Merge branch 'release/0.4' of https://github.com/alexsc6955/mini-arcade-native-backend into release/0.4

## [0.4.3] - 2025-12-16

### Added
- add alpha handling methods and refactor color extraction in NativeBackend
- update draw_rect and draw_text methods to support alpha channel in color

### Other
- Merge branch 'release/0.4' of https://github.com/alexsc6955/mini-arcade-native-backend into release/0.4

## [0.4.2] - 2025-12-16

### Added
- enhance event handling by adding key_code to event mapping in NativeBackend

## [0.4.1] - 2025-12-15

### Added
- extend event handling with additional mouse and window events in engine and bindings
- enhance font handling by returning font ID and updating draw_text signature

### Fixed
- update mini-arcade-core dependency version to ensure compatibility

### Other
- Merge release/0.3 into develop

## [0.4.0] - 2025-12-15

### Added
- extend event handling with additional mouse and window events in engine and bindings
- enhance font handling by returning font ID and updating draw_text signature

### Fixed
- update mini-arcade-core dependency version to ensure compatibility

### Other
- Merge release/0.3 into develop

## [0.3.3] - 2025-12-05

### Other
- docs: improve docstring formatting for capture_frame method in NativeBackend
- Merge branch 'release/0.3' of https://github.com/alexsc6955/mini-arcade-native-backend into release/0.3

## [0.3.2] - 2025-12-05

### Added
- add draw_rect_rgba method to Engine for RGBA rectangle drawing and update Python bindings
- add capture_frame method to Engine and expose it in Python bindings
- add clear color customization and update draw_rect method

### Other
- Merge branch 'release/0.3' of https://github.com/alexsc6955/mini-arcade-native-backend into release/0.3
- Merge branch 'release/0.3' of https://github.com/alexsc6955/mini-arcade-native-backend into release/0.3

## [0.3.1] - 2025-12-05

### Added
- add capture_frame method to Engine and expose it in Python bindings
- add clear color customization and update draw_rect method

### Other
- Merge branch 'release/0.3' of https://github.com/alexsc6955/mini-arcade-native-backend into release/0.3

## [0.3.0] - 2025-12-05

### Added
- add text rendering support with SDL2_ttf integration

### Other
- Merge pull request #7 from alexsc6955/feature/text_support
- Merge release/0.2 into develop

## [0.2.3] - 2025-12-04

- Internal changes only.

## [0.2.2] - 2025-12-04

- Internal changes only.

## [0.2.1] - 2025-12-04

### Other
- Merge pull request #2 from alexsc6955/main
- Merge pull request #1 from alexsc6955/feature/ci_cd
- Implement CI workflow for automated testing and linting
- Add SDL2.dll search path for Windows when using vcpkg
- Initial Commit

## [0.2.0] - 2025-12-04

### Other
- Merge pull request #2 from alexsc6955/main
- Merge pull request #1 from alexsc6955/feature/ci_cd
- Implement CI workflow for automated testing and linting
- Add SDL2.dll search path for Windows when using vcpkg
- Initial Commit

## [0.2.0] - 2025-12-03

### Added

- Initial documented release.
