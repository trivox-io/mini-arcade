#include "mini/sdl_text.h"
#include <stdexcept>
#include <string>

namespace mini {

    SdlTextRenderer::SdlTextRenderer(IRenderer& renderer)
        : renderer_(renderer)
        {
        }

    SdlTextRenderer::~SdlTextRenderer() {
        for (auto* f : fonts_) {
            if (f) TTF_CloseFont(f);
        }
        fonts_.clear();
    }

    int SdlTextRenderer::load_font(const std::string& path, int pt) {
        if (path.empty()) {
            throw std::runtime_error("load_font: path is empty");
        }
        TTF_Font* f = TTF_OpenFont(path.c_str(), pt);
        if (!f) {
            throw std::runtime_error(std::string("TTF_OpenFont Error: ") + TTF_GetError());
        }
        fonts_.push_back(f);
        int id = static_cast<int>(fonts_.size() - 1);
        if (default_font_id_ < 0) default_font_id_ = id;
        return id;
    }

    std::pair<int,int> SdlTextRenderer::measure_utf8(const std::string& text, int font_id) {
        int idx = font_id;
        if (idx < 0) idx = default_font_id_;
        if (idx < 0 || idx >= (int)fonts_.size() || !fonts_[idx]) return {0,0};

        int w=0,h=0;
        if (text.empty()) return {0,0};
        if (TTF_SizeUTF8(fonts_[idx], text.c_str(), &w, &h) != 0) return {0,0};
        return {w,h};
    }

    void SdlTextRenderer::draw_utf8(
        const std::string& text, int x, int y,
        int r, int g, int b, int a,
        int font_id
    ) {
        int idx = font_id;
        if (idx < 0) idx = default_font_id_;
        if (idx < 0 || idx >= (int)fonts_.size() || !fonts_[idx]) return;
        if (text.empty()) return;

        SDL_Color c{
            (Uint8) (r < 0 ? 0 : (r > 255 ? 255 : r)),
            (Uint8) (g < 0 ? 0 : (g > 255 ? 255 : g)),
            (Uint8) (b < 0 ? 0 : (b > 255 ? 255 : b)),
            (Uint8) (a < 0 ? 0 : (a > 255 ? 255 : a))
        };

        SDL_Surface* surf = TTF_RenderUTF8_Blended(fonts_[idx], text.c_str(), c);
        if (!surf) return;

        // Convert to RGBA32 so renderer texture upload is consistent
        SDL_Surface* rgba = SDL_ConvertSurfaceFormat(surf, SDL_PIXELFORMAT_RGBA32, 0);
        SDL_FreeSurface(surf);
        if (!rgba) return;

        TextureHandle tex = renderer_.create_texture_rgba(rgba->w, rgba->h, rgba->pixels, rgba->pitch);
        int w = rgba->w;
        int h = rgba->h;
        SDL_FreeSurface(rgba);

        if (tex == 0) return;

        renderer_.draw_texture(tex, x, y, w, h);
        renderer_.destroy_texture(tex);
    }

} // namespace mini
