import sys
import pygame

from LoadLevels import load_level
from Platforms import PlatformManager
from Characters import (
    Creature,
    GhostMouse,
    CharacterManager,
    ProjectileManager
)
from GUI import (
    MainMenu,
    OptionsMenu,
    CreditsMenu,
    FailureMenu,
    VictoryMenu
)

# =========================================================
# KONFIGURACJA I STAŁE
# =========================================================
FPS = 60
WIDTH, HEIGHT = 900, 600

MENU = 0
PLAYING = 1
OPTIONS = 2
CREDITS = 3
FAILURE = 4
VICTORY = 5


def create_player(start_pos):
    """Tworzy i konfiguruje postać gracza wraz z animacjami."""
    player = Creature(start_pos[0], start_pos[1], "../pictures/ludzik.png")

    player.add_anim("idle", [0], 3, 3, speed=100, priority=Creature.PRIORITY_IDLE,
                    spritesheet_path="../pictures/ludzik.png", scale=2.0)
    player.add_anim("walk", [0, 1, 2, 3, 4, 5], 3, 3, speed=150, priority=Creature.PRIORITY_WALK,
                    spritesheet_path="../pictures/ludzik.png", scale=2.0)
    player.add_anim("attack", list(range(19)), 5, 4, speed=35, loop=False,
                    priority=Creature.PRIORITY_ATTACK, spritesheet_path="../pictures/Gracz_atak.png", scale=0.5)

    player.set_walk_idle("walk", "idle")
    player.play("idle")
    return player


def reset_game(player, ghost, spawn_pos):
    """Resetuje stan gracza i ducha do wartości początkowych."""
    player.hp = 100
    player.pos.x = spawn_pos[0]
    player.pos.y = spawn_pos[1]
    player.vel_y = 0
    ghost.hp = 50
    ghost.pos.x = 0
    ghost.pos.y = 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Alien space")
    clock = pygame.time.Clock()

    # --- ŁADOWANIE POZIOMU I ZASOBÓW ---
    level = load_level("../levels/level.txt")
    interactive_mgr = level.interactive_manager
    platform_mgr = PlatformManager("../pictures/platforma.png", level.platforms)
    projectile_mgr = ProjectileManager()

    # --- POSTACIE ---
    player = create_player(level.player_pos)
    ghost = GhostMouse(0, 0)

    char_mgr = CharacterManager()
    char_mgr.add("player", player)
    char_mgr.add("ghost", ghost)

    # --- MENUS ---
    main_menu = MainMenu(WIDTH, HEIGHT)
    options_menu = OptionsMenu(WIDTH, HEIGHT)
    credits_menu = CreditsMenu(WIDTH, HEIGHT)
    failure_menu = FailureMenu(WIDTH, HEIGHT)
    victory_menu = VictoryMenu(WIDTH, HEIGHT)

    current_state = MENU
    running = True

    # =========================================================
    # PĘTLA GŁÓWNA
    # =========================================================
    while running:
        dt = clock.tick(FPS) / 1000.0

        # ----------------------------------------------------
        # 1. OBSŁUGA ZDARZEŃ (EVENTS)
        # ----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    pygame.mouse.set_visible(True)

                if current_state == PLAYING:
                    if event.key == pygame.K_w:
                        player.jump()
                    if event.key == pygame.K_2:
                        player.play("attack")

            if current_state == PLAYING:
                interactive_mgr.handle_event_all(event)
                pygame.event.set_grab(True)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Obsługa menu (używamy dokładnych metod z Twojego GUI.py)
                if current_state == MENU:
                    action = main_menu.handle_click(event.pos, (1, 0, 0))
                    if action == "play":
                        reset_game(player, ghost, level.player_pos)
                        pygame.mouse.set_visible(False)
                        current_state = PLAYING
                    elif action == "options":
                        current_state = OPTIONS
                    elif action == "credits":
                        current_state = CREDITS
                    elif action == "quit":
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
                        reset_game(player, ghost, level.player_pos)
                        pygame.mouse.set_visible(False)
                        current_state = PLAYING
                    elif action == "menu":
                        current_state = MENU

                elif current_state == VICTORY:
                    action = victory_menu.handle_input(event.pos, (1, 0, 0))
                    if action == "next":
                        reset_game(player, ghost, level.player_pos)
                        pygame.mouse.set_visible(False)
                        current_state = PLAYING
                    elif action == "menu":
                        current_state = MENU

        # ----------------------------------------------------
        # 2. AKTUALIZACJA LOGIKI (UPDATE)
        # ----------------------------------------------------
        if current_state == PLAYING:
            solid_interactive = [
                obj for obj in interactive_mgr.objects
                if hasattr(obj, 'is_open') and not obj.is_open
            ]
            all_obstacles = platform_mgr.platforms + solid_interactive

            char_mgr.update_all(dt, platforms=all_obstacles)

            for enemy in level.enemies:
                enemy.update(dt, player_pos=player.pos, platforms=platform_mgr.platforms)
                if (enemy.pos - player.pos).length() < enemy.detection_range and enemy.shoot_cooldown <= 0:
                    projectile_mgr.add(enemy.shoot(player.pos.x, player.pos.y))
                    enemy.shoot_cooldown = enemy.shoot_interval

            projectile_mgr.update(dt)
            interactive_mgr.update_all(player, ghost, dt)

        # ----------------------------------------------------
        # 3. RYSOWANIE (DRAW)
        # ----------------------------------------------------
        screen.fill((30, 30, 30))

        if current_state == MENU:
            main_menu.draw(screen)
            pygame.event.set_grab(False)
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
            interactive_mgr.draw_all(screen)
            char_mgr.draw_all(screen)

            for enemy in level.enemies:
                enemy.draw(screen)
            projectile_mgr.draw_all(screen)

            # HUD
            font = pygame.font.Font(None, 32)
            hud_text = font.render(
                f"Player HP: {player.hp} | Ghost HP: {ghost.hp} | Power: {player.power}",
                True, (255, 255, 255)
            )
            screen.blit(hud_text, (10, 10))

            info = font.render(
                "A/D = Move, W = Jump, S = Fast Fall, 2 = Attack, ESC = Menu",
                True, (200, 200, 200)
            )
            screen.blit(info, (10, 50))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()