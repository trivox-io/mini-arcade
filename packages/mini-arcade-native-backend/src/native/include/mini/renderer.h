#pragma once
#include <cstdint>
#include <utility>
#include "color.h"

namespace mini {

using TextureHandle = uint32_t;

class IRenderer {
    public:
        virtual ~IRenderer() = default;

        virtual void set_clear_color(ColorRGBA c) = 0;
        virtual void begin_frame() = 0;
        virtual void end_frame() = 0;

        virtual void draw_rect(int x,int y,int w,int h, ColorRGBA c) = 0;
        virtual void draw_line(int x1,int y1,int x2,int y2, ColorRGBA c) = 0;

        virtual void set_clip_rect(int x,int y,int w,int h) = 0;
        virtual void clear_clip_rect() = 0;

        virtual std::pair<int,int> drawable_size() const = 0;

        // Texture API (needed for text now, sprites later)
        virtual TextureHandle create_texture_rgba(int w, int h, const void* pixels, int pitch) = 0;
        virtual void draw_texture(TextureHandle tex, int x, int y, int w, int h) = 0;
        virtual void destroy_texture(TextureHandle tex) = 0;
        virtual void draw_texture_tiled_y(TextureHandle tex, int x, int y, int w, int h) = 0;

        // Capture hook (ARGB8888)
        virtual bool read_pixels_argb8888(void* dst, int pitch, int w, int h) = 0;
};

} // namespace mini
