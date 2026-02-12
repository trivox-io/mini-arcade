#pragma once
#include <SDL.h>
#include <utility>
#include "config.h"

namespace mini {

class Window {
public:
    Window() = default;
    ~Window();

    Window(const Window&) = delete;
    Window& operator=(const Window&) = delete;

    void create(const WindowConfig& cfg);
    void set_title(const char* title);
    void resize(int w, int h);

    SDL_Window* sdl() const { return window_; }

    std::pair<int,int> size() const;          // logical
    std::pair<int,int> drawable_size() const; // HiDPI drawable

    private:
        SDL_Window* window_ = nullptr;
        bool high_dpi_ = true;
};

} // namespace mini
