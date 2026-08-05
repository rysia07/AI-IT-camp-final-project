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

    Usage:
        char = Character(100, 100, 50, spritesheet_path='sprite.png')
        char.add_anim('idle', [0], cols=3, rows=3, priority=char.PRIORITY_IDLE)
        char.add_anim('walk', [0,1,2,3], cols=3, rows=3, priority=char.PRIORITY_WALK)
        char.set_walk_idle('walk', 'idle')
        char.play('idle')
    """

    PRIORITY_IDLE = 1
    PRIORITY_WALK = 1
    PRIORITY_ATTACK = 3

    def __init__(self, x: float, y: float, size: float,
                 image: Optional[pygame.Surface] = None,
                 spritesheet_path: Optional[str] = None):
        """
        Initialize character.

        Args:
            x, y: Position
            size: Character size/radius
            image: Static image (fallback if no spritesheet)
            spritesheet_path: Path to sprite sheet
        """
        self.pos = pygame.Vector2(x, y)
        self.last_pos = pygame.Vector2(x, y)
        self.size = size
        self.image = image
        self.rect = pygame.Rect(x - size, y - size, size * 2, size * 2)

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
        """
        Add animation to character.

        Args:
            name: Animation name (e.g., 'walk', 'attack')
            frames: List of frame indices [0, 1, 2, 3]
            cols, rows: Spritesheet grid dimensions
            speed: Frame duration in ms
            loop: Whether animation loops
            priority: Animation priority (higher = can't be interrupted)
        """
        if not self.sprite:
            raise ValueError("Character needs spritesheet_path to use animations")
        self.sprite.add_frames(name, frames, cols, rows, speed, loop)
        self.anim_priority[name] = priority

    def set_walk_idle(self, walk_anim: str, idle_anim: str) -> None:
        """Enable auto-switching between walk/idle based on movement."""
        self.walk_anim = walk_anim
        self.idle_anim = idle_anim

    def play(self, anim_name: str, reset: bool = True) -> bool:
        """
        Play animation respecting priority hierarchy.

        Returns:
            True if animation started, False if blocked by higher priority
        """
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
        """
        Check if animation is playing.

        Args:
            anim_name: Specific animation to check (None = any animation)
        """
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

        # Don't auto-switch if high-priority animation is playing
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
        """Update character (call every frame)."""
        self.rect.center = self.pos

        if self.sprite and not self.is_paused:
            self.sprite.update(dt)
            self.sprite.set_position(int(self.pos.x - self.size),
                                     int(self.pos.y - self.size))

        self._clear_priority_if_done()
        self._check_movement()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw character (call every frame)."""
        if self.sprite and self.sprite.current:
            self.sprite.draw(surface)
        elif self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.circle(surface, "red", self.pos, self.size)


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

    def update_all(self, dt: int) -> None:
        """Update all characters."""
        for char in self.characters.values():
            char.update(dt)

    def draw_all(self, surface: pygame.Surface) -> None:
        """Draw all characters."""
        for char in self.characters.values():
            char.draw(surface)


# ============= DEMO =============
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    clock = pygame.time.Clock()

    # Create manager
    manager = CharacterManager()

    # Create hero
    hero = Character(450, 300, 50, spritesheet_path='ludzik.png')
    hero.add_anim('idle', frames=[0], cols=3, rows=3,
                  priority=Character.PRIORITY_IDLE)
    hero.add_anim('walk', frames=[0, 1, 2, 3, 4, 5], cols=3, rows=3,
                  speed=150, priority=Character.PRIORITY_WALK)
    hero.add_anim('attack', frames=[6, 7, 8], cols=3, rows=3,
                  speed=300, loop=False, priority=Character.PRIORITY_ATTACK)
    hero.set_walk_idle('walk', 'idle')
    hero.play('idle')

    manager.add('hero', hero)

    # Create enemy
    enemy = Character(200, 300, 50, spritesheet_path='ludzik.png')
    enemy.add_anim('idle', frames=[0], cols=3, rows=3,
                   priority=Character.PRIORITY_IDLE)
    enemy.add_anim('walk', frames=[0, 1, 2, 3, 4, 5], cols=3, rows=3,
                   speed=150, priority=Character.PRIORITY_WALK)
    enemy.set_walk_idle('walk', 'idle')
    enemy.play('idle')

    manager.add('enemy', enemy)

    a = 250
    b = False

    running = True
    while running:
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_2:
                    hero.play('attack')
                elif ev.key == pygame.K_SPACE:
                    hero.pause() if not hero.is_paused else hero.resume()
        if a > 0:
            a -= 1
        if a == 0:
            if b:
                b = False
            else:
                b = True
            a = 250

        if b and a >= 50:
            enemy.move(1,0)
        elif not b and a >= 50:
            enemy.move(-1,0)


        if keys[pygame.K_LEFT]:
            hero.move(-5, 0)
        if keys[pygame.K_RIGHT]:
            hero.move(5, 0)
        if keys[pygame.K_UP]:
            hero.move(0, -5)
        if keys[pygame.K_DOWN]:
            hero.move(0, 5)

        # Update all
        manager.update_all(dt)

        screen.fill((30, 30, 30))
        manager.draw_all(screen)

        font = pygame.font.Font(None, 32)
        text = font.render(f"Hero: {hero.current_anim} | Enemy: {enemy.current_anim}",
                           True, (255, 255, 255))
        screen.blit(text, (10, 10))

        info = font.render("Arrows=Move, Space=Pause, 2=Attack", True, (200, 200, 200))
        screen.blit(info, (10, 50))

        pygame.display.flip()

    pygame.quit()