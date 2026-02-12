#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "mini/backend.h"
#include "mini/sdl_renderer.h" // only for types if needed
#include "mini/event.h"
#include "mini/config.h"
#include "mini/capture_bytes.h"

namespace py = pybind11;
using namespace mini;

PYBIND11_MODULE(_native, m) {
    m.doc() = "Mini Arcade native backend (SDL2 today, OpenGL-ready design)";

    py::enum_<EventType>(m, "EventType")
        .value("Unknown", EventType::Unknown)
        .value("Quit", EventType::Quit)
        .value("KeyDown", EventType::KeyDown)
        .value("KeyUp", EventType::KeyUp)
        .value("MouseMotion", EventType::MouseMotion)
        .value("MouseButtonDown", EventType::MouseButtonDown)
        .value("MouseButtonUp", EventType::MouseButtonUp)
        .value("MouseWheel", EventType::MouseWheel)
        .value("WindowResized", EventType::WindowResized)
        .value("TextInput", EventType::TextInput)
        .export_values();

    py::class_<Event>(m, "Event")
        .def_readonly("type", &Event::type)
        .def_readonly("key", &Event::key)
        .def_readonly("scancode", &Event::scancode)
        .def_readonly("mod", &Event::mod)
        .def_readonly("repeat", &Event::repeat)
        .def_readonly("x", &Event::x)
        .def_readonly("y", &Event::y)
        .def_readonly("dx", &Event::dx)
        .def_readonly("dy", &Event::dy)
        .def_readonly("button", &Event::button)
        .def_readonly("wheel_x", &Event::wheel_x)
        .def_readonly("wheel_y", &Event::wheel_y)
        .def_readonly("width", &Event::width)
        .def_readonly("height", &Event::height)
        .def_readonly("text", &Event::text);

    py::enum_<RenderAPI>(m, "RenderAPI")
        .value("SDL2", RenderAPI::SDL2)
        .value("OpenGL", RenderAPI::OpenGL)
        .export_values();

    py::class_<WindowConfig>(m, "WindowConfig")
        .def(py::init<>())
        .def_readwrite("width", &WindowConfig::width)
        .def_readwrite("height", &WindowConfig::height)
        .def_readwrite("title", &WindowConfig::title)
        .def_readwrite("resizable", &WindowConfig::resizable)
        .def_readwrite("high_dpi", &WindowConfig::high_dpi);

    py::class_<ColorRGBA>(m, "ColorRGBA")
        .def(py::init<>())
        .def_readwrite("r", &ColorRGBA::r)
        .def_readwrite("g", &ColorRGBA::g)
        .def_readwrite("b", &ColorRGBA::b)
        .def_readwrite("a", &ColorRGBA::a);


    py::class_<RenderConfig>(m, "RenderConfig")
        .def(py::init<>())
        .def_readwrite("api", &RenderConfig::api)
        .def_readwrite("clear_color", &RenderConfig::clear_color);

    py::class_<TextConfig>(m, "TextConfig")
        .def(py::init<>())
        .def_readwrite("default_font_path", &TextConfig::default_font_path)
        .def_readwrite("default_font_size", &TextConfig::default_font_size);

    py::class_<AudioConfig>(m, "AudioConfig")
        .def(py::init<>())
        .def_readwrite("enabled", &AudioConfig::enabled)
        .def_readwrite("frequency", &AudioConfig::frequency)
        .def_readwrite("channels", &AudioConfig::channels)
        .def_readwrite("chunk_size", &AudioConfig::chunk_size);

    py::class_<BackendConfig>(m, "BackendConfig")
        .def(py::init<>())
        .def_readwrite("window", &BackendConfig::window)
        .def_readwrite("render", &BackendConfig::render)
        .def_readwrite("text", &BackendConfig::text)
        .def_readwrite("audio", &BackendConfig::audio)
        .def_readwrite("sounds", &BackendConfig::sounds);

    // Subsystems: bind minimal methods
    py::class_<Window>(m, "Window")
        .def("set_title", &Window::set_title)
        .def("resize", &Window::resize)
        .def("size", &Window::size)
        .def("drawable_size", &Window::drawable_size);

    py::class_<Audio>(m, "Audio")
        .def("init", &Audio::init, py::arg("frequency")=44100, py::arg("channels")=2, py::arg("chunk_size")=2048)
        .def("shutdown", &Audio::shutdown)
        .def("load_sound", &Audio::load_sound)
        .def("play_sound", &Audio::play_sound, py::arg("id"), py::arg("loops")=0)
        .def("set_master_volume", &Audio::set_master_volume)
        .def("set_sound_volume", &Audio::set_sound_volume)
        .def("stop_all", &Audio::stop_all);

    py::class_<Input>(m, "Input")
        // NOTE: poll needs window+renderer, but backend.input.poll() is what you want,
        // so we expose polling on Backend instead (below).
        ;

    // Renderer interface: expose a concrete minimal surface (we bind through Backend methods)
    // Text: expose via Backend too.

    py::class_<Capture>(m, "Capture")
        // same: use Backend.capture_frame() wrapper; but you can expose this later.
        ;

    // Backend: user entry-point
    py::class_<Backend>(m, "Backend")
        .def(py::init<const BackendConfig&>(), py::arg("config"))

        .def_property_readonly("window", &Backend::window, py::return_value_policy::reference_internal)
        .def_property_readonly("audio", &Backend::audio, py::return_value_policy::reference_internal)

        // Render wrappers
        .def("set_clear_color", [](Backend& b, int r,int g,int bb) {
            b.render().set_clear_color(ColorRGBA{
                (uint8_t)r,(uint8_t)g,(uint8_t)bb,255
            });
        })
        .def("begin_frame", [](Backend& b){ b.render().begin_frame(); })
        .def("end_frame", [](Backend& b){ b.render().end_frame(); })
        .def("draw_rect", [](Backend& b,int x,int y,int w,int h,int r,int g,int bb,int a){
            b.render().draw_rect(x,y,w,h, ColorRGBA{(uint8_t)r,(uint8_t)g,(uint8_t)bb,(uint8_t)a});
        })
        .def("draw_line", [](Backend& b,int x1,int y1,int x2,int y2,int r,int g,int bb,int a){
            b.render().draw_line(x1,y1,x2,y2, ColorRGBA{(uint8_t)r,(uint8_t)g,(uint8_t)bb,(uint8_t)a});
        })
        .def("set_clip_rect", [](Backend& b,int x,int y,int w,int h){
            b.render().set_clip_rect(x,y,w,h);
        })
        .def("clear_clip_rect", [](Backend& b){
            b.render().clear_clip_rect();
        })
        .def("create_texture_rgba",
            [](Backend& b, int w, int h, py::buffer data, int pitch) -> int {
                py::buffer_info info = data.request();

                // Expect a flat uint8 buffer
                if (info.ndim != 1) {
                    throw std::runtime_error("create_texture_rgba: expected 1D bytes buffer");
                }
                if (info.itemsize != 1) {
                    throw std::runtime_error("create_texture_rgba: expected uint8 buffer");
                }

                const std::size_t expected = static_cast<std::size_t>(h) * static_cast<std::size_t>(pitch);
                if (static_cast<std::size_t>(info.size) < expected) {
                    throw std::runtime_error("create_texture_rgba: buffer too small for h*pitch");
                }

                return static_cast<int>(
                    b.render().create_texture_rgba(w, h, info.ptr, pitch)
                );
            },
            py::arg("width"),
            py::arg("height"),
            py::arg("data"),
            py::arg("pitch") = -1
        )

        .def("destroy_texture",
            [](Backend& b, int texture_id) {
                b.render().destroy_texture(static_cast<TextureHandle>(texture_id));
            },
            py::arg("texture_id")
        )

        .def("draw_texture",
            [](Backend& b, int texture_id, int x, int y, int w, int h) {
                b.render().draw_texture(static_cast<TextureHandle>(texture_id), x, y, w, h);
            },
            py::arg("texture_id"),
            py::arg("x"),
            py::arg("y"),
            py::arg("width"),
            py::arg("height")
        )

        .def("draw_texture_tiled_y",
            [](Backend& b, int texture_id, int x, int y, int w, int h) {
                b.render().draw_texture_tiled_y(
                    static_cast<TextureHandle>(texture_id), x, y, w, h
                );
            },
            py::arg("texture_id"),
            py::arg("x"),
            py::arg("y"),
            py::arg("width"),
            py::arg("height")
        )


        // Text wrappers
        .def("load_font", [](Backend& b, const std::string& path, int pt){
            return b.text().load_font(path, pt);
        })
        .def("measure_text", [](Backend& b, const std::string& text, int font_id){
            return b.text().measure_utf8(text, font_id);
        }, py::arg("text"), py::arg("font_id")=-1)
        .def("draw_text", [](Backend& b, const std::string& text,int x,int y,int r,int g,int bb,int a,int font_id){
            b.text().draw_utf8(text, x,y, r,g,bb,a, font_id);
        }, py::arg("text"), py::arg("x"), py::arg("y"), py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a"), py::arg("font_id")=-1)

        // Events
        .def("poll_events", [](Backend& b){
            return b.input().poll(b.window(), b.render());
        })

        // Capture
        .def("capture_bmp", [](Backend& b, const std::string& path){
            return b.capture().save_bmp(b.render(), path);
        })
        .def("capture_argb8888_bytes", [](Backend& b){
            PixelBuffer pb = mini::capture_argb8888(b.render());
            return py::make_tuple(pb.w, pb.h, py::bytes(
                reinterpret_cast<const char*>(pb.bytes.data()),
                pb.bytes.size()
            ));
        });
}
