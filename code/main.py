import sys
import os
import pygame

# Importy z Twoich modułów
from LoadLevels import load_level
from Platforms import PlatformManager
from Characters import (
    Creature,
    GhostMouse,
    CharacterManager,
    ProjectileManager
)
from Interactive import CodePanel

from GUI import (
    MainMenu,
    LevelSelectMenu,
    OptionsMenu,
    CreditsMenu,
    FailureMenu,
    VictoryMenu
)

from pause_menu import PauseMenu


# =========================================================
# KONFIGURACJA
# =========================================================

FPS = 60
WIDTH = 900
HEIGHT = 600

# Stany gry
MENU = 0
PLAYING = 1
OPTIONS = 2
CREDITS = 3
FAILURE = 4
VICTORY = 5
PAUSE = 6
LEVEL_SELECT = 7


# =========================================================
# ŚCIEŻKI DO GRAFIKI
# =========================================================

PICTURES = "../pictures"

BACKGROUND_PATH = os.path.join(
    PICTURES,
    "background.png"
)

DOOR_CLOSED_PATH = os.path.join(
    PICTURES,
    "door_closed.png"
)

DOOR_OPEN_PATH = os.path.join(
    PICTURES,
    "door_open.png"
)

LEVER_OFF_PATH = os.path.join(
    PICTURES,
    "lever_off.png"
)

LEVER_ON_PATH = os.path.join(
    PICTURES,
    "lever_on.png"
)

SCORING_PLATE_PATH = os.path.join(
    PICTURES,
    "scoring_plate.png"
)

SCORING_PLATE_ACTIVE_PATH = os.path.join(
    PICTURES,
    "scoring_plate_active.png"
)

CODE_PANEL_PATH = os.path.join(
    PICTURES,
    "code_panel.png"
)


# =========================================================
# POMOCNICZE - ŁADOWANIE GRAFIKI
# =========================================================

def load_image(path, alpha=True):

    """
    Ładuje obraz.

    Jeżeli pliku nie ma albo wystąpi błąd,
    zwraca None zamiast wywalać całą grę.
    """

    if not os.path.exists(path):

        print(
            f"[ART] Brak pliku: {path}"
        )

        return None

    try:

        image = pygame.image.load(path)

        if alpha:

            image = image.convert_alpha()

        else:

            image = image.convert()

        return image

    except pygame.error as error:

        print(
            f"[ART] Nie można załadować {path}: {error}"
        )

        return None


# =========================================================
# ART MANAGER
# =========================================================

