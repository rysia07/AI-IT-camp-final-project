import pygame


class Button:
    """Uniwersalny, klikalny przycisk dla interfejsu użytkownika."""
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        color=(100, 100, 100),
        hover_color=(150, 150, 150),
        text_color=(255, 255, 255)
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.hovered = False

    def update(self, mouse_pos):
        """Aktualizuje stan najechania myszą."""
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.hovered else self.color

    def is_clicked(self, mouse_pos, mouse_pressed):
        """Sprawdza, czy przycisk został kliknięty lewym przyciskiem myszy."""
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

    def draw(self, surface, font):
        """Rysuje przycisk na podanej powierzchni."""
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class MainMenu:
    """Główne menu gry."""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 40)
        self.title_font = pygame.font.Font(None, 70)

        button_width = 200
        button_height = 60
        start_x = 50
        start_y = 150
        spacing = 80

        self.buttons = {
            'play': Button(start_x, start_y, button_width, button_height, "Play"),
            'options': Button(start_x, start_y + spacing, button_width, button_height, "Options"),
            'credits': Button(start_x, start_y + spacing * 2, button_width, button_height, "Credits"),
            'quit': Button(start_x, start_y + spacing * 3, button_width, button_height, "Quit"),
        }

    def update(self, mouse_pos):
        """Aktualizuje stan przycisków w menu."""
        for button in self.buttons.values():
            button.update(mouse_pos)

    def handle_click(self, mouse_pos, mouse_pressed):
        """Obsługuje kliknięcia w menu i zwraca nazwę akcji."""
        for name, button in self.buttons.items():
            if button.is_clicked(mouse_pos, mouse_pressed):
                return name
        return None

    def draw(self, screen):
        """Rysuje menu główne."""
        title = self.title_font.render("MAIN MENU", True, (255, 200, 50))
        screen.blit(title, (50, 50))

        for button in self.buttons.values():
            button.draw(screen, self.font)


class OptionsMenu:
    """Ekran opcji z ustawieniami głośności i sterowania."""
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.active = False
        self.show_controls = False
        self.volume = 100
        self.font = pygame.font.Font(None, 38)

        button_width = 220
        button_height = 60
        center_x = screen_width // 2 - button_width // 2

        self.volume_button = Button(center_x, screen_height // 2 - 40, button_width, button_height, "VOLUME: 100")
        self.controls_button = Button(center_x, screen_height // 2 + 40, button_width, button_height, "CONTROLS")
        self.back_button = Button(center_x, screen_height // 2 + 130, button_width, button_height, "BACK")
        self.buttons = [self.volume_button, self.controls_button, self.back_button]

    def update(self, mouse_pos):
        for button in self.buttons:
            button.update(mouse_pos)

    def handle_input(self, mouse_pos, mouse_pressed):
        for button in self.buttons:
            if button.is_clicked(mouse_pos, mouse_pressed):
                if button == self.volume_button:
                    self.volume = 100 if self.volume == 0 else 0
                    self.volume_button.text = f"VOLUME: {self.volume}"
                    return "volume"
                elif button == self.controls_button:
                    self.show_controls = not self.show_controls
                    return "controls"
                elif button == self.back_button:
                    self.active = False
                    self.show_controls = False
                    return "back"
        return None

    def draw(self, surface):
        surface.fill((30, 30, 30))

        font_large = pygame.font.Font(None, 70)
        title = font_large.render("OPTIONS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 5))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface, self.font)

        if self.show_controls:
            panel = pygame.Surface((520, 220))
            panel.fill((50, 70, 90))
            panel.set_alpha(230)
            surface.blit(panel, (self.width // 2 - 260, self.height // 2 - 100))

            font_title = pygame.font.Font(None, 40)
            t = font_title.render("Controls", True, (255, 255, 255))
            surface.blit(t, (self.width // 2 - 50, self.height // 2 - 85))

            font_text = pygame.font.Font(None, 32)
            lines = [
                "A / D  - Move",
                "W      - Jump",
                "S      - Fast Fall",
                "2      - Attack",
                "ESC    - Pause / Menu"
            ]
            y = self.height // 2 - 40
            for line in lines:
                text = font_text.render(line, True, (240, 240, 240))
                surface.blit(text, (self.width // 2 - 140, y))
                y += 30


class CreditsMenu:
    """Ekran twórców gry."""
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.active = False
        self.font = pygame.font.Font(None, 38)

        button_width = 220
        button_height = 60
        center_x = screen_width // 2 - button_width // 2

        self.back_button = Button(center_x, screen_height // 2 + 120, button_width, button_height, "BACK")
        self.buttons = [self.back_button]

    def update(self, mouse_pos):
        for button in self.buttons:
            button.update(mouse_pos)

    def handle_input(self, mouse_pos, mouse_pressed):
        for button in self.buttons:
            if button.is_clicked(mouse_pos, mouse_pressed):
                if button == self.back_button:
                    self.active = False
                    return "back"
        return None

    def draw(self, surface):
        surface.fill((30, 30, 30))

        font_large = pygame.font.Font(None, 70)
        title = font_large.render("CREDITS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        surface.blit(title, title_rect)

        font_text = pygame.font.Font(None, 36)
        text = font_text.render("Made by G-Team", True, (220, 220, 220))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(text, text_rect)

        for button in self.buttons:
            button.draw(surface, self.font)


class PauseMenu:
    """Menu pauzy nakładane na aktualny stan gry."""
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.active = False
        self.font = pygame.font.Font(None, 36)

        button_width = 200
        button_height = 50
        center_x = screen_width // 2 - button_width // 2

        self.resume_button = Button(center_x, screen_height // 2 - 40, button_width, button_height, "RESUME")
        self.quit_button = Button(center_x, screen_height // 2 + 30, button_width, button_height, "MENU")
        self.buttons = [self.resume_button, self.quit_button]

    def toggle(self):
        self.active = not self.active

    def update(self, mouse_pos):
        for button in self.buttons:
            button.update(mouse_pos)

    def handle_input(self, mouse_pos, mouse_pressed):
        for button in self.buttons:
            if button.is_clicked(mouse_pos, mouse_pressed):
                if button == self.resume_button:
                    self.active = False
                    return "resume"
                elif button == self.quit_button:
                    self.active = False
                    return "menu"
        return None

    def draw(self, surface):
        if not self.active:
            return

        # Przyciemnienie tła gry
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 64)
        title = font_large.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface, self.font)