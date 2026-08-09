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
from Interactive import CodePanel
from GUI import (
    MainMenu,
    OptionsMenu,
    CreditsMenu,
    FailureMenu,
    VictoryMenu
)

# =========================================================
# KLASA PAUSE MENU
# =========================================================
class PauseMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 48)
        self.btn_font = pygame.font.Font(None, 36)
        self.resume_btn = pygame.Rect(width // 2 - 100, 200, 200, 50)
        self.options_btn = pygame.Rect(width // 2 - 100, 270, 200, 50)
        self.main_menu_btn = pygame.Rect(width // 2 - 100, 340, 200, 50)

    def draw(self, surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title = self.font.render("PAUZA", True, (255, 255, 255))
        surface.blit(title, (self.width // 2 - title.get_width() // 2, 120))

        for rect, text in [
            (self.resume_btn, "Wznów"),
            (self.options_btn, "Opcje"),
            (self.main_menu_btn, "Główne Menu")
        ]:
            pygame.draw.rect(surface, (70, 70, 70), rect, border_radius=8)
            pygame.draw.rect(surface, (200, 200, 200), rect, 2, border_radius=8)
            txt_surf = self.btn_font.render(text, True, (255, 255, 255))
            surface.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2, rect.centery - txt_surf.get_height() // 2))

    def handle_input(self, pos):
        if self.resume_btn.collidepoint(pos):
            return "resume"
        if self.options_btn.collidepoint(pos):
            return "options"
        if self.main_menu_btn.collidepoint(pos):
            return "main_menu"
        return None


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
PAUSE = 6


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
    ghost.pos.x = spawn_pos[0]
    ghost.pos.y = spawn_pos[1]


def move_ghost_with_collisions(ghost, dx, dy, platforms):
    """Przesuwa ducha z precyzyjną kolizją w osiach X i Y."""

    # 1. Tworzymy tymczasowy Rect na podstawie aktualnej pozycji ducha
    width = getattr(ghost, 'width', 32)
    height = getattr(ghost, 'height', 32)
    ghost_rect = pygame.Rect(int(ghost.pos.x), int(ghost.pos.y), width, height)

    # --- 2. RUCH W OSI X (Lewo / Prawo) ---
    ghost_rect.x += int(dx)
    for p in platforms:
        plat_rect = p.rect if hasattr(p, 'rect') else pygame.Rect(p[0], p[1], p[2], p[3])
        if ghost_rect.colliderect(plat_rect):
            if dx > 0:  # Idziemy w prawo -> zatrzymaj na lewej krawędzi ściany
                ghost_rect.right = plat_rect.left
            elif dx < 0:  # Idziemy w lewo -> zatrzymaj na prawej krawędzi ściany
                ghost_rect.left = plat_rect.right

    # --- 3. RUCH W OSI Y (Góra / Dół) ---
    ghost_rect.y += int(dy)
    for p in platforms:
        plat_rect = p.rect if hasattr(p, 'rect') else pygame.Rect(p[0], p[1], p[2], p[3])
        if ghost_rect.colliderect(plat_rect):
            if dy > 0:  # Idziemy w DÓŁ -> zatrzymaj na GÓRZE platformy
                ghost_rect.bottom = plat_rect.top
            elif dy < 0:  # Idziemy w GÓRĘ -> zatrzymaj na DOLE platformy
                ghost_rect.top = plat_rect.bottom

    # --- 4. OSTATECZNA AKTUALIZACJA POSITION ---
    ghost.pos.x = float(ghost_rect.x)
    ghost.pos.y = float(ghost_rect.y)

    if hasattr(ghost, 'rect') and ghost.rect:
        ghost.rect.topleft = (ghost_rect.x, ghost_rect.y)

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
    ghost = GhostMouse(level.player_pos[0], level.player_pos[1])

    char_mgr = CharacterManager()
    char_mgr.add("player", player)
    char_mgr.add("ghost", ghost)

    # --- MENUS ---
    main_menu = MainMenu(WIDTH, HEIGHT)
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
    # PĘTLA GŁÓWNA
    # =========================================================
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Zmienne przechowujące ruch myszy w danej klatce
        mouse_dx, mouse_dy = 0, 0

        # ----------------------------------------------------
        # 1. OBSŁUGA ZDARZEŃ (EVENTS)
        # ----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == PLAYING:
                        current_state = PAUSE
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                    elif current_state == PAUSE:
                        current_state = PLAYING
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()

                if current_state == PLAYING:
                    if event.key == pygame.K_w:
                        player.jump()
                    if event.key == pygame.K_2:
                        player.play("attack")

            if current_state == PLAYING:
                interactive_mgr.handle_event_all(event)

                # Zamiast od razu przesuwać ducha, zliczamy przesunięcie
                if event.type == pygame.MOUSEMOTION:
                    dx, dy = event.rel
                    mouse_dx += dx
                    mouse_dy += dy

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_state == MENU:
                    action = main_menu.handle_click(event.pos, (1, 0, 0))
                    if action == "play":
                        reset_game(player, ghost, level.player_pos)
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()
                        current_state = PLAYING
                    elif action == "options":
                        previous_state = MENU
                        current_state = OPTIONS
                    elif action == "credits":
                        current_state = CREDITS
                    elif action == "quit":
                        running = False

                elif current_state == PAUSE:
                    action = pause_menu.handle_input(event.pos)
                    if action == "resume":
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()
                        current_state = PLAYING
                    elif action == "options":
                        previous_state = PAUSE
                        current_state = OPTIONS
                    elif action == "main_menu":
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
                        reset_game(player, ghost, level.player_pos)
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()
                        current_state = PLAYING
                    elif action == "menu":
                        current_state = MENU

                elif current_state == VICTORY:
                    action = victory_menu.handle_input(event.pos, (1, 0, 0))
                    if action == "next":
                        reset_game(player, ghost, level.player_pos)
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.get_rel()
                        current_state = PLAYING
                    elif action == "menu":
                        current_state = MENU

        # ----------------------------------------------------
        # 2. AKTUALIZACJA LOGIKI (UPDATE)
        # ----------------------------------------------------
        if current_state == PLAYING:
            solid_interactive = [
                obj for obj in interactive_mgr.objects
                if hasattr(obj, 'is_open') and not obj.is_open and not isinstance(obj, CodePanel)
            ]
            all_obstacles = platform_mgr.platforms + solid_interactive

            # --- RUCH DUCHA Z KOLIZJAMI ---
            if mouse_dx != 0 or mouse_dy != 0:
                move_ghost_with_collisions(ghost, mouse_dx, mouse_dy, all_obstacles)

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

        if current_state in (PLAYING, PAUSE):
            platform_mgr.draw(screen)
            interactive_mgr.draw_all(screen)
            char_mgr.draw_all(screen)

            for enemy in level.enemies:
                enemy.draw(screen)
            projectile_mgr.draw_all(screen)

            font = pygame.font.Font(None, 32)
            hud_text = font.render(
                f"Player HP: {player.hp} | Ghost HP: {ghost.hp} | Power: {player.power}",
                True, (255, 255, 255)
            )
            screen.blit(hud_text, (10, 10))

            info = font.render(
                "A/D = Move, W = Jump, S = Fast Fall, 2 = Attack, ESC = Pause",
                True, (200, 200, 200)
            )
            screen.blit(info, (10, 50))

            if current_state == PAUSE:
                pause_menu.draw(screen)

        elif current_state == MENU:
            main_menu.draw(screen)
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