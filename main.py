import sys
import pygame

# Importujemy zdefiniowane przez Ciebie klasy
from Characters import Creature, GhostMouse
from ClickableBox import ClickableBox

# 1. Inicjalizacja Pygame i okna
pygame.init()
WIDTH, HEIGHT = 1280, 720
okno = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nasza Gra w Pygame")
clock = pygame.time.Clock()

# Ukrywamy domyślny kursor myszy, bo gracz steruje duchem (GhostMouse)
pygame.mouse.set_visible(False)

# 2. Przygotowanie platform (poziomu)
floor = pygame.Rect(0, 650, 1280, 70)
platforms = [
    floor,
    pygame.Rect(300, 500, 200, 20),
    pygame.Rect(600, 380, 200, 20),
    pygame.Rect(900, 250, 200, 20)
]

# Ładowanie tekstur (z zabezpieczeniem try-except)
try:
    obraz_oryginalny = pygame.image.load('kievinay-train-6558870_1920.png').convert_alpha()
except pygame.error:
    obraz_oryginalny = pygame.Surface((50, 50))
    obraz_oryginalny.fill((139, 69, 19))

tekstura_podlogi = pygame.transform.scale(obraz_oryginalny, floor.size)
tekstura_platformy = pygame.transform.scale(obraz_oryginalny, (200, 20))

# 3. Tworzenie obiektów gry
creature = Creature(x=WIDTH // 2 - 100, y=HEIGHT // 2)
ghost = GhostMouse(x=0, y=0)

box1 = ClickableBox(100, 100, 100, 100, (255, 0, 0), (255, 100, 100), (0, 255, 0))

# Zmienne pomocnicze dla fizyki gracza (Creature)
player_vel_y = 0
jump_force = -1000
gravity = 2000
is_grounded = False

# 4. Główna pętla gry
dt = 0
running = True

while running:
    # --- 1. OBSŁUGA ZDARZEŃ ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Przekazujemy zdarzenia do klikalnego przycisku
        box1.handle_event(event)

    # --- 2. AKTUALIZACJA LOGIKI ---
    # Ruch ducha podążającego za myszką
    ghost.update()

    # Logika fizyki i skoku Creature (sterowanie klawiaturą)
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] and is_grounded:
        player_vel_y = jump_force
        is_grounded = False

    current_gravity = gravity * 3 if (not is_grounded and keys[pygame.K_s]) else gravity
    if not is_grounded:
        player_vel_y += current_gravity * dt

    creature.pos.y += player_vel_y * dt

    if keys[pygame.K_a]:
        creature.pos.x -= creature.speed * dt
    if keys[pygame.K_d]:
        creature.pos.x += creature.speed * dt

    # Aktualizacja obszaru kolizji gracza
    creature.update_rect()

    # Kolizje z platformami
    was_grounded_this_frame = False
    for platform in platforms:
        if creature.rect.colliderect(platform) and player_vel_y >= 0:
            if (creature.pos.y + creature.size) - player_vel_y * dt <= platform.top + 10:
                creature.pos.y = platform.top - creature.size
                player_vel_y = 0
                was_grounded_this_frame = True
                creature.update_rect()

    is_grounded = was_grounded_this_frame

    # Interakcja ducha z obiektami w zasięgu
    ghost.interact([box1])

    # --- 3. RYSOWANIE ---
    okno.fill((63, 94, 76))  # Tło

    # Rysowanie platform
    okno.blit(tekstura_podlogi, floor)
    for platforma in platforms[1:]:
        okno.blit(tekstura_platformy, platforma)

    # Rysowanie klikalnego pudełka
    box1.draw(okno)

    # Rysowanie postaci
    creature.draw(okno)
    ghost.draw(okno)

    pygame.display.flip()

    # Pobranie czasu delta w sekundach
    dt = clock.tick(60) / 1000.0

pygame.quit()
sys.exit()