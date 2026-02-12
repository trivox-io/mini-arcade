#include "mini/capture.h"
#include <SDL.h>
#include <iostream>

namespace mini {

    bool Capture::save_bmp(IRenderer& renderer, const std::string& path) {
        auto [w, h] = renderer.drawable_size();
        if (w <= 0 || h <= 0) return false;

        SDL_Surface* surface = SDL_CreateRGBSurfaceWithFormat(
            0, w, h, 32, SDL_PIXELFORMAT_ARGB8888
        );
        if (!surface) return false;

        if (!renderer.read_pixels_argb8888(surface->pixels, surface->pitch, w, h)) {
            SDL_FreeSurface(surface);
            return false;
        }

        if (SDL_SaveBMP(surface, path.c_str()) != 0) {
            SDL_FreeSurface(surface);
            return false;
        }

        SDL_FreeSurface(surface);
        return true;
    }

} // namespace mini
