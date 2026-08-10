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

    # =====================================================
    # PLAY
    # =====================================================

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

    # =====================================================
    # UPDATE ANIMATION
    # =====================================================

    def update_animation(
        self,
        dt
    ):

        if self.sprite is None:
            return

        self.sprite.update(
            dt
        )

        self.sprite.set_position(
            self.rect.centerx,
            self.rect.centery
        )

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

        self.update_animation(
            dt
        )

    # =====================================================
    # EVENT
    # =====================================================

    def handle_event(
        self,
        event
    ):

        pass

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        surface
    ):

        if (
            self.sprite
            and self.sprite.current
        ):

            self.sprite.draw(
                surface
            )

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

        old_rect = ghost.rect.copy()

        old_rect.center = (
            int(ghost.last_pos.x),
            int(ghost.last_pos.y)
        )

        new_rect = ghost.rect.copy()

        # =================================================
        # LEFT / RIGHT
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

            if (
                old_rect.right <= self.rect.left
                and new_rect.right > self.rect.left
            ):

                self.enter_side = "left"

            elif (
                old_rect.left >= self.rect.right
                and new_rect.left < self.rect.right
            ):

                self.enter_side = "right"

            if (
                self.enter_side == "left"
                and new_rect.left >= self.rect.right
            ):

                self.enabled = (
                    self.direction == "right"
                )

                self.enter_side = None

            elif (
                self.enter_side == "right"
                and new_rect.right <= self.rect.left
            ):

                self.enabled = (
                    self.direction == "left"
                )

                self.enter_side = None

        # =================================================
        # TOP / BOTTOM
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

            if (
                old_rect.bottom <= self.rect.top
                and new_rect.bottom > self.rect.top
            ):

                self.enter_side = "top"

            elif (
                old_rect.top >= self.rect.bottom
                and new_rect.top < self.rect.bottom
            ):

                self.enter_side = "bottom"

            if (
                self.enter_side == "top"
                and new_rect.top >= self.rect.bottom
            ):

                self.enabled = (
                    self.direction == "bottom"
                )

                self.enter_side = None

            elif (
                self.enter_side == "bottom"
                and new_rect.bottom <= self.rect.top
            ):

                self.enabled = (
                    self.direction == "top"
                )

                self.enter_side = None

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        surface
    ):

        self.color = (
            (46, 204, 113)
            if self.enabled
            else (231, 76, 60)
        )

        super().draw(
            surface
        )


# =========================================================
# CODE PANEL / PLAYER BUTTON
# =========================================================

