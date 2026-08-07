import sys
import pygame

from Characters import Creature, CharacterManager, GhostMouse
from Platforms import PlatformManager

# =====================================================
# INITIALIZATION
# =====================================================

pygame.init()

WIDTH = 900
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coop Game")

clock = pygame.time.Clock()

# =====================================================
# WORLD
# =====================================================

platform_manager = PlatformManager(
    "kievinay-train-6558870_1920.png"
)

# =====================================================
# CHARACTERS
# =====================================================

manager = CharacterManager()

player_pos_x , player_pos_y= platform_manager.player_pos


player = Creature(
    player_pos_x,
    player_pos_y,
    spritesheet_path="ludzik.png"
)

# Animacje gracza
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

manager.add(
    "player",
    player
)

# =====================================================
# MAIN LOOP
# =====================================================

running = True

while running:

    dt = clock.tick(60) / 1000.0

    # =================================================
    # EVENTS
    # =================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.jump()

            if event.key == pygame.K_2:
                player.play("attack")

    # =================================================
    # INPUT & MOVEMENT
    # =================================================
    keys = pygame.key.get_pressed()
    direction = 0

    if keys[pygame.K_a]:
        direction -= 1
    if keys[pygame.K_d]:
        direction += 1


    # =================================================
    # UPDATE
    # =================================================
    manager.update_all(
        dt,
        platform_manager.platforms
    )

    # =================================================
    # DRAW
    # =================================================
    screen.fill((30, 30, 30))

    # Platformy
    platform_manager.draw(screen)

    # DEBUG HITBOXY
    for rect in platform_manager.platforms:
        pygame.draw.rect(
            screen,
            (0, 0, 255),
            rect,
            2
        )

    pygame.draw.rect(
        screen,
        (255, 0, 0),
        player.rect,
        2
    )
    pygame.draw.circle(
        screen,
        (0, 255, 0),
        player.pos,
        5
    )

    # Rysowanie postaci z managerem
    manager.draw_all(screen)

    # =================================================
    # UI
    # =================================================
    font = pygame.font.Font(None, 32)

    info = font.render(
        f"Anim: {player.current_anim} | Grounded: {player.is_grounded}",
        True,
        (255, 255, 255)
    )
    screen.blit(info, (10, 10))

    controls = font.render(
        "A/D ruch | W skok | S szybki spadek | 2 atak",
        True,
        (200, 200, 200)
    )
    screen.blit(controls, (10, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()