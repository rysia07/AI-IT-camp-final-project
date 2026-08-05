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


    def update_rect(self):
        self.rect.center = self.pos


    def draw(self, surface):

        if self.image:
            surface.blit(self.image, self.rect)

        else:
            pygame.draw.circle(
                surface,
                "white",
                self.pos,
                self.size
            )



class Creature(Character):

    def __init__(self, x, y):
        super().__init__(x, y, 40)

        self.speed = 500
        self.health = 100


    def update(self, dt):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.pos.x -= self.speed * dt

        if keys[pygame.K_d]:
            self.pos.x += self.speed * dt

        self.update_rect()



    def attack(self):
        print("Atak!")



class GhostMouse(Character):

    def __init__(self, x, y):
        super().__init__(x, y, 20)

        self.interaction_range = 100


    def update(self):

        mouse_x, mouse_y = pygame.mouse.get_pos()

        self.pos.x = mouse_x
        self.pos.y = mouse_y

        self.update_rect()



    def interact(self, objects):

        for obj in objects:

            if self.rect.colliderect(obj.rect):
                print("Duch oddziałuje z obiektem")