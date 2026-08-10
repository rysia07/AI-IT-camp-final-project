import os
import pygame


class GameAudio:

    def __init__(self, game):

        self.game = game

        # =================================================
        # FOLDER PROJEKTU
        # =================================================

        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        # /project/code/GameAudio.py
        # /project/audio/...

        self.project_dir = os.path.dirname(
            self.base_dir
        )

        self.audio_dir = os.path.join(
            self.project_dir,
            "audio"
        )

        # =================================================
        # GŁOŚNOŚĆ
        # =================================================

        self.master_volume = 1.0
        self.music_volume = 0.7
        self.sfx_volume = 0.4

        # =================================================
        # MIXER
        # =================================================
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            pass
        # =================================================
        # DŹWIĘKI
        # =================================================

        self.sounds = {}

        self._load_sound(
            "jump",
            "jump.wav"
        )

        self._load_sound(
            "attack",
            "Monster-thing (Bounce).wav"
        )

        self._load_sound(
            "credits",
            "phokin credits enter sfx.mp3"
        )

        self._load_sound(
            "shoot",
            "shoot.wav"
        )
        # =================================================
        # KOMPATYBILNOŚĆ
        # =================================================

        self.jump_audio = self.get_sound("jump")
        self.attack_audio = self.get_sound("attack")
        self.credits_audio = self.get_sound("credits")
        self.shoot_audio = self.get_sound("shoot")

        self.game.jump_audio = self.jump_audio
        self.game.attack_audio = self.attack_audio
        self.game.credits_audio = self.credits_audio
        self.game.shoot_audio = self.shoot_audio
        # =================================================
        # MUZYKA
        # =================================================

        self.music_path = os.path.join(
            self.audio_dir,
            "background_ost.wav"
        )

        self.music_loaded = False

        if os.path.isfile(self.music_path):

            try:

                pygame.mixer.music.load(
                    self.music_path
                )

                self.music_loaded = True

                pygame.mixer.music.set_volume(
                    self.get_music_volume()
                )

                pygame.mixer.music.play(
                    loops=-1
                )

                print(
                    "🔊 Załadowano muzykę:",
                    self.music_path
                )

            except pygame.error as error:

                print(
                    f"⚠️ Nie udało się załadować muzyki: {error}"
                )

        else:

            print(
                f"⚠️ Nie znaleziono muzyki: {self.music_path}"
            )

        # =================================================
        # KOMPATYBILNOŚĆ Z GAMEINPUT
        # =================================================

        self.game.jump_audio = (
            self.get_sound("jump")
        )

        self.game.attack_audio = (
            self.get_sound("attack")
        )

        self.game.credits_audio = (
            self.get_sound("credits")
        )

        self.game.shoot_audio = (
            self.get_sound("shoot")
        )

    # =====================================================
    # LOAD SOUND
    # =====================================================

    def _load_sound(
        self,
        name,
        filename
    ):

        path = os.path.join(
            self.audio_dir,
            filename
        )

        if not os.path.isfile(path):

            print(
                f"⚠️ Nie znaleziono dźwięku: {path}"
            )

            self.sounds[name] = None

            return

        try:

            sound = pygame.mixer.Sound(
                path
            )

            self.sounds[name] = sound

            sound.set_volume(
                self.get_sfx_volume()
            )

            print(
                f"🔊 Załadowano SFX: {filename}"
            )

        except pygame.error as error:

            print(
                f"⚠️ Błąd ładowania {filename}: {error}"
            )

            self.sounds[name] = None

    # =====================================================
    # GET SOUND
    # =====================================================

    def get_sound(
        self,
        name
    ):

        sound = self.sounds.get(
            name
        )

        if sound is None:

            return _SilentSound()

        return sound

    # =====================================================
    # PLAY SFX
    # =====================================================

    def play(
        self,
        name
    ):

        sound = self.sounds.get(
            name
        )

        if sound is None:
            return

        sound.set_volume(
            self.get_sfx_volume()
        )

        sound.play()

    # =====================================================
    # STOP SFX
    # =====================================================

    def stop(
        self,
        name
    ):

        sound = self.sounds.get(
            name
        )

        if sound is None:
            return

        sound.stop()

    # =====================================================
    # MASTER VOLUME
    # =====================================================

    def set_master_volume(
        self,
        value
    ):

        self.master_volume = max(
            0.0,
            min(
                1.0,
                float(value)
            )
        )

        self._update_volumes()

    # =====================================================
    # MUSIC VOLUME
    # =====================================================

    def set_music_volume(
        self,
        value
    ):

        self.music_volume = max(
            0.0,
            min(
                1.0,
                float(value)
            )
        )

        pygame.mixer.music.set_volume(
            self.get_music_volume()
        )

    # =====================================================
    # SFX VOLUME
    # =====================================================

    def set_sfx_volume(
        self,
        value
    ):

        self.sfx_volume = max(
            0.0,
            min(
                1.0,
                float(value)
            )
        )

        for sound in self.sounds.values():

            if sound is not None:

                sound.set_volume(
                    self.get_sfx_volume()
                )

    # =====================================================
    # GET MUSIC VOLUME
    # =====================================================

    def get_music_volume(
        self
    ):

        return (
            self.master_volume
            * self.music_volume
        )

    # =====================================================
    # GET SFX VOLUME
    # =====================================================

    def get_sfx_volume(
        self
    ):

        return (
            self.master_volume
            * self.sfx_volume
        )

    # =====================================================
    # UPDATE VOLUMES
    # =====================================================

    def _update_volumes(
        self
    ):

        pygame.mixer.music.set_volume(
            self.get_music_volume()
        )

        for sound in self.sounds.values():

            if sound is not None:

                sound.set_volume(
                    self.get_sfx_volume()
                )

    # =====================================================
    # MUSIC
    # =====================================================

    def play_music(
        self
    ):

        if not self.music_loaded:
            return

        pygame.mixer.music.play(
            loops=-1
        )

    def stop_music(
        self
    ):

        pygame.mixer.music.stop()

    def pause_music(
        self
    ):

        pygame.mixer.music.pause()

    def resume_music(
        self
    ):

        pygame.mixer.music.unpause()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self
    ):

        try:

            pygame.mixer.music.stop()

            pygame.mixer.stop()

        except Exception as error:

            print(
                f"⚠️ Błąd zatrzymywania audio: {error}"
            )


class _SilentSound:
    """
    Bezpieczny pusty dźwięk.

    Dzięki temu:

        game.jump_audio.stop()
        game.jump_audio.play()

    nadal działa nawet jeśli pliku brakuje.
    """

    def play(self):
        pass

    def stop(self):
        pass

    def set_volume(
        self,
        volume
    ):
        pass