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
        self.rect.center = (int(self.pos.x), int(self.pos.y))


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

        # Parametry ruchu i fizyki
        self.speed = 500
        self.jump_force = -1000
        self.gravity = 2000
        self.vel_y = 0
        self.is_grounded = False

    def update(self, dt, platforms):
        keys = pygame.key.get_pressed()

        # 1. Skok (klawisz W)
        if keys[pygame.K_w] and self.is_grounded:
            self.vel_y = self.jump_force
            self.is_grounded = False

        # 2. Grawitacja i opadanie (klawisz S przyspiesza opadanie)
        if not self.is_grounded:
            current_gravity = self.gravity * 3 if keys[pygame.K_s] else self.gravity
            self.vel_y += current_gravity * dt

        self.pos.y += self.vel_y * dt

        # 3. Ruch w lewo/prawo (A / D)
        if keys[pygame.K_a]:
            self.pos.x -= self.speed * dt
        if keys[pygame.K_d]:
            self.pos.x += self.speed * dt

        # Aktualizacja pozycji prostokąta kolizji
        self.update_rect()

        # 4. Kolizje z platformami
        was_grounded_this_frame = False
        for platform in platforms:
            if self.rect.colliderect(platform) and self.vel_y >= 0:
                if (self.pos.y + self.size) - self.vel_y * dt <= platform.top + 10:
                    self.pos.y = platform.top - self.size
                    self.vel_y = 0
                    was_grounded_this_frame = True
                    self.update_rect()

        self.is_grounded = was_grounded_this_frame


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
                print()