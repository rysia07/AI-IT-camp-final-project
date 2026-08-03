import io
import io
import tempfile
import pygame
from pydub import AudioSegment

class AudioAdapter:
    def __init__(self, freq=44100, size=-16, channels=2, buffer=512, max_channels=32, reserved=4):
        # store config and runtime state
        self.freq = freq
        self.size = size
        self.channels = channels
        self.buffer = buffer
        self.max_channels = max_channels
        self.reserved_count = reserved

        self.sounds = {}               # key -> pygame.mixer.Sound
        self.sound_meta = {}           # key -> metadata (path/segment, volume, etc.)
        self.reserved = set()          # reserved channel indices
        self.master_vol = 1.0

        # do not init mixer here if you prefer manual control; helper below available
    def init_mixer(self):
        # Initialize pygame mixer and allocate channels
        pygame.mixer.pre_init(frequency=self.freq, size=self.size, channels=self.channels, buffer=self.buffer)
        pygame.init()
        pygame.mixer.set_num_channels(self.max_channels)
        for i in range(self.reserved_count):
            self.reserved.add(i)

    def _segment_to_sound(self, seg: AudioSegment) -> pygame.mixer.Sound:
        # Convert pydub AudioSegment to pygame.mixer.Sound via in-memory WAV
        seg = seg.set_frame_rate(self.freq).set_sample_width(2).set_channels(self.channels)
        buf = io.BytesIO()
        seg.export(buf, format="wav")
        buf.seek(0)
        return pygame.mixer.Sound(file=buf)

    def load_sound(self, key, path_or_segment):
        # Load an SFX (from file path or AudioSegment) and store under key
        if isinstance(path_or_segment, AudioSegment):
            snd = self._segment_to_sound(path_or_segment)
            self.sounds[key] = snd
            self.sound_meta[key] = {"source": "segment"}
        else:
            # path string -> let pygame load (pydub optional for processing)
            snd = pygame.mixer.Sound(path_or_segment)
            self.sounds[key] = snd
            self.sound_meta[key] = {"source": path_or_segment}

    def play_sound(self, key, loops=0, vol=1.0, pan=0.0):
        # Play a loaded sound: loops, per-sound volume, and pan (-1..1)
        snd = self.sounds.get(key)
        if not snd:
            return None
        ch = pygame.mixer.find_channel()
        if ch is None:
            return None
        # apply volume and panning
        left = max(0.0, min(1.0, (1 - pan) / 2))
        right = max(0.0, min(1.0, (1 + pan) / 2))
        ch.set_volume(self.master_vol * vol * left, self.master_vol * vol * right)
        ch.play(snd, loops=loops)
        return ch

    def stop_sound(self, channel=None, key=None):
        # Stop playback by channel or by key (stops channels playing that Sound)
        if channel:
            channel.stop()
            return
        if key:
            target = self.sounds.get(key)
            if not target:
                return
            for i in range(self.max_channels):
                ch = pygame.mixer.Channel(i)
                if ch.get_sound() == target:
                    ch.stop()

    def play_music(self, path_or_segment, loops=-1, start=0.0, fade_ms=0):
        # Play (stream) background music; if segment provided, export to temp WAV first
        if isinstance(path_or_segment, AudioSegment):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            seg = path_or_segment.set_frame_rate(self.freq).set_sample_width(2).set_channels(self.channels)
            seg.export(tmp.name, format="wav")
            tmp.close()  # Close file before pygame loads
            pygame.mixer.music.load(tmp.name)
        else:
            pygame.mixer.music.load(path_or_segment)
        pygame.mixer.music.play(loops=loops, start=start, fade_ms=fade_ms)
        pygame.mixer.music.set_volume(self.master_vol)

    def stop_music(self, fade_ms=0):
        # Stop or fade out music
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()

    def fadeout_music(self, ms):
        # Convenience for fading out music
        pygame.mixer.music.fadeout(ms)

    def set_volume(self, key_or_channel, vol: float):
        # Set volume for a stored sound (affects new plays) or a channel (current)
        if isinstance(key_or_channel, str):
            snd = self.sounds.get(key_or_channel)
            if snd:
                snd.set_volume(vol)
                self.sound_meta[key_or_channel]["volume"] = vol
        else:
            # assume channel object / index
            if isinstance(key_or_channel, int):
                ch = pygame.mixer.Channel(key_or_channel)
            else:
                ch = key_or_channel
            # set both left/right equally (no pan change)
            ch.set_volume(vol, vol)

    def master_volume(self, vol: float):
        # Set master volume (applies to music and future channel volumes multiplicatively)
        self.master_vol = vol
        pygame.mixer.music.set_volume(vol)
        # Existing channels must be adjusted manually if needed

    def set_panning(self, channel_or_key, pan: float):
        # Set panning for a channel or for all current channels playing a key
        left = max(0.0, min(1.0, (1 - pan) / 2))
        right = max(0.0, min(1.0, (1 + pan) / 2))
        if isinstance(channel_or_key, str):
            snd = self.sounds.get(channel_or_key)
            if not snd:
                return
            for i in range(self.max_channels):
                ch = pygame.mixer.Channel(i)
                if ch.get_sound() == snd:
                    ch.set_volume(self.master_vol * left, self.master_vol * right)
        else:
            if isinstance(channel_or_key, int):
                ch = pygame.mixer.Channel(channel_or_key)
            else:
                ch = channel_or_key
            ch.set_volume(self.master_vol * left, self.master_vol * right)

    def reserve_channel(self, idx):
        # Reserve a channel index so find_channel skips it
        self.reserved.add(idx)

    def release_channel(self, idx):
        # Release a reserved channel
        self.reserved.discard(idx)

    def cleanup(self):
        # Stop everything and quit mixer
        pygame.mixer.music.stop()
        for i in range(self.max_channels):
            pygame.mixer.Channel(i).stop()
        pygame.mixer.quit()