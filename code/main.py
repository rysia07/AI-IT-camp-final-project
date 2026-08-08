import sys
import pygame

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

pygame.init()

WIDTH, HEIGHT = 900, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Placeholder")

clock = pygame.time.Clock()

# Przywracamy normalny kursor
pygame.mouse.set_visible(True)

# =========================================================
# PLATFORMY
# =========================================================

platform_mgr = PlatformManager("../pictures/kievinay-train-6558870_1920.png")

# =========================================================
# CHARACTERS
# =========================================================

manager = CharacterManager()

player = Creature(450, 300, "../pictures/ludzik.png")
player.movement_threshold = 0.1

player.add_anim("idle", frames=[0], cols=3, rows=3, priority=Creature.PRIORITY_IDLE)
player.add_anim("walk", frames=[0, 1, 2, 3, 4, 5], cols=3, rows=3, speed=150, priority=Creature.PRIORITY_WALK)
player.add_anim("attack", frames=[6, 7, 8], cols=3, rows=3, speed=300, loop=False, priority=Creature.PRIORITY_ATTACK)

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

    dt = clock.tick(60) / 1000.0
    events = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()

    # =====================================================
    # EVENTS
    # =====================================================
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if current_state == PLAYING:
            # Obsługa pojedynczych wciśnięć klawiszy (KEYDOWN)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:  # Lub K_SPACE
                    player.jump()

                if event.key == pygame.K_2:
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
        # 1. Aktualizacja fizyki postaci i platform
        manager.update_all(dt, platform_mgr.platforms)

        # 2. Aktualizacja obiektów interaktywnych
        interactive_manager.update_all(player, ghost)

    elif current_state == MENU:
        menu.update(mouse_pos)

    # =====================================================
    # DRAW
    # =====================================================

    screen.fill((30, 30, 30))

    if current_state == MENU:
        menu.draw(screen)

    elif current_state == PLAYING:
        # Platformy
        for platform in platform_mgr.platforms:
            platform_mgr.draw(screen)

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