class ArtManager:

    """
    Zarządza grafiką tła oraz grafikami obiektów interaktywnych.

    Nie zmienia logiki obiektów z Interactive.py.
    Tylko odczytuje ich stan i rysuje odpowiednią grafikę.
    """

    def __init__(self, screen_width, screen_height):

        self.screen_width = screen_width
        self.screen_height = screen_height

        # -------------------------------------------------
        # BACKGROUND
        # -------------------------------------------------

        self.background = load_image(
            BACKGROUND_PATH,
            alpha=False
        )

        self.background_scaled = None

        if self.background:

            self.background_scaled = pygame.transform.scale(
                self.background,
                (
                    self.screen_width,
                    self.screen_height
                )
            )

        # -------------------------------------------------
        # DOORS
        # -------------------------------------------------

        self.door_closed = load_image(
            DOOR_CLOSED_PATH
        )

        self.door_open = load_image(
            DOOR_OPEN_PATH
        )

        # -------------------------------------------------
        # LEVERS
        # -------------------------------------------------

        self.lever_off = load_image(
            LEVER_OFF_PATH
        )

        self.lever_on = load_image(
            LEVER_ON_PATH
        )

        # -------------------------------------------------
        # SCORING PLATES
        # -------------------------------------------------

        self.scoring_plate = load_image(
            SCORING_PLATE_PATH
        )

        self.scoring_plate_active = load_image(
            SCORING_PLATE_ACTIVE_PATH
        )

        # -------------------------------------------------
        # CODE PANEL
        # -------------------------------------------------

        self.code_panel = load_image(
            CODE_PANEL_PATH
        )

    # =====================================================
    # BACKGROUND
    # =====================================================

    def draw_background(self, screen):

        if self.background_scaled:

            screen.blit(
                self.background_scaled,
                (0, 0)
            )

        else:

            # Fallback jeżeli nie ma background.png

            screen.fill(
                (30, 30, 30)
            )

    # =====================================================
    # RECT OBIEKTU
    # =====================================================

    @staticmethod
    def get_object_rect(obj):

        # Najpierw standardowe rect

        if hasattr(obj, "rect"):

            return obj.rect

        # Niektóre klasy mogą używać hitbox

        if hasattr(obj, "hitbox"):

            return obj.hitbox

        # Albo collider

        if hasattr(obj, "collider"):

            return obj.collider

        return None

    # =====================================================
    # STAN BOOLEAN
    # =====================================================

    @staticmethod
    def get_bool_state(obj, names):

        """
        Szuka pierwszego istniejącego atrybutu
        z listy names.
        """

        for name in names:

            if hasattr(obj, name):

                value = getattr(
                    obj,
                    name
                )

                if isinstance(value, bool):

                    return value

        return False

    # =====================================================
    # NAZWA KLASY
    # =====================================================

    @staticmethod
    def get_object_type(obj):

        """
        Pobiera nazwę klasy obiektu.

        Dzięki temu nie musimy importować:
        Door
        Lever
        ScoringPlate

        itd.
        """

        return obj.__class__.__name__.lower()

    # =====================================================
    # DOPASOWANIE GRAFIKI DO RECT
    # =====================================================

    @staticmethod
    def draw_image_to_rect(
        screen,
        image,
        rect
    ):

        if image is None:
            return

        if rect is None:
            return

        # Skalowanie grafiki do rozmiaru obiektu

        scaled = pygame.transform.smoothscale(
            image,
            (
                max(1, rect.width),
                max(1, rect.height)
            )
        )

        screen.blit(
            scaled,
            rect.topleft
        )

    # =====================================================
    # DRAW DOOR
    # =====================================================

    def draw_door(
        self,
        screen,
        obj
    ):

        rect = self.get_object_rect(obj)

        if rect is None:
            return

        is_open = self.get_bool_state(
            obj,
            [
                "is_open",
                "opened",
                "open",
                "active"
            ]
        )

        if is_open:

            image = self.door_open

        else:

            image = self.door_closed

        self.draw_image_to_rect(
            screen,
            image,
            rect
        )

    # =====================================================
    # DRAW LEVER
    # =====================================================

    def draw_lever(
        self,
        screen,
        obj
    ):

        rect = self.get_object_rect(obj)

        if rect is None:
            return

        is_on = self.get_bool_state(
            obj,
            [
                "activated",
                "active",
                "is_active",
                "on",
                "is_on",
                "triggered",
                "used"
            ]
        )

        if is_on:

            image = self.lever_on

        else:

            image = self.lever_off

        self.draw_image_to_rect(
            screen,
            image,
            rect
        )

    # =====================================================
    # DRAW SCORING PLATE
    # =====================================================

    def draw_scoring_plate(
        self,
        screen,
        obj
    ):

        rect = self.get_object_rect(obj)

        if rect is None:
            return

        active = self.get_bool_state(
            obj,
            [
                "pressed",
                "active",
                "is_active",
                "activated",
                "triggered",
                "occupied"
            ]
        )

        if active:

            image = self.scoring_plate_active

        else:

            image = self.scoring_plate

        self.draw_image_to_rect(
            screen,
            image,
            rect
        )

    # =====================================================
    # DRAW CODE PANEL
    # =====================================================

    def draw_code_panel(
        self,
        screen,
        obj
    ):

        rect = self.get_object_rect(obj)

        if rect is None:
            return

        self.draw_image_to_rect(
            screen,
            self.code_panel,
            rect
        )

    # =====================================================
    # DRAW INTERACTIVE ART
    # =====================================================

    def draw_interactive_art(
        self,
        screen,
        interactive_objects
    ):

        for obj in interactive_objects:

            object_type = self.get_object_type(
                obj
            )

            # -------------------------------------------------
            # DOOR
            # -------------------------------------------------

            if (
                "door" in object_type
                or "drzwi" in object_type
            ):

                self.draw_door(
                    screen,
                    obj
                )

            # -------------------------------------------------
            # LEVER
            # -------------------------------------------------

            elif (
                "lever" in object_type
                or "switch" in object_type
                or "dzwign" in object_type
            ):

                self.draw_lever(
                    screen,
                    obj
                )

            # -------------------------------------------------
            # SCORING PLATE
            # -------------------------------------------------

            elif (
                "scoringplate" in object_type
                or "scoring_plate" in object_type
                or "pressureplate" in object_type
                or "pressure_plate" in object_type
                or "plate" in object_type
            ):

                self.draw_scoring_plate(
                    screen,
                    obj
                )

            # -------------------------------------------------
            # CODE PANEL
            # -------------------------------------------------

            elif isinstance(
                obj,
                CodePanel
            ):

                self.draw_code_panel(
                    screen,
                    obj
                )


# =========================================================
# TWORZENIE GRACZA
# =========================================================

