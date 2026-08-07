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

    def __init__(self, x, y, w=100, h=20, direction="left"):
        super().__init__(x, y, w, h)
        self.enabled = False
        self.direction = direction
        self.enter_side = None

    def update(self, creature, ghost):
        # Pobieramy dokładną pozycję ŚRODKA ducha z tej i poprzedniej klatki
        prev_x, prev_y = ghost.last_pos.x, ghost.last_pos.y
        curr_x, curr_y = ghost.pos.x, ghost.pos.y

        # ==========================================
        # LEWO / PRAWO (Przełączanie po przejściu w poziomie)
        # ==========================================
        if self.direction in ("left", "right"):
            # Upewniamy się, że duch jest na wysokości Y dźwigni
            if self.rect.top <= curr_y <= self.rect.bottom:

                if self.enter_side is None:
                    # Wejście od lewej
                    if prev_x <= self.rect.left and curr_x > self.rect.left:
                        self.enter_side = "left"
                    # Wejście od prawej
                    elif prev_x >= self.rect.right and curr_x < self.rect.right:
                        self.enter_side = "right"

                elif self.enter_side == "left":
                    # Przejście całkowicie na drugą stronę (w prawo)
                    if curr_x >= self.rect.right:
                        self.enabled = not self.enabled
                        self.enter_side = None

                elif self.enter_side == "right":
                    # Przejście całkowicie na drugą stronę (w lewo)
                    if curr_x <= self.rect.left:
                        self.enabled = not self.enabled
                        self.enter_side = None

            else:
                # Jeśli duch odleciał w górę/dół poza dźwignię, resetujemy stan przejścia
                self.enter_side = None

        # ==========================================
        # GÓRA / DÓŁ (Przełączanie po przejściu w pionie)
        # ==========================================
        elif self.direction in ("top", "bottom"):
            # Upewniamy się, że duch jest na szerokości X dźwigni
            if self.rect.left <= curr_x <= self.rect.right:

                if self.enter_side is None:
                    # Wejście od góry
                    if prev_y <= self.rect.top and curr_y > self.rect.top:
                        self.enter_side = "top"
                    # Wejście od dołu
                    elif prev_y >= self.rect.bottom and curr_y < self.rect.bottom:
                        self.enter_side = "bottom"

                elif self.enter_side == "top":
                    # Przejście całkowicie w dół
                    if curr_y >= self.rect.bottom:
                        self.enabled = not self.enabled
                        self.enter_side = None

                elif self.enter_side == "bottom":
                    # Przejście całkowicie w górę
                    if curr_y <= self.rect.top:
                        self.enabled = not self.enabled
                        self.enter_side = None

            else:
                self.enter_side = None

    def draw(self, surface):

        color = "green" if self.enabled else "red"

        pygame.draw.rect(
            surface,
            color,
            self.rect
        )


class CodePanel(Interactive):

    def __init__(self, x, y, code):
        super().__init__(x, y, 60, 60)

        self.code = code
        self.current = ""
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

                # Sprawdzenie poprawności kodu
                if self.current == self.code:
                    print("Kod poprawny! Otwieranie...")
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
        # Sprawdzamy kolizję hitboksu gracza z przyciskiem
        if creature.rect.colliderect(self.rect):

            # ==========================================
            # 1. LOGIKA PRZYZNAWANIA PUNKTÓW
            # ==========================================
            if not self.used and creature.power >= self.required_power:
                # Jeśli gracz ma zmienną score w klasie, dodajemy punkty
                if hasattr(creature, 'score'):
                    creature.score += self.points

                print(f"+ {self.points} pkt!")
                self.used = True

            # ==========================================
            # 2. FIZYCZNA KOLIZJA (Gracz staje na przycisku)
            # ==========================================
            # Jeśli gracz opada na przycisk z góry
            if creature.vel_y > 0 and creature.rect.bottom <= self.rect.top + 15:
                creature.rect.bottom = self.rect.top
                creature.vel_y = 0
                creature.is_grounded = True
                creature.pos.y = creature.rect.centery

    def draw(self, surface):
        color = "gray" if self.used else "yellow"

        # Rysujemy sam przycisk
        pygame.draw.rect(surface, color, self.rect)
        # Rysujemy delikatną czarną ramkę wokół niego
        pygame.draw.rect(surface, "black", self.rect, 2)

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