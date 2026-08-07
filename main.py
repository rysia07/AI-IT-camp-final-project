import sys
import pygame

from Characters import Creature, GhostMouse, CharacterManager
from Interactive import (
    Lever,
    CodePanel,
    ScoringButton,
    LevelGate
)
from GUI import MainMenu
from Platforms import PlatformManager
from options_menu import OptionsMenu
from credits_menu import CreditsMenu


# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()

WIDTH, HEIGHT = 900, 600

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Game - ludzik.png with Animations"
)

clock = pygame.time.Clock()

# =========================================================
# MYSZKA
# =========================================================

# Przywracamy normalny kursor
pygame.mouse.set_visible(True)


# =========================================================
# PLATFORMY
# =========================================================

platform_mgr = PlatformManager(
    "kievinay-train-6558870_1920.png"
)


# =========================================================
# CHARACTERS
# =========================================================

manager = CharacterManager()


player = Creature(
    450,
    300,
    "ludzik.png"
)

player.movement_threshold = 0.1


player.add_anim(
    "idle",
    frames=[0],
    cols=3,
    rows=3,
    priority=Creature.PRIORITY_IDLE
)

player.add_anim(
    "walk",
    frames=[0, 1, 2, 3, 4, 5],
    cols=3,
    rows=3,
    speed=150,
    priority=Creature.PRIORITY_WALK
)

player.add_anim(
    "attack",
    frames=[6, 7, 8],
    cols=3,
    rows=3,
    speed=300,
    loop=False,
    priority=Creature.PRIORITY_ATTACK
)

player.set_walk_idle(
    "walk",
    "idle"
)

player.play("idle")


# =========================================================
# GHOST
# =========================================================

ghost = GhostMouse(
    0,
    0
)


manager.add(
    "player",
    player
)

manager.add(
    "ghost",
    ghost
)


# =========================================================
# INTERACTIVE OBJECTS
# =========================================================

lever = Lever(
    500,
    300
)

panel = CodePanel(
    700,
    300
)

button = ScoringButton(
    250,
    500,
    1
)

gate = LevelGate(
    1100,
    500
)

objects = [
    lever,
    panel,
    button,
    gate
]


# =========================================================
# MENU / GAME STATE
# =========================================================

MENU = 0
PLAYING = 1
OPTIONS = 2
CREDITS = 3

current_state = MENU

menu = MainMenu(
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


# =========================================================
# GAME LOOP
# =========================================================

running = True

while running:

    # =====================================================
    # TIME
    # =====================================================

    dt = clock.tick(60) / 1000.0

    # =====================================================
    # EVENTS
    # =====================================================

    events = pygame.event.get()

    mouse_pos = pygame.mouse.get_pos()

    for event in events:

        if event.type == pygame.QUIT:

            running = False

        # ---------------------------------------------
        # ESC
        # ---------------------------------------------

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE

        ):
            pygame.mouse.set_visible(True)
            if current_state == OPTIONS:
                options_menu.active = False
            elif current_state == CREDITS:
                credits_menu.active = False
            current_state = MENU

        # =================================================
        # GAME EVENTS
        # =================================================

        if current_state == PLAYING:

            # Atak
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_2
            ):

                player.play(
                    "attack"
                )

            # Interaktywne obiekty
            for obj in objects:

                obj.handle_event(event)

        # =================================================
        # MENU EVENTS
        # =================================================

        elif current_state == MENU:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                clicked = menu.handle_click(
                    event.pos,
                    (1, 0, 0)
                )

                if clicked == "play":
                    pygame.mouse.set_visible(False)
                    current_state = PLAYING

                elif clicked == "quit":

                    running = False

                elif clicked == "options":
                    options_menu.active = True
                    current_state = OPTIONS
                    pygame.mouse.set_visible(True)

                elif clicked == "credits":
                    credits_menu.active = True
                    current_state = CREDITS
                    pygame.mouse.set_visible(True)

        elif current_state == OPTIONS:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                action = options_menu.handle_input()

                if action == "back":
                    options_menu.active = False
                    current_state = MENU

        elif current_state == CREDITS:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                action = credits_menu.handle_input()

                if action == "back":
                    credits_menu.active = False
                    current_state = MENU

    # =====================================================
    # UPDATE
    # =====================================================

    if current_state == PLAYING:

        manager.update_all(
            dt,
            platform_mgr.platforms
        )

        for obj in objects:

            obj.update(
                player,
                ghost
            )

    elif current_state == MENU:

        menu.update(
            mouse_pos
        )

    elif current_state == OPTIONS:

        options_menu.update(
            mouse_pos
        )

    elif current_state == CREDITS:

        credits_menu.update(
            mouse_pos
        )

    # =====================================================
    # DRAW
    # =====================================================

    screen.fill(
        (30, 30, 30)
    )

    # =====================================================
    # MENU
    # =====================================================

    if current_state == MENU:

        menu.draw(
            screen
        )

    elif current_state == OPTIONS:

        options_menu.draw(
            screen
        )

    elif current_state == CREDITS:

        credits_menu.draw(
            screen
        )

    # =====================================================
    # GAME
    # =====================================================

    elif current_state == PLAYING:

        # ---------------------------------------------
        # PLATFORMY
        # ---------------------------------------------

        for platform in platform_mgr.platforms:

            platform_mgr.draw(
                screen
            )

        # ---------------------------------------------
        # POSTACIE
        # ---------------------------------------------

        manager.draw_all(
            screen
        )

        # ---------------------------------------------
        # OBIEKTY
        # ---------------------------------------------

        for obj in objects:

            obj.draw(
                screen
            )

        # ---------------------------------------------
        # UI
        # ---------------------------------------------

        font = pygame.font.Font(
            None,
            32
        )

        text = font.render(
            f"Animation: {player.current_anim} | "
            f"Grounded: {player.is_grounded}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            text,
            (10, 10)
        )

        info = font.render(
            "A/D = Move, W = Jump, S = Fast Fall, "
            "2 = Attack, ESC = Menu",
            True,
            (200, 200, 200)
        )

        screen.blit(
            info,
            (10, 50)
        )

    # =====================================================
    # DISPLAY
    # =====================================================

    pygame.display.flip()


# =========================================================
# EXIT
# =========================================================

pygame.quit()
sys.exit()