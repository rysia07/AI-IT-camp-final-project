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


class CreditsMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.active = False

        button_width = 220
        button_height = 60
        center_x = width // 2 - button_width // 2

        self.back_button = Button(center_x, height // 2 + 120, button_width, button_height, "BACK")
        self.buttons = [self.back_button]

    def update(self, mouse_pos):
        for button in self.buttons:
            button.update(mouse_pos)

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for button in self.buttons:
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_pressed):
                if button == self.back_button:
                    self.active = False
                    return "back"

        return None

    def draw(self, surface):
        if not self.active:
            return

        surface.fill((30, 30, 30))

        font_large = pygame.font.Font(None, 70)
        title = font_large.render("CREDITS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        surface.blit(title, title_rect)

        font_text = pygame.font.Font(None, 36)
        text = font_text.render("Made by your team", True, (220, 220, 220))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(text, text_rect)

        font_button = pygame.font.Font(None, 38)
        for button in self.buttons:
            button.draw(surface, font_button)
