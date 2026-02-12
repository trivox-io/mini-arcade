#pragma once
#include <vector>
#include "event.h"
#include "window.h"
#include "renderer.h"

namespace mini {

class Input {
public:
    std::vector<Event> poll(Window& window, IRenderer& renderer);
};

} // namespace mini
