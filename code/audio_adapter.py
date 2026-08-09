import pygame
import os
from typing import Optional, Callable, Dict
from dataclasses import dataclass
from enum import Enum


# =========================================================
# AUDIO STATE
# =========================================================

class AudioState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2


# =========================================================
# FADE CONFIG
# =========================================================

@dataclass
class FadeConfig:
    duration: int
    target_volume: float
    start_volume: float = 0.0


# =========================================================
# AUDIO ADAPTER
# =========================================================

class AudioAdapter:
    """
    System audio gry.

    Obsługuje:

        STARE API:
            audio.load(...)
            audio.play(...)
            audio.pause(...)
            audio.unpause()
            audio.stop()
            audio.set_volume(...)

        MUZYKĘ:
            play_music(...)
            play_level_music(...)
            stop_music(...)
            pause_music()
            resume_music()

        EFEKTY:
            load_sound(...)
            play_sound(...)
            stop_sound(...)

        GŁOŚNOŚĆ:
            master_volume
            music_volume
            sfx_volume

        DODATKOWO:
            fade in/out
            automatyczna muzyka leveli
            callback końca muzyki
    """

    SUPPORTED_FORMATS = {
        ".flac",
        ".mp3",
        ".wav",
        ".ogg"
    }

    def __init__(
        self,
        frequency: int = 44100,
        size: int = -16,
        channels: int = 2,
        buffer: int = 512,
        max_channels: int = 16
    ):

        # =====================================================
        # MIXER
        # =====================================================

        if not pygame.mixer.get_init():

            pygame.mixer.init(
                frequency=frequency,
                size=size,
                channels=channels,
                buffer=buffer
            )

        pygame.mixer.set_num_channels(
            max_channels
        )

        # =====================================================
        # STARE API / SOUND
        # =====================================================

        self.current_sound: Optional[
            pygame.mixer.Sound
        ] = None

        self.current_channel: Optional[
            pygame.mixer.Channel
        ] = None

        self.state = AudioState.STOPPED

        self.current_file: Optional[str] = None

        self.current_volume = 1.0

        # =====================================================
        # MUZYKA
        # =====================================================

        self.current_music: Optional[str] = None

        self.music_state = AudioState.STOPPED

        self.music_volume = 0.5

        # =====================================================
        # MASTER
        # =====================================================

        self.master_volume = 1.0

        # =====================================================
        # SFX
        # =====================================================

        self.sounds: Dict[
            str,
            pygame.mixer.Sound
        ] = {}

        self.sfx_volume = 0.8

        # =====================================================
        # FADE
        # =====================================================

        self.fade_config: Optional[
            FadeConfig
        ] = None

        self.fade_start_time = 0

        # =====================================================
        # CALLBACKI
        # =====================================================

        self.on_end_callback: Optional[
            Callable
        ] = None

        self.on_music_end: Optional[
            Callable
        ] = None

    # =========================================================
    # VOLUME
    # =========================================================

    def set_master_volume(
        self,
        volume: float
    ):

        self.master_volume = max(
            0.0,
            min(1.0, float(volume))
        )

        self._update_music_volume()

        # Aktualizujemy również aktualny efekt
        if self.current_channel:
            self.current_channel.set_volume(
                self.master_volume
                * self.current_volume
            )

    def get_master_volume(self) -> float:

        return self.master_volume

    # ---------------------------------------------------------

    def set_music_volume(
        self,
        volume: float
    ):

        self.music_volume = max(
            0.0,
            min(1.0, float(volume))
        )

        self._update_music_volume()

    def get_music_volume(self) -> float:

        return self.music_volume

    # ---------------------------------------------------------

    def set_sfx_volume(
        self,
        volume: float
    ):

        self.sfx_volume = max(
            0.0,
            min(1.0, float(volume))
        )

    def get_sfx_volume(self) -> float:

        return self.sfx_volume

    # =========================================================
    # MUSIC VOLUME
    # =========================================================

    def _update_music_volume(self):

        volume = (
            self.master_volume
            * self.music_volume
        )

        pygame.mixer.music.set_volume(
            max(
                0.0,
                min(1.0, volume)
            )
        )

    # =========================================================
    # STARE API
    # LOAD
    # =========================================================

    def load(
        self,
        file_path: str
    ) -> bool:
        """
        Stare API:

            audio.load("music.wav")

        Ładuje plik jako Sound.

        Dzięki temu stary kod nadal działa.
        """

        if not os.path.exists(file_path):

            raise FileNotFoundError(
                f"Audio file not found: {file_path}"
            )

        ext = os.path.splitext(
            file_path
        )[1].lower()

        if ext not in self.SUPPORTED_FORMATS:

            raise ValueError(
                f"Unsupported format: {ext}. "
                f"Supported: {self.SUPPORTED_FORMATS}"
            )

        try:

            self.current_sound = (
                pygame.mixer.Sound(
                    file_path
                )
            )

            self.current_file = file_path

            self.state = AudioState.STOPPED

            self.current_volume = 1.0

            self.fade_config = None

            return True

        except pygame.error as error:

            raise RuntimeError(
                f"Failed to load audio file: {error}"
            )

    # =========================================================
    # STARE API
    # PLAY
    # =========================================================

    def play(
        self,
        loops: int = 0
    ):
        """
        Stare API:

            audio.load("music.wav")
            audio.play(loops=-1)
        """

        if not self.current_sound:

            raise RuntimeError(
                "No audio file loaded. "
                "Call load() first."
            )

        if (
            self.state == AudioState.PAUSED
            and self.current_channel
        ):

            self.current_channel.unpause()

        else:

            self.current_channel = (
                self.current_sound.play(
                    loops=loops
                )
            )

        if self.current_channel:

            self.current_channel.set_volume(
                self.master_volume
                * self.current_volume
            )

        self.state = AudioState.PLAYING

        self.fade_config = None

        return self.current_channel

    # =========================================================
    # STARE API
    # PAUSE
    # =========================================================

    def pause(self):

        if (
            self.state == AudioState.PLAYING
            and self.current_channel
        ):

            self.current_channel.pause()

            self.state = AudioState.PAUSED

    # =========================================================
    # STARE API
    # UNPAUSE
    # =========================================================

    def unpause(self):

        if (
            self.state == AudioState.PAUSED
            and self.current_channel
        ):

            self.current_channel.unpause()

            self.state = AudioState.PLAYING

    # =========================================================
    # STARE API
    # STOP
    # =========================================================

    def stop(self):

        if self.current_channel:

            self.current_channel.stop()

        self.state = AudioState.STOPPED

        self.fade_config = None

    # =========================================================
    # STARE API
    # VOLUME
    # =========================================================

    def set_volume(
        self,
        volume: float
    ):

        volume = max(
            0.0,
            min(1.0, float(volume))
        )

        self.current_volume = volume

        if self.current_channel:

            self.current_channel.set_volume(
                self.master_volume
                * volume
            )

    # =========================================================
    # GET VOLUME
    # =========================================================

    def get_volume(self) -> float:

        return self.current_volume

    # =========================================================
    # MUSIC
    # =========================================================

    def play_music(
        self,
        file_path: str,
        loops: int = -1,
        fade_ms: int = 500
    ) -> bool:

        if not os.path.exists(file_path):

            print(
                f"⚠️ Nie znaleziono muzyki: "
                f"{file_path}"
            )

            return False

        ext = os.path.splitext(
            file_path
        )[1].lower()

        if ext not in self.SUPPORTED_FORMATS:

            print(
                f"⚠️ Nieobsługiwany format muzyki: "
                f"{ext}"
            )

            return False

        # Ten sam utwór już gra
        if (
            self.current_music == file_path
            and pygame.mixer.music.get_busy()
        ):

            return True

        try:

            pygame.mixer.music.load(
                file_path
            )

            self.current_music = file_path

            self._update_music_volume()

            pygame.mixer.music.play(
                loops=loops,
                fade_ms=max(0, fade_ms)
            )

            self.music_state = (
                AudioState.PLAYING
            )

            return True

        except pygame.error as error:

            print(
                f"❌ Nie udało się odtworzyć "
                f"muzyki: {error}"
            )

            return False

    # =========================================================
    # MUSIC LEVEL
    # =========================================================

    def play_level_music(
        self,
        level_filename: str,
        music_directory: str = "../audio/music",
        fade_ms: int = 700
    ) -> bool:
        """
        Przykład:

            level1.txt
            -> ../audio/music/level1.wav

            level2.txt
            -> ../audio/music/level2.wav

        Sprawdzane są:
            .ogg
            .mp3
            .wav
            .flac
        """

        level_name = os.path.splitext(
            os.path.basename(level_filename)
        )[0]

        extensions = [
            ".ogg",
            ".mp3",
            ".wav",
            ".flac"
        ]

        for extension in extensions:

            path = os.path.join(
                music_directory,
                level_name + extension
            )

            if os.path.exists(path):

                return self.play_music(
                    path,
                    loops=-1,
                    fade_ms=fade_ms
                )

        print(
            f"⚠️ Nie znaleziono muzyki dla "
            f"poziomu: {level_filename}"
        )

        return False

    # =========================================================
    # STOP MUSIC
    # =========================================================

    def stop_music(
        self,
        fade_ms: int = 500
    ):

        if not pygame.mixer.music.get_busy():

            self.music_state = (
                AudioState.STOPPED
            )

            self.current_music = None

            return

        if fade_ms > 0:

            pygame.mixer.music.fadeout(
                fade_ms
            )

        else:

            pygame.mixer.music.stop()

        self.music_state = (
            AudioState.STOPPED
        )

        self.current_music = None

    # =========================================================
    # PAUSE MUSIC
    # =========================================================

    def pause_music(self):

        if (
            self.music_state
            == AudioState.PLAYING
        ):

            pygame.mixer.music.pause()

            self.music_state = (
                AudioState.PAUSED
            )

    # =========================================================
    # RESUME MUSIC
    # =========================================================

    def resume_music(self):

        if (
            self.music_state
            == AudioState.PAUSED
        ):

            pygame.mixer.music.unpause()

            self.music_state = (
                AudioState.PLAYING
            )

    # =========================================================
    # SFX LOAD
    # =========================================================

    def load_sound(
        self,
        name: str,
        file_path: str
    ) -> bool:

        if not os.path.exists(file_path):

            print(
                f"⚠️ Nie znaleziono efektu: "
                f"{file_path}"
            )

            return False

        try:

            sound = pygame.mixer.Sound(
                file_path
            )

            self.sounds[name] = sound

            return True

        except pygame.error as error:

            print(
                f"❌ Nie udało się załadować "
                f"efektu {name}: {error}"
            )

            return False

    # =========================================================
    # PLAY SFX
    # =========================================================

    def play_sound(
        self,
        name: str,
        volume: float = 1.0
    ):

        sound = self.sounds.get(
            name
        )

        if sound is None:

            print(
                f"⚠️ Nie załadowano dźwięku: "
                f"{name}"
            )

            return None

        final_volume = (
            self.master_volume
            * self.sfx_volume
            * max(
                0.0,
                min(1.0, volume)
            )
        )

        channel = sound.play()

        if channel:

            channel.set_volume(
                final_volume
            )

        return channel

    # =========================================================
    # STOP SFX
    # =========================================================

    def stop_sound(
        self,
        name: str
    ):

        sound = self.sounds.get(
            name
        )

        if sound:

            sound.stop()

    # =========================================================
    # STOP ALL SFX
    # =========================================================

    def stop_all_sounds(self):

        for sound in self.sounds.values():

            sound.stop()

    # =========================================================
    # PAUSE ALL
    # =========================================================

    def pause_all(self):

        pygame.mixer.pause()

        self.music_state = (
            AudioState.PAUSED
        )

        if self.current_channel:

            self.state = AudioState.PAUSED

    # =========================================================
    # RESUME ALL
    # =========================================================

    def resume_all(self):

        pygame.mixer.unpause()

        if pygame.mixer.music.get_busy():

            self.music_state = (
                AudioState.PLAYING
            )

        if self.current_channel:

            self.state = AudioState.PLAYING

    # =========================================================
    # STOP EVERYTHING
    # =========================================================

    def stop_all(self):

        pygame.mixer.music.stop()

        self.stop_all_sounds()

        if self.current_channel:

            self.current_channel.stop()

        self.music_state = (
            AudioState.STOPPED
        )

        self.state = AudioState.STOPPED

        self.current_music = None

        self.fade_config = None

    # =========================================================
    # FADE IN - STARE API
    # =========================================================

    def fade_in(
        self,
        duration: int
    ):

        if not self.current_sound:

            raise RuntimeError(
                "No audio file loaded."
            )

        self.current_channel = (
            self.current_sound.play(
                loops=-1
            )
        )

        if not self.current_channel:

            return

        self.current_channel.set_volume(
            0.0
        )

        self.fade_config = FadeConfig(
            duration=max(1, duration),
            target_volume=self.current_volume,
            start_volume=0.0
        )

        self.fade_start_time = (
            pygame.time.get_ticks()
        )

        self.state = AudioState.PLAYING

    # =========================================================
    # FADE OUT - STARE API
    # =========================================================

    def fade_out(
        self,
        duration: int
    ):

        if (
            self.state != AudioState.PLAYING
            or not self.current_channel
        ):

            raise RuntimeError(
                "No audio currently playing."
            )

        self.fade_config = FadeConfig(
            duration=max(1, duration),
            target_volume=0.0,
            start_volume=self.current_volume
        )

        self.fade_start_time = (
            pygame.time.get_ticks()
        )

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self):

        # -----------------------------------------------------
        # STARE API FADE
        # -----------------------------------------------------

        if (
            self.fade_config
            and self.current_channel
        ):

            elapsed = (
                pygame.time.get_ticks()
                - self.fade_start_time
            )

            progress = min(
                elapsed
                / self.fade_config.duration,
                1.0
            )

            start = (
                self.fade_config.start_volume
            )

            target = (
                self.fade_config.target_volume
            )

            volume = (
                start
                + (target - start)
                * progress
            )

            self.current_channel.set_volume(
                self.master_volume
                * max(
                    0.0,
                    min(1.0, volume)
                )
            )

            if progress >= 1.0:

                target_volume = target

                self.fade_config = None

                if target_volume == 0.0:

                    self.stop()

        # -----------------------------------------------------
        # STARE API KONIEC SOUND
        # -----------------------------------------------------

        if (
            self.state == AudioState.PLAYING
            and self.current_channel
            and not self.current_channel.get_busy()
        ):

            self.state = AudioState.STOPPED

            if self.on_end_callback:

                self.on_end_callback()

        # -----------------------------------------------------
        # KONIEC MUZYKI
        # -----------------------------------------------------

        if (
            self.music_state
            == AudioState.PLAYING
            and not pygame.mixer.music.get_busy()
        ):

            self.music_state = (
                AudioState.STOPPED
            )

            if self.on_music_end:

                self.on_music_end()

    # =========================================================
    # STATE
    # =========================================================

    def is_playing(self) -> bool:

        return (
            self.state
            == AudioState.PLAYING
        )

    def is_paused(self) -> bool:

        return (
            self.state
            == AudioState.PAUSED
        )

    def get_state(self) -> AudioState:

        return self.state

    def get_loaded_file(
        self
    ) -> Optional[str]:

        return self.current_file

    def get_busy(self) -> bool:

        return (
            self.current_channel is not None
            and self.current_channel.get_busy()
        )

    def is_music_playing(self) -> bool:

        return (
            self.music_state
            == AudioState.PLAYING
        )

    def is_music_paused(self) -> bool:

        return (
            self.music_state
            == AudioState.PAUSED
        )

    def get_current_music(self):

        return self.current_music

    # =========================================================
    # CALLBACKI
    # =========================================================

    def set_on_end_callback(
        self,
        callback: Callable
    ):

        self.on_end_callback = callback

    def set_on_music_end(
        self,
        callback: Callable
    ):

        self.on_music_end = callback

    # =========================================================
    # QUIT
    # =========================================================

    def quit(self):

        self.stop_all()

        self.sounds.clear()

        if pygame.mixer.get_init():

            pygame.mixer.quit()


