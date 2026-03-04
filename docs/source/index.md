# Mini Arcade

Mini Arcade is a Python-first mini game engine and monorepo built to ship
small arcade games while keeping engine architecture simple, explicit, and
testable.

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

```{toctree}
:caption: Start Here
:hidden:

README <readme>
Quickstart <quickstart>
Architecture <concepts/architecture>
Capabilities <concepts/capabilities>
Tutorials <tutorials/index>
Games <games/index>
Contributing <contributing/index>
```

```{toctree}
:hidden:
:caption: API Reference

autoapi/index
```
