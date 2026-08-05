import pygame
from dataclasses import dataclass
from typing import List, Optional, Dict


# ==========================================
# 1. SYSTEM ANIMACJI (z animations.py)
# ==========================================

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

    def create_grid_frames(self, cols: int, rows: int, total_frames: Optional[int] = None,
                           duration: int = 100, start_x: int = 0, start_y: int = 0,
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

    def update(self, dt_ms: int) -> Optional[pygame.Surface]:
        if not self.frames:
            return None
        if self._finished:
            return self.spritesheet.get_frame(self.frames[-1].rect)
        self.elapsed += dt_ms
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


# ==========================================
# 2. BAZOWA KLASA POSTACI ZE SPRITEM
# ==========================================

class AnimatedCharacter:
    def __init__(self, x: float, y: float, spritesheet_path: Optional[str] = None):
        self.pos = pygame.Vector2(x, y)
        self.animations: Dict[str, Animation] = {}
        self.current_anim: Optional[str] = None
        self.spritesheet = Spritesheet(spritesheet_path) if spritesheet_path else None
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)

    def add_animation(self, name: str, cols: int, rows: int, frame_indices: List[int],
                      frame_duration: int = 100, loop: bool = True):
        if not self.spritesheet:
            return
        full_frames = self.spritesheet.create_grid_frames(cols=cols, rows=rows, duration=frame_duration)
        filtered = [full_frames[i] for i in frame_indices if 0 <= i < len(full_frames)]
        self.animations[name] = Animation(self.spritesheet, filtered, loop)

    def play(self, name: str, reset: bool = False):
        if name in self.animations and self.current_anim != name:
            self.current_anim = name
            if reset:
                self.animations[name].reset()

    def update_rect(self):
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface: pygame.Surface, dt_ms: int):
        if self.current_anim and self.current_anim in self.animations:
            img = self.animations[self.current_anim].update(dt_ms)
            if img:
                # Rysowanie wyśrodkowanego sprajtu
                img_rect = img.get_rect(center=self.rect.center)
                surface.blit(img, img_rect)
        else:
            # Rezerwowy rysunek (kółko) jeśli brak animacji
            pygame.draw.circle(surface, "red", (int(self.pos.x), int(self.pos.y)), 20)


# ==========================================
# 3. KLASY DLA GRACZA I DUCHA
# ==========================================

class Creature(AnimatedCharacter):
    def __init__(self, x: float, y: float, spritesheet_path: Optional[str] = None):
        super().__init__(x, y, spritesheet_path)

        # Statystyki gracza
        self.hp = 100
        self.power = 0

        # Parametry fizyki
        self.speed = 400
        self.jump_force = -1000
        self.gravity = 2000
        self.vel_y = 0
        self.is_grounded = False
        self.size = 40
        self.rect = pygame.Rect(x - self.size, y - self.size, self.size * 2, self.size * 2)

    def update(self, dt: float, platforms: list):
        keys = pygame.key.get_pressed()

        # 1. Skok
        if keys[pygame.K_w] and self.is_grounded:
            self.vel_y = self.jump_force
            self.is_grounded = False

        # 2. Grawitacja
        if not self.is_grounded:
            current_gravity = self.gravity * 3 if keys[pygame.K_s] else self.gravity
            self.vel_y += current_gravity * dt

        self.pos.y += self.vel_y * dt

        # 3. Ruch i sterowanie animacjami
        moving = False
        if keys[pygame.K_a]:
            self.pos.x -= self.speed * dt
            moving = True
        if keys[pygame.K_d]:
            self.pos.x += self.speed * dt
            moving = True

        # Przełączanie animacji na podstawie stanu gracza
        if moving:
            self.play('walk')
        else:
            self.play('idle')

        self.update_rect()

        # 4. Kolizje z platformami
        was_grounded_this_frame = False
        for platform in platforms:
            if self.rect.colliderect(platform) and self.vel_y >= 0:
                if (self.pos.y + self.size) - self.vel_y * dt <= platform.top + 10:
                    self.pos.y = platform.top - self.size
                    self.vel_y = 0
                    was_grounded_this_frame = True
                    self.update_rect()

        self.is_grounded = was_grounded_this_frame


class GhostMouse(AnimatedCharacter):
    def __init__(self, x=0, y=0):
        super().__init__(x, y)
        self.hp = 50

    def interact(self, objects):
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                print("Duch oddziałuje z obiektem")

    def update(self, dt=0):
        self.pos = pygame.Vector2(pygame.mouse.get_pos())
        self.update_rect()

    def draw(self, surface: pygame.Surface, dt_ms: int = 0):
        # Domyślne kółko dla ducha
        pygame.draw.circle(surface, "cyan", (int(self.pos.x), int(self.pos.y)), 20)