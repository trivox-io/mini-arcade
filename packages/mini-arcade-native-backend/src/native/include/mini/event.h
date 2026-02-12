#pragma once
#include <string>

namespace mini {

enum class EventType {
    Unknown = 0,
    Quit,
    KeyDown,
    KeyUp,
    MouseMotion,
    MouseButtonDown,
    MouseButtonUp,
    MouseWheel,
    WindowResized,
    TextInput
};

struct Event {
    EventType type = EventType::Unknown;

    // Keyboard
    int key = 0;       // SDL_Keycode
    int scancode = 0;  // SDL_Scancode
    int mod = 0;       // SDL_Keymod bitmask
    int repeat = 0;    // 1 if key repeat, else 0

    // Mouse
    int x = 0;
    int y = 0;
    int dx = 0;
    int dy = 0;
    int button = 0;
    int wheel_x = 0;
    int wheel_y = 0;

    // Window
    int width = 0;
    int height = 0;

    // Text input
    std::string text;
};

} // namespace mini
