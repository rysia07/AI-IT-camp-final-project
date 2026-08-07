import pygame


class Interactive:

    def __init__(self, x, y, w, h):

        self.rect = pygame.Rect(
            x,
            y,
            w,
            h
        )

        self.active = True

    def update(self, creature, ghost):
        pass

    def handle_event(self, event):
        pass

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            "white",
            self.rect,
            2
        )


class Lever(Interactive):

    def __init__(self, x, y,w = 20, h =100, direction= "left"):

        super().__init__(
            x,
            y,
            h,
            w
        )

        self.enabled = False
        self.direction = direction

    def update(self, creature, ghost):

        if self.enabled:
            return

        if not ghost.rect.colliderect(self.rect):
            return

        # =========================
        # WEJŚCIE OD LEWEJ
        # =========================

        if self.direction == "left":

            if ghost.last_pos.x <= self.rect.left:
                self.enabled = True

        # =========================
        # WEJŚCIE OD PRAWEJ
        # =========================

        elif self.direction == "right":

            if ghost.last_pos.x >= self.rect.right:
                self.enabled = True

        # =========================
        # WEJŚCIE OD GÓRY
        # =========================

        elif self.direction == "top":

            if ghost.last_pos.y <= self.rect.top:
                self.enabled = True

        # =========================
        # WEJŚCIE OD DOŁU
        # =========================

        elif self.direction == "bottom":

            if ghost.last_pos.y >= self.rect.bottom:
                self.enabled = True

        if self.enabled:
            print("Dźwignia aktywowana!")

    def draw(self, surface):

        color = "green" if self.enabled else "red"

        pygame.draw.rect(
            surface,
            color,
            self.rect
        )

class CodePanel(Interactive):

    def __init__(self, x, y):

        super().__init__(
            x,
            y,
            60,
            60
        )

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

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            "blue",
            self.rect
        )


class ScoringButton(Interactive):

    def __init__(self, x, y, required_power):

        super().__init__(
            x,
            y,
            80,
            20
        )

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

        color = "gray" if self.used else "yellow"

        pygame.draw.rect(
            surface,
            color,
            self.rect
        )


class LevelGate(Interactive):

    def __init__(self, x, y):

        super().__init__(
            x,
            y,
            100,
            120
        )

        self.triggered = False

    def update(self, creature, ghost):

        if self.triggered:
            return

        if (
            creature.rect.colliderect(self.rect)
            and
            ghost.rect.colliderect(self.rect)
        ):

            print("NEXT LEVEL")

            self.triggered = True

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            "purple",
            self.rect
        )