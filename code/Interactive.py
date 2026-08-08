import pygame


class Interactive:

    def __init__(self, x, y, w, h):

        self.rect = pygame.Rect(
            x,
            y,
            w,
            h
        )

        self.active = True

    def update(self, creature, ghost):
        pass

    def handle_event(self, event):
        pass

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            "white",
            self.rect,
            2
        )


class Lever(Interactive):

    def __init__(self, x, y, w, h, direction="left"):
        super().__init__(x, y, w, h)
        self.enabled = False
        self.direction = direction  # "left", "right", "top", lub "bottom"
        self.enter_side = None

    def update(self, creature, ghost):
        # Pobieramy pozycję ŚRODKA ducha
        prev_x, prev_y = ghost.last_pos.x, ghost.last_pos.y
        curr_x, curr_y = ghost.pos.x, ghost.pos.y

        # ==========================================
        # LEWO / PRAWO (Ruch poziomy)
        # ==========================================
        if self.direction in ("left", "right"):
            # Sprawdzamy czy duch znajduje się na wysokości Y dźwigni
            if self.rect.top <= curr_y <= self.rect.bottom:

                # 1. WYKRYWANIE WEJŚCIA
                if self.enter_side is None:
                    if prev_x <= self.rect.left and curr_x > self.rect.left:
                        self.enter_side = "left"
                    elif prev_x >= self.rect.right and curr_x < self.rect.right:
                        self.enter_side = "right"

                # 2. WYKRYWANIE WYJŚCIA (Przejście na wylot)
                elif self.enter_side == "left" and curr_x >= self.rect.right:
                    # Przejście Z LEWEJ NA PRAWO:
                    # Jeśli `direction == "left"` -> WŁĄCZA (True)
                    # Jeśli `direction == "right"` -> WYŁĄCZA (False)
                    self.enabled = (self.direction == "left")
                    self.enter_side = None

                elif self.enter_side == "right" and curr_x <= self.rect.left:
                    # Przejście Z PRAWEJ NA LEWO:
                    # Jeśli `direction == "right"` -> WŁĄCZA (True)
                    # Jeśli `direction == "left"` -> WYŁĄCZA (False)
                    self.enabled = (self.direction == "right")
                    self.enter_side = None

            else:
                # Jeśli duch wyleciał góra/dół - anulujemy ruch
                self.enter_side = None

        # ==========================================
        # GÓRA / DÓŁ (Ruch pionowy)
        # ==========================================
        elif self.direction in ("top", "bottom"):
            if self.rect.left <= curr_x <= self.rect.right:

                # 1. WYKRYWANIE WEJŚCIA
                if self.enter_side is None:
                    if prev_y <= self.rect.top and curr_y > self.rect.top:
                        self.enter_side = "top"
                    elif prev_y >= self.rect.bottom and curr_y < self.rect.bottom:
                        self.enter_side = "bottom"

                # 2. WYKRYWANIE WYJŚCIA (Przejście na wylot)
                elif self.enter_side == "top" and curr_y >= self.rect.bottom:
                    # Przejście Z GÓRY W DÓŁ
                    self.enabled = (self.direction == "top")
                    self.enter_side = None

                elif self.enter_side == "bottom" and curr_y <= self.rect.top:
                    # Przejście Z DOŁU W GÓRĘ
                    self.enabled = (self.direction == "bottom")
                    self.enter_side = None

            else:
                self.enter_side = None

    def draw(self, surface):
        color = "green" if self.enabled else "red"
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, "black", self.rect, 2)


