#pragma once
#include <vector>
#include <cstdint>

namespace mini {

    class IRenderer;

    struct PixelBuffer {
        int w = 0;
        int h = 0;
        // bytes in SDL_PIXELFORMAT_ARGB8888 (or whatever you choose)
        std::vector<uint8_t> bytes;
    };

    PixelBuffer capture_argb8888(IRenderer& renderer);
}
