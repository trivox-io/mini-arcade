#pragma once
#include <memory>
#include "config.h"
#include "platform.h"
#include "window.h"
#include "input.h"
#include "renderer.h"
#include "text.h"
#include "audio.h"
#include "capture.h"

namespace mini {

class Backend {
    public:
        explicit Backend(const BackendConfig& cfg);
        ~Backend();

        Backend(const Backend&) = delete;
        Backend& operator=(const Backend&) = delete;

        Window& window() { return window_; }
        Input& input() { return input_; }
        IRenderer& render() { return *renderer_; }
        ITextRenderer& text() { return *text_; }
        Audio& audio() { return audio_; }
        Capture& capture() { return capture_; }

    private:
        Platform platform_;
        Window window_;
        Input input_;
        std::unique_ptr<IRenderer> renderer_;
        std::unique_ptr<ITextRenderer> text_;
        Audio audio_;
        Capture capture_;
};

} // namespace mini
