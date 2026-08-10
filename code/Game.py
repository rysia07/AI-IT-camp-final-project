import sys
import pygame

from GameRenderer import GameRenderer
from GameInput import GameInput
from GameUpdate import GameUpdate
from GameLevel import GameLevel
from GameAudio import GameAudio
from GameState import GameState

from GUI import (
    MainMenu,
    LevelSelectMenu,
    OptionsMenu,
    CreditsMenu,
    FailureMenu,
    VictoryMenu,
)

from pause_menu import PauseMenu


class Game:

    # =====================================================
    # STANY
    # =====================================================

    MENU = GameState.MENU
    PLAYING = GameState.PLAYING
    OPTIONS = GameState.OPTIONS
    CREDITS = GameState.CREDITS
    FAILURE = GameState.FAILURE
    VICTORY = GameState.VICTORY
    PAUSE = GameState.PAUSE
    LEVEL_SELECT = GameState.LEVEL_SELECT

    # =====================================================
    # INIT
    # =====================================================

    def __init__(
        self,
        width=900,
        height=600,
        fps=60
    ):

        pygame.init()

        # -------------------------------------------------
        # WINDOW
        # -------------------------------------------------

        self.width = width
        self.height = height
        self.fps = fps

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

        self.audio_manager = GameAudio(self)

        self.jump_audio = self.audio_manager.jump_audio
        self.attack_audio = self.audio_manager.attack_audio
        self.credits_audio = self.audio_manager.credits_audio

        pygame.display.set_caption(
            "Alien Space"
        )

        self.clock = pygame.time.Clock()

        self.running = True

        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

        self.state = GameState(self)

        # -------------------------------------------------
        # COMPATIBILITY
        #
        # GameInput / GameUpdate / GameRenderer
        # mogą jeszcze korzystać z current_state.
        # -------------------------------------------------

        self.current_state = self.state.current
        self.previous_state = self.state.previous

        # -------------------------------------------------
        # LEVELS
        # -------------------------------------------------

        self.available_levels = [
            "level1.txt",
            "level2.txt",
            "level3.txt",
            "level4.txt",
            "level5.txt"
        ]

        self.current_level_file = (
            "level1.txt"
        )

        self.final_score = 0

        # -------------------------------------------------
        # GAME OBJECTS
        # -------------------------------------------------

        self.level = None
        self.interactive_mgr = None
        self.platform_mgr = None
        self.projectile_mgr = None

        self.player = None
        self.ghost = None
        self.char_mgr = None

        # -------------------------------------------------
        # MOUSE
        # -------------------------------------------------

        self.mouse_dx = 0
        self.mouse_dy = 0

        # -------------------------------------------------
        # MENUS
        # -------------------------------------------------

        self._setup_menus()

        # -------------------------------------------------
        # LEVEL MANAGER
        # -------------------------------------------------

        self.level_manager = GameLevel(self)

        # -------------------------------------------------
        # INPUT
        # -------------------------------------------------

        self.input = GameInput(self)

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        self.update_manager = GameUpdate(self)

        # -------------------------------------------------
        # RENDERER
        # -------------------------------------------------

        self.renderer = GameRenderer(self)

        # -------------------------------------------------
        # FIRST LEVEL
        # -------------------------------------------------

        self.level_manager.load_level(
            self.current_level_file
        )

        self.sync_state()

    # =====================================================
    # STATE SYNC
    # =====================================================

    def sync_state(self):
        """
        Synchronizuje stary interfejs Game
        z nowym GameState.

        Dzięki temu obecne moduły nie muszą
        być od razu przepisywane.
        """

        self.current_state = (
            self.state.current
        )

        self.previous_state = (
            self.state.previous
        )

    # =====================================================
    # STATE SETTER
    # =====================================================

    def set_state(
        self,
        state,
        save_previous=True
    ):
        """
        Centralna zmiana stanu gry.
        """

        if save_previous:
            self.state.set(state)
        else:
            self.state.set_direct(state)

        self.sync_state()

    # =====================================================
    # MENUS
    # =====================================================

    def _setup_menus(self):

        self.main_menu = MainMenu(
            self.width,
            self.height
        )

        self.level_select_menu = LevelSelectMenu(
            self.width,
            self.height,
            self.available_levels
        )

        self.options_menu = OptionsMenu(
            self.width,
            self.height,
            self.audio_manager
        )

        self.credits_menu = CreditsMenu(
            self.width,
            self.height,
            self.audio_manager
        )

        self.failure_menu = FailureMenu(
            self.width,
            self.height
        )

        self.victory_menu = VictoryMenu(
            self.width,
            self.height
        )

        self.pause_menu = PauseMenu(
            self.width,
            self.height
        )

    # =====================================================
    # LEVEL
    # =====================================================

    def load_selected_level(
        self,
        level_filename
    ):
        """
        Kompatybilna metoda dla GameInput,
        GameUpdate i innych modułów.

        Właściwe ładowanie znajduje się
        teraz w GameLevel.
        """

        self.current_level_file = (
            level_filename
        )

        self.level_manager.load_level(
            level_filename
        )

    # =====================================================
    # PLAYER
    # =====================================================

    def create_player(
        self,
        start_pos
    ):
        """
        Kompatybilność ze starszym kodem.

        Właściwe tworzenie gracza znajduje się
        w GameLevel.
        """

        return self.level_manager.create_player(
            start_pos
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset_game(
        self,
        player,
        ghost,
        spawn_pos
    ):
        """
        Reset gracza i ducha.
        """

        player.pos.update(
            spawn_pos[0],
            spawn_pos[1]
        )

        player.update_rect()

        player.hp = 100

        player.vel_x = 0
        player.vel_y = 0

        player.is_grounded = False

        player.jumps_left = (
            player.max_jumps
        )

        ghost.pos.update(
            spawn_pos[0],
            spawn_pos[1]
        )

        ghost.update_rect()

        ghost.last_pos = (
            ghost.pos.copy()
        )

        ghost.hp = 50

    # =====================================================
    # MOUSE GAME MODE
    # =====================================================
    def start_game_mouse(self):

        pygame.mouse.set_visible(False)

        pygame.event.set_grab(True)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        mouse_x = max(
            0,
            min(mouse_x, self.width - 1)
        )

        mouse_y = max(
            0,
            min(mouse_y, self.height - 1)
        )

        pygame.mouse.set_pos(
            mouse_x,
            mouse_y
        )

        pygame.mouse.get_rel()

    # =====================================================

    def stop_game_mouse(self):

        pygame.mouse.set_visible(
            True
        )

        pygame.event.set_grab(
            False
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt
    ):
        """
        Cała aktualizacja gry jest obsługiwana
        przez GameUpdate.
        """

        self.update_manager.update(
            dt
        )

        self.sync_state()

    # =====================================================
    # RUN
    # =====================================================
    def run(self):

        # Na starcie jesteśmy w MENU,
        # więc mysz musi być widoczna.
        self.stop_game_mouse()

        pygame.mouse.get_rel()

        while self.running:
            dt = (
                    self.clock.tick(self.fps)
                    / 1000.0
            )

            self.input.handle_events()

            self.update(dt)

            self.renderer.draw()

        self.shutdown()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        try:

            self.audio_manager.shutdown()

        except Exception as error:

            print(
                f"⚠️ Błąd zamykania audio: {error}"
            )

        pygame.quit()

        sys.exit()