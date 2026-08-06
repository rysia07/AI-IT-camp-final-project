# UPDATED main.py - INCREASE SPEED
import sys
import pygame
from Characters import Creature, CharacterManager

# ============= INITIALIZATION =============
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game - ludzik.png with Animations")
clock = pygame.time.Clock()

# ============= CREATE PLAYER =============
manager = CharacterManager()

player = Creature(150, 300,10000, -1000, spritesheet_path='enemy.png')

player.movement_threshold = 0.1  # LOWER threshold for animation detection
player.add_anim('idle', frames=[0], cols=3, rows=3,
                priority=Creature.PRIORITY_IDLE)
player.add_anim('walk', frames=[0], cols=3, rows=3,
                speed=150, priority=Creature.PRIORITY_WALK)
player.add_anim('attack', frames=[0,1,2,3,4,5,6], cols=3, rows=3,
                speed=50, loop=False, priority=Creature.PRIORITY_ATTACK)
player.set_walk_idle('walk', 'idle')
player.play('idle')
manager.add('player', player)

# ============= PLATFORMS =============
platforms = [
    pygame.Rect(50, 500, 800, 50),  # Ground
    pygame.Rect(200, 400, 150, 50),  # Platform 1
    pygame.Rect(550, 300, 150, 50),  # Platform 2
]

# ============= MAIN LOOP =============
running = True

while running:
    dt = clock.tick(60) / 1000.0

    # ========== INPUT HANDLING (ONLY IN MAIN) ==========
    keys = pygame.key.get_pressed()

    # Movement (A / D)
    if keys[pygame.K_a]:
        player.move(-player.speed * dt, 0)
    if keys[pygame.K_d]:
        player.move(player.speed * dt, 0)

    # Jump (W key)
    if keys[pygame.K_w]:
        player.jump()

    # Fast fall (S key)
    player.apply_gravity(dt, fast_fall=keys[pygame.K_s])

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_2:
                player.play('attack')

    # ========== UPDATE LOGIC ==========
    manager.update_all(dt, platforms)

    # ========== RENDERING (ONLY IN MAIN) ==========
    screen.fill((30, 30, 30))

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, (100, 200, 100), platform)

    # Draw player
    if player.sprite and player.sprite.current:
        player.sprite.draw(screen)
    else:
        pygame.draw.circle(screen, "white", player.pos, player.size)

    # ========== UI INFO ==========
    font = pygame.font.Font(None, 32)
    text = font.render(f"Animation: {player.current_anim} | Grounded: {player.is_grounded}",
                       True, (255, 255, 255))
    screen.blit(text, (10, 10))

    info = font.render("A/D=Move, W=Jump, S=Fast Fall, 2=Attack", True, (200, 200, 200))
    screen.blit(info, (10, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()