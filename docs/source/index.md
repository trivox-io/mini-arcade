# Mini Arcade

Mini Arcade is a Python-first mini game engine and monorepo built to ship
small arcade games while keeping engine architecture simple, explicit, and
testable.

A Trivox project for building and shipping small arcade games with a clean,
testable Python-first architecture.

::::{grid} 2 2 4 4
:gutter: 2

:::{grid-item-card} Docs
:link: quickstart
:link-type: doc

Start with the quickstart, architecture, tutorials, and API reference.
:::

:::{grid-item-card} Repo
:link: https://github.com/trivox-io/mini-arcade

Browse the monorepo, packages, games, and tooling on GitHub.
:::

:::{grid-item-card} Play the Games
:link: games/index
:link-type: doc

See the reference games used to validate engine architecture in practice.
:::

:::{grid-item-card} Back to Trivox
:link: https://trivox.io/

Return to the wider Trivox ecosystem of tools, pipelines, and experiments.
:::

::::

```{button-link} quickstart.html
:color: primary
:shadow:

Get Started
```

```{button-link} concepts/architecture.html
:color: secondary
:shadow:

Read Architecture
```

## Why Mini Arcade exists

Mini Arcade exists to validate engine architecture through real games, not
just isolated demos. It is a Python-first engine playground inside the broader
Trivox ecosystem, built to turn small arcade games into a practical way to
test reusable systems, scene patterns, rendering flows, and tooling.

The emphasis is on reusable systems rather than throwaway prototypes. Games in
the repo are meant to help harden the engine, expose weak spots in the
architecture, and keep the path from experiment to shippable small game clean
and testable.

## What you get

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Engine Core
Simulation-first scenes, entities, systems, commands, and render packets.
:::

:::{grid-item-card} Swappable Backends
Run with native SDL2 or pygame through the same backend protocol.
:::

:::{grid-item-card} Learning Path
Progressive tutorials and reference games that validate real features.
:::

:::{grid-item-card} Capture Tooling
Screenshots, replay recording/playback, and video frame capture hooks.
:::

::::

## Project Status

- Active project
- Monorepo evolving
- Games used as validation
- More tools and examples coming

## Explore

::::{grid} 1 1 3 3
:gutter: 2

:::{grid-item-card} Docs
:link: quickstart
:link-type: doc

Quick start, architecture, capabilities, and contributing guides.
:::

:::{grid-item-card} Tutorials
:link: tutorials/index
:link-type: doc

Runnable examples designed to teach engine concepts incrementally.
:::

:::{grid-item-card} Games
:link: games/index
:link-type: doc

Reference games used to validate architecture and catch regressions.
:::

::::

Built by Santiago under [Trivox](https://trivox.io/).

```{toctree}
:caption: Start Here
:hidden:

README <readme>
Quickstart <quickstart>
Architecture <concepts/architecture>
Capabilities <concepts/capabilities>
Configuration Internals <concepts/configuration>
Backends Internals <concepts/backends>
Scene Internals <concepts/scenes_internals>
Grid Gameplay Internals <concepts/grid_gameplay>
Falling Blocks Internals <concepts/falling_blocks_gameplay>
Brick Breaker Internals <concepts/brick_breaker_gameplay>
Maze Gameplay Internals <concepts/maze_gameplay>
Bomberman Gameplay Internals <concepts/bomberman_gameplay>
Menu Scenes Internals <concepts/menu_scenes>
Scene Transitions Internals <concepts/scene_transitions>
Overlay Policies Internals <concepts/overlay_policies>
Window and Viewport Internals <concepts/window_viewports>
Entities Internals <concepts/entities>
Shapes and Layering Internals <concepts/shapes_layers>
Sprites and Animations Internals <concepts/sprites_animations>
Input Coordinate Mapping Internals <concepts/input_coordinate_mapping>
Tutorials <tutorials/index>
Games <games/index>
Contributing <contributing/index>
```

```{toctree}
:hidden:
:caption: API Reference

autoapi/index
```
