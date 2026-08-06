import pygame
from typing import Optional, List, Dict
from animations import SpriteObject


class Character:
    """
    Character class with animation hierarchy support.

    Priority levels (higher = can't be interrupted):
    - PRIORITY_IDLE = 1
    - PRIORITY_WALK = 1
    - PRIORITY_ATTACK = 3
    """

    PRIORITY_IDLE = 1
    PRIORITY_WALK = 1
    PRIORITY_ATTACK = 3

    def __init__(self, x: float, y: float, size: float,
                 image: Optional[pygame.Surface] = None,
                 spritesheet_path: Optional[str] = None):
        """Initialize character."""
        self.pos = pygame.Vector2(x, y)
        self.last_pos = pygame.Vector2(x, y)
        self.size = size
        self.image = image
        self.rect = pygame.Rect(x, y, size * 2, size * 4)

        self.sprite = None
        if spritesheet_path:
            self.sprite = SpriteObject('char', spritesheet_path, int(x), int(y))

        self.current_anim: Optional[str] = None
        self.current_priority = 0
        self.is_paused = False
        self.walk_anim: Optional[str] = None
        self.idle_anim: Optional[str] = None
        self.movement_threshold = 0.5
        self.anim_priority: Dict[str, int] = {}

    def add_anim(self, name: str, frames: List[int], cols: int, rows: int,
                 speed: int = 100, loop: bool = True,
                 priority: int = 0) -> None:
        """Add animation to character."""
        if not self.sprite:
            raise ValueError("Character needs spritesheet_path to use animations")
        self.sprite.add_frames(name, frames, cols, rows, speed, loop)
        self.anim_priority[name] = priority

    def set_walk_idle(self, walk_anim: str, idle_anim: str) -> None:
        """Enable auto-switching between walk/idle based on movement."""
        self.walk_anim = walk_anim
        self.idle_anim = idle_anim

    def play(self, anim_name: str, reset: bool = True) -> bool:
        """Play animation respecting priority hierarchy."""
        if not self.sprite or anim_name not in self.sprite.animations:
            return False

        new_priority = self.anim_priority.get(anim_name, 0)

        # Block if current animation has higher priority
        if self.current_anim and self.current_priority > new_priority:
            return False

        self.sprite.play(anim_name, reset)
        self.current_anim = anim_name
        self.current_priority = new_priority
        return True

    def pause(self) -> None:
        """Pause current animation."""
        self.is_paused = True

    def resume(self) -> None:
        """Resume paused animation."""
        self.is_paused = False

    def stop(self) -> None:
        """Stop all animations."""
        if self.sprite:
            self.sprite.current = None
        self.current_anim = None
        self.current_priority = 0
        self.is_paused = False

    def is_playing(self, anim_name: Optional[str] = None) -> bool:
        """Check if animation is playing."""
        if not self.sprite or not self.sprite.current or self.is_paused:
            return False
        if anim_name:
            return self.sprite.current == anim_name
        return True

    def is_done(self) -> bool:
        """Check if current animation finished."""
        if not self.sprite:
            return False
        return self.sprite.is_finished()

    def move(self, dx: float, dy: float) -> None:
        """Move character by offset."""
        self.pos.x += dx
        self.pos.y += dy

    def set_position(self, x: float, y: float) -> None:
        """Set character position."""
        self.pos.x = x
        self.pos.y = y

    def update_rect(self) -> None:
        """Update collision rect to match position."""
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def _clear_priority_if_done(self) -> None:
        """Reset priority once high-priority animation finishes."""
        if self.current_anim and self.is_done():
            self.current_priority = self.anim_priority.get(
                self.idle_anim or self.walk_anim, 1
            )

    def _check_movement(self) -> None:
        """Auto-switch between walk/idle based on movement."""
        if not self.walk_anim or not self.idle_anim:
            return

        if self.current_priority > self.anim_priority.get(self.walk_anim, 1):
            return

        moved = self.pos.distance_to(self.last_pos)

        if moved > self.movement_threshold:
            if self.current_anim != self.walk_anim:
                self.play(self.walk_anim)
        else:
            if self.current_anim != self.idle_anim:
                self.play(self.idle_anim)

        self.last_pos = self.pos.copy()

    def update(self, dt: int) -> None:
        """Update character logic and animations (call every frame)."""
        self.update_rect()

        if self.sprite and not self.is_paused:
            self.sprite.update(dt)
            self.sprite.set_position(int(self.pos.x - self.size),
                                     int(self.pos.y - self.size))

        self._clear_priority_if_done()
        self._check_movement()

    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Get current animation frame for rendering."""
        if self.sprite and self.sprite.current:
            return self.sprite.spritesheet.get_frame(
                self.sprite.animations[self.sprite.current].frames[
                    self.sprite.animations[self.sprite.current].current
                ].rect
            )
        return None


class Creature(Character):
    """Character with physics (gravity, jumping, platforms)."""

    def __init__(self, x: float, y: float, speed: float = 2000, jump_force: float = -1000,
                 spritesheet_path: Optional[str] = None):
        """Initialize creature with physics."""
        super().__init__(x, y, 40, spritesheet_path=spritesheet_path)

        # Physics
        self.speed = speed
        self.jump_force = jump_force
        self.gravity = 2000
        self.vel_y = 0
        self.is_grounded = False
        self.velocity = pygame.Vector2(0, 0)

    def move(self, dx: float, dy: float = 0) -> None:
        """Move creature (input from main.py)."""
        self.velocity.x = dx

    def jump(self) -> None:
        """Jump (input from main.py)."""
        if self.is_grounded:
            self.vel_y = self.jump_force
            self.is_grounded = False

    def apply_gravity(self, dt: float, fast_fall: bool = False) -> None:
        """Apply gravity (called from main.py)."""
        if not self.is_grounded:
            current_gravity = self.gravity * 3 if fast_fall else self.gravity
            self.vel_y += current_gravity * dt

    def update(self, dt: float, platforms: List[pygame.Rect]) -> None:
        """Update creature physics and animation."""
        # Apply horizontal movement
        self.pos.x += self.velocity.x * dt
        self.velocity.x = 0

        # Apply vertical movement
        self.pos.y += self.vel_y * dt

        self.update_rect()

        # Collision with platforms - IMPROVED
        self.is_grounded = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                # Only collide if falling (vel_y >= 0)

                    # Check if we're above the platform

                self.pos.y = platform.top - self.size +1
                self.vel_y = 0
                self.is_grounded = True
                break

        self.update_rect()

        # Update animations (no input handling here)
        Character.update(self, int(dt * 1000))


class GhostMouse(Character):
    """Character that follows mouse cursor."""

    def __init__(self, x: float, y: float,
                 spritesheet_path: Optional[str] = None):
        """Initialize ghost mouse."""
        super().__init__(x, y, 20, spritesheet_path=spritesheet_path)
        self.interaction_range = 100

    def update(self, dt: int) -> None:
        """Update position to follow mouse."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.pos.x = mouse_x
        self.pos.y = mouse_y
        self.update_rect()

        super().update(dt)

    def interact(self, objects: List) -> Optional[object]:
        """Check if interacting with any object."""
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                return obj
        return None


class CharacterManager:
    """Manage multiple characters easily."""

    def __init__(self):
        self.characters: Dict[str, Character] = {}

    def add(self, name: str, character: Character) -> None:
        """Add character to manager."""
        self.characters[name] = character

    def remove(self, name: str) -> None:
        """Remove character from manager."""
        if name in self.characters:
            del self.characters[name]

    def get(self, name: str) -> Optional[Character]:
        """Get character by name."""
        return self.characters.get(name)

    def update_all(self, dt: float, platforms: Optional[List[pygame.Rect]] = None) -> None:
        """Update all characters."""
        for char in self.characters.values():
            if isinstance(char, Creature) and platforms:
                char.update(dt, platforms)
            else:
                char.update(int(dt * 1000))