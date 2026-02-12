#pragma once
#include <SDL.h>
#include <unordered_map>
#include "renderer.h"
#include "window.h"

namespace mini {

class SdlRenderer final : public IRenderer {
    public:
        explicit SdlRenderer(Window& window);
        ~SdlRenderer() override;

        void set_clear_color(ColorRGBA c) override;
        void begin_frame() override;
        void end_frame() override;

        void draw_rect(int x,int y,int w,int h, ColorRGBA c) override;
        void draw_line(int x1,int y1,int x2,int y2, ColorRGBA c) override;

        void set_clip_rect(int x,int y,int w,int h) override;
        void clear_clip_rect() override;

        std::pair<int,int> drawable_size() const override;

        TextureHandle create_texture_rgba(int w, int h, const void* pixels, int pitch) override;
        void draw_texture(TextureHandle tex, int x, int y, int w, int h) override;
        void destroy_texture(TextureHandle tex) override;
        void draw_texture_tiled_y(TextureHandle tex, int x, int y, int w, int h) override;

        bool read_pixels_argb8888(void* dst, int pitch, int w, int h) override;
        

        SDL_Renderer* sdl() const { return renderer_; }

    private:
        Window& window_;
        SDL_Renderer* renderer_ = nullptr;
        ColorRGBA clear_{0,0,0,255};

        TextureHandle next_tex_id_ = 1;
        std::unordered_map<TextureHandle, SDL_Texture*> textures_;
};

} // namespace mini
