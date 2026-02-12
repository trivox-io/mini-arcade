# Capabilities

Keep this page updated. It answers: **what works today, where, and what proves it?**

| Feature | Core | Pygame backend | Native backend | Proof (example/game) |
|---|---:|---:|---:|---|
| Window + event polling | ✅ | ✅ | ✅ | E01 Boot & Blank Window |
| Clear + primitive rendering (rect, line) | ✅ | ✅ | ✅ | (no example yet) |
| Primitive rendering (circle, others) | ⚠️ | ⚠️ | ⚠️ | (planned) |
| Text rendering | ✅ | ✅ | ✅ | (no example yet) |
| Audio (play SFX/music) | ✅ | ✅ | ✅ | (no example yet) |
| Input mapping (events → keys) | ✅ | ✅ | ✅ | (no example yet) |
| InputFrame (keys_down/pressed/released) | ✅ | ✅ | ✅ | (no example yet) |
| Input → Intent pattern (input system) | ✅ | ✅ | ✅ | (no example yet) |
| 2D math (Vec2) | ✅ | ✅ | ✅ | E03 Collisions 2D |
| Transforms / geometry basics (Position/Size/Transform2D) | ✅ | ✅ | ✅ | (no example yet) |
| Kinematics (Velocity/advance, Kinematic2D) | ✅ | ✅ | ✅ | (no example yet) |
| Collisions 2D (AABB/rect collider) | ✅ | ✅ | ✅ | (no example yet) |
| Simple bouncing / responses (game-level) | ✅ | ✅ | ✅ | (no example yet) |
| Sprites (textures) | ✅ | ✅ | ✅ | (no example yet) |
| Sprite animation (frame-based) | ✅ | ✅ | ✅ | (no example yet) |
| Scene registry / auto-registration | ✅ | ✅ | ✅ | (no example yet) |
| Scene stack / overlays (visible_entries, input_entry) | ✅ | ✅ | ✅ | (no example yet) |
| System pipeline (ordered systems) | ✅ | ✅ | ✅ | (no example yet) |
| Render pipeline (multi-pass structure) | ✅ | ⚠️ | ⚠️ | (no example yet) |
| UI pass (WIP) | ⚠️ | ⚠️ | ⚠️ | (planned) |
| Lighting pass (WIP) | ⚠️ | ⚠️ | ⚠️ | (planned) |
| PostFX stack (CRT, vignette noise) | ✅ | ⚠️ | ⚠️ | (no example yet) |
| Screenshots (still capture) | ✅ | ✅ | ✅ | E05 Capture |
| Recordings (video frames → encoded video) | ✅ | ❌ | ⚠️ | (no example yet) |
| Replays (input recording/playback) | ⚠️ | ⚠️ | ⚠️ | (no example yet) |
| Determinism helpers (frame_index/dt authoritative) | ⚠️ | ⚠️ | ⚠️ | (no example yet) |
| Profiler / frame timer reporting | ✅ | ✅ | ✅ | (no example yet) |