def create_player(start_pos):

<<<<<<< HEAD
    player = Creature(
        start_pos[0],
        start_pos[1],
        "../pictures/ludzik.png"
    )

    # -----------------------------------------------------
    # IDLE
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # WALK
    # -----------------------------------------------------

    player.add_anim(
        "walk",
        [0, 1, 2, 3, 4, 5],
        3,
        3,
        speed=120,
        priority=Creature.PRIORITY_WALK,
        spritesheet_path="../pictures/ludzik.png",
        scale=2.0
    )

    # -----------------------------------------------------
    # ATTACK
    # -----------------------------------------------------

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

    player.set_walk_idle(
        "walk",
        "idle"
    )

    player.play("idle")

=======
    # Dodanie animacji (z domyślnym wyłapywaniem ewentualnego braku grafiki)
    try:
        player.add_anim("idle", [0], 3, 3, speed=100, priority=Creature.PRIORITY_IDLE,
                        spritesheet_path="../pictures/ludzik.png", scale=2.0)
        player.add_anim("walk", [0, 1, 2, 3, 4, 5], 3, 3, speed=150, priority=Creature.PRIORITY_WALK,
                        spritesheet_path="../pictures/ludzik.png", scale=2.0)
        player.add_anim("attack", list(range(19)), 5, 4, speed=35, loop=False,
                        priority=Creature.PRIORITY_ATTACK, spritesheet_path="../pictures/Gracz_atak.png", scale=0.5)
    except Exception as e:
        print(f"⚠️ Uwaga podczas ładowania animacji gracza: {e}")

    if hasattr(player, 'set_walk_idle'):
        player.set_walk_idle("walk", "idle")
    if hasattr(player, 'play'):
        player.play("idle")

>>>>>>> master
    return player


# =========================================================
# RESET GRY
# =========================================================

def reset_game(
    player,
    ghost,
    spawn_pos
):

    # -----------------------------------------------------
    # PLAYER
    # -----------------------------------------------------

    player.hp = 100

    player.pos.x = spawn_pos[0]
    player.pos.y = spawn_pos[1]
<<<<<<< HEAD

    player.vel_y = 0

    player.jumps_left = (
        player.max_jumps
    )

    player.is_grounded = False

    # -----------------------------------------------------
    # RESET ANIMATION
    # -----------------------------------------------------

    player.current_priority = 0

    if player.sprite:

        for animation in (
            player.sprite.animations.values()
        ):

            animation.reset()

    player.play("idle")

    # -----------------------------------------------------
    # GHOST
    # -----------------------------------------------------

=======
    if hasattr(player, 'vel_y'):
        player.vel_y = 0
>>>>>>> master
    ghost.hp = 50

    ghost.pos.x = spawn_pos[0]
    ghost.pos.y = spawn_pos[1]

    ghost.update_rect()

<<<<<<< HEAD
=======
def move_ghost_with_collisions(ghost, dx, dy, platforms):
    """Przesuwa ducha z precyzyjną kolizją w osiach X i Y."""
    # Użyj istniejącego rect zamiast tworzyć nowy
    if not hasattr(ghost, 'rect') or ghost.rect is None:
        width = getattr(ghost, 'width', getattr(ghost, 'size', 32))
        height = getattr(ghost, 'height', getattr(ghost, 'size', 32))
        ghost.rect = pygame.Rect(int(ghost.pos.x), int(ghost.pos.y), width, height)

    ghost_rect = ghost.rect.copy()
>>>>>>> master

<<<<<<< HEAD
# =========================================================
# KOLIZJE DUCHA
# =========================================================

def move_ghost_with_collisions(
    ghost,
    dx,
    dy,
    platforms
):

    width = getattr(
        ghost,
        "width",
        30
    )

    height = getattr(
        ghost,
        "height",
        30
    )

    ghost_rect = pygame.Rect(
        int(
            ghost.pos.x
            - width / 2
        ),
        int(
            ghost.pos.y
            - height / 2
        ),
        width,
        height
    )

    # =====================================================
    # X
    # =====================================================

=======
>>>>>>> master
    ghost_rect.x += int(dx)

    for p in platforms:
<<<<<<< HEAD

        if hasattr(
            p,
            "rect"
        ):

            plat_rect = p.rect

        else:

            plat_rect = pygame.Rect(
                p[0],
                p[1],
                p[2],
                p[3]
            )

        if ghost_rect.colliderect(
            plat_rect
        ):

=======
        plat_rect = p.rect if hasattr(p, 'rect') else (
            pygame.Rect(p[0], p[1], p[2], p[3]) if isinstance(p, (tuple, list)) else p)
        if ghost_rect.colliderect(plat_rect):
