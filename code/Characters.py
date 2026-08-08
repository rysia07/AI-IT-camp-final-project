import pygame
from typing import Optional
from animations import SpriteObject


class Character:

    PRIORITY_IDLE = 1
    PRIORITY_WALK = 1
    PRIORITY_ATTACK = 3

    def __init__(
        self,
        x: float,
        y: float,
        size: float,
        image: Optional[pygame.Surface] = None,
        spritesheet_path: Optional[str] = None
    ):
        self.pos = pygame.Vector2(x, y)
        self.last_pos = pygame.Vector2(x, y)

        self.size = size
        self.image = image

        # Hitbox tworzymy wyśrodkowany wokół (x, y)
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = (int(x), int(y))

        # =====================
        # ANIMACJE
        # =====================

        self.sprite = None

        if spritesheet_path:
            self.sprite = SpriteObject(
                "character",
                spritesheet_path,
                int(x),
                int(y)
            )

        self.current_anim = None
        self.current_priority = 0

        self.anim_priority = {}

        self.walk_anim = None
        self.idle_anim = None

        self.is_paused = False
        self.movement_threshold = 0.5

    # =====================
    # ANIMACJE
    # =====================

    def add_anim(
        self,
        name,
        frames,
        cols,
        rows,
        speed=100,
        loop=True,
        priority=0
    ):
        if not self.sprite:
            raise ValueError("Brak spritesheet_path")

        self.sprite.add_frames(
            name,
            frames,
            cols,
            rows,
            speed,
            loop
        )

        self.anim_priority[name] = priority

    def set_walk_idle(self, walk_anim_name, idle_anim_name):
        self.walk_anim = walk_anim_name
        self.idle_anim = idle_anim_name

    def play(self, name, reset=True):

        if not self.sprite:
            return False

        if name not in self.sprite.animations:
            return False

        priority = self.anim_priority.get(name, 0)

        if self.current_priority > priority:
            return False

        self.sprite.play(name, reset)

        self.current_anim = name
        self.current_priority = priority

        return True

    # =====================
    # POZYCJA
    # =====================

    def update_rect(self):
        """Aktualizuje pozycję hitboksu do punktu pozycji obiektu."""
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    # =====================
    # UPDATE
    # =====================

    def update(self, dt):

        self.update_rect()

        if self.sprite:

            if self.sprite.is_finished():
                self.current_priority = 0

            self.sprite.update(dt)

            self.sprite.set_position(
                int(self.pos.x),
                int(self.pos.y)
            )

    # =====================
    # DRAW
    # =====================

    def draw(self, surface):

        if self.sprite and self.sprite.current:

            self.sprite.draw(surface)

        else:

            pygame.draw.circle(
                surface,
                "red",
                (
                    int(self.pos.x),
                    int(self.pos.y)
                ),
                int(self.size / 2)
            )

    def draw_hitbox(self, surface, color="red"):

        pygame.draw.rect(
            surface,
            color,
            self.rect,
            2
        )
class Creature(Character):
    def __init__(self, x, y, spritesheet_path=None):
        super().__init__(x, y, 64, spritesheet_path=spritesheet_path)

        self.hp = 100
        self.power = 0

        self.speed = 400
        self.gravity = 2000
        self.jump_force = -850

        self.vel_y = 0
        self.is_grounded = False

        # System skoków
        self.max_jumps = 2
        self.jumps_left = 2
        self.jump_cooldown = 0

    def jump(self):
        if self.jumps_left > 0 and self.jump_cooldown <= 0:
            self.vel_y = self.jump_force
            self.jumps_left -= 1
            self.is_grounded = False
            self.jump_cooldown = 0.15

            # Ustawiamy podstawową moc skoku (1)
            self.power = 1

    def reset_jumps(self):
        """Odnawia skoki i resetuje siłę po wylądowaniu."""
        self.is_grounded = True
        self.jumps_left = self.max_jumps
        self.power = 0  # Po opadnięciu na podłoże moc wraca do 0

    def update(self, dt, platforms=None):
        keys = pygame.key.get_pressed()

        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt

        # Ruch A / D
        moving = False
        dx = 0
        if keys[pygame.K_a]:
            dx -= self.speed * dt
            moving = True
        if keys[pygame.K_d]:
            dx += self.speed * dt
            moving = True

        if moving:
            if self.walk_anim:
                self.play(self.walk_anim, reset=False)
        else:
            if self.idle_anim:
                self.play(self.idle_anim, reset=False)

        self.pos.x += dx
        self.update_rect()

        # Kolizje X
        if platforms:
            for platform in platforms:
                p_rect = platform.rect if hasattr(platform, 'rect') else platform
                if self.rect.colliderect(p_rect):
                    if dx > 0:
                        self.rect.right = p_rect.left
                    elif dx < 0:
                        self.rect.left = p_rect.right
                    self.pos.x = self.rect.centerx

        # Skok (W)
        if keys[pygame.K_w]:
            self.jump()

        # Grawitacja i wyliczanie POWER w zależności od Dropdown (S)
        current_gravity = self.gravity

        if not self.is_grounded and keys[pygame.K_s]:
            current_gravity *= 3  # Szybsze opadanie (Dropdown)

            # Jeśli wykonano 2 skoki (zostało 0 skoków) i wciśnięto S -> Power 3 (Double Jump Dropdown)
            if self.jumps_left == 0:
                self.power = 3
            # Jeśli wykonano 1 skok (został 1 skok) i wciśnięto S -> Power 2 (Standard Dropdown)
            else:
                self.power = 2

        self.vel_y += current_gravity * dt
        self.pos.y += self.vel_y * dt
        self.update_rect()

        # Kolizje Y
        self.is_grounded = False

        if platforms:
            for platform in platforms:
                p_rect = platform.rect if hasattr(platform, 'rect') else platform

                if self.rect.colliderect(p_rect):
                    if self.vel_y > 0:
                        self.rect.bottom = p_rect.top
                        self.vel_y = 0
                        self.reset_jumps()

                    elif self.vel_y < 0:
                        self.rect.top = p_rect.bottom
                        self.vel_y = 0

                    self.pos.y = self.rect.centery

        super().update(int(dt * 1000))

# =========================================================
# GHOST
# =========================================================

class GhostMouse(Character):

    def __init__(self, x=0, y=0, spritesheet_path=None):

        super().__init__(
            x,
            y,
            20,
            spritesheet_path=spritesheet_path
        )

        self.hp = 50


    def update(self, dt):

        self.last_pos = self.pos.copy()

        self.pos = pygame.Vector2(
            pygame.mouse.get_pos()
        )

        super().update(
            int(dt * 1000)
        )

# =========================================================
# CHARACTER MANAGER
# =========================================================

class CharacterManager:

    def __init__(self):

        self.characters = {}

    def add(self, name, character):

        self.characters[name] = character

    def remove(self, name):

        if name in self.characters:
            del self.characters[name]

    def get(self, name):

        return self.characters.get(name)

    def update_all(self, dt, platforms=None):

        for character in self.characters.values():

            if isinstance(character, Creature):

                character.update(
                    dt,
                    platforms
                )

            else:

                character.update(dt)

    def draw_all(self, surface):

        for character in self.characters.values():

            character.draw(surface)