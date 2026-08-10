class GameState:
    """
    Zarządza stanem gry.

    Stany:
        MENU
        PLAYING
        OPTIONS
        CREDITS
        FAILURE
        VICTORY
        PAUSE
        LEVEL_SELECT
    """

    MENU = 0
    PLAYING = 1
    OPTIONS = 2
    CREDITS = 3
    FAILURE = 4
    VICTORY = 5
    PAUSE = 6
    LEVEL_SELECT = 7

    def __init__(self, game):
        self.game = game

        self.current = self.MENU
        self.previous = self.MENU

    # =====================================================
    # SET STATE
    # =====================================================

    def set(self, state):
        """
        Zmienia aktualny stan gry.
        """

        self.previous = self.current
        self.current = state

    def change(self, state, save_previous=True):
        """
        Centralna zmiana stanu gry.
        """

        if save_previous:
            self.previous = self.current

        self.current = state

    # =====================================================
    # SET STATE WITHOUT SAVING PREVIOUS
    # =====================================================

    def set_direct(self, state):
        """
        Zmienia stan bez zapisywania poprzedniego.
        """

        self.current = state

    # =====================================================
    # RETURN TO PREVIOUS
    # =====================================================

    def back(self):
        """
        Powraca do poprzedniego stanu.
        """

        self.current = self.previous

    # =====================================================
    # STATE CHECKS
    # =====================================================

    def is_menu(self):
        return self.current == self.MENU

    def is_playing(self):
        return self.current == self.PLAYING

    def is_options(self):
        return self.current == self.OPTIONS

    def is_credits(self):
        return self.current == self.CREDITS

    def is_failure(self):
        return self.current == self.FAILURE

    def is_victory(self):
        return self.current == self.VICTORY

    def is_pause(self):
        return self.current == self.PAUSE

    def is_level_select(self):
        return self.current == self.LEVEL_SELECT

    # =====================================================
    # GAMEPLAY
    # =====================================================

    def start_game(self):
        """
        Przechodzi do rozgrywki.
        """

        self.set_direct(self.PLAYING)

        self.game.start_game_mouse()

    # =====================================================
    # PAUSE
    # =====================================================

    def pause(self):
        """
        Otwiera pauzę podczas gry.
        """

        if not self.is_playing():
            return

        self.set_direct(self.PAUSE)

        if hasattr(self.game, "pause_menu"):
            self.game.pause_menu.active = True

        self.game.stop_game_mouse()

    # =====================================================
    # RESUME
    # =====================================================

    def resume(self):
        """
        Wznawia grę z pauzy.
        """

        if not self.is_pause():
            return

        self.set_direct(self.PLAYING)

        if hasattr(self.game, "pause_menu"):
            self.game.pause_menu.active = False

        self.game.start_game_mouse()

    # =====================================================
    # MAIN MENU
    # =====================================================

    def main_menu(self):
        """
        Powrót do głównego menu.
        """

        self.set_direct(self.MENU)

        if hasattr(self.game, "pause_menu"):
            self.game.pause_menu.active = False

        self.game.stop_game_mouse()

    # =====================================================
    # LEVEL SELECT
    # =====================================================

    def level_select(self, previous=None):
        """
        Otwiera wybór poziomu.

        Jeśli previous zostanie podany,
        zostanie zapamiętany jako poprzedni stan.
        """

        if previous is not None:
            self.previous = previous
        else:
            self.previous = self.current

        self.current = self.LEVEL_SELECT

    # =====================================================
    # OPTIONS
    # =====================================================

    def options(self, previous=None):
        """
        Otwiera opcje.
        """

        if previous is not None:
            self.previous = previous
        else:
            self.previous = self.current

        self.current = self.OPTIONS

    # =====================================================
    # CREDITS
    # =====================================================

    def credits(self):
        """
        Otwiera napisy końcowe.
        """

        self.previous = self.current
        self.current = self.CREDITS

        if hasattr(self.game, "credits_audio"):
            self.game.credits_audio.stop()
            self.game.credits_audio.play()

    # =====================================================
    # FAILURE
    # =====================================================

    def failure(self):
        """
        Ekran przegranej.
        """

        self.current = self.FAILURE

        self.game.stop_game_mouse()

    # =====================================================
    # VICTORY
    # =====================================================

    def victory(self):
        """
        Ekran zwycięstwa.
        """

        self.current = self.VICTORY

        self.game.stop_game_mouse()