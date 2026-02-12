#include "mini/window.h"
#include <stdexcept>
#include <string>

namespace mini {

    Window::~Window() {
        if (window_) {
            SDL_DestroyWindow(window_);
            window_ = nullptr;
        }
    }

    void Window::create(const WindowConfig& cfg) {
        if (window_) return;

        high_dpi_ = cfg.high_dpi;

        Uint32 flags = SDL_WINDOW_SHOWN;
        if (cfg.resizable) flags |= SDL_WINDOW_RESIZABLE;
        if (cfg.high_dpi)  flags |= SDL_WINDOW_ALLOW_HIGHDPI;

        window_ = SDL_CreateWindow(
            cfg.title.c_str(),
            SDL_WINDOWPOS_CENTERED,
            SDL_WINDOWPOS_CENTERED,
            cfg.width,
            cfg.height,
            flags
        );

        if (!window_) {
            throw std::runtime_error(std::string("SDL_CreateWindow Error: ") + SDL_GetError());
        }
    }

    void Window::set_title(const char* title) {
        if (!window_) return;
        SDL_SetWindowTitle(window_, title ? title : "");
    }

    void Window::resize(int w, int h) {
        if (!window_) return;
        SDL_SetWindowSize(window_, w, h);
    }

    std::pair<int,int> Window::size() const {
        int w=0,h=0;
        if (window_) SDL_GetWindowSize(window_, &w, &h);
        return {w,h};
    }

    std::pair<int,int> Window::drawable_size() const {
    // In SDL_Renderer path you typically query renderer output size, but we
    // also provide a fallback here.
        int w=0,h=0;
        if (window_) SDL_GL_GetDrawableSize(window_, &w, &h); // returns logical if not GL; ok as fallback
        if (w == 0 || h == 0) {
            auto sz = size();
            w = sz.first;
            h = sz.second;
        }
        return {w,h};
    }

} // namespace mini
