import sys
import pygame
from LoadLevels import load_level


# Importujemy wszystkie potrzebne klasy z pliku Interactive.py
from Interactive import (
    Lever,
    CodePanel,
    ScoringButton,
    Door,
    LevelGate,
    InteractiveManager
)
from Characters import Creature, GhostMouse, CharacterManager
from GUI import MainMenu
from Platforms import PlatformManager

# =========================================================
# INITIALIZATION
# =========================================================

FPS = 60


pygame.init()

WIDTH, HEIGHT = 900, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Placeholder")

clock = pygame.time.Clock()

# Przywracamy normalny kursor
pygame.mouse.set_visible(True)
pygame.event.set_grab(True)

# =========================================================
# PLATFORMY
# =========================================================

level = load_level("../levels/level.txt")

platform_mgr = PlatformManager(
    "../pictures/platforma.png",
    level.platforms
)

interactive_manager = level.interactive_manager


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

interactive_manager = InteractiveManager()

# Dodajemy obiekty bezpośrednio do menedżeralever =

lever = Lever(300, 300, 100, 20, direction="left")

door = Door(700, 250, 30, 120, trigger_object=lever) # Drzwi otwierają się dźwignią!

interactive_manager.add(lever)
interactive_manager.add(door)
interactive_manager.add(CodePanel(700, 300, code="1234"))
interactive_manager.add(ScoringButton(490, 490, required_power=0))  # Power 0, żeby działało od razu
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

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mouse.set_visible(True)
            current_state = MENU

        # Eventy w grze
        if current_state == PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                player.play("attack")

            # Przekazujemy zdarzenia klawiatury do obiektów (np. do wpisania kodu)
            interactive_manager.handle_event_all(event)

        # Eventy w Menu
        elif current_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = menu.handle_click(event.pos, (1, 0, 0))

                if clicked == "play":
                    pygame.mouse.set_visible(False)
                    current_state = PLAYING
                elif clicked == "quit":
                    running = False
                elif clicked == "options":
                    print("Options pressed")
                elif clicked == "credits":
                    print("Credits pressed")

    # =====================================================
    # UPDATE
    # =====================================================

    if current_state == PLAYING:

        manager.update_all(
            dt,
            platform_mgr.platforms
        )

        interactive_manager.update_all(
            player,
            ghost
        )

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

        # Platforms

        platform_mgr.draw(screen)

        # Levers, doors, panels, etc.

        interactive_manager.draw_all(screen)

        # Characters

        manager.draw_all(screen)

        player.draw_hitbox(screen, "red")

        ghost.draw_hitbox(screen, "cyan")

        # Obiekty interaktywne
        interactive_manager.draw_all(screen)

        # Postacie & Hitboxy
        manager.draw_all(screen)
        player.draw_hitbox(screen, "red")
        ghost.draw_hitbox(screen, "cyan")

        # UI / Tekst
        font = pygame.font.Font(None, 32)
        text = font.render(
            f"Animation: {player.current_anim} | Grounded: {player.is_grounded}",
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

# =========================================================
# EXIT
# =========================================================

pygame.quit()
sys.exit()