#pragma once
#include <SDL_mixer.h>
#include <string>
#include <unordered_map>

namespace mini {

class Audio {
public:
    Audio() = default;
    ~Audio();

    Audio(const Audio&) = delete;
    Audio& operator=(const Audio&) = delete;

    void init(int frequency=44100, int channels=2, int chunk_size=2048);
    void shutdown();

    void load_sound(const std::string& id, const std::string& path);
    void play_sound(const std::string& id, int loops=0);

    void set_master_volume(int volume); // 0..128
    void set_sound_volume(const std::string& id, int volume); // 0..128
    void stop_all();

    bool initialized() const { return initialized_; }

    private:
        bool initialized_ = false;
        int master_volume_ = MIX_MAX_VOLUME;
        std::unordered_map<std::string, Mix_Chunk*> sounds_;
};

} // namespace mini
