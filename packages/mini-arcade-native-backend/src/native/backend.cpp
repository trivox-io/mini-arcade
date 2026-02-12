#include "mini/backend.h"
#include "mini/sdl_renderer.h"
#include "mini/sdl_text.h"
#include <stdexcept>

namespace mini {

Backend::Backend(const BackendConfig& cfg)
    : platform_()
{
    window_.create(cfg.window);

  // Renderer selection (OpenGL placeholder)
    switch (cfg.render.api) {
        case RenderAPI::SDL2:
            renderer_ = std::make_unique<SdlRenderer>(window_);
            break;
        case RenderAPI::OpenGL:
            throw std::runtime_error("RenderAPI::OpenGL not implemented yet");
    }

    renderer_->set_clear_color(cfg.render.clear_color);

    // Text renderer depends on renderer (future: GlTextRenderer)
    text_ = std::make_unique<SdlTextRenderer>(*renderer_);

    // Load default font (optional)
    if (!cfg.text.default_font_path.empty()) {
        int fid = text_->load_font(cfg.text.default_font_path, cfg.text.default_font_size);
        // If it's the SDL text renderer, it sets default automatically; fine.
        (void)fid;
    }

  // Audio (optional)
    if (cfg.audio.enabled) {
        audio_.init(cfg.audio.frequency, cfg.audio.channels, cfg.audio.chunk_size);
    }

    // Optional sound preload
    for (const auto& kv : cfg.sounds) {
        audio_.load_sound(kv.first, kv.second);
    }
}

Backend::~Backend() {
    // Order matters:
    // - text may reference renderer textures
    // - renderer references window
    // members destruct in reverse order, so we’re good:
    // capture_, audio_, text_, renderer_, input_, window_, platform_
}

} // namespace mini