class CodePanel(Interactive):

    def __init__(self, x, y, code):
        super().__init__(x, y, 60, 60)

        self.code = code
        self.current = ""
        self.is_unlocked = False  # Czy kod został poprawnie wpisany?
        self.is_open = False  # Czy okienko wpisywania jest aktywne?
        self.player_near = False  # Czy gracz stoi blisko panelu?

    def update(self, creature, ghost):
        # Sprawdzamy, czy gracz stoi przy panelu
        self.player_near = creature.rect.colliderect(self.rect)

        # Jeśli gracz odejdzie od panelu, automatycznie zamykamy okienko
        if not self.player_near and self.is_open:
            self.is_open = False
            self.current = ""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Otwieranie / Zamykanie okienka klawiszem Q (tylko gdy gracz stoi blisko)
            if event.key == pygame.K_q and self.player_near:
                self.is_open = not self.is_open
                self.current = ""  # Resetujemy kod przy otwarciu/zamknięciu

            # Zamykanie okienka klawiszem ESC
            elif event.key == pygame.K_ESCAPE and self.is_open:
                self.is_open = False
                self.current = ""

            # Wpisywanie kodu (działa TYLKO gdy okienko jest otwarte)
            elif self.is_open:
                if event.unicode.isdigit():
                    self.current += event.unicode

                # Usuwanie ostatniej cyfry klawiszem Backspace
                elif event.key == pygame.K_BACKSPACE:
                    self.current = self.current[:-1]

                # Jeśli wpisano za dużo cyfr -> reset
                if len(self.current) > len(self.code):
                    self.current = ""

                if self.current == self.code:
                    print("Kod poprawny!")
                    self.is_unlocked = True  # <--- To otworzy połączone drzwi!
                    self.is_open = False
                    self.current = ""

    def draw(self, surface):
        # Rysujemy główny niebieski panel
        pygame.draw.rect(surface, "blue", self.rect)

        # 1. Podpowiedź "Press Q" gdy gracz stoi w zasięgu
        if self.player_near and not self.is_open:
            font = pygame.font.Font(None, 24)
            hint = font.render("[Q] Enter Code", True, (255, 255, 255))
            surface.blit(hint, (self.rect.x - 10, self.rect.y - 25))

        # 2. OKIENKO POP-UP do wpisywania kodu
        if self.is_open:
            # Tło okienka (szary prostokąt nad panelem)
            popup_rect = pygame.Rect(self.rect.x - 30, self.rect.y - 70, 120, 50)
            pygame.draw.rect(surface, (40, 40, 40), popup_rect)
            pygame.draw.rect(surface, "white", popup_rect, 2)  # Biała ramka

            # Wyświetlanie wpisywanych cyfr (lub gwiazdek)
            font = pygame.font.Font(None, 32)
            # Pokazujemy cyfry i kropki/gwiazdki dla pozostałych miejsc
            display_text = self.current + "_" * (len(self.code) - len(self.current))
            text_surf = font.render(display_text, True, (0, 255, 0))  # Zielony tekst

            # Wyśrodkowanie tekstu w okienku
            text_rect = text_surf.get_rect(center=popup_rect.center)
            surface.blit(text_surf, text_rect)

