import sys
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
from audio_adapter import AudioAdapter

# =========================================================
# KONFIGURACJA I STAŁE
# =========================================================
FPS = 60
WIDTH, HEIGHT = 900, 600

# Stany gry
MENU = 0
PLAYING = 1
OPTIONS = 2
CREDITS = 3
FAILURE = 4
VICTORY = 5
PAUSE = 6
LEVEL_SELECT = 7


def create_player(start_pos):
    """Tworzy i konfiguruje postać gracza wraz z animacjami."""
    player = Creature(start_pos[0], start_pos[1], "../pictures/ludzik.png")

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

    return player


def reset_game(player, ghost, spawn_pos):
    """Resetuje stan gracza i ducha do wartości początkowych."""
    player.hp = 100
    player.pos.x = spawn_pos[0]
    player.pos.y = spawn_pos[1]
    if hasattr(player, 'vel_y'):
        player.vel_y = 0
    ghost.hp = 50
    ghost.pos.x = spawn_pos[0]
    ghost.pos.y = spawn_pos[1]


def move_ghost_with_collisions(ghost, dx, dy, platforms):
    """Przesuwa ducha z precyzyjną kolizją w osiach X i Y."""
    # Użyj istniejącego rect zamiast tworzyć nowy
    if not hasattr(ghost, 'rect') or ghost.rect is None:
        width = getattr(ghost, 'width', getattr(ghost, 'size', 32))
        height = getattr(ghost, 'height', getattr(ghost, 'size', 32))
        ghost.rect = pygame.Rect(int(ghost.pos.x), int(ghost.pos.y), width, height)

    ghost_rect = ghost.rect.copy()

    ghost_rect.x += int(dx)
    for p in platforms:
        plat_rect = p.rect if hasattr(p, 'rect') else (
            pygame.Rect(p[0], p[1], p[2], p[3]) if isinstance(p, (tuple, list)) else p)
        if ghost_rect.colliderect(plat_rect):
            if dx > 0:
                ghost_rect.right = plat_rect.left
            elif dx < 0:
                ghost_rect.left = plat_rect.right

    ghost_rect.y += int(dy)
    for p in platforms:
        plat_rect = p.rect if hasattr(p, 'rect') else (
            pygame.Rect(p[0], p[1], p[2], p[3]) if isinstance(p, (tuple, list)) else p)
        if ghost_rect.colliderect(plat_rect):
            if dy > 0:
                ghost_rect.bottom = plat_rect.top
            elif dy < 0:
                ghost_rect.top = plat_rect.bottom

    ghost.pos.x = float(ghost_rect.x)
    ghost.pos.y = float(ghost_rect.y)
    ghost.rect.topleft = (ghost_rect.x, ghost_rect.y)


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

    char_mgr = CharacterManager()
    char_mgr.add("player", player)
    char_mgr.add("ghost", ghost)

    return level, interactive_mgr, platform_mgr, projectile_mgr, player, ghost, char_mgr


def main():
    pygame.init()

    audio = AudioAdapter()
    jump_audio = AudioAdapter()
    shoot_audio = AudioAdapter()

    audio.load("../głosy do gry/background_ost.wav")
    jump_audio.load("../głosy do gry/jump.wav")
    shoot_audio.load("../głosy do gry/shoot.wav")
    audio.set_volume(0.5)
    audio.play(loops=-1)

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

    current_state = MENU
    previous_state = MENU
    running = True

    pygame.mouse.get_rel()

    # =========================================================
    # PĘTLA GŁÓWNA GRY
    # =========================================================
    while running:
        dt = clock.tick(FPS) / 1000.0

        audio.update()
        jump_audio.update()
        shoot_audio.update()

        mouse_dx, mouse_dy = 0, 0

        # ----------------------------------------------------
        # 1. OBSŁUGA ZDARZEŃ (INPUT)
        # ----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_state == OPTIONS:
                if hasattr(options_menu, 'handle_event'):
                    options_menu.handle_event(event)

            # Obsługa przycisków klawiatury
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == PLAYING:
                        current_state = PAUSE
                        pause_menu.active = True
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                    elif current_state == PAUSE:
                        current_state = PLAYING
                        pause_menu.active = False
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()

                if current_state == PLAYING:
                    if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
                        if hasattr(player, 'jump'):
                            player.jump()
                            jump_audio.play()
                    if event.key == pygame.K_2 and hasattr(player, 'play'):
                        player.play("attack")
                        shoot_audio.play()

            elif event.type == pygame.MOUSEMOTION:
                if current_state == PLAYING:
                    dx, dy = event.rel
                    mouse_dx += dx
                    mouse_dy += dy

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
                    elif action == "options":
                        previous_state = MENU
                        current_state = OPTIONS
                    elif action == "credits":
                        current_state = CREDITS
                    elif action == "quit":
                        running = False

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

                elif current_state == PAUSE:
                    action = pause_menu.handle_input(event.pos, (1, 0, 0))
                    if action == "resume":
                        pause_menu.active = False
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()
                        current_state = PLAYING
                    elif action == "level_select":
                        pause_menu.active = False
                        previous_state = PAUSE
                        current_state = LEVEL_SELECT
                    elif action == "options":
                        previous_state = PAUSE
                        current_state = OPTIONS
                    elif action == "main_menu":
                        pause_menu.active = False
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                        current_state = MENU

                elif current_state == OPTIONS:
                    action = options_menu.handle_input(event.pos, (1, 0, 0))
                    if action == "back":
                        current_state = previous_state

                elif current_state == CREDITS:
                    action = credits_menu.handle_input(event.pos, (1, 0, 0))
                    if action == "back":
                        current_state = MENU

                elif current_state == FAILURE:
                    action = failure_menu.handle_input(event.pos, (1, 0, 0))
                    if action == "retry":
                        level, interactive_mgr, platform_mgr, projectile_mgr, player, ghost, char_mgr = load_selected_level(
                            current_level_file)
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()
                        current_state = PLAYING
                    elif action == "menu":
                        current_state = MENU

                elif current_state == VICTORY:
                    action = victory_menu.handle_input(event.pos, (1, 0, 0))
                    if action == "level_select":
                        previous_state = MENU
                        current_state = LEVEL_SELECT
                    elif action == "menu":
                        current_state = MENU

            # Zdarzenia dla obiektów interaktywnych (dźwignie, klawiatura w codepanelu)
            if current_state == PLAYING:
                if hasattr(interactive_mgr, 'handle_event'):
                    interactive_mgr.handle_event(event)

        # ----------------------------------------------------
        # 2. AKTUALIZACJA LOGIKI (UPDATE)
        # ----------------------------------------------------
        if current_state == MENU:
            main_menu.update()
        elif current_state == LEVEL_SELECT:
            level_select_menu.update()
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

        elif current_state == PLAYING:
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
            ]
            all_obstacles = platform_mgr.platforms + solid_interactive

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
            )
            screen.blit(hud_text, (10, 10))

            info = font.render(
                "A/D = Move, W/Space = Jump, 2 = Attack, ESC = Pause",
                True, (200, 200, 200)
            )
            screen.blit(info, (10, 50))

            # Menu pauzy rysowane na wierzchu gry
            if current_state == PAUSE:
                pause_menu.draw(screen)

        elif current_state == MENU:
            main_menu.draw(screen)
        elif current_state == LEVEL_SELECT:
            level_select_menu.draw(screen)
        elif current_state == OPTIONS:
            options_menu.draw(screen)
        elif current_state == CREDITS:
            credits_menu.draw(screen)
        elif current_state == FAILURE:
            failure_menu.draw(screen)
        elif current_state == VICTORY:
            victory_menu.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()