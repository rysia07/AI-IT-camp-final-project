import sys
import pygame

# Importujemy wszystkie potrzebne klasy z pliku Interactive.py
from Interactive import (
    Lever,
    CodePanel,
    ScoringButton,
    LevelGate,
    InteractiveManager
)
from Characters import Creature, GhostMouse, CharacterManager, ShootingEnemy, ProjectileManager
from GUI import MainMenu
from Platforms import PlatformManager
from options_menu import OptionsMenu
from credits_menu import CreditsMenu

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
# ENEMIES (Wrogowie)
# =========================================================

projectile_manager = ProjectileManager()

enemy = ShootingEnemy(700, 200, "../pictures/ludzik.png")
enemy.add_anim("idle", frames=[0], cols=3, rows=3, priority=ShootingEnemy.PRIORITY_IDLE)
enemy.add_anim("walk", frames=[0, 1, 2, 3, 4, 5], cols=3, rows=3, speed=150, priority=ShootingEnemy.PRIORITY_WALK)
enemy.add_anim("shoot", frames=[6, 7, 8], cols=3, rows=3, speed=300, loop=False, priority=ShootingEnemy.PRIORITY_SHOOT)
enemy.set_walk_idle("walk", "idle")
enemy.play("idle")
enemy_alive = True

# =========================================================
# INTERACTIVE OBJECTS (Dźwignie, Panele itp.)
# =========================================================

interactive_manager = InteractiveManager()

# Dodajemy obiekty bezpośrednio do menedżera
interactive_manager.add(Lever(300, 300, 100, 20, direction="left"))
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
options_menu = OptionsMenu(WIDTH, HEIGHT)
credits_menu = CreditsMenu(WIDTH, HEIGHT)

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

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mouse.set_visible(True)
            if current_state == OPTIONS:
                options_menu.active = False
            elif current_state == CREDITS:
                credits_menu.active = False
            current_state = MENU

        # Eventy w grze
        if current_state == PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                player.play("attack")
                # Zadaj obrażenia wrogowi jeśli jest w zasięgu
                if player.rect.colliderect(enemy.rect):
                    enemy.take_damage(20)

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
                    options_menu.active = True
                    current_state = OPTIONS
                    pygame.mouse.set_visible(True)
                elif clicked == "credits":
                    credits_menu.active = True
                    current_state = CREDITS
                    pygame.mouse.set_visible(True)

        elif current_state == OPTIONS:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = options_menu.handle_input()
                if action == "back":
                    options_menu.active = False
                    current_state = MENU

        elif current_state == CREDITS:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = credits_menu.handle_input()
                if action == "back":
                    credits_menu.active = False
                    current_state = MENU

    # =====================================================
    # UPDATE
    # =====================================================

    if current_state == PLAYING:
        # 1. Aktualizacja fizyki postaci i platform
        manager.update_all(dt, platform_mgr.platforms)

        # 2. Aktualizacja wrogów
        if enemy_alive:
            enemy.update(dt, player.pos, platform_mgr.platforms)
            
            # 3. Strzelanie wroga
            if enemy.shoot_cooldown <= 0 and enemy.is_alive():
                projectile = enemy.shoot(player.pos.x, player.pos.y)
                projectile_manager.add(projectile)
                enemy.shoot_cooldown = enemy.shoot_interval
            
            # Sprawdzenie czy wróg umarł
            if not enemy.is_alive():
                enemy_alive = False

        # 4. Aktualizacja pocisków
        projectile_manager.update(dt)
        
        # 5. Kolizje pocisków z graczem
        projectiles_to_remove = []
        for projectile in projectile_manager.get_projectiles():
            if player.rect.colliderect(projectile.rect):
                player.hp -= projectile.damage
                projectiles_to_remove.append(projectile)
        
        for projectile in projectiles_to_remove:
            if projectile in projectile_manager.projectiles:
                projectile_manager.projectiles.remove(projectile)

        # 6. Aktualizacja obiektów interaktywnych
        interactive_manager.update_all(player, ghost)

    elif current_state == MENU:
        menu.update(mouse_pos)

    elif current_state == OPTIONS:
        options_menu.update(mouse_pos)

    elif current_state == CREDITS:
        credits_menu.update(mouse_pos)

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

    elif current_state == PLAYING:
        # Platformy
        for platform in platform_mgr.platforms:
            platform_mgr.draw(screen)

        # Obiekty interaktywne
        interactive_manager.draw_all(screen)

        # Postacie & Hitboxy
        manager.draw_all(screen)
        if enemy_alive:
            enemy.draw(screen)
            player.draw_hitbox(screen, "red")
            ghost.draw_hitbox(screen, "cyan")
            enemy.draw_hitbox(screen, "green")
        else:
            player.draw_hitbox(screen, "red")
            ghost.draw_hitbox(screen, "cyan")
        
        # Pociski
        projectile_manager.draw_all(screen)

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
        
        # HP wyświetlane
        hp_text = font.render(f"Player HP: {player.hp} | Enemy HP: {enemy.hp}", True, (255, 0, 0))
        screen.blit(hp_text, (10, 90))

    pygame.display.flip()

# =========================================================
# EXIT
# =========================================================

pygame.quit()
sys.exit()