class ScoringButton(Interactive):

    def __init__(self, x, y, required_power=0):
        super().__init__(x, y, 80, 20)

        self.required_power = required_power
        self.points = 100
        self.used = False

    def update(self, creature, ghost):
        # Sprawdzamy, czy gracz w ogóle dotyka przycisku
        if creature.rect.colliderect(self.rect):

            # ==========================================
            # 1. LOGIKA PRZYZNAWANIA PUNKTÓW
            # ==========================================
            if not self.used and creature.power >= self.required_power:
                if hasattr(creature, 'score'):
                    creature.score += self.points
                print(f"+ {self.points} pkt!")
                self.used = True

            # ==========================================
            # 2. KOLIZJA ZE WSZYSTKICH 4 STRON
            # ==========================================
            # Obliczamy ile pikseli gracz wnika w obiekt z każdej strony
            overlap_left   = creature.rect.right - self.rect.left
            overlap_right  = self.rect.right - creature.rect.left
            overlap_top    = creature.rect.bottom - self.rect.top
            overlap_bottom = self.rect.bottom - creature.rect.top

            # Znajdujemy najmniejsze wniknięcie (najkrótszy kierunek wypchnięcia)
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            # --- KOLIZJA Z GÓRY (Lądowanie na przycisku) ---
            if min_overlap == overlap_top and creature.vel_y >= 0:
                # Przy lądowaniu na obiekcie z góry (min_overlap == overlap_top):
                creature.rect.bottom = self.rect.top
                creature.vel_y = 0
                creature.is_grounded = True
                creature.jumps_left = creature.max_jumps  # <--- PRZYWRACAMY PODWÓJNY SKOK!
                creature.pos.y = creature.rect.centery

            # --- KOLIZJA Z DOŁU (Uderzenie głową od dołu) ---
            elif min_overlap == overlap_bottom and creature.vel_y < 0:
                creature.rect.top = self.rect.bottom
                creature.vel_y = 0
                creature.pos.y = creature.rect.centery

            # --- KOLIZJA Z LEWEJ STRONY (Wpadnięcie od lewej) ---
            elif min_overlap == overlap_left:
                creature.rect.right = self.rect.left
                creature.pos.x = creature.rect.centerx

            # --- KOLIZJA Z PRAWEJ STRONY (Wpadnięcie od prawej) ---
            elif min_overlap == overlap_right:
                creature.rect.left = self.rect.right
                creature.pos.x = creature.rect.centerx

    def draw(self, surface):
        color = "gray" if self.used else "yellow"

        # Wypełnienie przycisku
        pygame.draw.rect(surface, color, self.rect)
        # Czarna ramka wokół przycisku
        pygame.draw.rect(surface, "black", self.rect, 2)


class Door(Interactive):
    def __init__(self, x, y, w=30, h=120, trigger_object=None):
        super().__init__(x, y, w, h)
        self.is_open = False
        self.trigger_object = trigger_object

    def update(self, creature, ghost):
        if self.trigger_object:
            if hasattr(self.trigger_object, 'enabled'):
                self.is_open = self.trigger_object.enabled
            elif hasattr(self.trigger_object, 'is_unlocked'):
                self.is_open = self.trigger_object.is_unlocked

        if not self.is_open and creature.rect.colliderect(self.rect):
            overlap_left = creature.rect.right - self.rect.left
            overlap_right = self.rect.right - creature.rect.left
            overlap_top = creature.rect.bottom - self.rect.top
            overlap_bottom = self.rect.bottom - creature.rect.top

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left:
                creature.rect.right = self.rect.left
                creature.pos.x = creature.rect.centerx
            elif min_overlap == overlap_right:
                creature.rect.left = self.rect.right
                creature.pos.x = creature.rect.centerx
            elif min_overlap == overlap_top and creature.vel_y >= 0:
                # LĄDOWANIE NA DRZWIACH Z GÓRY:
                creature.rect.bottom = self.rect.top
                creature.vel_y = 0
                creature.pos.y = creature.rect.centery

                # REKODUJEMY PODWÓJNY SKOK!
                if hasattr(creature, 'reset_jumps'):
                    creature.reset_jumps()
                else:
                    creature.is_grounded = True

            elif min_overlap == overlap_bottom and creature.vel_y < 0:
                creature.rect.top = self.rect.bottom
                creature.vel_y = 0
                creature.pos.y = creature.rect.centery

class LevelGate(Interactive):

    def __init__(self, x, y):

        super().__init__(
            x,
            y,
            100,
            120
        )

        self.triggered = False

    def update(self, creature, ghost):

        if self.triggered:
            return

        if (
            creature.rect.colliderect(self.rect)
            and
            ghost.rect.colliderect(self.rect)
        ):

            print("NEXT LEVEL")

            self.triggered = True

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            "purple",
            self.rect
        )

# =========================================================
# INTERACTIVE MANAGER
# =========================================================

class InteractiveManager():

    def __init__(self):
        self.objects = []

    def add(self, obj: Interactive):
        self.objects.append(obj)

    def update_all(self, creature, ghost):
        for obj in self.objects:
            if obj.active:
                obj.update(creature, ghost)

    def handle_event_all(self, event):
        for obj in self.objects:
            if obj.active:
                obj.handle_event(event)

    def draw_all(self, surface):
        for obj in self.objects:
            if obj.active:
                obj.draw(surface)