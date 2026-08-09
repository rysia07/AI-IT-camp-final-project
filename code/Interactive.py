
import pygame

from animations import SpriteObject


# =========================================================
# INTERACTIVE
# =========================================================

class Interactive:

    def __init__(
        self,
        x,
        y,
        w,
        h
    ):

        self.rect = pygame.Rect(
            int(x),
            int(y),
            int(w),
            int(h)
        )

        self.active = True

        self.color = (
            150,
            150,
            150
        )

        self.sprite = None
        self.current_anim = None

    # =====================================================
    # ANIMATION
    # =====================================================

    def add_anim(
        self,
        name,
        frames,
        cols,
        rows,
        speed=100,
        loop=True,
        spritesheet_path=None,
        scale=1.0
    ):

        if self.sprite is None:

            if spritesheet_path is None:

                raise ValueError(
                    "spritesheet_path is required "
                    "for the first animation."
                )

            self.sprite = SpriteObject(
                "interactive",
                spritesheet_path,
                self.rect.centerx,
                self.rect.centery
            )

        self.sprite.add_frames(
            name=name,
            indices=frames,
            cols=cols,
            rows=rows,
            frame_duration=speed,
            loop=loop,
            spritesheet_path=spritesheet_path,
            scale=scale
        )

    def play(
        self,
        name,
        reset=True
    ):

        if (
            self.sprite is None
            or name not in self.sprite.animations
        ):

            return False

        self.sprite.play(
            name,
            reset
        )

        self.current_anim = name

        return True

    def update_animation(
        self,
        dt
    ):

        if self.sprite is None:
            return

        self.sprite.update(dt)

        self.sprite.set_position(
            self.rect.centerx,
            self.rect.centery
        )

    def update(
        self,
        creature,
        ghost=None,
        dt=0,
        *args,
        **kwargs
    ):

        self.update_animation(dt)

    def handle_event(
        self,
        event
    ):

        pass

    def draw(
        self,
        surface
    ):

        if (
            self.sprite
            and self.sprite.current
        ):

            self.sprite.draw(surface)

        else:

            pygame.draw.rect(
                surface,
                self.color,
                self.rect
            )


# =========================================================
# LEVER
# =========================================================

class Lever(Interactive):

    def __init__(
        self,
        x,
        y,
        w=100,
        h=20,
        direction="left"
    ):

        super().__init__(
            x,
            y,
            w,
            h
        )

        self.enabled = False

        self.direction = (
            direction.lower()
        )

        self.enter_side = None

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        creature,
        ghost=None,
        dt=0,
        *args,
        **kwargs
    ):

        if ghost is None:
            return

        if not hasattr(
            ghost,
            "last_pos"
        ):

            return

        # =================================================
        # POPRZEDNI HITBOX DUCHA
        # =================================================

        old_rect = ghost.rect.copy()

        old_rect.center = (
            int(ghost.last_pos.x),
            int(ghost.last_pos.y)
        )

        # Aktualny hitbox
        new_rect = ghost.rect.copy()

        # =================================================
        # LEWO / PRAWO
        # =================================================

        if self.direction in (
            "left",
            "right"
        ):

            vertical_overlap = (
                old_rect.bottom > self.rect.top
                and old_rect.top < self.rect.bottom
            ) or (
                new_rect.bottom > self.rect.top
                and new_rect.top < self.rect.bottom
            )

            if not vertical_overlap:

                self.enter_side = None

                return

            # Duch wszedł z lewej
            if (
                old_rect.right <= self.rect.left
                and new_rect.right > self.rect.left
            ):

                self.enter_side = "left"

            # Duch wszedł z prawej
            elif (
                old_rect.left >= self.rect.right
                and new_rect.left < self.rect.right
            ):

                self.enter_side = "right"

            # Wszedł z lewej i wyszedł prawą
            if (
                self.enter_side == "left"
                and new_rect.left >= self.rect.right
            ):

                self.enabled = (
                    self.direction == "right"
                )

                self.enter_side = None

            # Wszedł z prawej i wyszedł lewą
            elif (
                self.enter_side == "right"
                and new_rect.right <= self.rect.left
            ):

                self.enabled = (
                    self.direction == "left"
                )

                self.enter_side = None

        # =================================================
        # GÓRA / DÓŁ
        # =================================================

        elif self.direction in (
            "top",
            "bottom"
        ):

            horizontal_overlap = (
                old_rect.right > self.rect.left
                and old_rect.left < self.rect.right
            ) or (
                new_rect.right > self.rect.left
                and new_rect.left < self.rect.right
            )

            if not horizontal_overlap:

                self.enter_side = None

                return

            # Duch wszedł od góry
            if (
                old_rect.bottom <= self.rect.top
                and new_rect.bottom > self.rect.top
            ):

                self.enter_side = "top"

            # Duch wszedł od dołu
            elif (
                old_rect.top >= self.rect.bottom
                and new_rect.top < self.rect.bottom
            ):

                self.enter_side = "bottom"

            # Góra -> dół
            if (
                self.enter_side == "top"
                and new_rect.top >= self.rect.bottom
            ):

                self.enabled = (
                    self.direction == "bottom"
                )

                self.enter_side = None

            # Dół -> góra
            elif (
                self.enter_side == "bottom"
                and new_rect.bottom <= self.rect.top
            ):

                self.enabled = (
                    self.direction == "top"
                )

                self.enter_side = None

    def draw(
        self,
        surface
    ):

        self.color = (
            (46, 204, 113)
            if self.enabled
            else
            (231, 76, 60)
        )

        super().draw(surface)


