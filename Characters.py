import pygame


class Character:
    def __init__(self, x, y, size, image=None):
        self.pos = pygame.Vector2(x, y)
        self.size = size
        self.image = image

        self.rect = pygame.Rect(
            x - size,
            y - size,
            size * 2,
            size * 2
        )


    def update(self):
        self.rect.center = self.pos


    def draw(self, surface):
        if self.image:
            surface.blit(
                self.image,
                self.rect
            )
        else:
            # placeholder
            pygame.draw.circle(
                surface,
                "red",
                self.pos,
                self.size
            )