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

        # Zdarzenia przekazujemy TYLKO do obiektów, które ich potrzebują
        box1.handle_event(event)

    # --- 2. AKTUALIZACJA LOGIKI (POZA PĘTLĄ FOR!) ---
    # To musi się wykonywać co klatkę, niezależnie od zdarzeń!
    ghost.update()
    creature.update(dt, platforms)
    ghost.interact([box1])

    # --- 3. RYSOWANIE ---
    okno.fill((63, 94, 76))

    okno.blit(tekstura_podlogi, floor)
    for platforma in platforms[1:]:
        okno.blit(tekstura_platformy, platforma)

    box1.draw(okno)
    creature.draw(okno)
    ghost.draw(okno)

    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

pygame.quit()
sys.exit()