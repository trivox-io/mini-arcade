#pragma once
#include <SDL_ttf.h>
#include <vector>
#include "text.h"
#include "renderer.h"

namespace mini {

// Uses SDL_ttf to rasterize to pixels, then uses IRenderer texture API to draw.
class SdlTextRenderer final : public ITextRenderer {
    public:
        explicit SdlTextRenderer(IRenderer& renderer);
        ~SdlTextRenderer() override;

        int load_font(const std::string& path, int pt) override;
        std::pair<int,int> measure_utf8(const std::string& text, int font_id) override;

        void draw_utf8(
            const std::string& text,
            int x, int y,
            int r, int g, int b, int a,
            int font_id
        ) override;

        int default_font_id() const { return default_font_id_; }
        void set_default_font(int id) { default_font_id_ = id; }

    private:
        IRenderer& renderer_;
        std::vector<TTF_Font*> fonts_;
        int default_font_id_ = -1;
};

} // namespace mini
