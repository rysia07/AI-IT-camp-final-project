
pygame.init()
okno = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

pygame.mouse.set_visible(False)

try:
    obraz_oryginalny = pygame.image.load('kievinay-train-6558870_1920.png').convert_alpha()
except pygame.error:
    obraz_oryginalny = pygame.Surface((50, 50))
    obraz_oryginalny.fill((139, 69, 19))

floor = pygame.Rect(0, 650, 1280, 70)
platforms = [
    floor,
    pygame.Rect(300, 500, 200, 20),
    pygame.Rect(600, 380, 200, 20),
    pygame.Rect(900, 250, 200, 20)
]
clickable = [pygame.Rect(100, 100, 100, 100)]
color = (255, 0, 0)

tekstura_podlogi = pygame.transform.scale(obraz_oryginalny, floor.size)
tekstura_platformy = pygame.transform.scale(obraz_oryginalny, (200, 20))

player_vel_y = 0
player_size = 40
jump_force = -1000
gravity = 2000
is_grounded = False
player_pos = pygame.Vector2(1280 / 2 - 100, 720 / 2)

player2_size = 40


while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if clickable[0].collidepoint(event.pos):
                color = (0, 255, 0)

    pygame.draw.rect(okno, color, clickable[0])

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] and is_grounded:
        player_vel_y = jump_force
        is_grounded = False

    if not is_grounded:
        if keys[pygame.K_s]:
            current_gravity = gravity * 3
        else:
            current_gravity = gravity
        player_vel_y += current_gravity * dt

    player_pos.y += player_vel_y * dt

    if keys[pygame.K_a]:
        player_pos.x -= 500 * dt
    if keys[pygame.K_d]:
        player_pos.x += 500 * dt

    player_rect = pygame.Rect(player_pos.x - player_size, player_pos.y - player_size, player_size * 2, player_size * 2)
    was_grounded_this_frame = False

    for platform in platforms:
        if player_rect.colliderect(platform) and player_vel_y >= 0:
            if (player_pos.y + player_size) - player_vel_y * dt <= platform.top + 10:
                player_pos.y = platform.top - player_size
                player_vel_y = 0
                was_grounded_this_frame = True

    is_grounded = was_grounded_this_frame

    okno.fill((63, 94, 76))

    okno.blit(tekstura_podlogi, floor)
    for platforma in platforms[1:]:
        okno.blit(tekstura_platformy, platforma)

    pygame.draw.rect(okno, color, clickable[0])

    pygame.draw.circle(okno, "red", (int(player_pos.x), int(player_pos.y)), player_size)
    pygame.draw.circle(okno, "blue", (mouse_x, mouse_y), player2_size)

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
sys.exit()
