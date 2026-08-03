# Example file showing a circle moving on screen
import pygame
import sys

# pygame setup
pygame.init()
okno = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# Ukrywa systemowy kursor myszy
pygame.mouse.set_visible(False)

# --- 1. WCZYTANIE TEKSTURY ---
try:
    obraz_oryginalny = pygame.image.load('kievinay-train-6558870_1920.png').convert_alpha()
except pygame.error:
    obraz_oryginalny = pygame.Surface((50, 50))
    obraz_oryginalny.fill((139, 69, 19))  # Brązowy kolor

# --- 2. DEFINICJA PLATFORM ---
floor = pygame.Rect(0, 650, 1280, 70)
platforms = [
    floor,  # Główna podłoga
    pygame.Rect(300, 500, 200, 20),  # Pierwsza platforma
    pygame.Rect(600, 380, 200, 20),  # Druga platforma
    pygame.Rect(900, 250, 200, 20)  # Trzecia platforma
]

# --- 3. SKALOWANIE TEKSTUR DO ROZMIARU PLATFORM ---
tekstura_podlogi = pygame.transform.scale(obraz_oryginalny, floor.size)
tekstura_platformy = pygame.transform.scale(obraz_oryginalny, (200, 20))

# --- GRACZ 1 (Klawiatura - Czerwony) ---
player_vel_y = 0
player_size = 40
jump_force = -1000
gravity = 2000
is_grounded = False
player_pos = pygame.Vector2(1280 / 2 - 100, 720 / 2)

# --- GRACZ 2 (Myszka - Niebieski) ---
player2_size = 40  # Promień niebieskiej kropki

while running:
    # Pobieranie aktualnej pozycji myszki
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Obsługa zdarzeń wyjścia
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- INPUTY I FIZYKA GRACZA 1 (KLAWIATURA) ---
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

    # --- KOLIZJE Z PLATFORMAMI (TYLKO GRACZ 1) ---
    player_rect = pygame.Rect(player_pos.x - player_size, player_pos.y - player_size, player_size * 2, player_size * 2)
    was_grounded_this_frame = False

    for platform in platforms:
        if player_rect.colliderect(platform) and player_vel_y >= 0:
            if (player_pos.y + player_size) - player_vel_y * dt <= platform.top + 10:
                player_pos.y = platform.top - player_size
                player_vel_y = 0
                was_grounded_this_frame = True

    is_grounded = was_grounded_this_frame

    # --- RYSOWANIE GRAFIKI ---
    okno.fill((63, 94, 76))  # Tło

    # Rysowanie platform z teksturami
    okno.blit(tekstura_podlogi, floor)
    for platforma in platforms[1:]:
        okno.blit(tekstura_platformy, platforma)

    # Rysowanie Gracza 1 (Czerwony)
    pygame.draw.circle(okno, "red", (int(player_pos.x), int(player_pos.y)), player_size)

    # Rysowanie Gracza 2 (Niebieski - przypisany bezpośrednio pod kursor myszy)
    pygame.draw.circle(okno, "blue", (mouse_x, mouse_y), player2_size)

    # Odświeżenie ekranu
    pygame.display.flip()

    # Zliczanie czasu delty
    dt = clock.tick(60) / 1000

pygame.quit()
sys.exit()