# =========================================================
# CODE PANEL
# =========================================================

class CodePanel(Interactive):

    def __init__(
        self,
        x,
        y,
        code="1234"
    ):

        super().__init__(
            x,
            y,
            60,
            60
        )

        self.code = str(code)

        self.current = ""

        self.is_unlocked = False
        self.is_open = False

        self.player_near = False

        self.color = (
            70,
            130,
            180
        )

    def update(
        self,
        creature,
        ghost=None,
        dt=0,
        *args,
        **kwargs
    ):

        self.player_near = (
            creature.rect.colliderect(
                self.rect
            )
        )

        if (
            not self.player_near
            and self.is_open
        ):

            self.is_open = False
            self.current = ""

    def handle_event(
        self,
        event
    ):

        if event.type != pygame.KEYDOWN:
            return

        # Otwieranie panelu
        if (
            event.key == pygame.K_q
            and self.player_near
        ):

            self.is_open = (
                not self.is_open
            )

            self.current = ""

            return

        # Escape zamyka panel
        if (
            event.key == pygame.K_ESCAPE
            and self.is_open
        ):

            self.is_open = False
            self.current = ""

            return

        if not self.is_open:
            return

        # Cyfry
        if event.unicode.isdigit():

            self.current += (
                event.unicode
            )

        # Backspace
        elif event.key == pygame.K_BACKSPACE:

            self.current = (
                self.current[:-1]
            )

        # Za długi kod
        if len(self.current) > len(
            self.code
        ):

            self.current = ""

        # Poprawny kod
        if self.current == self.code:

            self.is_unlocked = True

            self.is_open = False

            self.current = ""

    def draw(
        self,
        surface
    ):

        super().draw(surface)

        # Podpowiedź
        if (
            self.player_near
            and not self.is_open
        ):

            font = pygame.font.Font(
                None,
                24
            )

            hint = font.render(
                "[Q] Code",
                True,
                (255, 255, 255)
            )

            surface.blit(
                hint,
                (
                    self.rect.x - 10,
                    self.rect.y - 25
                )
            )

        # Panel kodu
        if self.is_open:

            popup_rect = pygame.Rect(
                self.rect.x - 30,
                self.rect.y - 70,
                120,
                50
            )

            pygame.draw.rect(
                surface,
                (40, 40, 40),
                popup_rect
            )

            font = pygame.font.Font(
                None,
                32
            )

            display_text = (
                self.current
                + "_"
                * (
                    len(self.code)
                    - len(self.current)
                )
            )

            text_surf = font.render(
                display_text,
                True,
                (0, 255, 0)
            )

            text_rect = (
                text_surf.get_rect(
                    center=popup_rect.center
                )
            )

            surface.blit(
                text_surf,
                text_rect
            )


# =========================================================
# SCORING BUTTON
# =========================================================

class ScoringButton(Interactive):

    def __init__(
        self,
        x,
        y,
        required_power=1
    ):

        super().__init__(
            x,
            y,
            80,
            20
        )

        self.required_power = (
            required_power
        )

        self.points = 100

        self.used = False

        self.color = (
            241,
            196,
            15
        )

    def update(
        self,
        creature,
        ghost=None,
        dt=0,
        *args,
        **kwargs
    ):

        if not creature.rect.colliderect(
            self.rect
        ):

            return

        current_power = getattr(
            creature,
            "power",
            0
        )

        if (
            not self.used
            and current_power
            >= self.required_power
        ):

            if hasattr(
                creature,
                "score"
            ):

                creature.score += (
                    self.points
                )

            self.used = True

            self.color = (
                127,
                140,
                141
            )


# =========================================================
# DOOR
# =========================================================

