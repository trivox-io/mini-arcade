#include "mini/input.h"
#include <SDL.h>
#include <cmath>

namespace mini {

    static void scale_mouse(
        Window& window,
        IRenderer& renderer,
        int& x, int& y, int& dx, int& dy
    ) {
        auto [ww, wh] = window.size();
        auto [rw, rh] = renderer.drawable_size();

        if (ww > 0 && wh > 0) {
            float sx = (float)rw / (float)ww;
            float sy = (float)rh / (float)wh;
            x  = (int)lroundf(x  * sx);
            y  = (int)lroundf(y  * sy);
            dx = (int)lroundf(dx * sx);
            dy = (int)lroundf(dy * sy);
        }
    }

    std::vector<Event> Input::poll(Window& window, IRenderer& renderer) {
        std::vector<Event> events;
        SDL_Event e;

        while (SDL_PollEvent(&e)) {
            Event ev;

            switch (e.type) {
                case SDL_QUIT:
                    ev.type = EventType::Quit;
                    break;

                case SDL_KEYDOWN:
                    ev.type = EventType::KeyDown;
                    ev.key = e.key.keysym.sym;
                    ev.scancode = (int)e.key.keysym.scancode;
                    ev.mod = (int)e.key.keysym.mod;
                    ev.repeat = (int)e.key.repeat;
                    break;

                case SDL_KEYUP:
                    ev.type = EventType::KeyUp;
                    ev.key = e.key.keysym.sym;
                    ev.scancode = (int)e.key.keysym.scancode;
                    ev.mod = (int)e.key.keysym.mod;
                    ev.repeat = 0;
                    break;

                case SDL_MOUSEMOTION:
                    ev.type = EventType::MouseMotion;
                    ev.x = e.motion.x;
                    ev.y = e.motion.y;
                    ev.dx = e.motion.xrel;
                    ev.dy = e.motion.yrel;
                    scale_mouse(window, renderer, ev.x, ev.y, ev.dx, ev.dy);
                    break;

                case SDL_MOUSEBUTTONDOWN:
                    ev.type = EventType::MouseButtonDown;
                    ev.button = (int)e.button.button;
                    ev.x = e.button.x;
                    ev.y = e.button.y;
                    // scale x/y consistently (important for HiDPI)
                    scale_mouse(window, renderer, ev.x, ev.y, ev.dx, ev.dy);
                    break;

                case SDL_MOUSEBUTTONUP:
                    ev.type = EventType::MouseButtonUp;
                    ev.button = (int)e.button.button;
                    ev.x = e.button.x;
                    ev.y = e.button.y;
                    scale_mouse(window, renderer, ev.x, ev.y, ev.dx, ev.dy);
                    break;

                case SDL_MOUSEWHEEL:
                    ev.type = EventType::MouseWheel;
                    ev.wheel_x = e.wheel.x;
                    ev.wheel_y = e.wheel.y;
                    break;

                case SDL_TEXTINPUT:
                    ev.type = EventType::TextInput;
                    ev.text = e.text.text;
                    break;

                case SDL_WINDOWEVENT:
                    if (e.window.event == SDL_WINDOWEVENT_RESIZED ||
                        e.window.event == SDL_WINDOWEVENT_SIZE_CHANGED) {
                    ev.type = EventType::WindowResized;
                    auto [rw, rh] = renderer.drawable_size();
                    ev.width = rw;
                    ev.height = rh;
            } else {
                continue;
            }
            break;

            default:
                ev.type = EventType::Unknown;
                break;
            }

            events.push_back(std::move(ev));
        }

        return events;
    }

} // namespace mini
