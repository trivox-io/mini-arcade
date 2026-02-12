#pragma once
#include <string>
#include <unordered_map>
#include "color.h"

namespace mini {

enum class RenderAPI { SDL2, OpenGL };

struct WindowConfig {
    int width = 1280;
    int height = 720;
    std::string title = "";
    bool resizable = true;
    bool high_dpi = true;
};

struct RenderConfig {
    RenderAPI api = RenderAPI::SDL2;
    ColorRGBA clear_color = {0,0,0,255};
};

struct TextConfig {
    std::string default_font_path = ""; // empty => text no-op
    int default_font_size = 24;
};

struct AudioConfig {
    bool enabled = false;
    int frequency = 44100;
    int channels = 2;
    int chunk_size = 2048;
};

struct BackendConfig {
    WindowConfig window;
    RenderConfig render;
    TextConfig text;
    AudioConfig audio;

    // Optional “auto-load sounds” convenience
    std::unordered_map<std::string, std::string> sounds; // id -> path
};

} // namespace mini
