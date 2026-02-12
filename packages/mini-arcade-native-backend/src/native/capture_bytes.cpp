#include "mini/capture_bytes.h"
#include "mini/renderer.h"
#include <SDL.h>
#include <cstring>

namespace mini {

    PixelBuffer capture_argb8888(IRenderer& renderer) {
        PixelBuffer out;
        auto [w, h] = renderer.drawable_size();
        if (w <= 0 || h <= 0) return out;

        SDL_Surface* surface = SDL_CreateRGBSurfaceWithFormat(
            0, w, h, 32, SDL_PIXELFORMAT_ARGB8888
        );
        if (!surface) return out;

        if (!renderer.read_pixels_argb8888(surface->pixels, surface->pitch, w, h)) {
            SDL_FreeSurface(surface);
            return out;
        }

        out.w = w;
        out.h = h;
        out.bytes.resize(static_cast<size_t>(surface->pitch) * h);
        std::memcpy(out.bytes.data(), surface->pixels, out.bytes.size());

        SDL_FreeSurface(surface);
        return out;
    }

} // namespace mini
