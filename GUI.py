import pygame

class Button:
    def __init__(self, x, y, width, height, text,
                 color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def update(self, mouse_pos):
        self.current_color = self.hover_color if self.is_hovered(mouse_pos) else self.color

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 50)

        button_width = 200
        button_height = 80
        start_x = 100
        start_y = 200
        spacing = 120

        self.buttons = {
            'play': Button(start_x, start_y, button_width, button_height, "Play"),
            'options': Button(start_x, start_y + spacing, button_width, button_height, "Options"),
            'credits': Button(start_x, start_y + spacing * 2, button_width, button_height, "Credits"),
            'quit': Button(start_x, start_y + spacing * 3, button_width, button_height, "Quit"),
        }

    # update expects mouse_pos (not screen)
    def update(self, mouse_pos):
        for button in self.buttons.values():
            button.update(mouse_pos)

    def draw(self, screen):
        for button in self.buttons.values():
            button.draw(screen, self.font)

    def handle_click(self, mouse_pos, mouse_pressed):
        for name, button in self.buttons.items():
            if button.is_clicked(mouse_pos, mouse_pressed):
                return name
        return None