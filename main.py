import sys
import pygame

# Importujemy wszystkie klasy z naszych modułów
from Characters import Creature, GhostMouse
from ClickableBox import ClickableBox
from Platforms import PlatformManager

# 1. Inicjalizacja Pygame i okna
pygame.init()
WIDTH, HEIGHT = 1280, 720
okno = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nasza Gra w Pygame")
clock = pygame.time.Clock()

# Ukrywamy kursor myszy (gracz steruje duchem)
pygame.mouse.set_visible(False)

# 2. Tworzenie obiektów gry
level = PlatformManager('kievinay-train-6558870_1920.png')
creature = Creature(x=WIDTH // 2 - 100, y=HEIGHT // 2)
ghost = GhostMouse(x=0, y=0)

box1 = ClickableBox(100, 100, 100, 100, (255, 0, 0), (255, 100, 100), (0, 255, 0))

# 3. Główna pętla gry
dt = 0
running = True

while running:
    # --- 1. OBSŁUGA ZDARZEŃ ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Zdarzenia trafiają do obiektów interaktywnych
        box1.handle_event(event)

    # --- 2. AKTUALIZACJA LOGIKI (poza pętlą zdarzeń!) ---
    ghost.update()
    # Przekazujemy listę platform bezpośrednio z obiektu level:
    creature.update(dt, level.platforms)
    ghost.interact([box1])

    # --- 3. RYSOWANIE ---
    okno.fill((63, 94, 76))  # Tło

    # Rysujemy poziom za pomocą jednej linijki!
    level.draw(okno)

    # Rysujemy pozostałe obiekty
    box1.draw(okno)
    creature.draw(okno)
    ghost.draw(okno)

    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

pygame.quit()
sys.exit()