import pygame
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

@dataclass
class Frame:
    rect: pygame.Rect
    duration: int  # ms

class Spritesheet:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.image = pygame.image.load(filepath).convert_alpha()
        self.rect = self.image.get_rect()

    def get_frame(self, rect: pygame.Rect) -> pygame.Surface:
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surf.blit(self.image, (0, 0), rect)
        return surf

    def create_grid_frames(self,
                           cols: int, rows: int,
                           total_frames: Optional[int] = None,
                           duration: int = 100,
                           start_x: int = 0, start_y: int = 0,
                           x_spacing: int = 0, y_spacing: int = 0) -> List[Frame]:
        frames: List[Frame] = []
        if cols <= 0 or rows <= 0:
            return frames
        usable_w = self.rect.width - start_x
        usable_h = self.rect.height - start_y
        frame_w = usable_w // cols
        frame_h = usable_h // rows
        max_frames = cols * rows
        take = max_frames if total_frames is None else min(total_frames, max_frames)
        count = 0
        for r in range(rows):
            for c in range(cols):
                if count >= take:
                    break
                x = start_x + c * (frame_w + x_spacing)
                y = start_y + r * (frame_h + y_spacing)
                frames.append(Frame(pygame.Rect(x, y, frame_w, frame_h), duration))
                count += 1
            if count >= take:
                break
        return frames

class Animation:
    def __init__(self, spritesheet: Spritesheet, frames: List[Frame], loop: bool = True):
        self.spritesheet = spritesheet
        self.frames = frames
        self.loop = loop
        self.current = 0
        self.elapsed = 0
        self._finished = False

    def update(self, dt: int) -> Optional[pygame.Surface]:
        if not self.frames:
            return None
        if self._finished:
            return self.spritesheet.get_frame(self.frames[-1].rect)
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
        return self.spritesheet.get_frame(self.frames[self.current].rect)

    def reset(self):
        self.current = 0
        self.elapsed = 0
        self._finished = False

    def is_finished(self) -> bool:
        return self._finished

    def add_frame(self, rect: pygame.Rect, duration: int = 100):
        self.frames.append(Frame(rect, duration))

    def insert_frame(self, idx: int, rect: pygame.Rect, duration: int = 100):
        self.frames.insert(idx, Frame(rect, duration))

    def remove_frame(self, idx: int):
        if 0 <= idx < len(self.frames):
            self.frames.pop(idx)
            if self.current >= len(self.frames):
                self.current = max(0, len(self.frames)-1)

