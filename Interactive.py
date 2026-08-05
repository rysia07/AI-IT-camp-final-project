import pygame
class ClickableBox:
    def __init__(self, x, y, width, height, color, hover_color, click_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.click_color = click_color
        self.is_hovered = False
        self.is_clicked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_clicked = True

    def draw(self, surface):
        color = self.click_color if self.is_clicked else self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)