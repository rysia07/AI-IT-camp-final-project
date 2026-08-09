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
from Characters import Creature, GhostMouse, CharacterManager
from GUI import MainMenu, OptionsMenu, CreditsMenu, FailureMenu, VictoryMenu
from Platforms import PlatformManager

# =========================================================
# INITIALIZATION
# =========================================================

FPS = 60

pygame.init()

WIDTH, HEIGHT = 900, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alien space")

clock = pygame.time.Clock()

pygame.mouse.set_visible(True)

# =========================================================
# PLATFORMY I POZIOM
# =========================================================

level = load_level("../levels/level.txt")

platform_mgr = PlatformManager(
    "../pictures/platforma.png",
    level.platforms
)

# =========================================================
# POSTACIE
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
# INTERAKTYWNE OBIEKTY
# =========================================================

interactive_manager = InteractiveManager()

lever = Lever(300, 300, 100, 20, "left")
door = Door(700, 250, 30, 120, trigger_object=lever)

interactive_manager.add(lever)
interactive_manager.add(door)
interactive_manager.add(CodePanel(700, 300, code="1234"))
interactive_manager.add(ScoringButton(490, 490, required_power=3))
interactive_manager.add(LevelGate(800, 400))

# =========================================================
# STANY GRY I MENU
# =========================================================

MENU = 0
PLAYING = 1
OPTIONS = 2
CREDITS = 3
FAILURE = 4
VICTORY = 5

current_state = MENU

menu = MainMenu(WIDTH, HEIGHT)
options_menu = OptionsMenu(WIDTH, HEIGHT)
credits_menu = CreditsMenu(WIDTH, HEIGHT)
failure_menu = FailureMenu(WIDTH, HEIGHT)
victory_menu = VictoryMenu(WIDTH, HEIGHT)

next_level = False


def reset_game():
    """Resetuje pozycje i punkty zdrowia graczy przy restarcie."""
    global next_level
    player.hp = 100
    player.pos.x = level.player_pos[0]
    player.pos.y = level.player_pos[1]
    player.vel_y = 0
    ghost.hp = 50
    ghost.pos.x = 0
    ghost.pos.y = 0
    next_level = False


# =========================================================
# PĘTLA GŁÓWNA
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

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_state in (OPTIONS, CREDITS, FAILURE, VICTORY):
                    current_state = MENU
                    pygame.mouse.set_visible(True)
                elif current_state == PLAYING:
                    current_state = MENU
                    pygame.mouse.set_visible(True)

            if current_state == PLAYING:
                if event.key == pygame.K_w:
                    player.jump()
                if event.key == pygame.K_2:
                    player.play("attack")

        if current_state == PLAYING:
            interactive_manager.handle_event_all(event)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == MENU:
                clicked = menu.handle_click(event.pos, (1, 0, 0))
                if clicked == "play":
                    reset_game()
                    pygame.mouse.set_visible(False)
                    current_state = PLAYING
                elif clicked == "options":
                    current_state = OPTIONS
                elif clicked == "credits":
                    current_state = CREDITS
                elif clicked == "quit":
                    running = False

            elif current_state == OPTIONS:
                action = options_menu.handle_input(event.pos, (1, 0, 0))
                if action == "back":
                    current_state = MENU

            elif current_state == CREDITS:
                action = credits_menu.handle_input(event.pos, (1, 0, 0))
                if action == "back":
                    current_state = MENU

            elif current_state == FAILURE:
                action = failure_menu.handle_input(event.pos, (1, 0, 0))
                if action == "retry":
                    reset_game()
                    pygame.mouse.set_visible(False)
                    current_state = PLAYING
                elif action == "menu":
                    current_state = MENU

            elif current_state == VICTORY:
                action = victory_menu.handle_input(event.pos, (1, 0, 0))
                if action == "next":
                    reset_game()
                    pygame.mouse.set_visible(False)
                    current_state = PLAYING
                elif action == "menu":
                    current_state = MENU

    # =====================================================
    # UPDATE
    # =====================================================

    if current_state == PLAYING:
        manager.update_all(dt, platform_mgr.platforms)
        interactive_manager.update_all(player, ghost)
        pygame.event.set_grab(True)

        # Warunki zakończenia rozgrywki:
        if player.hp <= 0 or ghost.hp <= 0:
            current_state = FAILURE
            pygame.mouse.set_visible(True)

        if next_level:
            current_state = VICTORY
            pygame.mouse.set_visible(True)

    else:
        pygame.event.set_grab(False)
        if current_state == MENU:
            menu.update(mouse_pos)
        elif current_state == OPTIONS:
            options_menu.update(mouse_pos)
        elif current_state == CREDITS:
            credits_menu.update(mouse_pos)
        elif current_state == FAILURE:
            failure_menu.update(mouse_pos)
        elif current_state == VICTORY:
            victory_menu.update(mouse_pos)

    # =====================================================
    # DRAW
    # =====================================================

    screen.fill((30, 30, 30))

    if current_state == MENU:
        menu.draw(screen)

    elif current_state == OPTIONS:
        options_menu.draw(screen)

    elif current_state == CREDITS:
        credits_menu.draw(screen)

    elif current_state == FAILURE:
        failure_menu.draw(screen)

    elif current_state == VICTORY:
        victory_menu.draw(screen)

    elif current_state == PLAYING:
        platform_mgr.draw(screen)
        interactive_manager.draw_all(screen)
        manager.draw_all(screen)

        # HUD / Punkty życia
        font = pygame.font.Font(None, 32)
        text = font.render(
            f"Player HP: {player.hp} | Ghost HP: {ghost.hp} | Power: {player.power}",
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