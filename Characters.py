import pygame
from typing import Optional, List, Dict
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

        # Hitbox
        self.rect = pygame.Rect(
            x - size,
            y - size,
            size * 2,
            size * 4
        )

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

    # ---------------------
    # ANIMACJE
    # ---------------------

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

    def set_walk_idle(self, walk_anim_name: str, idle_anim_name: str):
        """Ustawia nazwy animacji dla chodzenia i stania w miejscu."""
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

    # ---------------------
    # POZYCJA
    # ---------------------

    def update_rect(self):
        self.rect.center = (
            int(self.pos.x),
            int(self.pos.y)
        )

    # ---------------------
    # UPDATE
    # ---------------------

    def update(self, dt):
        self.update_rect()

        if self.sprite:
            # Jeśli animacja się skończyła (np. jednorazowy atak), zwalniamy priorytet
            if self.sprite.is_finished():
                self.current_priority = 0

            self.sprite.update(dt)

            self.sprite.set_position(
                int(self.pos.x),
                int(self.pos.y)
            )

    # ---------------------
    # DRAW
    # ---------------------

    def draw(self, surface):
        if self.sprite and self.sprite.current:
            self.sprite.draw(surface)
        else:
            # Placeholder
            pygame.draw.circle(
                surface,
                "red",
                (
                    int(self.pos.x),
                    int(self.pos.y)
                ),
                self.size
            )


class Creature(Character):

    def __init__(self, x, y, spritesheet_path=None):
        super().__init__(
            x,
            y,
            40,
            spritesheet_path=spritesheet_path
        )

        self.hp = 100
        self.power = 0

        self.speed = 400
        self.gravity = 2000
        self.jump_force = -1000

        self.vel_y = 0
        self.is_grounded = False

    def jump(self):
        if self.is_grounded:
            self.vel_y = self.jump_force
            self.is_grounded = False

    def update(self, dt, platforms):
        keys = pygame.key.get_pressed()

        # ==========================================
        # 1. RUCH POZIOMY (Oś X)
        # ==========================================
        moving = False
        dx = 0

        if keys[pygame.K_a]:
            dx -= self.speed * dt
            moving = True
        if keys[pygame.K_d]:
            dx += self.speed * dt
            moving = True

        # Animacje
        if moving:
            if self.walk_anim:
                self.play(self.walk_anim, reset=False)
        else:
            if self.idle_anim:
                self.play(self.idle_anim, reset=False)

        # Aktualizacja pozycji X i kolizji bocznych
        self.pos.x += dx
        self.update_rect()

        for platform in platforms:
            if self.rect.colliderect(platform):
                if dx > 0:  # Ruch w prawo -> uderzenie w lewą ściankę platformy
                    self.rect.right = platform.left
                elif dx < 0:  # Ruch w lewo -> uderzenie w prawą ściankę platformy
                    self.rect.left = platform.right
                self.pos.x = self.rect.centerx

        # ==========================================
        # 2. RUCH PIONOWY (Oś Y - Grawitacja i Skok)
        # ==========================================
        if keys[pygame.K_w] and self.is_grounded:
            self.jump()

        current_gravity = self.gravity * 3 if (not self.is_grounded and keys[pygame.K_s]) else self.gravity
        self.vel_y += current_gravity * dt

        self.pos.y += self.vel_y * dt
        self.update_rect()

        # Kolizje pionowe (Lądowanie i Uderzenie Głową od dołu)
        self.is_grounded = False

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    # Opadanie -> LĄDOWANIE NA PLATFORMIE
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.is_grounded = True
                elif self.vel_y < 0:
                    # Skok w górę -> UDERZENIE GŁOWĄ OD DOŁU
                    self.rect.top = platform.bottom
                    self.vel_y = 0  # Zatrzymujemy ruch w górę (postać zaczyna spadać)

                self.pos.y = self.rect.centery

        # Aktualizacja animacji (przekazanie ms)
        super().update(int(dt * 1000))


class GhostMouse(Character):

    def __init__(self, x, y, spritesheet_path=None):
        super().__init__(
            x,
            y,
            20,
            spritesheet_path=spritesheet_path
        )
        self.hp = 50

    def update(self, dt):
        self.pos = pygame.Vector2(
            pygame.mouse.get_pos()
        )

        super().update(
            int(dt * 1000)
        )


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
            if isinstance(character, Creature) and platforms:
                character.update(dt, platforms)
            else:
                character.update(dt, platforms)

    def draw_all(self, surface):
        for character in self.characters.values():
            character.draw(surface)