# =========================================================
# AUDIO MANAGER
# =========================================================

class AudioManager:
    """
    Kompatybilny manager audio.

    Możesz mieć jeden adapter:

        audio_manager = AudioManager()
        audio = audio_manager.create_adapter("main")

    albo kilka adapterów.
    """

    def __init__(
        self,
        max_channels: int = 16
    ):

        self.adapters = {}

        self.max_channels = (
            max_channels
        )

        if not pygame.mixer.get_init():

            pygame.mixer.init()

        pygame.mixer.set_num_channels(
            max_channels
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create_adapter(
        self,
        adapter_id: str
    ) -> AudioAdapter:

        if adapter_id in self.adapters:

            raise ValueError(
                f"Adapter '{adapter_id}' "
                f"already exists."
            )

        adapter = AudioAdapter(
            max_channels=self.max_channels
        )

        self.adapters[
            adapter_id
        ] = adapter

        return adapter

    # =====================================================
    # GET
    # =====================================================

    def get_adapter(
        self,
        adapter_id: str
    ) -> Optional[AudioAdapter]:

        return self.adapters.get(
            adapter_id
        )

    # =====================================================
    # REMOVE
    # =====================================================

    def remove_adapter(
        self,
        adapter_id: str
    ):

        if adapter_id in self.adapters:

            adapter = self.adapters[
                adapter_id
            ]

            def stop_all(self):
                """Zatrzymuje całe audio, jeśli mixer jest aktywny."""

                if not pygame.mixer.get_init():
                    return

                pygame.mixer.music.stop()

                self.stop_all_sounds()

                if self.current_channel:
                    self.current_channel.stop()

                self.music_state = AudioState.STOPPED
                self.state = AudioState.STOPPED

                self.current_music = None
                self.fade_config = None

    # =====================================================
    # UPDATE
    # =====================================================

    def update_all(self):

        for adapter in (
            self.adapters.values()
        ):

            adapter.update()

    # =====================================================
    # STOP
    # =====================================================

    def stop_all(self):

        for adapter in (
            self.adapters.values()
        ):

            adapter.stop_all()

    # =====================================================
    # PAUSE
    # =====================================================

    def pause_all(self):

        for adapter in (
            self.adapters.values()
        ):

            adapter.pause_all()

    # =====================================================
    # RESUME
    # =====================================================

    def resume_all(self):

        for adapter in (
            self.adapters.values()
        ):

            adapter.resume_all()

    # =====================================================
    # QUIT
    # =====================================================
    def quit(self):
        """Bezpiecznie zamyka adapter audio."""

        if not pygame.mixer.get_init():
            return

        self.stop_all()

        self.sounds.clear()

        pygame.mixer.quit()