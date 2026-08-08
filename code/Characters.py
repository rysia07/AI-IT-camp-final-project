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


# =========================================================
# CREATURE
# =========================================================

class Creature(Character):
    def __init__(self, x, y, spritesheet_path=None):
        super().__init__(
            x,
            y,
            64,  # <-- Zwiększyliśmy rozmiar hitboksu z 32 na 64!
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

    def update(self, dt, platforms=None):

        keys = pygame.key.get_pressed()

        # =================================================
        # RUCH POZIOMY
        # =================================================

        moving = False
        dx = 0

        if keys[pygame.K_a]:

            dx -= self.speed * dt
            moving = True

        if keys[pygame.K_d]:

            dx += self.speed * dt
            moving = True

        # =================================================
        # ANIMACJE
        # =================================================

        if moving:

            if self.walk_anim:
                self.play(
                    self.walk_anim,
                    reset=False
                )

        else:

            if self.idle_anim:
                self.play(
                    self.idle_anim,
                    reset=False
                )

        # =================================================
        # RUCH X
        # =================================================

        self.pos.x += dx

        self.update_rect()

        if platforms:
            for platform in platforms:

                if self.rect.colliderect(platform):

                    if dx > 0:

                        self.rect.right = platform.left

                    elif dx < 0:

                        self.rect.left = platform.right

                    self.pos.x = self.rect.centerx

        # =================================================
        # SKOK
        # =================================================

        if keys[pygame.K_w] and self.is_grounded:

            self.jump()

        # =================================================
        # GRAWITACJA
        # =================================================

        current_gravity = self.gravity

        if not self.is_grounded and keys[pygame.K_s]:

            current_gravity *= 3

        self.vel_y += current_gravity * dt

        self.pos.y += self.vel_y * dt

        self.update_rect()

        # =================================================
        # KOLIZJE PIONOWE
        # =================================================

        self.is_grounded = False

        if platforms:
            for platform in platforms:

                if self.rect.colliderect(platform):

                    if self.vel_y > 0:

                        # LĄDOWANIE

                        self.rect.bottom = platform.top

                        self.vel_y = 0

                        self.is_grounded = True

                    elif self.vel_y < 0:

                        # UDERZENIE OD DOŁU

                        self.rect.top = platform.bottom

                        self.vel_y = 0

                    self.pos.y = self.rect.centery

        # =================================================
        # ANIMACJA
        # =================================================

        super().update(
            int(dt * 1000)
        )


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

class WalkingEnemy(Character):

    def __init__(self, x, y, target=None, spritesheet_path=None):

        super().__init__(
            x,
            y,
            64,
            spritesheet_path=spritesheet_path
        )

        self.hp = 50

        #movement
        self.speed = 250

        #gravity
        self.gravity = 2000
        self.vel_y = 0

        self.is_grounded = False

        #Target To Follow
        self.target = target
    def update(self, dt, platforms=None):

        # =====================================================
        # FOLLOW MOVEMENT
        # =====================================================

        dx = 0

        if self.target:

            if self.target.pos.x < self.pos.x:
                dx = -self.speed * dt

            elif self.target.pos.x > self.pos.x:
                dx = self.speed * dt

        # =====================================================
        # EDGE CHECK
        # =====================================================

        next_x = self.pos.x + dx

        check_x = next_x

        if
        # =====================================================
        # HORIZONTAL COLLISION
        # =====================================================

        if platforms:

            for platform in platforms:

                if self.rect.colliderect(platform):

                    if dx > 0:
                        self.rect.right = platform.left

                    elif dx < 0:
                        self.rect.left = platform.right

                    self.pos.x = self.rect.centerx

        # =====================================================
        # gravity
        # =====================================================

        self.vel_y += self.gravity * dt

        self.pos.y += self.vel_y * dt

        self.update_rect()

        # =====================================================
        # vertical collision
        # =====================================================

        self.is_grounded = False

        if platforms:

            for platform in platforms:

                #falling
                if self.vel_y > 0:

                    self.rect.bottom = platform.top

                    self.vel_y = 0
                    self.is_grounded = True

                # Hitting Ceiling
                elif self.vel_y < 0:

                    self.rect.top = platform.bottom

                    self.vel_y = 0

                self.pos.y = self.rect.centery

        # =====================================================
        # ANIMATION / SPRITE
        # =====================================================

        Character.update(
            self,
            int(dt * 1000)
        )
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