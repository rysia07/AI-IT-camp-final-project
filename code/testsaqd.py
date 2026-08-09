import pygame
import pygame_gui
pygame.init()
# Ustawienia okna gry
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Przykład GUI z pygame_gui")
# Menedżer GUI
manager = pygame_gui.UIManager(window_size)
# Dodanie przycisku
button = pygame_gui.elements.UIButton(
   relative_rect=pygame.Rect((350, 275), (100, 50)),
   text='Kliknij mnie',
   manager=manager
)
# Główna pętla gry
clock = pygame.time.Clock()
running = True
while running:
   time_delta = clock.tick(60) / 1000.0 # Czas między klatkami
   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           running = False
       # Obsługa zdarzeń GUI
       if event.type == pygame.USEREVENT:
           if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
               if event.ui_element == button:
                   print("Przycisk został kliknięty!")
       manager.process_events(event)
   # Aktualizacja GUI
   manager.update(time_delta)
   # Renderowanie
   screen.fill((0, 0, 0)) # Czyszczenie ekranu
   manager.draw_ui(screen) # Rysowanie elementów GUI
   pygame.display.update()
pygame.quit()