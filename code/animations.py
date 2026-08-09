import pygame
from dataclasses import dataclass


# =========================================================
# FRAME
# =========================================================

@dataclass
class Frame:

    rect: pygame.Rect
    duration: int  # milliseconds


# =========================================================
# SPRITESHEET
# =========================================================

class Spritesheet:

    def __init__(self, filepath):

        self.filepath = filepath

        self.image = pygame.image.load(
            filepath
        ).convert_alpha()

        self.rect = self.image.get_rect()

    # =====================================================
    # GET FRAME
    # =====================================================

    def get_frame(self, rect):

        surface = pygame.Surface(
            (
                rect.width,
                rect.height
            ),
            pygame.SRCALPHA
        )

        surface.blit(
            self.image,
            (0, 0),
            rect
        )

        return surface

    # =====================================================
    # CREATE GRID
    # =====================================================

    def create_grid_frames(
        self,
        cols,
        rows,
        total_frames=None,
        duration=100,
        start_x=0,
        start_y=0,
        x_spacing=0,
        y_spacing=0
    ):

        frames = []

        if cols <= 0 or rows <= 0:
            return frames

        usable_w = (
            self.rect.width
            - start_x
        )

        usable_h = (
            self.rect.height
            - start_y
        )

        frame_w = (
            usable_w // cols
        )

        frame_h = (
            usable_h // rows
        )

        max_frames = (
            cols * rows
        )

        if total_frames is None:

            take = max_frames

        else:

            take = min(
                total_frames,
                max_frames
            )

        count = 0

        for row in range(rows):

            for col in range(cols):

                if count >= take:
                    break

                x = (
                    start_x
                    + col * (
                        frame_w
                        + x_spacing
                    )
                )

                y = (
                    start_y
                    + row * (
                        frame_h
                        + y_spacing
                    )
                )

                frames.append(
                    Frame(
                        pygame.Rect(
                            x,
                            y,
                            frame_w,
                            frame_h
                        ),
                        duration
                    )
                )

                count += 1

            if count >= take:
                break

        return frames


# =========================================================
# ANIMATION
# =========================================================

