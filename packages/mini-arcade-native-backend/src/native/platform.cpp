#include "mini/platform.h"
#include <SDL.h>
#include <SDL_ttf.h>
#include <stdexcept>
#include <string>

namespace mini {

    Platform::Platform() {
        if (SDL_Init(SDL_INIT_VIDEO) != 0) {
            throw std::runtime_error(std::string("SDL_Init Error: ") + SDL_GetError());
        }
        if (TTF_Init() != 0) {
            std::string msg = std::string("TTF_Init Error: ") + TTF_GetError();
            SDL_Quit();
            throw std::runtime_error(msg);
        }
        SDL_StartTextInput();
        initialized_ = true;
    }

    Platform::~Platform() {
        SDL_StopTextInput();
        if (initialized_) {
            TTF_Quit();
            SDL_Quit();
            initialized_ = false;
        }
    }

} // namespace mini