class CodePanel(Interactive):

    """
    Stary typ 'CodePanel' zostaje zachowany, aby stare
    pliki leveli nadal działały.

    NOWE DZIAŁANIE:

        codepanel 100 100 1234 nazwa

    Gracz podchodzi do przycisku i naciska E.

    Parametr '1234' jest ignorowany jako kod.
    Zostaje tylko dla kompatybilności ze starą składnią leveli.
    """

    def __init__(
        self,
        x,
        y,
        code="1234",
        name=None,
        width=50,
        height=50
    ):

        super().__init__(
            x,
            y,
            width,
            height
        )

        # Zachowujemy parametr code,
        # żeby nie psuć starego API.

        self.code = str(code)

        self.name = name

        # Stan przycisku

        self.triggered = False
        self.is_unlocked = False

        # Odległość, z której gracz może nacisnąć E

        self.interaction_distance = 80

        # Kolory

        self.color = (
            231,
            76,
            60
        )

        self.pressed_color = (
            46,
            204,
            113
        )

    # =====================================================
    # PRESS
    # =====================================================

    def press(self):

        if self.triggered:
            return

        self.triggered = False
        self.is_unlocked = True

        print(
            "🔘 CodePanel: przycisk aktywowany!"
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        player,
        ghost=None,
        dt=0,
        *args,
        **kwargs
    ):

        if self.triggered:
            return

        if player is None:
            return

        player_rect = getattr(
            player,
            "rect",
            None
        )

        if player_rect is None:
            return

        player_center = pygame.Vector2(
            player_rect.center
        )

        button_center = pygame.Vector2(
            self.rect.center
        )

        distance = (
            player_center
            - button_center
        ).length()

        if (
            distance <= self.interaction_distance
            and pygame.key.get_pressed()[pygame.K_e]
        ):

            self.press()

    # =====================================================
    # EVENT
    # =====================================================

    def handle_event(
        self,
        event
    ):

        # Przycisk jest aktywowany w update()
        # przez klawisz E.
        #
        # Nic nie trzeba tutaj robić.

        pass

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        surface
    ):

        if self.triggered:

            color = self.pressed_color

        else:

            color = self.color

        pygame.draw.rect(
            surface,
            color,
            self.rect
        )

        pygame.draw.rect(
            surface,
            "black",
            self.rect,
            2
        )

        # -------------------------------------------------
        # INFORMACJA DLA GRACZA
        # -------------------------------------------------

        if not self.triggered:

            font = pygame.font.Font(
                None,
                20
            )

            info = font.render(
                "E - przycisk",
                True,
                "white"
            )

            info_rect = info.get_rect(
                centerx=self.rect.centerx,
                bottom=self.rect.top - 5
            )

            surface.blit(
                info,
                info_rect
            )

        else:

            font = pygame.font.Font(
                None,
                18
            )

            info = font.render(
                "AKTYWNY",
                True,
                "white"
            )

            info_rect = info.get_rect(
                center=self.rect.center
            )

            surface.blit(
                info,
                info_rect
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
            and current_power >= self.required_power
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
        self.previous_open = False

        self.trigger_object = (
            trigger_object
        )

        self.color = (
            139,
            69,
            19
        )

        self.closed_animation = "closed"
        self.open_animation = "open"

    # =====================================================
    # SET DOOR ANIMATIONS
    # =====================================================

    def set_door_animations(
        self,
        closed="closed",
        opened="open"
    ):

        self.closed_animation = closed
        self.open_animation = opened

        if self.is_open:

            self.play(
                self.open_animation
            )

        else:

            self.play(
                self.closed_animation
            )

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

        new_open_state = False

        # =================================================
        # SPRAWDZENIE TRIGGERA
        # =================================================

        if self.trigger_object:

            if hasattr(
                    self.trigger_object,
                    "enabled"
            ):

                new_open_state = (
                    self.trigger_object.enabled
                )

            elif hasattr(
                    self.trigger_object,
                    "is_unlocked"
            ):

                new_open_state = (
                    self.trigger_object.is_unlocked
                )

            elif hasattr(
                    self.trigger_object,
                    "triggered"
            ):

                new_open_state = (
                    self.trigger_object.triggered
                )

        # =================================================
        # ZMIANA STANU DRZWI
        # =================================================

        if new_open_state != self.is_open:

            self.is_open = new_open_state

            if self.is_open:

                if (
                        self.sprite
                        and self.open_animation in self.sprite.animations
                ):
                    self.play(
                        self.open_animation,
                        reset=True
                    )

            else:

                if (
                        self.sprite
                        and self.closed_animation in self.sprite.animations
                ):
                    self.play(
                        self.closed_animation,
                        reset=True
                    )

        # =================================================
        # ANIMACJA
        # =================================================

        self.update_animation(dt)

        self.previous_open = self.is_open

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        surface
    ):

        if (
            self.sprite
            and self.sprite.current
        ):

            self.sprite.draw(
                surface
            )

            return

        if not self.is_open:

            pygame.draw.rect(
                surface,
                self.color,
                self.rect
            )

            pygame.draw.rect(
                surface,
                "black",
                self.rect,
                2
            )


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
            self.triggered = False

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

            self.objects.append(
                obj
            )

    def remove(
        self,
        obj
    ):

        if obj in self.objects:

            self.objects.remove(
                obj
            )

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

            obj.handle_event(
                event
            )

    def handle_event_all(
        self,
        event
    ):

        self.handle_event(
            event
        )

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        surface
    ):

        for obj in self.objects:

            obj.draw(
                surface
            )

    def draw_all(
        self,
        surface
    ):

        self.draw(
            surface
        )
