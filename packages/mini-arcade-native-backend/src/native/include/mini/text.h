#pragma once
#include <string>
#include <utility>

namespace mini {

class ITextRenderer {
public:
    virtual ~ITextRenderer() = default;

    virtual int load_font(const std::string& path, int pt) = 0;
    virtual std::pair<int,int> measure_utf8(const std::string& text, int font_id) = 0;
    virtual void draw_utf8(
        const std::string& text,
        int x, int y,
        int r, int g, int b, int a,
        int font_id
    ) = 0;
};

} // namespace mini
