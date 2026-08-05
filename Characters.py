import pygame


class Character:
    def __init__(self, x, y, radius, color):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius
        self.color = color

        self.rect = pygame.Rect(
            x - radius,
            y - radius,
            radius * 2,
            radius * 2
        )

    def update_rect(self):
        # Konwersja na int chroni przed ostrzeżeniami typów
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt):
        self.update_rect()

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.pos.x), int(self.pos.y)),
            self.radius
        )


class Creature(Character):
    def __init__(self, x, y):
        super().__init__(x, y, 40, "red")

        # Statystyki gracza
        self.hp = 100
        self.power = 0  # 0 = jump, 1 = drop, 2 = double jump

        # Parametry ruchu i fizyki
        self.speed = 400
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
                if (self.pos.y + self.radius) - self.vel_y * dt <= platform.top + 10:
                    self.pos.y = platform.top - self.radius
                    self.vel_y = 0
                    was_grounded_this_frame = True
                    self.update_rect()

        self.is_grounded = was_grounded_this_frame


class GhostMouse(Character):
    def __init__(self, x=0, y=0):
        super().__init__(x, y, 20, "cyan")
        self.hp = 50

    def interact(self, objects):
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                print("Duch oddziałuje z obiektem")

    def update(self, dt=0):
        # Ruch podążający za pozycją myszy
        self.pos = pygame.Vector2(pygame.mouse.get_pos())
        super().update(dt)