>>>>>>> master
            if dx > 0:

                ghost_rect.right = (
                    plat_rect.left
                )

            elif dx < 0:

<<<<<<< HEAD
                ghost_rect.left = (
                    plat_rect.right
                )

    # =====================================================
    # Y
    # =====================================================

=======
>>>>>>> master
    ghost_rect.y += int(dy)

    for p in platforms:
<<<<<<< HEAD

        if hasattr(
            p,
            "rect"
        ):

            plat_rect = p.rect

        else:

            plat_rect = pygame.Rect(
                p[0],
                p[1],
                p[2],
                p[3]
            )

        if ghost_rect.colliderect(
            plat_rect
        ):

=======
        plat_rect = p.rect if hasattr(p, 'rect') else (
            pygame.Rect(p[0], p[1], p[2], p[3]) if isinstance(p, (tuple, list)) else p)
        if ghost_rect.colliderect(plat_rect):
>>>>>>> master
            if dy > 0:

                ghost_rect.bottom = (
                    plat_rect.top
                )

            elif dy < 0:

<<<<<<< HEAD
                ghost_rect.top = (
                    plat_rect.bottom
                )

    # =====================================================
    # POZYCJA
    # =====================================================

    ghost.pos.x = (
        ghost_rect.centerx
    )

    ghost.pos.y = (
        ghost_rect.centery
    )

    ghost.update_rect()
=======
    ghost.pos.x = float(ghost_rect.x)
    ghost.pos.y = float(ghost_rect.y)
    ghost.rect.topleft = (ghost_rect.x, ghost_rect.y)
>>>>>>> master


# =========================================================
# MAIN
# =========================================================

<<<<<<< HEAD
def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (
            WIDTH,
            HEIGHT
        )
    )

    pygame.display.set_caption(
        "Alien space"
    )

    clock = pygame.time.Clock()

    # =====================================================
    # ART
    # =====================================================

    art_manager = ArtManager(
        WIDTH,
        HEIGHT
    )

    # =====================================================
    # LEVEL
    # =====================================================

    level = load_level(
        "../levels/level.txt"
    )

    interactive_mgr = (
        level.interactive_manager
    )

    platform_mgr = PlatformManager(
        "../pictures/platforma.png",
        level.platforms
    )

    projectile_mgr = ProjectileManager()

    # =====================================================
    # POSTACIE
    # =====================================================

    player = create_player(
        level.player_pos
    )

    ghost = GhostMouse(
        level.player_pos[0],
        level.player_pos[1]
    )
=======
def load_selected_level(level_filename):
    """Funkcja pomocnicza ładowania wskazanego pliku poziomu."""
    # Ścieżka elastyczna (sprawdza katalog główny i katalog levels)
    try:
        level = load_level(f"../levels/{level_filename}")
    except FileNotFoundError:
        level = load_level(level_filename)

    interactive_mgr = level.interactive_manager
    platform_mgr = PlatformManager("../pictures/platforma.png", level.platforms)
    projectile_mgr = ProjectileManager()

    player = create_player(level.player_pos)
    ghost = GhostMouse(level.player_pos[0], level.player_pos[1])
>>>>>>> master

    char_mgr = CharacterManager()

<<<<<<< HEAD
    char_mgr.add(
        "player",
        player
    )

    char_mgr.add(
        "ghost",
        ghost
    )

    # =====================================================
    # MENU
    # =====================================================

    main_menu = MainMenu(
        WIDTH,
        HEIGHT
    )

    options_menu = OptionsMenu(
        WIDTH,
        HEIGHT
    )

    credits_menu = CreditsMenu(
        WIDTH,
        HEIGHT
    )

    failure_menu = FailureMenu(
        WIDTH,
        HEIGHT
    )

    victory_menu = VictoryMenu(
        WIDTH,
        HEIGHT
    )

    pause_menu = PauseMenu(
        WIDTH,
        HEIGHT
    )

    # =====================================================
    # STAN
    # =====================================================
=======
    return level, interactive_mgr, platform_mgr, projectile_mgr, player, ghost, char_mgr


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Alien Space")
    clock = pygame.time.Clock()

    # Domyślny poziom
    current_level_file = "level1.txt"
    level, interactive_mgr, platform_mgr, projectile_mgr, player, ghost, char_mgr = load_selected_level(
        current_level_file)

    # --- MENUS ---
    available_levels = ["level1.txt", "level2.txt"]
    main_menu = MainMenu(WIDTH, HEIGHT)
    level_select_menu = LevelSelectMenu(WIDTH, HEIGHT, available_levels)
    options_menu = OptionsMenu(WIDTH, HEIGHT)
    credits_menu = CreditsMenu(WIDTH, HEIGHT)
    failure_menu = FailureMenu(WIDTH, HEIGHT)
    victory_menu = VictoryMenu(WIDTH, HEIGHT)
    pause_menu = PauseMenu(WIDTH, HEIGHT)
