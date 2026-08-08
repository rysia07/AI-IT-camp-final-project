import sys
import pygame
from LoadLevels import load_level

from Interactive import (
    Lever,
    CodePanel,
    ScoringButton,
    Door,
    LevelGate,
    InteractiveManager
)
from Platforms import PlatformManager
from Characters import Creature, GhostMouse, CharacterManager
from GUI import MainMenu
# =========================================================
# INITIALIZATION
# =========================================================

FPS = 60

pygame.init()

WIDTH, HEIGHT = 900, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_state = "normal"
pygame.display.set_caption("Placeholder")

clock = pygame.time.Clock()

pygame.mouse.set_visible(True)

interactive_manager = InteractiveManager()
# =========================================================
# PLATFORMY
# =========================================================

level = load_level("../levels/level.txt")

platform_mgr = PlatformManager(
    "../pictures/platforma.png",
    level.platforms
)

# =========================================================
# CHARACTERS
# =========================================================

manager = CharacterManager()

player = Creature(
    level.player_pos[0],
    level.player_pos[1],
    "../pictures/ludzik.png"
)

player.add_anim(
    "idle",
    frames=[0],
    cols=3,
    rows=3,
    speed=100,
    priority=Creature.PRIORITY_IDLE,
    spritesheet_path="../pictures/ludzik.png",
    scale=2.0
)

player.add_anim(
    "walk",
    frames=[0, 1, 2, 3, 4, 5],
    cols=3,
    rows=3,
    speed=150,
    priority=Creature.PRIORITY_WALK,
    spritesheet_path="../pictures/ludzik.png",
    scale=2.0
)

player.add_anim(
    "attack",
    frames=list(range(19)),
    cols=5,
    rows=4,
    speed=35,
    loop=False,
    priority=Creature.PRIORITY_ATTACK,
    spritesheet_path="../pictures/Gracz_atak.png",
    scale=0.5
)

player.set_walk_idle("walk", "idle")
player.play("idle")

ghost = GhostMouse(0, 0)

manager.add("player", player)
manager.add("ghost", ghost)

# =========================================================
# INTERACTIVE OBJECTS (Dźwignie, Panele itp.)
# =========================================================



lever = Lever(300, 300, 100, 20, direction="left")
door = Door(700, 250, 30, 120, trigger_object=lever)

interactive_manager.add(lever)
interactive_manager.add(door)
interactive_manager.add(CodePanel(700, 300, code="1234"))
interactive_manager.add(ScoringButton(490, 490, required_power=3))
interactive_manager.add(LevelGate(800, 400))

# =========================================================
# MENU / GAME STATE
# =========================================================

MENU = 0
PLAYING = 1
OPTIONS = 2
CREDITS = 3

current_state = MENU
menu = MainMenu(WIDTH, HEIGHT)

# =========================================================
# GAME LOOP
# =========================================================

running = True

while running:
    dt = clock.tick(FPS) / 1000.0
    events = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()

    # =====================================================
    # EVENTS
    # =====================================================
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if current_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    player.jump()

                if event.key == pygame.K_2:
                    player.play("attack")

                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    pygame.mouse.set_visible(True)

            interactive_manager.handle_event_all(event)

        elif current_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = menu.handle_click(event.pos, (1, 0, 0))

                if clicked == "play":
                    pygame.mouse.set_visible(False)
                    current_state = PLAYING
                elif clicked == "quit":
                    running = False

    # =====================================================
    # UPDATE
    # =====================================================

    if current_state == PLAYING:
        # Jedno poprawne wywołanie update_all dla wszystkich postaci z przekazaniem platform
        manager.update_all(dt, platform_mgr.platforms)

        # Aktualizacja interakcji
        interactive_manager.update_all(player, ghost)

        pygame.event.set_grab(True)

    elif current_state == MENU:
        menu.update(mouse_pos)
        pygame.event.set_grab(False)

    # =====================================================
    # DRAW
    # =====================================================

    screen.fill((30, 30, 30))

    if current_state == MENU:
        menu.draw(screen)

    elif current_state == PLAYING:
        platform_mgr.draw(screen)
        interactive_manager.draw_all(screen)
        manager.draw_all(screen)

        font = pygame.font.Font(None, 32)
        text = font.render(
            f"Power: {player.power} | Grounded: {player.is_grounded}",
            True,
            (255, 255, 255)
        )
        screen.blit(text, (10, 10))

        info = font.render(
            "A/D = Move, W = Jump, S = Fast Fall, 2 = Attack, ESC = Menu",
            True,
            (200, 200, 200)
        )
        screen.blit(info, (10, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()