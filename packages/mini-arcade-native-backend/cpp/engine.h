#pragma once

#include <SDL.h>
#include <SDL_ttf.h>
#include <SDL_mixer.h>
#include <unordered_map>
#include <vector>
#include <string>
#include <utility>

// A minimal 2D graphics engine binding for Python using SDL.
namespace mini {

    // We define our own event types so Python doesn't need to know about SDL constants.
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

    // A simple event structure to pass events to Python.
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
        int dx = 0;        // motion relative
        int dy = 0;
        int button = 0;    // SDL_BUTTON_LEFT etc.
        int wheel_x = 0;
        int wheel_y = 0;

        // Window
        int width = 0;
        int height = 0;

        // Text input
        std::string text;
    };

    // The main engine class that wraps SDL functionality.
    class Engine {
    public:
        Engine();
        ~Engine();

        // Initialize the engine with a window of given width, height, and title.
        void init(int width, int height, const char* title);

        // Set the window title.
        void set_window_title(const char* title);

        // Set the clear color for the screen.
        void set_clear_color(int r, int g, int b);

        // Clear the screen to a default color (black) and get ready to draw.
        void begin_frame();

        // Present what has been drawn.
        void end_frame();

        // Draw a simple filled rectangle (we'll use a fixed color for now).
        void draw_rect(int x, int y, int w, int h, int r, int g, int b, int a);

        // Sprite drawing stub for later.
        void draw_sprite(int texture_id, int x, int y, int w, int h);

        // Poll all pending events and return them.
        std::vector<Event> poll_events();
        
        // Load a TTF font from file at specified point size.
        int load_font(const char* path, int pt_size);

        // Draw text at specified position.
        void draw_text(const char* text, int x, int y, int r, int g, int b, int a, int font_id = -1);

        // Capture the current frame into an image file (BMP for now).
        // Returns true on success, false on failure.
        bool capture_frame(const char* path);

        // Measure text (UTF-8) using a loaded font.
        // Returns (width, height) in pixels. Returns (0,0) if no valid font or error.
        std::pair<int, int> measure_text(const char* text, int font_id = -1);

        // --- Audio ---
        // Initialize audio subsystem.
        void init_audio(int frequency = 44100, int channels = 2, int chunk_size = 2048);
        // Shutdown audio subsystem.
        void shutdown_audio();

        // Load, play, and manage sounds.
        void load_sound(const std::string& sound_id, const std::string& path);
        // Play a loaded sound by its ID.
        void play_sound(const std::string& sound_id, int loops = 0);
        // Set the volume for a specific sound (0..128).
        void set_sound_volume(const std::string& sound_id, int volume); // 0..128
        // Set the master volume for all sounds (0..128).
        void set_master_volume(int volume); // 0..128
        // Stop all currently playing sounds.
        void stop_all_sounds();

        // Resize the application window.
        void resize_window(int width, int height);
        // Set clipping rectangle for rendering.
        void set_clip_rect(int x, int y, int w, int h);
        // Clear clipping rectangle (disable clipping).
        void clear_clip_rect();

        // Draw a line from (x1, y1) to (x2, y2) with specified color.
        void draw_line(int x1, int y1, int x2, int y2, int r, int g, int b, int a);

    private:
        SDL_Window* window_; // The main application window.
        SDL_Renderer* renderer_; // The renderer for drawing.
        bool initialized_; // Whether the engine has been initialized.
        SDL_Color clear_color_; // The clear color for the screen.
        std::vector<TTF_Font*> fonts_; // Loaded fonts.
        int default_font_id_; // Default font index.
        int default_alpha_; // Default alpha value for drawing.
        bool audio_initialized_ = false; // Whether audio subsystem is initialized.
        int master_volume_ = MIX_MAX_VOLUME; // 128 is max volume
        std::unordered_map<std::string, Mix_Chunk*> sounds_; // Audio data
    };

} // namespace mini
