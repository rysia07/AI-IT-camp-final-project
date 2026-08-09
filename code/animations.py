import pygame
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple


# =========================================================
# FRAME
# =========================================================

@dataclass
class Frame:
    rect: pygame.Rect
    duration: int  # ms


# =========================================================
# SPRITESHEET
# =========================================================

class Spritesheet:

    def __init__(self, filepath: str):

        self.filepath = filepath

        self.image = pygame.image.load(
            filepath
        ).convert_alpha()

        self.rect = self.image.get_rect()

    def get_frame(self, rect: pygame.Rect) -> pygame.Surface:

        surf = pygame.Surface(
            (rect.width, rect.height),
            pygame.SRCALPHA
        )

        surf.blit(
            self.image,
            (0, 0),
            rect
        )

        return surf

    def create_grid_frames(
        self,
        cols: int,
        rows: int,
        total_frames: Optional[int] = None,
        duration: int = 100,
        start_x: int = 0,
        start_y: int = 0,
        x_spacing: int = 0,
        y_spacing: int = 0
    ) -> List[Frame]:

        frames: List[Frame] = []

        if cols <= 0 or rows <= 0:
            return frames

        usable_w = self.rect.width - start_x
        usable_h = self.rect.height - start_y

        frame_w = usable_w // cols
        frame_h = usable_h // rows

        max_frames = cols * rows

        take = (
            max_frames
            if total_frames is None
            else min(total_frames, max_frames)
        )

        count = 0

        for r in range(rows):

            for c in range(cols):

                if count >= take:
                    break

                x = start_x + c * (frame_w + x_spacing)
                y = start_y + r * (frame_h + y_spacing)

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
        spritesheet: Spritesheet,
        frames: List[Frame],
        loop: bool = True,
        scale: float = 1.0,
        x_offset: float = 0,
        y_offset: float = 0
    ):

        self.spritesheet = spritesheet
        self.frames = frames

        self.loop = loop
        self.scale = scale

        # ==========================================
        # SPRITE OFFSET
        # ==========================================

        self.x_offset = x_offset
        self.y_offset = y_offset

        # ==========================================
        # ANIMATION STATE
        # ==========================================

        self.current = 0
        self.elapsed = 0
        self._finished = False

    def update(self, dt: int) -> Optional[pygame.Surface]:

        if not self.frames:
            return None

        if self._finished:

            return self.spritesheet.get_frame(
                self.frames[-1].rect
            )

        self.elapsed += dt

        dur = self.frames[self.current].duration

        if self.elapsed >= dur:

            self.elapsed -= dur
            self.current += 1

            if self.current >= len(self.frames):

                if self.loop:

                    self.current = 0

                else:

                    self.current = len(self.frames) - 1
                    self._finished = True

        return self.spritesheet.get_frame(
            self.frames[self.current].rect
        )

    def reset(self):

        self.current = 0
        self.elapsed = 0
        self._finished = False

    def is_finished(self) -> bool:

        return self._finished

    def add_frame(
        self,
        rect: pygame.Rect,
        duration: int = 100
    ):

        self.frames.append(
            Frame(
                rect,
                duration
            )
        )

    def insert_frame(
        self,
        idx: int,
        rect: pygame.Rect,
        duration: int = 100
    ):

        self.frames.insert(
            idx,
            Frame(
                rect,
                duration
            )
        )

    def remove_frame(self, idx: int):

        if 0 <= idx < len(self.frames):

            self.frames.pop(idx)

            if self.current >= len(self.frames):

                self.current = max(
                    0,
                    len(self.frames) - 1
                )


# =========================================================
# SPRITE OBJECT
# =========================================================

