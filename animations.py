import pygame
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class Frame:
    rect: pygame.Rect  # Position in spritesheet
    duration: int  # milliseconds


class Spritesheet:
    def __init__(self, filepath: str):
        self.image = pygame.image.load(filepath).convert_alpha()
        self.rect = self.image.get_rect()

    def get_frame(self, rect: pygame.Rect) -> pygame.Surface:
        frame = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        frame.blit(self.image, (0, 0), rect)
        return frame

    def create_grid_frames(self, frame_width: int, frame_height: int,
                           duration: int = 100) -> List[Frame]:
        """Create frames from uniform grid layout"""
        frames = []
        for y in range(0, self.rect.height, frame_height):
            for x in range(0, self.rect.width, frame_width):
                frames.append(Frame(
                    pygame.Rect(x, y, frame_width, frame_height),
                    duration
                ))
        return frames


class Animation:
    def __init__(self, spritesheet: Spritesheet, frames: List[Frame],
                 loop: bool = True):
        self.spritesheet = spritesheet
        self.frames = frames
        self.loop = loop
        self.current_frame = 0
        self.elapsed_time = 0

    def update(self, dt: int) -> pygame.Surface:
        self.elapsed_time += dt

        if self.elapsed_time >= self.frames[self.current_frame].duration:
            self.elapsed_time = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1

        return self.spritesheet.get_frame(self.frames[self.current_frame].rect)

    def reset(self):
        self.current_frame = 0
        self.elapsed_time = 0


class AnimationManager:
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[str] = None

    def add_animation(self, name: str, animation: Animation):
        self.animations[name] = animation

    def play(self, name: str):
        if name in self.animations:
            self.current_animation = name
            self.animations[name].reset()

    def update(self, dt: int) -> pygame.Surface:
        if self.current_animation and self.current_animation in self.animations:
            return self.animations[self.current_animation].update(dt)
        return None



pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()


spritesheet = Spritesheet('test.png')  # Single file!

    # Create animations from grid (4x4 grid, 64x64 frames, 100ms each)
walk_frames = spritesheet.create_grid_frames(30, 40, 100)
animation = Animation(spritesheet, walk_frames)

    # Setup manager
manager = AnimationManager()
manager.add_animation('walk', animation)
manager.play('walk')

   # Game loop
running = True
while running:
    dt = clock.tick(60)
    manager.play('walk')
    image = manager.update(dt)

    if image:
        screen.blit(image, (100, 100))

    pygame.display.flip()