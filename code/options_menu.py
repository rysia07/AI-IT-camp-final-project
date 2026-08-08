import pygame

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 150, 255), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False
        self.active_color = (150, 200, 255)
        self.idle_color = color

    def draw(self, surface, font):
        current_color = self.active_color if self.hovered else self.idle_color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)

        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]


class OptionsMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.active = False
        self.show_controls = False
        self.volume = 100

        button_width = 220
        button_height = 60
        center_x = width // 2 - button_width // 2

        self.volume_button = Button(center_x, height // 2 - 40, button_width, button_height, "VOLUME: 100")
        self.controls_button = Button(center_x, height // 2 + 40, button_width, button_height, "CONTROLS")
        self.back_button = Button(center_x, height // 2 + 130, button_width, button_height, "BACK")
        self.buttons = [self.volume_button, self.controls_button, self.back_button]

    def update(self, mouse_pos):
        for button in self.buttons:
            button.update(mouse_pos)

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for button in self.buttons:
            button.update(mouse_pos)
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
        if not self.active:
            return

        surface.fill((30, 30, 30))

        font_large = pygame.font.Font(None, 70)
        title = font_large.render("OPTIONS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        surface.blit(title, title_rect)

        font_button = pygame.font.Font(None, 38)
        for button in self.buttons:
            button.draw(surface, font_button)

        if self.show_controls:
            panel = pygame.Surface((520, 220))
            panel.fill((50, 70, 90))
            panel.set_alpha(230)
            surface.blit(panel, (190, 230))

            font_title = pygame.font.Font(None, 40)
            title = font_title.render("Controls", True, (255, 255, 255))
            surface.blit(title, (330, 245))

            font_text = pygame.font.Font(None, 32)
            lines = [
                "A / D  - Move",
                "W      - Jump",
                "S      - Fast Fall",
                "2      - Attack",
                "ESC    - Pause / Menu"
            ]
            y = 285
            for line in lines:
                text = font_text.render(line, True, (240, 240, 240))
                surface.blit(text, (240, y))
                y += 32