>>>>>>> master

    current_state = MENU
    previous_state = MENU

    running = True

    attack_locked = False

    pygame.mouse.get_rel()

<<<<<<< HEAD
    # =====================================================
    # PĘTLA
    # =====================================================

    while running:

        # dt w sekundach

        dt = (
            clock.tick(FPS)
            / 1000.0
        )

        mouse_dx = 0
        mouse_dy = 0

        # =================================================
        # EVENTY
        # =================================================

        for event in pygame.event.get():

            # -------------------------------------------------
            # QUIT
            # -------------------------------------------------

=======
    # =========================================================
    # PĘTLA GŁÓWNA GRY
    # =========================================================
    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_dx, mouse_dy = 0, 0

        # ----------------------------------------------------
        # 1. OBSŁUGA ZDARZEŃ (INPUT)
        # ----------------------------------------------------
        for event in pygame.event.get():
>>>>>>> master
            if event.type == pygame.QUIT:

                running = False

<<<<<<< HEAD
            # -------------------------------------------------
            # OPTIONS
            # -------------------------------------------------

            if current_state == OPTIONS:

                options_menu.handle_event(
                    event
                )

            # =================================================
            # KEYBOARD
            # =================================================

=======
            if current_state == OPTIONS:
                if hasattr(options_menu, 'handle_event'):
                    options_menu.handle_event(event)

            # Obsługa przycisków klawiatury
>>>>>>> master
            if event.type == pygame.KEYDOWN:

                # -------------------------------------------------
                # ESC
                # -------------------------------------------------

                if event.key == pygame.K_ESCAPE:

                    if current_state == PLAYING:

                        current_state = PAUSE

                        pause_menu.active = True

                        pygame.mouse.set_visible(
                            True
                        )

                        pygame.event.set_grab(
                            False
                        )

                    elif current_state == PAUSE:

                        current_state = PLAYING

                        pause_menu.active = False

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

                        pygame.mouse.get_rel()

<<<<<<< HEAD
                # -------------------------------------------------
                # GAME KEYS
                # -------------------------------------------------

=======
                if current_state == PLAYING:
                    if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
                        if hasattr(player, 'jump'):
                            player.jump()
                    if event.key == pygame.K_2 and hasattr(player, 'play'):
                        player.play("attack")

            elif event.type == pygame.MOUSEMOTION:
>>>>>>> master
                if current_state == PLAYING:

                    # JUMP

                    if event.key == pygame.K_w:

                        player.jump()

                    # ATTACK

                    if event.key == pygame.K_2:

                        if not player.is_attacking():

                            player.play(
                                "attack"
                            )

                            attack_locked = True

            # =================================================
            # MOUSE MOTION
            # =================================================

            elif event.type == pygame.MOUSEMOTION:

                if current_state == PLAYING:

                    dx, dy = event.rel

                    mouse_dx += dx
                    mouse_dy += dy

<<<<<<< HEAD
            # =================================================
            # LEFT CLICK
            # =================================================

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                # -------------------------------------------------
                # PLAYING
                # -------------------------------------------------

                if current_state == PLAYING:

                    interactive_mgr.handle_event_all(
                        event
                    )

                # -------------------------------------------------
                # MENU
                # -------------------------------------------------

                elif current_state == MENU:

                    action = main_menu.handle_click(
                        event.pos,
                        (1, 0, 0)
                    )

                    if action == "play":

                        reset_game(
                            player,
                            ghost,
                            level.player_pos
                        )

                        attack_locked = False

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

                        pygame.mouse.get_rel()

                        current_state = PLAYING

=======
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_state == PLAYING:
                    if hasattr(interactive_mgr, 'handle_event_all'):
                        interactive_mgr.handle_event_all(event)
                    elif hasattr(interactive_mgr, 'handle_event'):
                        interactive_mgr.handle_event(event)

                elif current_state == MENU:
                    action = main_menu.handle_click(event.pos, (1, 0, 0))
                    if action == "level_select":
                        previous_state = MENU
                        current_state = LEVEL_SELECT
>>>>>>> master
                    elif action == "options":

                        previous_state = MENU

                        current_state = OPTIONS

                    elif action == "credits":

                        current_state = CREDITS

                    elif action == "quit":

                        running = False