class SpriteObject:
    """
    Must supply explicit frame indices when creating an animation.
    Convenience: add_frames(name, indices, cols, rows, frame_duration, loop, ...)
    Indices are row-major, zero-based (0 = first frame from sheet).
    """
    def __init__(self, name: str, spritesheet_path: str, x: int = 0, y: int = 0):
        self.name = name
        self.spritesheet = Spritesheet(spritesheet_path)
        self.animations: Dict[str, Animation] = {}
        self.current: Optional[str] = None
        self.position: Tuple[int, int] = (x, y)

    def add_animation(self, name: str,
                      cols: int, rows: int,
                      frame_indices: List[int],
                      frame_duration: int = 100,
                      loop: bool = True,
                      start_x: int = 0, start_y: int = 0,
                      x_spacing: int = 0, y_spacing: int = 0,
                      total_frames: Optional[int] = None):
        """
        Create an animation from explicit frame_indices.
        frame_indices: REQUIRED list of indices (row-major, zero-based).
        """
        if not frame_indices:
            raise ValueError("frame_indices is required and must be a non-empty list.")

        # build full grid frames so indices map correctly
        full_frames = self.spritesheet.create_grid_frames(
            cols=cols, rows=rows, total_frames=total_frames,
            duration=frame_duration, start_x=start_x, start_y=start_y,
            x_spacing=x_spacing, y_spacing=y_spacing
        )

        filtered: List[Frame] = []
        for i in frame_indices:
            if 0 <= i < len(full_frames):
                f = full_frames[i]
                filtered.append(Frame(f.rect, frame_duration))
            else:
                raise IndexError(f"Frame index {i} out of range (0..{len(full_frames)-1}).")

        self.animations[name] = Animation(self.spritesheet, filtered, loop)

    # alias with shorter name requested by you
    def add_frames(self, name: str,
                   indices: List[int],
                   cols: int, rows: int,
                   frame_duration: int = 100,
                   loop: bool = True,
                   start_x: int = 0, start_y: int = 0,
                   x_spacing: int = 0, y_spacing: int = 0,
                   total_frames: Optional[int] = None):
        self.add_animation(name=name, cols=cols, rows=rows,
                           frame_indices=indices,
                           frame_duration=frame_duration, loop=loop,
                           start_x=start_x, start_y=start_y,
                           x_spacing=x_spacing, y_spacing=y_spacing,
                           total_frames=total_frames)

    def add_frame_to_animation(self, anim_name: str, rect: pygame.Rect, duration: int = 100):
        if anim_name in self.animations:
            self.animations[anim_name].add_frame(rect, duration)

    def play(self, name: str, reset: bool = True):
        if name in self.animations:
            self.current = name
            if reset:
                self.animations[name].reset()

    def update(self, dt: int) -> Optional[pygame.Surface]:
        if self.current and self.current in self.animations:
            return self.animations[self.current].update(dt)
        return None

    def draw(self, surface):
        if self.current and self.current in self.animations:
            anim = self.animations[self.current]

            img = anim.spritesheet.get_frame(
                anim.frames[anim.current].rect
            )

            # TUTAJ REGULUJESZ PRZESUNIĘCIE GRAFIKI WGLĘDEM HITBOXU:
            # - Pierwsza liczba (X): zmniejsz (np. do -100 lub -120), aby przesunąć postać W LEWO.
            # - Druga liczba (Y): zmniejsz (np. do -160 lub -180), aby podnieść postać W GÓRĘ.

            offset_x = -105 # <--- dostosuj, aż zielona kropka będzie na klatce piersiowej
            offset_y = -135  # <--- dostosuj, aż stopy będą dokładnie na dole czerwonej ramki

            surface.blit(
                img,
                (self.position[0] + offset_x, self.position[1] + offset_y)
            )

    def set_position(self, x: int, y: int):
        self.position = (x, y)

    def move(self, dx: int, dy: int):
        self.position = (self.position[0] + dx, self.position[1] + dy)

    def is_finished(self) -> bool:
        if self.current and self.current in self.animations:
            return self.animations[self.current].is_finished()
        return False

class ObjectManager:
    def __init__(self):
        self.objects: Dict[str, SpriteObject] = {}

    def add(self, obj: SpriteObject):
        self.objects[obj.name] = obj

    def remove(self, name: str):
        if name in self.objects:
            del self.objects[name]

    def play(self, obj_name: str, anim_name: str, reset: bool = True):
        if obj_name in self.objects:
            self.objects[obj_name].play(anim_name, reset)

    def update_all(self, dt: int):
        for obj in self.objects.values():
            obj.update(dt)

    def draw_all(self, surface: pygame.Surface):
        for obj in self.objects.values():
            obj.draw(surface)

    def is_finished(self, obj_name: str) -> bool:
        if obj_name in self.objects:
            return self.objects[obj_name].is_finished()
        return False

# ---------------- Example ----------------
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    clock = pygame.time.Clock()

    mgr = ObjectManager()

    player = SpriteObject('player', 'ludzik.png', x=100, y=100)
    # MUST supply indices now (required)
    player.add_frames('walk', indices=[0,1,2,3,4,5], cols=3, rows=3, frame_duration=150, loop=True)
    player.add_frames('attack', indices=[6,7,8], cols=3, rows=3, frame_duration=300, loop=False)
    mgr.add(player)



    mgr.play('player', 'walk')


    running = True
    while running:
        dt = clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    mgr.play('player', 'walk')
                elif ev.key == pygame.K_2:
                    mgr.play('player', 'attack')
                elif ev.key == pygame.K_3:
                    pass
                    #mgr.play('enemy', 'attack')

        mgr.update_all(dt)
        screen.fill((30, 30, 30))
        mgr.draw_all(screen)

        if mgr.is_finished('player'):
            mgr.play('player', 'walk')
        pygame.display.flip()

    pygame.quit()