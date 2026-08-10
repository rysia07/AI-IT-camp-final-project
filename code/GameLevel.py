from LoadLevels import load_level
from Platforms import PlatformManager

from Characters import (
    Creature,
    GhostMouse,
    CharacterManager,
    ProjectileManager,
)


class GameLevel:
    """
    Zarządza ładowaniem i przygotowywaniem poziomów.

    Odpowiada za:
    - wczytywanie pliku poziomu,
    - platformy,
    - obiekty interaktywne,
    - gracza,
    - ducha,
    - przeciwników,
    - pociski,
    - CharacterManager.
    """

    def __init__(self, game):
        self.game = game

    # =====================================================
    # LOAD LEVEL
    # =====================================================

    def load(self, level_filename):
        """
        Wczytuje poziom i tworzy wszystkie obiekty potrzebne
        do jego działania.
        """

        game = self.game

        try:
            level = load_level(
                f"../levels/{level_filename}"
            )

        except FileNotFoundError:
            level = load_level(
                level_filename
            )

        game.level = level

        # -------------------------------------------------
        # INTERACTIVE
        # -------------------------------------------------

        game.interactive_mgr = (
            level.interactive_manager
        )

        # -------------------------------------------------
        # PLATFORMS
        # -------------------------------------------------

        game.platform_mgr = PlatformManager(
            "../pictures/platforma.png",
            level.platforms
        )

        # -------------------------------------------------
        # PROJECTILES
        # -------------------------------------------------

        game.projectile_mgr = ProjectileManager()

        # -------------------------------------------------
        # PLAYER
        # -------------------------------------------------

        game.player = self.create_player(
            level.player_pos
        )

        # -------------------------------------------------
        # GHOST
        # -------------------------------------------------

        game.ghost = GhostMouse(
            level.player_pos[0],
            level.player_pos[1]
        )

        game.ghost.update_rect()

        game.ghost.last_pos = (
            game.ghost.pos.copy()
        )

        # -------------------------------------------------
        # CHARACTER MANAGER
        # -------------------------------------------------

        game.char_mgr = CharacterManager()

        game.char_mgr.add(
            "player",
            game.player
        )

        game.char_mgr.add(
            "ghost",
            game.ghost
        )

    # =====================================================
    # CREATE PLAYER
    # =====================================================

    def create_player(self, start_pos):
        """
        Tworzy gracza wraz z jego animacjami.
        """

        player = Creature(
            start_pos[0],
            start_pos[1],
            speed=400,
            jump_force=-700,
            spritesheet_path="../pictures/ludzik.png"
        )

        try:

            # -------------------------------------------------
            # IDLE
            # -------------------------------------------------

            player.add_anim(
                "idle",
                [0],
                3,
                3,
                speed=100,
                priority=Creature.PRIORITY_IDLE,
                spritesheet_path="../pictures/ludzik.png",
                scale=2.0
            )

            # -------------------------------------------------
            # WALK
            # -------------------------------------------------

            player.add_anim(
                "walk",
                [0, 1, 2, 3, 4, 5],
                3,
                3,
                speed=150,
                priority=Creature.PRIORITY_WALK,
                spritesheet_path="../pictures/ludzik.png",
                scale=2.0
            )

            # -------------------------------------------------
            # ATTACK
            # -------------------------------------------------

            player.add_anim(
                "attack",
                list(range(19)),
                5,
                4,
                speed=35,
                loop=False,
                priority=Creature.PRIORITY_ATTACK,
                spritesheet_path="../pictures/Gracz_atak.png",
                scale=0.5
            )

        except Exception as error:

            print(
                "⚠️ Uwaga podczas ładowania "
                f"animacji gracza: {error}"
            )

        player.set_walk_idle(
            "walk",
            "idle"
        )

        player.play(
            "idle"
        )

        return player

    # =====================================================
    # RESET GAME
    # =====================================================

    def reset_game(
        self,
        player,
        ghost,
        spawn_pos
    ):
        """
        Resetuje gracza i ducha do pozycji startowej.
        """

        # -------------------------------------------------
        # PLAYER
        # -------------------------------------------------

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

        # -------------------------------------------------
        # GHOST
        # -------------------------------------------------

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
    # LOAD NEXT LEVEL
    # =====================================================

    def load_level(self, level_filename):
        """
        Przechodzi do następnego poziomu.

        Zwraca:
            True  - jeżeli istnieje następny poziom
            False - jeżeli był to ostatni poziom
        """

        game = self.game

        try:
            current_index = (
                game.available_levels.index(
                    game.current_level_file
                )
            )

        except ValueError:

            current_index = -1

        # -------------------------------------------------
        # NEXT LEVEL
        # -------------------------------------------------

        if (
            current_index >= 0
            and current_index + 1
            < len(game.available_levels)
        ):

            next_level = (
                game.available_levels[
                    current_index + 1
                ]
            )

            print(
                f"➡️ Przejście: "
                f"{game.current_level_file} "
                f"-> "
                f"{next_level}"
            )

            game.current_level_file = next_level

            self.load(
                game.current_level_file
            )

            return True

        # -------------------------------------------------
        # LAST LEVEL
        # -------------------------------------------------

        print(
            "🏆 Ukończono wszystkie poziomy!"
        )

        return False

    def check_gate(self):

        game = self.game

        for obj in game.interactive_mgr:

            if not getattr(obj, "triggered", False):
                continue

            if self.load_next_level():

                obj.triggered = False

                game.start_game_mouse()
                game.current_state = game.PLAYING

            else:

                obj.triggered = False

                game.stop_game_mouse()
                game.current_state = game.VICTORY

            break

    def load_level(self, level_filename):
        """
        Ładuje poziom i tworzy wszystkie obiekty potrzebne przez Game.
        """

        try:
            level = load_level(
                f"../levels/{level_filename}"
            )

        except FileNotFoundError:
            level = load_level(
                level_filename
            )

        # -------------------------------------------------
        # ZAPIS POZIOMU
        # -------------------------------------------------

        self.game.level = level

        # -------------------------------------------------
        # INTERACTIVE
        # -------------------------------------------------

        self.game.interactive_mgr = (
            level.interactive_manager
        )

        # -------------------------------------------------
        # PLATFORMS
        # -------------------------------------------------

        self.game.platform_mgr = PlatformManager(
            "../pictures/platforma.png",
            level.platforms
        )

        # -------------------------------------------------
        # PROJECTILES
        # -------------------------------------------------

        self.game.projectile_mgr = (
            ProjectileManager()
        )

        # -------------------------------------------------
        # PLAYER
        # -------------------------------------------------

        self.game.player = self.game.create_player(
            level.player_pos
        )

        # -------------------------------------------------
        # GHOST
        # -------------------------------------------------

        self.game.ghost = GhostMouse(
            level.player_pos[0],
            level.player_pos[1]
        )

        self.game.ghost.update_rect()

        self.game.ghost.last_pos = (
            self.game.ghost.pos.copy()
        )

        # -------------------------------------------------
        # CHARACTER MANAGER
        # -------------------------------------------------

        self.game.char_mgr = CharacterManager()

        self.game.char_mgr.add(
            "player",
            self.game.player
        )

        self.game.char_mgr.add(
            "ghost",
            self.game.ghost
        )

        print(
            f"✅ Załadowano poziom: {level_filename}"
        )