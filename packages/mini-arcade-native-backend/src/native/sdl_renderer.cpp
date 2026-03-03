#include "mini/sdl_renderer.h"
#include <stdexcept>
#include <string>
#include <cmath>
#include <algorithm>
#include <vector>

namespace mini {

    static uint8_t clamp_u8(int v) {
        if (v < 0) return 0;
        if (v > 255) return 255;
        return static_cast<uint8_t>(v);
    }

    SdlRenderer::SdlRenderer(Window& window)
        : window_(window)
        {
            renderer_ = SDL_CreateRenderer(window_.sdl(), -1, SDL_RENDERER_ACCELERATED);
            if (!renderer_) {
                throw std::runtime_error(std::string("SDL_CreateRenderer Error: ") + SDL_GetError());
            }
            SDL_SetRenderDrawBlendMode(renderer_, SDL_BLENDMODE_BLEND);
        }

    SdlRenderer::~SdlRenderer() {
    // destroy textures first
        for (auto& kv : textures_) {
            if (kv.second) SDL_DestroyTexture(kv.second);
        }
        textures_.clear();

        if (renderer_) {
            SDL_DestroyRenderer(renderer_);
            renderer_ = nullptr;
        }
    }

    void SdlRenderer::set_clear_color(ColorRGBA c) { clear_ = c; }

    void SdlRenderer::begin_frame() {
        SDL_SetRenderDrawColor(renderer_, clear_.r, clear_.g, clear_.b, clear_.a);
        SDL_RenderClear(renderer_);
    }

    void SdlRenderer::end_frame() {
        SDL_RenderPresent(renderer_);
    }

    void SdlRenderer::draw_rect(int x,int y,int w,int h, ColorRGBA c) {
        SDL_Rect r{ x,y,w,h };
        SDL_SetRenderDrawColor(renderer_, c.r, c.g, c.b, c.a);
        SDL_RenderFillRect(renderer_, &r);
    }

    void SdlRenderer::draw_line(int x1,int y1,int x2,int y2, ColorRGBA c, int thickness) {
        SDL_SetRenderDrawColor(renderer_, c.r, c.g, c.b, c.a);
        if (thickness <= 1) {
            SDL_RenderDrawLine(renderer_, x1, y1, x2, y2);
        } else {
            // Simple thick line implementation using filled rectangles
            // This is a basic approach and may not be the most efficient or visually perfect.
            const float angle = std::atan2(static_cast<float>(y2 - y1), static_cast<float>(x2 - x1));
            const float dx = std::sin(angle) * (thickness / 2.0f);
            const float dy = std::cos(angle) * (thickness / 2.0f);

            SDL_FRect rect{
                static_cast<float>(x1) - dx,
                static_cast<float>(y1) + dy,
                static_cast<float>(x2 - x1) + dx * 2,
                static_cast<float>(y2 - y1) + dy * 2
            };
            SDL_RenderFillRectF(renderer_, &rect);
        }
    }

    void SdlRenderer::draw_circle(int cx, int cy, int radius, ColorRGBA c) {
        SDL_SetRenderDrawColor(renderer_, c.r, c.g, c.b, c.a);

        if (radius <= 0) return;

        // Filled circle: horizontal scanlines
        const int r2 = radius * radius;
        for (int dy = -radius; dy <= radius; ++dy) {
            int yy = cy + dy;
            int dx = static_cast<int>(std::sqrt(static_cast<double>(r2 - dy * dy)));
            SDL_RenderDrawLine(renderer_, cx - dx, yy, cx + dx, yy);
        }
    }

    void SdlRenderer::draw_poly(const std::pair<int,int>* points, size_t count, ColorRGBA c) {
        if (count < 3) return; // not a polygon

        SDL_SetRenderDrawColor(renderer_, c.r, c.g, c.b, c.a);

        // Simple filled polygon using SDL_RenderDrawLine for horizontal scanlines
        // This is a basic implementation and may not be the most efficient for complex polygons.
        // For production code, consider implementing a more robust polygon filling algorithm.

        // Find vertical bounds
        int min_y = points[0].second;
        int max_y = points[0].second;
        for (size_t i = 1; i < count; ++i) {
            if (points[i].second < min_y) min_y = points[i].second;
            if (points[i].second > max_y) max_y = points[i].second;
        }

        // For each scanline, find intersections with polygon edges
        for (int y = min_y; y <= max_y; ++y) {
            std::vector<int> intersections;

            for (size_t i = 0; i < count; ++i) {
                const auto& p1 = points[i];
                const auto& p2 = points[(i + 1) % count];

                if ((p1.second <= y && p2.second > y) || (p2.second <= y && p1.second > y)) {
                    // Edge intersects with scanline
                    int x = p1.first + (y - p1.second) * (p2.first - p1.first) / (p2.second - p1.second);
                    intersections.push_back(x);
                }
            }

            std::sort(intersections.begin(), intersections.end());

            // Draw horizontal lines between pairs of intersections
            for (size_t i = 0; i + 1 < intersections.size(); i += 2) {
                SDL_RenderDrawLine(renderer_, intersections[i], y, intersections[i + 1], y);
            }
        }
    }

