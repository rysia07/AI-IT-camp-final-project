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

    def __init__(self, x, y, w=100, h=20, direction="left"):

        super().__init__(
            x,
            y,
            w,
            h
        )

        self.enabled = False
        self.direction = direction
        self.enter_side = None

    def update(self, creature, ghost):

        # ==========================================
        # LEWO / PRAWO
        # ==========================================

        if self.direction in ("left", "right"):

            # POPRZEDNIA pozycja hitboxa ducha
            previous_left = ghost.last_pos.x - ghost.rect.width / 2
            previous_right = ghost.last_pos.x + ghost.rect.width / 2

            # OBECNA pozycja hitboxa ducha
            current_left = ghost.rect.left
            current_right = ghost.rect.right

            # ======================================
            # NIE ROZPOCZĘTO PRZEJŚCIA
            # ======================================

            if self.enter_side is None:

                # Duch wchodzi z lewej
                if (
                        previous_right <= self.rect.left
                        and
                        current_right > self.rect.left
                ):

                    self.enter_side = "left"


                # Duch wchodzi z prawej
                elif (
                        previous_left >= self.rect.right
                        and
                        current_left < self.rect.right
                ):

                    self.enter_side = "right"


            # ======================================
            # WESZEDŁ Z LEWEJ
            # ======================================

            elif self.enter_side == "left":

                # Musi CAŁKOWICIE przejść za prawą krawędź
                if current_left >= self.rect.right:
                    self.enabled = not self.enabled
                    self.enter_side = None


            # ======================================
            # WESZEDŁ Z PRAWEJ
            # ======================================

            elif self.enter_side == "right":

                # Musi CAŁKOWICIE przejść za lewą krawędź
                if current_right <= self.rect.left:
                    self.enabled = not self.enabled
                    self.enter_side = None


        # ==========================================
        # GÓRA / DÓŁ
        # ==========================================

        elif self.direction in ("top", "bottom"):

            # POPRZEDNIA pozycja hitboxa ducha
            previous_top = ghost.last_pos.y - ghost.rect.height / 2
            previous_bottom = ghost.last_pos.y + ghost.rect.height / 2

            # OBECNA pozycja hitboxa ducha
            current_top = ghost.rect.top
            current_bottom = ghost.rect.bottom

            # ======================================
            # NIE ROZPOCZĘTO PRZEJŚCIA
            # ======================================

            if self.enter_side is None:

                # Duch wchodzi z góry
                if (
                        previous_bottom <= self.rect.top
                        and
                        current_bottom > self.rect.top
                ):

                    self.enter_side = "top"


                # Duch wchodzi z dołu
                elif (
                        previous_top >= self.rect.bottom
                        and
                        current_top < self.rect.bottom
                ):

                    self.enter_side = "bottom"


            # ======================================
            # WESZEDŁ Z GÓRY
            # ======================================

            elif self.enter_side == "top":

                # Musi CAŁKOWICIE przejść za dół
                if current_top >= self.rect.bottom:
                    self.enabled = not self.enabled
                    self.enter_side = None


            # ======================================
            # WESZEDŁ Z DOŁU
            # ======================================

            elif self.enter_side == "bottom":

                # Musi CAŁKOWICIE przejść za górę
                if current_bottom <= self.rect.top:
                    self.enabled = not self.enabled
                    self.enter_side = None

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