<<<<<<< HEAD
                # -------------------------------------------------
                # PAUSE
                # -------------------------------------------------
=======
                elif current_state == LEVEL_SELECT:
                    action = level_select_menu.handle_input(event.pos, (1, 0, 0))
                    if action == "back":
                        current_state = previous_state
                    elif action and action.startswith("load_"):
                        level_file = action.replace("load_", "")
                        current_level_file = level_file
                        level, interactive_mgr, platform_mgr, projectile_mgr, player, ghost, char_mgr = load_selected_level(
                            current_level_file)

                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()
                        current_state = PLAYING
>>>>>>> master

                elif current_state == PAUSE:

                    action = pause_menu.handle_input(
                        event.pos,
                        (1, 0, 0)
                    )

                    if action == "resume":

                        pause_menu.active = False

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

                        pygame.mouse.get_rel()

                        current_state = PLAYING
<<<<<<< HEAD

=======
                    elif action == "level_select":
                        pause_menu.active = False
                        previous_state = PAUSE
                        current_state = LEVEL_SELECT
>>>>>>> master
                    elif action == "options":

                        previous_state = PAUSE

                        current_state = OPTIONS

                    elif action == "main_menu":

                        pause_menu.active = False

                        pygame.mouse.set_visible(
                            True
                        )

                        pygame.event.set_grab(
                            False
                        )

                        current_state = MENU

                # -------------------------------------------------
                # OPTIONS
                # -------------------------------------------------

                elif current_state == OPTIONS:

                    action = options_menu.handle_input(
                        event.pos,
                        (1, 0, 0)
                    )

                    if action == "back":

                        current_state = (
                            previous_state
                        )

                # -------------------------------------------------
                # CREDITS
                # -------------------------------------------------

                elif current_state == CREDITS:

                    action = credits_menu.handle_input(
                        event.pos,
                        (1, 0, 0)
                    )

                    if action == "back":

                        current_state = MENU

                # -------------------------------------------------
                # FAILURE
                # -------------------------------------------------

                elif current_state == FAILURE:

                    action = failure_menu.handle_input(
                        event.pos,
                        (1, 0, 0)
                    )

                    if action == "retry":
<<<<<<< HEAD

                        reset_game(
                            player,
                            ghost,
                            level.player_pos
                        )

                        attack_locked = False

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

=======
                        level, interactive_mgr, platform_mgr, projectile_mgr, player, ghost, char_mgr = load_selected_level(
                            current_level_file)
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
>>>>>>> master
                        pygame.mouse.get_rel()

                        current_state = PLAYING

                    elif action == "menu":

                        current_state = MENU

                # -------------------------------------------------
                # VICTORY
                # -------------------------------------------------

                elif current_state == VICTORY:
<<<<<<< HEAD

                    action = victory_menu.handle_input(
                        event.pos,
                        (1, 0, 0)
                    )

                    if action == "next":

                        reset_game(
                            player,
                            ghost,
                            level.player_pos
                        )

                        attack_locked = False

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

                        pygame.mouse.get_rel()

                        current_state = PLAYING

=======
                    action = victory_menu.handle_input(event.pos, (1, 0, 0))
                    if action == "level_select":
                        previous_state = MENU
                        current_state = LEVEL_SELECT
>>>>>>> master
                    elif action == "menu":

                        current_state = MENU

<<<<<<< HEAD
        # =====================================================
        # UPDATE
        # =====================================================

=======
            # Zdarzenia dla obiektów interaktywnych (dźwignie, klawiatura w codepanelu)
            if current_state == PLAYING:
                if hasattr(interactive_mgr, 'handle_event'):
                    interactive_mgr.handle_event(event)

        # ----------------------------------------------------
        # 2. AKTUALIZACJA LOGIKI (UPDATE)
        # ----------------------------------------------------
>>>>>>> master
        if current_state == MENU:

            main_menu.update()
<<<<<<< HEAD

=======
        elif current_state == LEVEL_SELECT:
            level_select_menu.update()
>>>>>>> master
        elif current_state == PAUSE:

            pause_menu.update()

        elif current_state == OPTIONS:

            options_menu.update()

        elif current_state == CREDITS:

            credits_menu.update()

        elif current_state == FAILURE:

            failure_menu.update()

        elif current_state == VICTORY:

            victory_menu.update()

        # =====================================================
        # PLAYING
        # =====================================================

        elif current_state == PLAYING:
<<<<<<< HEAD

            # -------------------------------------------------
            # PRZESZKODY
            # -------------------------------------------------

            solid_interactive = [
                obj
                for obj in interactive_mgr.objects
                if (
                    hasattr(
                        obj,
                        "is_open"
                    )
                    and not obj.is_open
                    and not isinstance(
                        obj,
                        CodePanel
                    )
                )
=======
            # Ruch gracza
            keys = pygame.key.get_pressed()
            move_x = 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_x -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_x += 1

            if hasattr(player, 'move'):
                player.move(move_x)
            elif hasattr(player, 'vel_x'):
                speed = getattr(player, 'speed', 200)
                player.vel_x = move_x * speed

            # Pobranie zamkniecia obiektów interaktywnych jako barier
            interactive_objs = getattr(interactive_mgr, 'objects', [])
            solid_interactive = [
                obj for obj in interactive_objs
                if hasattr(obj, 'is_open') and not obj.is_open and not isinstance(obj, CodePanel)
>>>>>>> master
            ]

<<<<<<< HEAD
            all_obstacles = (
                platform_mgr.platforms
                + solid_interactive
            )

            # -------------------------------------------------
            # GHOST
            # -------------------------------------------------

            if (
                mouse_dx != 0
                or mouse_dy != 0
            ):

                move_ghost_with_collisions(
                    ghost,
                    mouse_dx,
                    mouse_dy,
                    all_obstacles
                )

            # -------------------------------------------------
            # POSTACIE
            # -------------------------------------------------

            char_mgr.update_all(
                dt,
                platforms=all_obstacles
            )

            # -------------------------------------------------
            # ATAK
            # -------------------------------------------------

            if attack_locked:

                if not player.is_attacking():

                    attack_locked = False

            # -------------------------------------------------
            # ENEMIES
            # -------------------------------------------------

            for enemy in level.enemies:

                enemy.update(
                    dt,
                    player_pos=player.pos,
                    platforms=platform_mgr.platforms
                )

                distance = (
                    enemy.pos
                    - player.pos
                ).length()

                if (
                    distance
                    < enemy.detection_range
                    and enemy.shoot_cooldown <= 0
                ):

                    projectile_mgr.add(
                        enemy.shoot(
                            player.pos.x,
                            player.pos.y
                        )
                    )

                    enemy.shoot_cooldown = (
                        enemy.shoot_interval
                    )

            # -------------------------------------------------
            # PROJECTILES
            # -------------------------------------------------

            projectile_mgr.update(
                dt
            )

            # -------------------------------------------------
            # INTERACTIVE
            # -------------------------------------------------

            interactive_mgr.update_all(
                player,
                ghost,
                dt
            )

        # =====================================================
        # DRAW
        # =====================================================

        # -----------------------------------------------------
        # BACKGROUND
        # -----------------------------------------------------

        if current_state in (
            PLAYING,
            PAUSE
        ):

            art_manager.draw_background(
                screen
            )

        else:

            screen.fill(
                (30, 30, 30)
            )

        # =====================================================
        # GAME / PAUSE
        # =====================================================

        if current_state in (
            PLAYING,
            PAUSE
        ):

            # -------------------------------------------------
            # PLATFORMS
            # -------------------------------------------------

            platform_mgr.draw(
                screen
            )

            # -------------------------------------------------
            # EXISTING INTERACTIVE DRAW
            # -------------------------------------------------

            interactive_mgr.draw_all(
                screen
            )

            # -------------------------------------------------
            # CUSTOM ART
            # -------------------------------------------------

            art_manager.draw_interactive_art(
                screen,
                interactive_mgr.objects
            )

            # -------------------------------------------------
            # CHARACTERS
            # -------------------------------------------------

            char_mgr.draw_all(
                screen
            )

            # -------------------------------------------------
            # ENEMIES
            # -------------------------------------------------

            for enemy in level.enemies:

                enemy.draw(
                    screen
                )

            # -------------------------------------------------
            # PROJECTILES
            # -------------------------------------------------

            projectile_mgr.draw_all(
                screen
            )

            # -------------------------------------------------
            # HUD
            # -------------------------------------------------

            font = pygame.font.Font(
                None,
                32
            )

            hud_text = font.render(
                (
                    f"Player HP: {player.hp} | "
                    f"Ghost HP: {ghost.hp} | "
                    f"Power: {player.power}"
                ),
                True,
                (255, 255, 255)
            )

            screen.blit(
                hud_text,
                (10, 10)
=======
            # Ruch duchem myszy
            if mouse_dx != 0 or mouse_dy != 0:
                move_ghost_with_collisions(ghost, mouse_dx, mouse_dy, all_obstacles)

            # Aktualizacja postaci
            if hasattr(char_mgr, 'update_all'):
                char_mgr.update_all(dt, platforms=all_obstacles)
            elif hasattr(char_mgr, 'update'):
                char_mgr.update(dt, platforms=all_obstacles)
            else:
                player.update(dt, platforms=all_obstacles)
                ghost.update(dt, platforms=all_obstacles)

            # Aktualizacja wrogów i ich strzelanie
            for enemy in level.enemies:
                enemy.update(dt, player_pos=player.pos, platforms=platform_mgr)

                # Obsługa wystrzału
                if getattr(enemy, 'shoot_cooldown', 0) <= 0:
                    if hasattr(enemy, 'shoot'):
                        proj = enemy.shoot(player.pos.x, player.pos.y)
                        if proj:
                            projectile_mgr.add(proj)

            # Aktualizacja pocisków
            projectile_mgr.update(dt)

            # Kolizje pocisków z graczem
            for proj in projectile_mgr.get_projectiles():
                if hasattr(player, 'rect') and player.rect.colliderect(proj.rect):
                    player.hp -= getattr(proj, 'damage', 10)
                    proj.is_dead = True
                    print(f"💥 Trafienie! HP gracza: {player.hp}")

            # Sprawdzenie warunków przegranej
            if player.hp <= 0:
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
                current_state = FAILURE

            # Aktualizacja obiektów interaktywnych
            if hasattr(interactive_mgr, 'update_all'):
                interactive_mgr.update_all(player, ghost, dt)
            elif hasattr(interactive_mgr, 'update'):
                interactive_mgr.update(player, ghost, dt)

            # Sprawdzenie ukończenia poziomu (wygrana / LevelGate)
            for obj in interactive_mgr:
                if getattr(obj, "triggered", False):
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    current_state = VICTORY
                    obj.triggered = False

        # ----------------------------------------------------
        # 3. RYSOWANIE EKRANU (DRAW)
        # ----------------------------------------------------
        screen.fill((30, 30, 40))

        if current_state in (PLAYING, PAUSE):
            # Platformy i tło
            platform_mgr.draw(screen)

            # Interakcje i obiekty
            if hasattr(interactive_mgr, 'draw_all'):
                interactive_mgr.draw_all(screen)
            elif hasattr(interactive_mgr, 'draw'):
                interactive_mgr.draw(screen)

            # Postacie
            if hasattr(char_mgr, 'draw_all'):
                char_mgr.draw_all(screen)
            elif hasattr(char_mgr, 'draw'):
                char_mgr.draw(screen)
            else:
                player.draw(screen)
                ghost.draw(screen)

            # Wrogowie
            for enemy in level.enemies:
                if hasattr(enemy, 'is_alive') and enemy.is_alive():
                    enemy.draw(screen)
                elif not hasattr(enemy, 'is_alive'):
                    enemy.draw(screen)

            # Pociski
            if hasattr(projectile_mgr, 'draw_all'):
                projectile_mgr.draw_all(screen)
            elif hasattr(projectile_mgr, 'draw'):
                projectile_mgr.draw(screen)

            # HUD / Statystyki
            font = pygame.font.Font(None, 32)
            player_power = getattr(player, 'power', 0)
            hud_text = font.render(
                f"Player HP: {player.hp} | Ghost HP: {ghost.hp} | Power: {player_power}",
                True, (255, 255, 255)
>>>>>>> master
            )

            info = font.render(
<<<<<<< HEAD
                (
                    "A/D = Move, "
                    "W = Jump, "
                    "S = Fast Fall, "
                    "2 = Attack, "
                    "ESC = Pause"
                ),
                True,
                (200, 200, 200)
=======
                "A/D = Move, W/Space = Jump, 2 = Attack, ESC = Pause",
                True, (200, 200, 200)
>>>>>>> master
            )

            screen.blit(
                info,
                (10, 50)
            )

            # -------------------------------------------------
            # PAUSE
            # -------------------------------------------------

            # Menu pauzy rysowane na wierzchu gry
            if current_state == PAUSE:

                pause_menu.draw(
                    screen
                )

        # =====================================================
        # MENU
        # =====================================================

        elif current_state == MENU:
<<<<<<< HEAD

            main_menu.draw(
                screen
            )

=======
            main_menu.draw(screen)
        elif current_state == LEVEL_SELECT:
            level_select_menu.draw(screen)
>>>>>>> master
        elif current_state == OPTIONS:

            options_menu.draw(
                screen
            )

        elif current_state == CREDITS:

            credits_menu.draw(
                screen
            )

        elif current_state == FAILURE:

            failure_menu.draw(
                screen
            )

        elif current_state == VICTORY:

            victory_menu.draw(
                screen
            )

        # =====================================================
        # DISPLAY
        # =====================================================

        pygame.display.flip()

    pygame.quit()

    sys.exit()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()
