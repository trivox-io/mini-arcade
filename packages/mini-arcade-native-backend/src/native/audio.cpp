#include "mini/audio.h"
#include <SDL.h>
#include <stdexcept>
#include <string>

namespace mini {

    Audio::~Audio() {
        shutdown();
    }

    void Audio::init(int frequency, int channels, int chunk_size) {
        if (initialized_) return;

        if ((SDL_WasInit(SDL_INIT_AUDIO) & SDL_INIT_AUDIO) == 0) {
            if (SDL_InitSubSystem(SDL_INIT_AUDIO) != 0) {
                throw std::runtime_error(std::string("SDL_InitSubSystem(AUDIO) Error: ") + SDL_GetError());
            }
        }

        if (Mix_OpenAudio(frequency, MIX_DEFAULT_FORMAT, channels, chunk_size) != 0) {
            throw std::runtime_error(std::string("Mix_OpenAudio Error: ") + Mix_GetError());
        }

        Mix_AllocateChannels(16);
        Mix_Volume(-1, master_volume_);

        initialized_ = true;
    }

    void Audio::shutdown() {
        if (!initialized_) return;

        stop_all();

        for (auto& kv : sounds_) {
            if (kv.second) Mix_FreeChunk(kv.second);
        }
        sounds_.clear();

        Mix_CloseAudio();
        initialized_ = false;
    }

    void Audio::load_sound(const std::string& id, const std::string& path) {
        if (!initialized_) init();

        if (id.empty()) throw std::runtime_error("load_sound: id is empty");

        auto it = sounds_.find(id);
        if (it != sounds_.end() && it->second) {
            Mix_FreeChunk(it->second);
            it->second = nullptr;
        }

        Mix_Chunk* chunk = Mix_LoadWAV(path.c_str());
        if (!chunk) throw std::runtime_error(std::string("Mix_LoadWAV Error: ") + Mix_GetError());

        sounds_[id] = chunk;
    }

    void Audio::play_sound(const std::string& id, int loops) {
        if (!initialized_) init();
        auto it = sounds_.find(id);
        if (it == sounds_.end() || !it->second) return;
        Mix_PlayChannel(-1, it->second, loops);
    }

    void Audio::set_master_volume(int volume) {
        if (volume < 0) volume = 0;
        if (volume > MIX_MAX_VOLUME) volume = MIX_MAX_VOLUME;
        master_volume_ = volume;
        Mix_Volume(-1, master_volume_);
    }

    void Audio::set_sound_volume(const std::string& id, int volume) {
        if (volume < 0) volume = 0;
        if (volume > MIX_MAX_VOLUME) volume = MIX_MAX_VOLUME;
        auto it = sounds_.find(id);
        if (it == sounds_.end() || !it->second) return;
        Mix_VolumeChunk(it->second, volume);
    }

    void Audio::stop_all() {
        Mix_HaltChannel(-1);
    }

} // namespace mini
