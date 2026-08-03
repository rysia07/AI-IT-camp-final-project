# Example file showing a circle moving on screen
import pygame
import sys

# pygame setup
pygame.init()
okno = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# --- 1. WCZYTANIE TEKSTURY (Poza pętlą, tylko raz!) ---
try:
    obraz_oryginalny = pygame.image.load('kievinay-train-6558870_1920.png').convert_alpha()
except pygame.error:
    # Zastępcza tekstura, jeśli nie ma pliku tekstury
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
# Tworzymy osobną, dopasowaną teksturę dla podłogi i osobną dla mniejszych platform
tekstura_podlogi = pygame.transform.scale(obraz_oryginalny, floor.size)
tekstura_platformy = pygame.transform.scale(obraz_oryginalny, platforms[1].size)

# --- GRACZ ---
player_vel_y = 0  # Prędkość pionowa (0 = stoi w miejscu)
player_size = 40
jump_force = -1000  # Silniejsze wybicie w górę
gravity = 2000  # Słabsze przyciąganie (dłuższy lot)
is_grounded = False  # Czy gracz stoi na ziemi?

# Pozycja startowa na środku ekranu
player_pos = pygame.Vector2(okno.get_width() / 2, okno.get_height() / 2)

while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Czyszczenie ekranu kolorem tła
    okno.fill((63, 94, 76))

    # --- 4. RYSOWANIE TEKSTUR NA PLATFORMACH (Wewnątrz pętli gry!) ---
    # Rysujemy podłogę
    okno.blit(tekstura_podlogi, floor)

    # Rysujemy pozostałe platformy (od indeksu 1 do końca listy)
    for platforma in platforms[1:]:
        okno.blit(tekstura_platformy, platforma)

    # Rysowanie gracza (zmienione screen na okno)
    pygame.draw.circle(okno, "red", player_pos, 40)

    keys = pygame.key.get_pressed()
    # 1. AKTYWACJA SKOKU (Tylko jeśli gracz stoi na ziemi)
    if keys[pygame.K_w] and is_grounded:
        player_vel_y = jump_force
        is_grounded = False

    # 2. ZASTOSOWANIE GRAWITACJI (Gdy gracz jest w powietrzu)
    if not is_grounded:
        if keys[pygame.K_s]:
            current_gravity = gravity * 3
        else:
            current_gravity = gravity
        player_vel_y += current_gravity * dt

    # 3. AKTUALIZACJA POZYCJI Y
    player_pos.y += player_vel_y * dt

    # --- KOLIZJE Z PLATFORMAMI ---
    player_rect = pygame.Rect(player_pos.x - player_size // 2, player_pos.y - player_size // 2, player_size,
                              player_size)
    was_grounded_this_frame = False

    for platform in platforms:
        if player_rect.colliderect(platform) and player_vel_y >= 0:
            if (player_pos.y + player_size // 2) - player_vel_y * dt <= platform.top + 10:
                player_pos.y = platform.top - player_size // 2  # Postaw gracza na platformie
                player_vel_y = 0
                was_grounded_this_frame = True

    is_grounded = was_grounded_this_frame

    if not is_grounded and player_vel_y == 0:
        is_grounded = False

    if keys[pygame.K_a]:
        player_pos.x -= 500 * dt
    if keys[pygame.K_d]:
        player_pos.x += 500 * dt

    # Odświeżenie ekranu
    pygame.display.flip()

    # Zliczanie czasu delty
    dt = clock.tick(60) / 1000

pygame.quit()
sys.exit()
