#pragma once
#include <string>
#include "renderer.h"

namespace mini {

class Capture {
public:
    bool save_bmp(IRenderer& renderer, const std::string& path);
};

} // namespace mini
