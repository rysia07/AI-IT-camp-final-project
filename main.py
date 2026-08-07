# main.py (menu integrated)
import sys
import pygame
from Characters import Creature, CharacterManager
from GUI import MainMenu
from Platforms import PlatformManager

# ============= INITIALIZATION =============
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT) , pygame.FULLSCREEN)
pygame.display.set_caption("Game - ludzik.png with Animations")
clock = pygame.time.Clock()

# ============= CREATE PLAYER =============
manager = CharacterManager()

player_pos_x , player_pos_y= platform_manager.player_pos


player = Creature(
    player_pos_x,
    player_pos_y,
    spritesheet_path="ludzik.png"
)


player.movement_threshold = 0.1
player.add_anim('idle', frames=[0], cols=3, rows=3, priority=Creature.PRIORITY_IDLE)
player.add_anim('walk', frames=[0, 1, 2, 3, 4, 5], cols=3, rows=3, speed=150, priority=Creature.PRIORITY_WALK)
player.add_anim('attack', frames=[6, 7, 8], cols=3, rows=3, speed=300, loop=False, priority=Creature.PRIORITY_ATTACK)
player.set_walk_idle('walk', 'idle')
player.play('idle')
manager.add('player', player)


# ============= MENU / GAME STATE ============
MENU = 0
PLAYING = 1
current_state = MENU
menu = MainMenu(WIDTH, HEIGHT)

running = True

while running:
    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()
    events = pygame.event.get()

    # ========== EVENTS ==========
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # Global: ESC to return to menu when playing
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            current_state = MENU

        # Game-specific events
        if current_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_2:
                    player.play('attack')

        # Menu click handling (use MOUSEBUTTONDOWN to avoid continuous triggers)
        elif current_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = menu.handle_click(event.pos, (1, 0, 0))
                if clicked == 'play':
                    current_state = PLAYING
                elif clicked == 'quit':
                    running = False
                elif clicked == 'options':
                    print("Options pressed (implement later)")
                elif clicked == 'credits':
                    print("Credits pressed (implement later)")

    # ========== UPDATE ==========
    if current_state == PLAYING:
        # moved input handling from original main
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.move(-player.speed * dt, 0)
        if keys[pygame.K_d]:
            player.move(player.speed * dt, 0)
        if keys[pygame.K_w]:
            player.jump()
        player.apply_gravity(dt, fast_fall=keys[pygame.K_s])

        manager.update_all(dt, platforms)

    elif current_state == MENU:
        menu.update(mouse_pos)

    # ========== DRAW ==========
    screen.fill((30, 30, 30))

    if current_state == MENU:
        # draw menu (placeholder background handled by art later)
        menu.draw(screen)

    elif current_state == PLAYING:
        # Draw platforms
        for platform in platforms:
            pygame.draw.rect(screen, (100, 200, 100), platform)

        # Draw player (sprite or fallback)
        if player.sprite and player.sprite.current:
            player.sprite.draw(screen)
        else:
            pygame.draw.circle(screen, "white", player.pos, player.size)

        # UI info
        font = pygame.font.Font(None, 32)
        text = font.render(f"Animation: {player.current_anim} | Grounded: {player.is_grounded}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        info = font.render("A/D=Move, W=Jump, S=Fast Fall, 2=Attack, ESC=Menu", True, (200, 200, 200))
        screen.blit(info, (10, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()