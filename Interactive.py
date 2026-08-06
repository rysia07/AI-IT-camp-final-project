import sys
import pygame

pygame.init()

WIDTH, HEIGHT = 1280, 720

okno = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

running = True
dt = 0


# ==========================
#       CHARACTERS
# ==========================

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
        self.rect.center = self.pos

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

        self.hp = 100

        # 0 = jump
        # 1 = jump + drop
        # 2 = double jump + drop
        self.power = 0

    def update(self, dt):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.pos.x -= 400 * dt

        if keys[pygame.K_d]:
            self.pos.x += 400 * dt

        super().update(dt)


class GhostMouse(Character):

    def __init__(self):
        super().__init__(0, 0, 20, "cyan")

        self.hp = 50

    def update(self, dt):

        self.pos = pygame.Vector2(
            pygame.mouse.get_pos()
        )

        super().update(dt)


# ==========================
#      INTERACTIVE
# ==========================

class Interactive:

    def __init__(self, x, y, w, h):

        self.rect = pygame.Rect(x, y, w, h)

        self.active = True

    def update(self, creature, ghost):
        pass

    def draw(self, surface):
        pygame.draw.rect(surface, "white", self.rect, 2)


class Lever(Interactive):

    def __init__(self, x, y):
        super().__init__(x, y, 40, 60)

        self.enabled = False

    def update(self, creature, ghost):

        if ghost.rect.colliderect(self.rect):

            keys = pygame.key.get_pressed()

            if keys[pygame.K_e]:
                self.enabled = not self.enabled

    def draw(self, surface):

        color = "green" if self.enabled else "red"

        pygame.draw.rect(surface, color, self.rect)


class CodePanel(Interactive):

    def __init__(self, x, y):

        super().__init__(x, y, 60, 60)

        self.code = "1234"
        self.current = ""

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.unicode.isdigit():

                self.current += event.unicode

            if len(self.current) > len(self.code):

                self.current = ""

            if self.current == self.code:

                print("Kod poprawny!")

                self.current = ""


class ScoringButton(Interactive):

    def __init__(self, x, y, required_power):

        super().__init__(x, y, 80, 20)

        self.required_power = required_power

        self.points = 100

        self.used = False

    def update(self, creature, ghost):

        if self.used:
            return

        if creature.rect.colliderect(self.rect):

            if creature.power >= self.required_power:

                print("+", self.points, "pkt")

                self.used = True

    def draw(self, surface):

        color = "yellow"

        if self.used:
            color = "gray"

        pygame.draw.rect(surface, color, self.rect)


class LevelGate(Interactive):

    def __init__(self, x, y):

        super().__init__(x, y, 100, 120)

    def update(self, creature, ghost):

        if (
            creature.rect.colliderect(self.rect)
            and
            ghost.rect.colliderect(self.rect)
        ):

            print("NEXT LEVEL")

    def draw(self, surface):

        pygame.draw.rect(surface, "purple", self.rect)


# ==========================
#      WORLD
# ==========================

creature = Creature(300, 400)
ghost = GhostMouse()

lever = Lever(500, 300)

panel = CodePanel(700, 300)

button = ScoringButton(250, 500, 1)

gate = LevelGate(1100, 500)

objects = [
    lever,
    panel,
    button,
    gate
]


# ==========================
#      GAME LOOP
# ==========================

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        panel.handle_event(event)

    creature.update(dt)

    ghost.update(dt)

    for obj in objects:

        obj.update(creature, ghost)

    okno.fill((50, 60, 70))

    creature.draw(okno)

    ghost.draw(okno)

    for obj in objects:

        obj.draw(okno)

    pygame.display.flip()

    dt = clock.tick(60) / 1000


pygame.quit()
sys.exit()