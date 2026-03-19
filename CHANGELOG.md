# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.6.1] - 2026-03-19

### Other
- Merge branch 'main' of https://github.com/trivox-io/mini-arcade

## [1.6.0] - 2026-03-18

### Added
- Add power-up collection system and update game cases for breakout and snake
- Update render port to handle legacy draw_texture signature; add corresponding tests
- Enhance error handling and logging in game loop; update tests for example failures
- Add example systems for viewport culling, input frame visualization, pause intent, and phases/order management
- Add system lab scaffolding and visual runner
- Implement backend loading functionality and add tests for error handling
- Add core gameplay systems for Bomberman and Maze-style arcade games
- add brick-breaker gameplay systems and documentation for collision mechanics
- add falling-block gameplay systems and documentation for stacking puzzle games
- add game scaffolding CLI module and system lab for isolated system execution
- Introduce new gameplay scene structure and enhance projectile lifecycle systems with spawn and wave progression capabilities
- Enhance gameplay architecture with GameScene and entity management
- Add built-in movement systems and viewport constraints, enhance animation and culling systems with new functionality and tests
- Enhance BaseWorld to maintain entity indexes during mutations and add corresponding tests
- Add examples for entity features
- Implement data-driven entity configuration and enhance scene runtime settings
- Enhance scene documentation and controls, remove debug overlay references
- Implement configurable ESC behavior for scenes with gameplay settings integration
- Implement configurable debug overlay with gameplay settings integration
- Add automated smoke tests for scene discovery and gameplay validation
- Add tour command for running examples sequentially with options
- add backend swap tutorial and example implementation refactor: update engine configuration documentation and examples fix: enhance font handling in native backend with fallback options feat: implement texture drawing with rotation support in native backend style: improve command-line argument parsing for game runner
- implement capture controls and event handlers for screenshots and video recording
- add system phases and update systems to use them.

### Changed
- Refactor and enhance mini-arcade modules
- Refactor examples and add engine configuration tutorial

### Other
- docs: Update README and documentation for local development and backend setup
- Refactor input binding systems and enhance capture controls
- docs: Improve create games docs
- docs: add minimal scene tutorial with example implementation and configuration
- docs: update README and tutorial files for clarity and new game creation guide
- Refactor game module to engine module and update configuration classes
- style: format intent_for method for improved readability
- docs: update grid syntax for consistency and mark subprojects as dirty
- docs: Refactor documentation and examples for clarity and completeness

## [1.5.3] - 2026-03-04

### Other
- Merge branch 'main' of https://github.com/trivox-io/mini-arcade

## [1.5.2] - 2026-03-03

### Other
- Merge branch 'main' of https://github.com/trivox-io/mini-arcade

## [1.5.1] - 2026-03-03

### Other
- Merge branch 'main' of https://github.com/trivox-io/mini-arcade

## [1.5.0] - 2026-03-03

### Added
- Add minimal shape gallery example with debug overlay

### Changed
- mark subproject commits as dirty and update pylint configuration for design rules
- mark subproject commits as dirty and clean up import statements
- enhance docstrings and clean up code across multiple files
- Update subproject commit for space-invaders
- Update subproject commits and enhance input handling with new action bindings
- Update subproject commits for deja-bounce and space-invaders
- Improve input systems
- Improve scenes oranization
- Improve scenes oranization
- Improve scenes

### Other
- Refactor and enhance documentation across multiple modules
- Update asteroids submodule
- Add asteroids as submodule
- docs: Example 002 Added: Hello Overlay.
- chore(native): convert package from gitlink to monorepo folder
- chore(pygame): convert package from gitlink to monorepo folder
- chore(core): convert package from gitlink to monorepo folder
- Add games as submodules
- ci: add monorepo workflow