class SpriteObject:

    def __init__(
        self,
        name: str,
        spritesheet_path: str,
        x: int = 0,
        y: int = 0
    ):

        self.name = name

        self.spritesheet = Spritesheet(
            spritesheet_path
        )

        self.animations: Dict[str, Animation] = {}

        self.current: Optional[str] = None

        self.position: Tuple[int, int] = (
            x,
            y
        )

    # =====================================================
    # ADD ANIMATION
    # =====================================================

    def add_animation(
        self,
        name: str,
        cols: int,
        rows: int,
        frame_indices: List[int],
        frame_duration: int = 100,
        loop: bool = True,
        start_x: int = 0,
        start_y: int = 0,
        x_spacing: int = 0,
        y_spacing: int = 0,
        total_frames: Optional[int] = None,
        spritesheet_path: Optional[str] = None,
        scale: float = 1.0,
        x_offset: float = 0,
        y_offset: float = 0
    ):

        if not frame_indices:

            raise ValueError(
                "frame_indices is required "
                "and must be a non-empty list."
            )

        # ==========================================
        # SPRITESHEET
        # ==========================================

        if spritesheet_path:

            animation_spritesheet = Spritesheet(
                spritesheet_path
            )

        else:

            animation_spritesheet = self.spritesheet

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
        )

        filtered: List[Frame] = []

        for i in frame_indices:

            if 0 <= i < len(full_frames):

                f = full_frames[i]

                filtered.append(
                    Frame(
                        f.rect,
                        frame_duration
                    )
                )

            else:

                raise IndexError(
                    f"Frame index {i} out of range "
                    f"(0..{len(full_frames) - 1})."
                )

        # ==========================================
        # CREATE ANIMATION
        # ==========================================

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
        name: str,
        indices: List[int],
        cols: int,
        rows: int,
        frame_duration: int = 100,
        loop: bool = True,
        start_x: int = 0,
        start_y: int = 0,
        x_spacing: int = 0,
        y_spacing: int = 0,
        total_frames: Optional[int] = None,
        spritesheet_path: Optional[str] = None,
        scale: float = 1.0,
        x_offset: float = 0,
        y_offset: float = 0
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
    # ADD SINGLE FRAME
    # =====================================================

    def add_frame_to_animation(
        self,
        anim_name: str,
        rect: pygame.Rect,
        duration: int = 100
    ):

        if anim_name in self.animations:

            self.animations[anim_name].add_frame(
                rect,
                duration
            )

    # =====================================================
    # PLAY
    # =====================================================

    def play(
        self,
        name: str,
        reset: bool = True
    ):

        if name in self.animations:

            self.current = name

            if reset:

                self.animations[name].reset()

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt: int
    ) -> Optional[pygame.Surface]:

        if (
            self.current
            and self.current in self.animations
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

        if self.current not in self.animations:
            return

        anim = self.animations[
            self.current
        ]

        if not anim.frames:
            return

        # ==========================================
        # GET FRAME
        # ==========================================

        img = anim.spritesheet.get_frame(
            anim.frames[anim.current].rect
        )

        # ==========================================
        # SCALE
        # ==========================================

        scale_factor = anim.scale

        new_width = int(
            img.get_width() * scale_factor
        )

        new_height = int(
            img.get_height() * scale_factor
        )

        img = pygame.transform.scale(
            img,
            (
                new_width,
                new_height
            )
        )

        # ==========================================
        # POSITION + OFFSET
        # ==========================================

        img_rect = img.get_rect(
            center=(
                self.position[0] + anim.x_offset,
                self.position[1] + anim.y_offset
            )
        )

        # ==========================================
        # DRAW
        # ==========================================

        surface.blit(
            img,
            img_rect
        )

    # =====================================================
    # POSITION
    # =====================================================

    def set_position(
        self,
        x: int,
        y: int
    ):

        self.position = (
            x,
            y
        )

    def move(
        self,
        dx: int,
        dy: int
    ):

        self.position = (
            self.position[0] + dx,
            self.position[1] + dy
        )

    # =====================================================
    # FINISHED
    # =====================================================

    def is_finished(self) -> bool:

        if (
            self.current
            and self.current in self.animations
        ):

            return self.animations[
                self.current
            ].is_finished()

        return False


# =========================================================
# OBJECT MANAGER
# =========================================================

class ObjectManager:

    def __init__(self):

        self.objects: Dict[
            str,
            SpriteObject
        ] = {}

    def add(
        self,
        obj: SpriteObject
    ):

        self.objects[obj.name] = obj

    def remove(
        self,
        name: str
    ):

        if name in self.objects:

            del self.objects[name]

    def play(
        self,
        obj_name: str,
        anim_name: str,
        reset: bool = True
    ):

        if obj_name in self.objects:

            self.objects[obj_name].play(
                anim_name,
                reset
            )

    def update_all(
        self,
        dt: int
    ):

        for obj in self.objects.values():

            obj.update(dt)

    def draw_all(
        self,
        surface: pygame.Surface
    ):

        for obj in self.objects.values():

            obj.draw(surface)

    def is_finished(
        self,
        obj_name: str
    ) -> bool:

        if obj_name in self.objects:

            return self.objects[
                obj_name
            ].is_finished()

        return False
