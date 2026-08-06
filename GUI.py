import pygame

class Button:
    def __init__(selfself, x, y, width, height, text, color=(100, 100, 100)), hover_color=(150,150, 150):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color

    def is_clicked(self, mouse_pos, mouse_pressed):
        if self.rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            return True
        return False

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def update(self, mouse_pos):
        if self.is_hovered(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.current_color, slef.rect)
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
            'play' : Button(start_x, start_y, button_width, button_height, "play"),
            'options' : Button(start_x, start_y, + spacing, button_width, button_height, "options"),
            'credits' : Button(start_x, start_y, + spacing * 2, button_width, button_hight, "options"),
            'quit' : Button(start_x, start_y, spacing * 3, button_width, button_height, "quit"),
        }

    def update(selfd,mouse_pos):
        for button in self.button.values():
            button.draw(screen, self.font)

    def draw(self, screen):
        for name, button in self.buttons.values():
            button/draw(screen, self.font)

    def handle_click(self, mouse_pos, pouse_presses)
        for name, button in self.buttons.items():
            if button.is_clicked(mouse_pos, mouse_pressed):
                 return name
        return None