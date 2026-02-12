# Deja Bounce

A minimalist Pong-like arena prototype built on Mini Arcade.

Deja Bounce serves two roles:

1) a tiny shippable game  
2) a **reference project** that validates engine features

## Validates (engine features)

- scenes + system pipeline
- input → intents
- collisions (2D)
- fixed tick simulation (replay-friendly direction)
- backend swapping (native / pygame)
- capture hooks (screenshots / recordings) *(as implemented)*

## Run

```bash
mini-arcade run --game deja-bounce
```

## Roadmap

- replay format v1 (deterministic ticks)
- content pipeline presets (IG/YouTube aspect exports)
- difficulty + modifiers (Arena Pong direction)