class Animation:

    def __init__(
        self,
        spritesheet,
        frames,
        loop=True,
        scale=1.0,
        x_offset=0,
        y_offset=0
    ):

        self.spritesheet = spritesheet
        self.frames = frames

        self.loop = loop
        self.scale = scale

        self.x_offset = x_offset
        self.y_offset = y_offset

        self.current = 0
        self.elapsed = 0.0

        self._finished = False

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        if not self.frames:
            return None

        # -------------------------------------------------
        # ANIMACJA JUŻ SKOŃCZONA
        #
        # NIE WRACAMY DO POCZĄTKU.
        # ZOSTAJEMY NA OSTATNIEJ KLATCE.
        # -------------------------------------------------

        if self._finished:

            return self.spritesheet.get_frame(
                self.frames[-1].rect
            )

        # dt = sekundy
        #
        # duration = milisekundy

        self.elapsed += (
            dt * 1000.0
        )

        # -------------------------------------------------
        # PRZECHODZENIE PRZEZ KLATKI
        # -------------------------------------------------

        while (
            self.elapsed
            >= self.frames[
                self.current
            ].duration
        ):

            self.elapsed -= (
                self.frames[
                    self.current
                ].duration
            )

            self.current += 1

            # -------------------------------------------------
            # KONIEC
            # -------------------------------------------------

            if (
                self.current
                >= len(self.frames)
            ):

                # -------------------------------------------------
                # LOOP
                # -------------------------------------------------

                if self.loop:

                    self.current = 0

                # -------------------------------------------------
                # NON-LOOP
                # -------------------------------------------------

                else:

                    self.current = (
                        len(self.frames) - 1
                    )

                    self._finished = True

                    break

        return self.spritesheet.get_frame(
            self.frames[
                self.current
            ].rect
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.current = 0
        self.elapsed = 0.0
        self._finished = False

    # =====================================================
    # FINISHED
    # =====================================================

    def is_finished(self):

        return self._finished

    # =====================================================
    # CURRENT FRAME
    # =====================================================

    def get_current_frame(self):

        if not self.frames:
            return None

        return self.frames[
            self.current
        ]


# =========================================================
# SPRITE OBJECT
# =========================================================

class SpriteObject:

    def __init__(
        self,
        name,
        spritesheet_path,
        x=0,
        y=0
    ):

        self.name = name

        self.spritesheet = Spritesheet(
            spritesheet_path
        )

        self.animations = {}

        self.current = None

        self.position = (
            x,
            y
        )

    # =====================================================
    # ADD ANIMATION
    # =====================================================

    def add_animation(
        self,
        name,
        cols,
        rows,
        frame_indices,
        frame_duration=100,
        loop=True,
        start_x=0,
        start_y=0,
        x_spacing=0,
        y_spacing=0,
        total_frames=None,
        spritesheet_path=None,
        scale=1.0,
        x_offset=0,
        y_offset=0
    ):

        if not frame_indices:

            raise ValueError(
                "frame_indices must not be empty"
            )

        if spritesheet_path:

            animation_spritesheet = (
                Spritesheet(
                    spritesheet_path
                )
            )

        else:

            animation_spritesheet = (
                self.spritesheet
            )

<<<<<<< HEAD
        full_frames = (
            animation_spritesheet
            .create_grid_frames(
                cols=cols,
                rows=rows,
                total_frames=total_frames,
                duration=frame_duration,
                start_x=start_x,
                start_y=start_y,
                x_spacing=x_spacing,
                y_spacing=y_spacing
            )
=======
        # ==========================================
        # CREATE FRAME GRID
        # ==========================================

        # Jeśli total_frames nie jest ustawiony, oblicz go na podstawie max indeksu
        if total_frames is None:
            total_frames = max(frame_indices) + 1

        full_frames = animation_spritesheet.create_grid_frames(
            cols=cols,
            rows=rows,
            total_frames=total_frames,
            duration=frame_duration,
            start_x=start_x,
            start_y=start_y,
            x_spacing=x_spacing,
            y_spacing=y_spacing
>>>>>>> master
        )

        filtered = []

        for index in frame_indices:

            if (
                0 <= index
                < len(full_frames)
            ):

                frame = full_frames[
                    index
                ]

                filtered.append(
                    Frame(
                        frame.rect.copy(),
                        frame_duration
                    )
                )

            else:

                raise IndexError(
                    f"Frame index {index} "
                    f"out of range "
                    f"(0..{len(full_frames)-1})"
                )

        self.animations[name] = Animation(
            spritesheet=animation_spritesheet,
            frames=filtered,
            loop=loop,
            scale=scale,
            x_offset=x_offset,
            y_offset=y_offset
        )

    # =====================================================
    # ADD FRAMES
    # =====================================================

    def add_frames(
        self,
        name,
        indices,
        cols,
        rows,
        frame_duration=100,
        loop=True,
        start_x=0,
        start_y=0,
        x_spacing=0,
        y_spacing=0,
        total_frames=None,
        spritesheet_path=None,
        scale=1.0,
        x_offset=0,
        y_offset=0
    ):

        self.add_animation(
            name=name,
            cols=cols,
            rows=rows,
            frame_indices=indices,
            frame_duration=frame_duration,
            loop=loop,
            start_x=start_x,
            start_y=start_y,
            x_spacing=x_spacing,
            y_spacing=y_spacing,
            total_frames=total_frames,
            spritesheet_path=spritesheet_path,
            scale=scale,
            x_offset=x_offset,
            y_offset=y_offset
        )

    # =====================================================
    # PLAY
    # =====================================================

    def play(
        self,
        name,
        reset=True
    ):

        if name not in self.animations:
            return False

        # -------------------------------------------------
        # ZMIANA ANIMACJI
        # -------------------------------------------------

        if self.current != name:

            self.current = name

            self.animations[
                name
            ].reset()

            return True

        # -------------------------------------------------
        # TA SAMA ANIMACJA
        #
        # reset=False = NIE RESTARTUJ
        # -------------------------------------------------

        if reset:

            self.animations[
                name
            ].reset()

        return True

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        if (
            self.current
            and self.current
            in self.animations
        ):

            return self.animations[
                self.current
            ].update(dt)

        return None

    # =====================================================
    # DRAW
    # =====================================================

    def draw(self, surface):

        if not self.current:
            return

        if (
            self.current
            not in self.animations
        ):
            return

        animation = self.animations[
            self.current
        ]

        if not animation.frames:
            return

        frame = animation.frames[
            animation.current
        ]

        image = (
            animation.spritesheet
            .get_frame(
                frame.rect
            )
        )

        # -------------------------------------------------
        # SCALE
        # -------------------------------------------------

        if animation.scale != 1.0:

            width = max(
                1,
                int(
                    image.get_width()
                    * animation.scale
                )
            )

            height = max(
                1,
                int(
                    image.get_height()
                    * animation.scale
                )
            )

            image = pygame.transform.scale(
                image,
                (
                    width,
                    height
                )
            )

        # -------------------------------------------------
        # POSITION
        # -------------------------------------------------

        image_rect = image.get_rect(
            center=(
                int(
                    self.position[0]
                    + animation.x_offset
                ),
                int(
                    self.position[1]
                    + animation.y_offset
                )
            )
        )

        surface.blit(
            image,
            image_rect
        )

    # =====================================================
    # POSITION
    # =====================================================

    def set_position(
        self,
        x,
        y
    ):

        self.position = (
            x,
            y
        )

    def move(
        self,
        dx,
        dy
    ):

        self.position = (
            self.position[0] + dx,
            self.position[1] + dy
        )

    # =====================================================
    # FINISHED
    # =====================================================

    def is_finished(self):

        if (
            self.current
            and self.current
            in self.animations
        ):

            return self.animations[
                self.current
            ].is_finished()

        return False
