import pygame


class Button:
    """Uniwersalna klasa przycisku dla wszystkich menu."""

    def __init__(self, x, y, width, height, text, action, idle_color=(70, 70, 70), active_color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.idle_color = idle_color
        self.active_color = active_color
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font):
        color = self.active_color if self.hovered else self.idle_color

        # Wypełnienie z zaokrąglonymi rogami i jasne obramowanie
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=8)

        # Rysowanie tekstu
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class BaseMenu:
    """Bazowa klasa pomocnicza dla wspólnego wyglądu menu."""

    def __init__(self, width, height, title_text):
        self.width = width
        self.height = height
        self.title_text = title_text
        self.title_font = pygame.font.Font(None, 64)
        self.btn_font = pygame.font.Font(None, 36)
        self.buttons = []

    def handle_input(self, pos, mouse_buttons=None):
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                return button.action
        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)

    def draw_background_and_title(self, surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title_surf = self.title_font.render(self.title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.width // 2, 120))
        surface.blit(title_surf, title_rect)

    def draw(self, surface):
        self.draw_background_and_title(surface)
        for button in self.buttons:
            button.draw(surface, self.btn_font)


class MainMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "ALIEN SPACE")
        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2
        start_y = 200
        spacing = 70

        self.buttons = [
            Button(center_x, start_y, btn_w, btn_h, "Graj", "play"),
            Button(center_x, start_y + spacing, btn_w, btn_h, "Opcje", "options"),
            Button(center_x, start_y + spacing * 2, btn_w, btn_h, "Autorzy", "credits"),
            Button(center_x, start_y + spacing * 3, btn_w, btn_h, "Wyjście", "quit")
        ]

    # Kompatybilność z poprzednim kodem w main.py
    def handle_click(self, pos, mouse_buttons=None):
        return self.handle_input(pos, mouse_buttons)


class OptionsMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "OPCJE")
        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2

        self.buttons = [
            Button(center_x, 400, btn_w, btn_h, "Powrót", "back")
        ]


class CreditsMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "AUTORZY")
        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2

        self.buttons = [
            Button(center_x, 400, btn_w, btn_h, "Powrót", "back")
        ]


class FailureMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "PORAŻKA")
        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2
        start_y = 250
        spacing = 70

        self.buttons = [
            Button(center_x, start_y, btn_w, btn_h, "Spróbuj ponownie", "retry"),
            Button(center_x, start_y + spacing, btn_w, btn_h, "Menu Główna", "menu")
        ]


class VictoryMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "ZWYCIĘSTWO!")
        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2
        start_y = 250
        spacing = 70

        self.buttons = [
            Button(center_x, start_y, btn_w, btn_h, "Następny Poziom", "next"),
            Button(center_x, start_y + spacing, btn_w, btn_h, "Menu Główna", "menu")
        ]