import pygame

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

    Obsługuje:
    - platformy,
    - ściany,
    - obiekty interaktywne,
    - gracza,
    - ducha,
    - przeciwników,
    - pociski.
    """

    def __init__(
        self,
        game
    ):

        self.game = game

    # =====================================================
    # FIND LEVEL FILE
    # =====================================================

    @staticmethod
    def _load_level_file(
        level_filename
    ):

        try:

            return load_level(
                f"../levels/{level_filename}"
            )

        except FileNotFoundError:

            return load_level(
                level_filename
            )

    # =====================================================
    # CREATE PLATFORM MANAGER
    # =====================================================

    def create_platform_manager(
        self,
        level
    ):

        return PlatformManager(
            "../pictures/platform_left.png",
            "../pictures/platform_middle.png",
            "../pictures/platform_right.png",
            "../pictures/wall.png",
            platforms=level.platforms,
            walls=getattr(
                level,
                "walls",
                []
            )
        )

    # =====================================================
    # LOAD
    # =====================================================

    def load(
        self,
        level_filename
    ):

        game = self.game

        level = self._load_level_file(
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
        # PLATFORMS + WALLS
        # -------------------------------------------------

        game.platform_mgr = (
            self.create_platform_manager(
                level
            )
        )

        # -------------------------------------------------
        # PROJECTILES
        # -------------------------------------------------

        game.projectile_mgr = (
            ProjectileManager()
        )

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

        game.char_mgr = (
            CharacterManager()
        )

        game.char_mgr.add(
            "player",
            game.player
        )

        game.char_mgr.add(
            "ghost",
            game.ghost
        )

        print(
            f"✅ Załadowano poziom: "
            f"{level_filename}"
        )

        print(
            f"   Platformy: "
            f"{len(level.platforms)}"
        )

        print(
            f"   Ściany: "
            f"{len(getattr(level, 'walls', []))}"
        )

        print(
            f"   Wrogowie: "
            f"{len(level.enemies)}"
        )

        print(
            f"   Interaktywne: "
            f"{len(level.interactive_manager)}"
        )

        return level

    # =====================================================
    # CREATE PLAYER
    # =====================================================

    def create_player(
        self,
        start_pos
    ):

        player = Creature(
            start_pos[0],
            start_pos[1],
            speed=400,
            jump_force=-450,
            spritesheet_path="../pictures/ludzik.png"
        )

        try:

            # =================================================
            # IDLE
            # =================================================

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

            # =================================================
            # WALK
            # =================================================

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

            # =================================================
            # ATTACK
            # =================================================

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

    def load_level(
        self,
        level_filename
    ):

        game = self.game

        level = self._load_level_file(
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
        # PLATFORMS + WALLS
        # -------------------------------------------------

        game.platform_mgr = (
            self.create_platform_manager(
                level
            )
        )

        # -------------------------------------------------
        # PROJECTILES
        # -------------------------------------------------

        game.projectile_mgr = (
            ProjectileManager()
        )

        # -------------------------------------------------
        # PLAYER
        # -------------------------------------------------

        game.player = self.create_player(
            level.player_pos
        )

        # -------------------------------------------------
        # GHOST
        # -------------------------------------------------

        mouse_x, mouse_y = (
            pygame.mouse.get_pos()
        )

        game.ghost = GhostMouse(
            mouse_x,
            mouse_y
        )

        game.ghost.update_rect()

        game.ghost.last_pos = (
            game.ghost.pos.copy()
        )

        # -------------------------------------------------
        # CHARACTER MANAGER
        # -------------------------------------------------

        game.char_mgr = (
            CharacterManager()
        )

        game.char_mgr.add(
            "player",
            game.player
        )

        game.char_mgr.add(
            "ghost",
            game.ghost
        )

        print(
            f"✅ Załadowano poziom: "
            f"{level_filename}"
        )

        print(
            f"   Platformy: "
            f"{len(level.platforms)}"
        )

        print(
            f"   Ściany: "
            f"{len(getattr(level, 'walls', []))}"
        )

        print(
            f"   Wrogowie: "
            f"{len(level.enemies)}"
        )

        return True