    void SdlRenderer::set_clip_rect(int x,int y,int w,int h) {
        SDL_Rect r{ x,y,w,h };
        SDL_RenderSetClipRect(renderer_, &r);
    }

    void SdlRenderer::clear_clip_rect() {
        SDL_RenderSetClipRect(renderer_, nullptr);
    }

    std::pair<int,int> SdlRenderer::drawable_size() const {
        int w=0,h=0;
        if (SDL_GetRendererOutputSize(renderer_, &w, &h) == 0) return {w,h};
        // fallback
        return window_.drawable_size();
    }

    TextureHandle SdlRenderer::create_texture_rgba(int w, int h, const void* pixels, int pitch) {
        SDL_Texture* tex = SDL_CreateTexture(renderer_, SDL_PIXELFORMAT_RGBA32, SDL_TEXTUREACCESS_STATIC, w, h);
        if (!tex) return 0;

        SDL_SetTextureBlendMode(tex, SDL_BLENDMODE_BLEND);

        if (pixels) {
            if (SDL_UpdateTexture(tex, nullptr, pixels, pitch) != 0) {
                SDL_DestroyTexture(tex);
                return 0;
            }
        }

        TextureHandle id = next_tex_id_++;
        textures_[id] = tex;
        return id;
    }

    void SdlRenderer::draw_texture(TextureHandle tex, int x, int y, int w, int h) {
        auto it = textures_.find(tex);
        if (it == textures_.end() || !it->second) return;

        SDL_Rect dst{ x,y,w,h };
        SDL_RenderCopy(renderer_, it->second, nullptr, &dst);
    }

    void SdlRenderer::destroy_texture(TextureHandle tex) {
        auto it = textures_.find(tex);
        if (it == textures_.end()) return;
        if (it->second) SDL_DestroyTexture(it->second);
        textures_.erase(it);
    }

    void SdlRenderer::draw_texture_tiled_y(TextureHandle tex_id, int x, int y, int w, int h) {
        auto it = textures_.find(tex_id);
        if (it == textures_.end() || !it->second) return;

        SDL_Texture* tex = it->second;

        int src_w = 0;
        int src_h = 0;
        Uint32 fmt = 0;
        int access = 0;

        if (SDL_QueryTexture(tex, &fmt, &access, &src_w, &src_h) != 0) {
            return; // optionally log SDL_GetError()
        }

        // Match pygame behavior: keep tile height = original texture height
        const int tile_h = src_h;

        int cur_y = y;
        const int end_y = y + h;

        // Full source rect for one tile
        SDL_Rect src_full{0, 0, src_w, src_h};

        while (cur_y < end_y) {
            const int remaining = end_y - cur_y;

            if (remaining >= tile_h) {
                SDL_Rect dst{x, cur_y, w, tile_h}; // width scaled, height unchanged
                SDL_RenderCopy(renderer_, tex, &src_full, &dst);
                cur_y += tile_h;
            } else {
                // Crop vertically for the last partial piece
                SDL_Rect src_part{0, 0, src_w, remaining};
                SDL_Rect dst{x, cur_y, w, remaining};
                SDL_RenderCopy(renderer_, tex, &src_part, &dst);
                break;
            }
        }
    }

    bool SdlRenderer::read_pixels_argb8888(void* dst, int pitch, int w, int h) {
        // Read from current render target
        // Note: This reads ARGB8888 by request (matches your previous code).
        SDL_Rect rect{0,0,w,h};
        if (SDL_RenderReadPixels(renderer_, &rect, SDL_PIXELFORMAT_ARGB8888, dst, pitch) != 0) {
            return false;
        }
        return true;
    }

} // namespace mini
