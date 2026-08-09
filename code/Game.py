import pygame

from LoadLevels import load_level
from Platforms import PlatformManager

from Characters import (
    Creature,
    GhostMouse,
    CharacterManager,
    ProjectileManager,
)

from Interactive import (
    CodePanel,
    ScoringButton,
)

from GUI import (
    MainMenu,
    LevelSelectMenu,
    OptionsMenu,
    CreditsMenu,
    FailureMenu,
    VictoryMenu,
)

from pause_menu import PauseMenu
from audio_adapter import AudioAdapter


# =========================================================
# STANY GRY
# =========================================================

MENU = 0
PLAYING = 1
OPTIONS = 2
CREDITS = 3
FAILURE = 4
VICTORY = 5
PAUSE = 6
LEVEL_SELECT = 7


class Game:

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

        self.width = width
        self.height = height
        self.fps = fps

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

        pygame.display.set_caption(
            "Alien Space"
        )

        self.clock = pygame.time.Clock()

        self.running = True

        # =================================================
        # STAN GRY
        # =================================================

        self.current_state = MENU
        self.previous_state = MENU

        # =================================================
        # POZIOMY
        # =================================================

        self.available_levels = [
            "level1.txt",
            "level2.txt",
            "level3.txt",
            "level4.txt",
        ]

        self.current_level_file = (
            "level1.txt"
        )

        # =================================================
        # OBIEKTY GRY
        # =================================================

        self.level = None
        self.interactive_mgr = None
        self.platform_mgr = None
        self.projectile_mgr = None

        self.player = None
        self.ghost = None
        self.char_mgr = None

        # =================================================
        # MYSZ
        # =================================================

        self.mouse_dx = 0
        self.mouse_dy = 0

        # =================================================
        # AUDIO
        # =================================================

        self._setup_audio()

        # =================================================
        # MENU
        # =================================================

        self._setup_menus()

        # =================================================
        # PIERWSZY POZIOM
        # =================================================

        self.load_selected_level(
            self.current_level_file
        )

    # =====================================================
    # AUDIO
    # =====================================================

    def _setup_audio(self):

        self.audio = AudioAdapter()

        self.audio.load(
            "../audio/background_ost.wav"
        )

        self.audio.set_volume(0.4)

        self.audio.play(
            loops=-1
        )

        # -------------------------------------------------
        # JUMP
        # -------------------------------------------------

        self.jump_audio = AudioAdapter()

        self.jump_audio.load(
            "../audio/jump.wav"
        )

        self.jump_audio.set_volume(0.7)

        # -------------------------------------------------
        # ATTACK
        # -------------------------------------------------

        self.attack_audio = AudioAdapter()

        self.attack_audio.load(
            "../audio/shoot.wav"
        )

        self.attack_audio.set_volume(0.7)

        # -------------------------------------------------
        # CREDITS
        # -------------------------------------------------

        self.credits_audio = AudioAdapter()

        self.credits_audio.load(
            "../audio/Monster-thing (Bounce).wav"
        )

        self.credits_audio.set_volume(0.7)

        # -------------------------------------------------
        # ENEMY
        # -------------------------------------------------

        self.enemy_audio = AudioAdapter()

        self.enemy_audio.load(
            "../audio/phokin credits enter sfx.mp3"
        )

        self.enemy_audio.set_volume(0.4)

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
            self.height
        )

        self.credits_menu = CreditsMenu(
            self.width,
            self.height
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
    # PLAYER
    # =====================================================

    def create_player(self, start_pos):

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
    # GET RECT
    # =====================================================

    @staticmethod
    def get_rect(obj):

        if hasattr(obj, "rect"):
            return obj.rect

        return obj

    # =====================================================
    # GHOST COLLISIONS
    # =====================================================

    def move_ghost_with_collisions(
        self,
        ghost,
        dx,
        dy,
        obstacles
    ):

        ghost_rect = (
            ghost.rect.copy()
        )

        # =================================================
        # RUCH X
        # =================================================

        ghost_rect.x += int(dx)

        for obstacle in obstacles:

            obstacle_rect = self.get_rect(
                obstacle
            )

            if not ghost_rect.colliderect(
                obstacle_rect
            ):
                continue

            if dx > 0:

                ghost_rect.right = (
                    obstacle_rect.left
                )

            elif dx < 0:

                ghost_rect.left = (
                    obstacle_rect.right
                )

        # =================================================
        # RUCH Y
        # =================================================

        ghost_rect.y += int(dy)

        for obstacle in obstacles:

            obstacle_rect = self.get_rect(
                obstacle
            )

            if not ghost_rect.colliderect(
                obstacle_rect
            ):
                continue

            if dy > 0:

                ghost_rect.bottom = (
                    obstacle_rect.top
                )

            elif dy < 0:

                ghost_rect.top = (
                    obstacle_rect.bottom
                )

        # =================================================
        # SYNCHRONIZACJA
        # =================================================

        ghost.rect = ghost_rect

        ghost.pos.x = float(
            ghost_rect.centerx
        )

        ghost.pos.y = float(
            ghost_rect.centery
        )

    # =====================================================
    # LOAD LEVEL
    # =====================================================

    def load_selected_level(
        self,
        level_filename
    ):

        try:

            level = load_level(
                f"../levels/{level_filename}"
            )

        except FileNotFoundError:

            level = load_level(
                level_filename
            )

        self.level = level

        # =================================================
        # INTERACTIVE
        # =================================================

        self.interactive_mgr = (
            level.interactive_manager
        )

        # =================================================
        # PLATFORMS
        # =================================================

        self.platform_mgr = PlatformManager(
            "../pictures/platforma.png",
            level.platforms
        )

        # =================================================
        # PROJECTILES
        # =================================================

        self.projectile_mgr = (
            ProjectileManager()
        )

        # =================================================
        # PLAYER
        # =================================================

        self.player = self.create_player(
            level.player_pos
        )

        # =================================================
        # GHOST
        # =================================================

        self.ghost = GhostMouse(
            level.player_pos[0],
            level.player_pos[1]
        )

        self.ghost.update_rect()

        self.ghost.last_pos = (
            self.ghost.pos.copy()
        )

        # =================================================
        # CHARACTER MANAGER
        # =================================================

        self.char_mgr = CharacterManager()

        self.char_mgr.add(
            "player",
            self.player
        )

        self.char_mgr.add(
            "ghost",
            self.ghost
        )

    # =====================================================
    # KEYBOARD
    # =====================================================

    def handle_keydown(self, event):

        # =================================================
        # ESC
        # =================================================

        if event.key == pygame.K_ESCAPE:

            if self.current_state == PLAYING:

                self.current_state = PAUSE

                self.pause_menu.active = True

                pygame.mouse.set_visible(
                    True
                )

                pygame.event.set_grab(
                    False
                )

                return

            elif self.current_state == PAUSE:

                self.current_state = PLAYING

                self.pause_menu.active = False

                pygame.mouse.set_visible(
                    False
                )

                pygame.event.set_grab(
                    True
                )

                pygame.mouse.get_rel()

                return

        # =================================================
        # GAMEPLAY
        # =================================================

        if self.current_state != PLAYING:
            return

        # =================================================
        # JUMP
        # =================================================

        if event.key in (
            pygame.K_w,
        ):

            if self.player.jump():

                self.jump_audio.stop()

                self.jump_audio.play()

        # =================================================
        # ATTACK
        # =================================================

        if event.key == pygame.K_2:

            if hasattr(
                self.player,
                "play"
            ):

                self.attack_audio.stop()

                self.attack_audio.play()

                self.player.play(
                    "attack"
                )

    # =====================================================
    # MOUSE
    # =====================================================

    def handle_mouse_motion(self, event):

        if self.current_state != PLAYING:
            return

        dx, dy = event.rel

        self.mouse_dx += dx
        self.mouse_dy += dy

    # =====================================================
    # LEFT CLICK
    # =====================================================

    def handle_left_click(self, event):

        # =================================================
        # PLAYING
        # =================================================

        if self.current_state == PLAYING:

            self.interactive_mgr.handle_event_all(
                event
            )

            return

        # =================================================
        # MENU
        # =================================================

        if self.current_state == MENU:

            action = (
                self.main_menu.handle_click(
                    event.pos,
                    (1, 0, 0)
                )
            )

            if action == "level_select":

                self.previous_state = MENU

                self.current_state = (
                    LEVEL_SELECT
                )

            elif action == "options":

                self.previous_state = MENU

                self.current_state = OPTIONS

            elif action == "credits":

                self.current_state = CREDITS

            elif action == "quit":

                self.running = False

            return

        # =================================================
        # LEVEL SELECT
        # =================================================

        if self.current_state == LEVEL_SELECT:

            action = (
                self.level_select_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            if action == "back":

                self.current_state = (
                    self.previous_state
                )

            elif (
                action
                and action.startswith("load_")
            ):

                level_file = (
                    action.replace(
                        "load_",
                        ""
                    )
                )

                self.current_level_file = (
                    level_file
                )

                self.load_selected_level(
                    self.current_level_file
                )

                self.start_game_mouse()

                self.current_state = PLAYING

            return

        # =================================================
        # PAUSE
        # =================================================

        if self.current_state == PAUSE:

            action = (
                self.pause_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            if action == "resume":

                self.pause_menu.active = False

                self.start_game_mouse()

                self.current_state = PLAYING

            elif action == "level_select":

                self.pause_menu.active = False

                self.previous_state = PAUSE

                self.current_state = LEVEL_SELECT

            elif action == "options":

                self.previous_state = PAUSE

                self.current_state = OPTIONS

            elif action == "main_menu":

                self.pause_menu.active = False

                self.stop_game_mouse()

                self.current_state = MENU

            return

        # =================================================
        # OPTIONS
        # =================================================

        if self.current_state == OPTIONS:

            action = (
                self.options_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            if action == "back":

                self.current_state = (
                    self.previous_state
                )

            return

        # =================================================
        # CREDITS
        # =================================================

        if self.current_state == CREDITS:

            action = (
                self.credits_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            if action == "back":

                self.current_state = MENU

            return

        # =================================================
        # FAILURE
        # =================================================

        if self.current_state == FAILURE:

            action = (
                self.failure_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            if action == "retry":

                self.load_selected_level(
                    self.current_level_file
                )

                self.start_game_mouse()

                self.current_state = PLAYING

            elif action == "menu":

                self.current_state = MENU

            return

        # =================================================
        # VICTORY
        # =================================================

        if self.current_state == VICTORY:

            action = (
                self.victory_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            if action == "level_select":

                self.previous_state = MENU

                self.current_state = (
                    LEVEL_SELECT
                )

            elif action == "menu":

                self.current_state = MENU

    # =====================================================
    # EVENTS
    # =====================================================

    def handle_events(self):

        self.mouse_dx = 0
        self.mouse_dy = 0

        for event in pygame.event.get():

            # -------------------------------------------------
            # QUIT
            # -------------------------------------------------

            if event.type == pygame.QUIT:

                self.running = False

                continue

            # -------------------------------------------------
            # OPTIONS
            # -------------------------------------------------

            if self.current_state == OPTIONS:

                if hasattr(
                    self.options_menu,
                    "handle_event"
                ):

                    self.options_menu.handle_event(
                        event
                    )

            # -------------------------------------------------
            # KEYBOARD
            # -------------------------------------------------

            if event.type == pygame.KEYDOWN:

                self.handle_keydown(
                    event
                )

            # -------------------------------------------------
            # MOUSE MOTION
            # -------------------------------------------------

            elif event.type == pygame.MOUSEMOTION:

                self.handle_mouse_motion(
                    event
                )

            # -------------------------------------------------
            # LEFT CLICK
            # -------------------------------------------------

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                self.handle_left_click(
                    event
                )

            # -------------------------------------------------
            # INTERACTIVE
            # -------------------------------------------------

            if self.current_state == PLAYING:

                self.interactive_mgr.handle_event(
                    event
                )

    # =====================================================
    # GAMEPLAY UPDATE
    # =====================================================

    def update_game(self, dt):

        # =================================================
        # PLAYER INPUT
        # =================================================

        keys = pygame.key.get_pressed()

        move_x = 0

        if (
            keys[pygame.K_a]
            or keys[pygame.K_LEFT]
        ):

            move_x -= 1

        if (
            keys[pygame.K_d]
            or keys[pygame.K_RIGHT]
        ):

            move_x += 1

        self.player.move(
            move_x
        )

        # =================================================
        # OBSTACLES
        # =================================================

        interactive_objs = (
            self.interactive_mgr.objects
        )

        solid_interactive = [
            obj
            for obj in interactive_objs
            if (
                (
                    hasattr(obj, "is_open")
                    and not obj.is_open
                    and not isinstance(
                        obj,
                        CodePanel
                    )
                )
                or isinstance(
                    obj,
                    ScoringButton
                )
            )
        ]

        all_obstacles = (
            self.platform_mgr.platforms
            + solid_interactive
        )

        # =================================================
        # GHOST
        # =================================================

        self.ghost.last_pos = (
            self.ghost.pos.copy()
        )

        if (
            self.mouse_dx != 0
            or self.mouse_dy != 0
        ):

            self.move_ghost_with_collisions(
                self.ghost,
                self.mouse_dx,
                self.mouse_dy,
                all_obstacles
            )

        else:

            self.ghost.update_rect()

        # =================================================
        # PLAYER
        # =================================================

        self.char_mgr.update_all(
            dt,
            platforms=all_obstacles
        )

        # =================================================
        # GHOST SPRITE
        # =================================================

        self.ghost.update(
            dt
        )

        # =================================================
        # ENEMIES
        # =================================================

        for enemy in self.level.enemies:

            enemy.update(
                dt,
                player_pos=self.player.pos,
                platforms=self.platform_mgr
            )

            if (
                getattr(
                    enemy,
                    "shoot_cooldown",
                    0
                ) <= 0
            ):

                if hasattr(
                    enemy,
                    "shoot"
                ):

                    projectile = enemy.shoot(
                        self.player.pos.x,
                        self.player.pos.y
                    )

                    if projectile:

                        self.projectile_mgr.add(
                            projectile
                        )

        # =================================================
        # PROJECTILES
        # =================================================

        self.projectile_mgr.update(
            dt
        )

        # =================================================
        # PROJECTILE COLLISION
        # =================================================

        for projectile in (
            self.projectile_mgr.get_projectiles()
        ):

            if self.player.rect.colliderect(
                projectile.rect
            ):

                self.player.hp -= getattr(
                    projectile,
                    "damage",
                    10
                )

                projectile.is_dead = True

                print(
                    "💥 Trafienie! "
                    f"HP gracza: {self.player.hp}"
                )

        # =================================================
        # DEATH
        # =================================================

        if self.player.hp <= 0:

            self.stop_game_mouse()

            self.current_state = FAILURE

        # =================================================
        # INTERACTIVE OBJECTS
        # =================================================

        self.interactive_mgr.update_all(
            self.player,
            self.ghost,
            dt
        )

        # =================================================
        # LEVEL GATE
        # =================================================

        self.check_level_gate()

    # =====================================================
    # LEVEL GATE
    # =====================================================

    def check_level_gate(self):

        for obj in self.interactive_mgr:

            if not getattr(
                obj,
                "triggered",
                False
            ):

                continue

            try:

                current_index = (
                    self.available_levels.index(
                        self.current_level_file
                    )
                )

            except ValueError:

                current_index = -1

            # =================================================
            # NEXT LEVEL
            # =================================================

            if (
                current_index >= 0
                and current_index + 1
                < len(self.available_levels)
            ):

                next_level = (
                    self.available_levels[
                        current_index + 1
                    ]
                )

                print(
                    f"➡️ Przejście: "
                    f"{self.current_level_file} "
                    f"-> "
                    f"{next_level}"
                )

                self.current_level_file = (
                    next_level
                )

                self.load_selected_level(
                    self.current_level_file
                )

                obj.triggered = False

                self.start_game_mouse()

                self.current_state = PLAYING

            # =================================================
            # LAST LEVEL
            # =================================================

            else:

                print(
                    "🏆 Ukończono wszystkie poziomy!"
                )

                self.stop_game_mouse()

                obj.triggered = False

                self.current_state = VICTORY

            break

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        if self.current_state == MENU:

            self.main_menu.update()

        elif self.current_state == LEVEL_SELECT:

            self.level_select_menu.update()

        elif self.current_state == PAUSE:

            self.pause_menu.update()

        elif self.current_state == OPTIONS:

            self.options_menu.update()

        elif self.current_state == CREDITS:

            self.credits_menu.update()

        elif self.current_state == FAILURE:

            self.failure_menu.update()

        elif self.current_state == VICTORY:

            self.victory_menu.update()

        elif self.current_state == PLAYING:

            self.update_game(
                dt
            )

    # =====================================================
    # DRAW HUD
    # =====================================================

    def draw_hud(self):

        font = pygame.font.Font(
            None,
            32
        )

        player_power = getattr(
            self.player,
            "power",
            0
        )

        hud_text = font.render(
            (
                f"Player HP: {self.player.hp} "
                f"| Ghost HP: {self.ghost.hp} "
                f"| Power: {player_power}"
            ),
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            hud_text,
            (10, 10)
        )

        info = font.render(
            (
                "A/D = Move, "
                "W/Space = Jump, "
                "2 = Attack, "
                "ESC = Pause"
            ),
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            info,
            (10, 50)
        )

    # =====================================================
    # DRAW GAME
    # =====================================================

    def draw_game(self):

        # -------------------------------------------------
        # PLATFORMY
        # -------------------------------------------------

        self.platform_mgr.draw(
            self.screen
        )

        # -------------------------------------------------
        # INTERACTIVE
        # -------------------------------------------------

        self.interactive_mgr.draw_all(
            self.screen
        )

        # -------------------------------------------------
        # CHARACTERS
        # -------------------------------------------------

        self.char_mgr.draw_all(
            self.screen
        )

        # -------------------------------------------------
        # ENEMIES
        # -------------------------------------------------

        for enemy in self.level.enemies:

            if (
                hasattr(
                    enemy,
                    "is_alive"
                )
                and enemy.is_alive()
            ):

                enemy.draw(
                    self.screen
                )

            elif not hasattr(
                enemy,
                "is_alive"
            ):

                enemy.draw(
                    self.screen
                )

        # -------------------------------------------------
        # PROJECTILES
        # -------------------------------------------------

        self.projectile_mgr.draw_all(
            self.screen
        )

        # -------------------------------------------------
        # HUD
        # -------------------------------------------------

        self.draw_hud()

        # -------------------------------------------------
        # PAUSE
        # -------------------------------------------------

        if self.current_state == PAUSE:

            self.pause_menu.draw(
                self.screen
            )

    # =====================================================
    # DRAW
    # =====================================================

    def draw(self):

        self.screen.fill(
            (30, 30, 40)
        )

        # =================================================
        # GAME
        # =================================================

        if self.current_state in (
            PLAYING,
            PAUSE
        ):

            self.draw_game()

        # =================================================
        # MENU
        # =================================================

        elif self.current_state == MENU:

            self.main_menu.draw(
                self.screen
            )

        # =================================================
        # LEVEL SELECT
        # =================================================

        elif self.current_state == LEVEL_SELECT:

            self.level_select_menu.draw(
                self.screen
            )

        # =================================================
        # OPTIONS
        # =================================================

        elif self.current_state == OPTIONS:

            self.options_menu.draw(
                self.screen
            )

        # =================================================
        # CREDITS
        # =================================================

        elif self.current_state == CREDITS:

            self.credits_menu.draw(
                self.screen
            )

        # =================================================
        # FAILURE
        # =================================================

        elif self.current_state == FAILURE:

            self.failure_menu.draw(
                self.screen
            )

        # =================================================
        # VICTORY
        # =================================================

        elif self.current_state == VICTORY:

            self.victory_menu.draw(
                self.screen
            )

        pygame.display.flip()

    # =====================================================
    # MOUSE GAME MODE
    # =====================================================

    def start_game_mouse(self):

        pygame.mouse.set_visible(
            False
        )

        pygame.event.set_grab(
            True
        )

        pygame.mouse.get_rel()

    def stop_game_mouse(self):

        pygame.mouse.set_visible(
            True
        )

        pygame.event.set_grab(
            False
        )

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        pygame.mouse.get_rel()

        while self.running:

            dt = (
                self.clock.tick(self.fps)
                / 1000.0
            )

            self.handle_events()

            self.update(
                dt
            )

            self.draw()

        self.shutdown()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        try:

            self.audio.quit()

        except Exception:
            pass