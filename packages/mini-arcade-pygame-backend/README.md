# mini-arcade-pygame-backend

Pygame backend for Mini Arcade.

This package implements the shared Mini Arcade backend protocol with pygame and
is the simplest backend to use during early development.

It provides:

- window creation and lifecycle handling
- event polling mapped into core input events
- primitive rendering, texture drawing, and text rendering
- audio and capture ports that match the core runtime contract

## When to use it

Use `pygame` when you want:

- the easiest setup path
- fast iteration on gameplay and UI
- a stable reference backend for parity comparisons

## Install

```bash
pip install mini-arcade-pygame-backend
```

## Docs

See the monorepo docs for backend selection and parity testing:

- `docs/source/concepts/backends.md`
- `docs/source/tutorials/config/backend_swap.md`
