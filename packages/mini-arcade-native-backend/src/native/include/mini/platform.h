#pragma once

namespace mini {

// RAII: SDL + TTF lifecycle.
// Note: SDL_mixer is managed by Audio subsystem.
class Platform {
public:
    Platform();
    ~Platform();

    Platform(const Platform&) = delete;
    Platform& operator=(const Platform&) = delete;

    bool initialized() const { return initialized_; }

    private:
    bool initialized_ = false;
};

} // namespace mini