class Door(Interactive):

    def __init__(
        self,
        x,
        y,
        w=30,
        h=120,
        trigger_object=None
    ):

        super().__init__(
            x,
            y,
            w,
            h
        )

        self.is_open = False

        self.trigger_object = (
            trigger_object
        )

        self.color = (
            139,
            69,
            19
        )

    def update(
        self,
        creature,
        ghost=None,
        dt=0,
        *args,
        **kwargs
    ):

        # Sprawdzenie triggera
        if self.trigger_object:

            if hasattr(
                self.trigger_object,
                "enabled"
            ):

                self.is_open = (
                    self.trigger_object.enabled
                )

            elif hasattr(
                self.trigger_object,
                "is_unlocked"
            ):

                self.is_open = (
                    self.trigger_object.is_unlocked
                )

        # NIE przesuwamy tutaj gracza.
        #
        # Zamknięte drzwi są dodawane przez main.py
        # do listy obstacles.
        #
        # Dzięki temu Creature ma jeden system kolizji.

    def draw(
        self,
        surface
    ):

        if not self.is_open:

            super().draw(surface)


# =========================================================
# LEVEL GATE
# =========================================================

class LevelGate(Interactive):

    def __init__(
        self,
        x,
        y
    ):

        super().__init__(
            x,
            y,
            100,
            120
        )

        self.triggered = False

        self.color = (
            142,
            68,
            173
        )

    def update(
        self,
        creature,
        ghost=None,
        dt=0,
        *args,
        **kwargs
    ):

        if self.triggered:
            return

        if ghost is None:
            return

        creature_rect = getattr(
            creature,
            "rect",
            None
        )

        ghost_rect = getattr(
            ghost,
            "rect",
            None
        )

        if (
            creature_rect
            and ghost_rect
        ):

            creature_inside = (
                creature_rect.colliderect(
                    self.rect
                )
            )

            ghost_inside = (
                ghost_rect.colliderect(
                    self.rect
                )
            )

            if (
                creature_inside
                and ghost_inside
            ):

                print(
                    "NEXT LEVEL"
                )

                self.triggered = True


# =========================================================
# SAFE ZONE
# =========================================================

class SafeZone(Interactive):

    def __init__(
        self,
        x,
        y,
        w=150,
        h=150
    ):

        super().__init__(
            x,
            y,
            w,
            h
        )

        self.color = (
            46,
            204,
            113,
            100
        )

        self.is_ghost_inside = False
        self.is_creature_inside = False

    def update(
        self,
        creature,
        ghost=None,
        dt=0,
        *args,
        **kwargs
    ):

        self.is_creature_inside = (
            self.rect.colliderect(
                creature.rect
            )
        )

        if ghost is not None:

            self.is_ghost_inside = (
                self.rect.colliderect(
                    ghost.rect
                )
            )

    def draw(
        self,
        surface
    ):

        surface_alpha = pygame.Surface(
            (
                self.rect.width,
                self.rect.height
            ),
            pygame.SRCALPHA
        )

        surface_alpha.fill(
            (
                46,
                204,
                113,
                80
            )
        )

        surface.blit(
            surface_alpha,
            (
                self.rect.x,
                self.rect.y
            )
        )

        pygame.draw.rect(
            surface,
            (46, 204, 113),
            self.rect,
            2
        )


# =========================================================
# INTERACTIVE MANAGER
# =========================================================

class InteractiveManager:

    def __init__(self):

        self.objects = []

    def add(
        self,
        obj
    ):

        if obj not in self.objects:

            self.objects.append(obj)

    def remove(
        self,
        obj
    ):

        if obj in self.objects:

            self.objects.remove(obj)

    def clear(self):

        self.objects.clear()

    # =====================================================
    # DUNDER
    # =====================================================

    def __len__(self):

        return len(
            self.objects
        )

    def __iter__(self):

        return iter(
            self.objects
        )

    def __getitem__(
        self,
        index
    ):

        return self.objects[index]

    def __contains__(
        self,
        obj
    ):

        return obj in self.objects

    def __repr__(self):

        return (
            f"<InteractiveManager "
            f"({len(self.objects)} objects)>"
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        player,
        ghost=None,
        dt=0
    ):

        for obj in self.objects:

            obj.update(
                player,
                ghost=ghost,
                dt=dt
            )

    def update_all(
        self,
        player,
        ghost=None,
        dt=0
    ):

        self.update(
            player,
            ghost=ghost,
            dt=dt
        )

    # =====================================================
    # EVENTS
    # =====================================================

    def handle_event(
        self,
        event
    ):

        for obj in self.objects:

            obj.handle_event(event)

    def handle_event_all(
        self,
        event
    ):

        self.handle_event(event)

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        surface
    ):

        for obj in self.objects:

            obj.draw(surface)

    def draw_all(
        self,
        surface
    ):

        self.draw(surface)