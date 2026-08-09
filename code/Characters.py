import random
from typing import Optional
import pygame
from animations import SpriteObject


# =========================================================
# BASE CHARACTER
# =========================================================

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

        self.rect = pygame.Rect(0, 0, int(size), int(size))
        self.rect.center = (int(x), int(y))

        # ANIMACJE
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

    def add_anim(
        self,
        name,
        frames,
        cols,
        rows,
        speed=100,
        loop=True,
        priority=0,
        spritesheet_path: Optional[str] = None,
        scale: float = 1.0
    ):
        if not self.sprite:
            if spritesheet_path:
                self.sprite = SpriteObject("character", spritesheet_path, int(self.pos.x), int(self.pos.y))
            else:
                raise ValueError("Brak spritesheet_path")

        self.sprite.add_frames(
            name,
            frames,
            cols,
            rows,
            frame_duration=speed,
            loop=loop,
            spritesheet_path=spritesheet_path,
            scale=scale
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

    def update_rect(self):
        """Aktualizuje pozycję hitboksu do punktu pozycji obiektu."""
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt, *args, **kwargs):
        self.update_rect()

        if self.sprite:
            if self.sprite.is_finished():
                self.current_priority = 0

            self.sprite.update(dt)
            self.sprite.set_position(int(self.pos.x), int(self.pos.y))

    def draw(self, surface):
        if self.sprite and self.sprite.current:
            self.sprite.draw(surface)
        else:
            pygame.draw.circle(
                surface,
                "red",
                (int(self.pos.x), int(self.pos.y)),
                int(self.size / 2)
            )


# =========================================================
# CREATURE
# =========================================================

class Creature(Character):

    def __init__(self, x, y, spritesheet_path=None):
        super().__init__(
            x=x,
            y=y,
            size=50,
            spritesheet_path=spritesheet_path
        )

        self.vel_y = 0
        self.hp = 100
        self.power = 0
        self.score = 0

        # RUCH
        self.speed = 400

        # SKOK
        self.max_jumps = 2
        self.jumps_left = self.max_jumps
        self.is_grounded = False
        self.jump_speed = 400

        # ANIMACJE
        self.walk_anim = "walk"
        self.idle_anim = "idle"

    def jump(self):
        if self.jumps_left > 0:
            self.vel_y = -self.jump_speed
            self.jumps_left -= 1
            self.is_grounded = False

    def update(self, dt, platforms=None, *args, **kwargs):
        keys = pygame.key.get_pressed()

        # POZIOMO
        dx = 0
        if keys[pygame.K_a]:
            dx -= self.speed * dt
        if keys[pygame.K_d]:
            dx += self.speed * dt

        self.pos.x += dx
        self.update_rect()

        # KOLIZJE POZIOME
        if platforms:
            for platform in platforms:
                plat_rect = platform.rect if hasattr(platform, "rect") else platform
                if self.rect.colliderect(plat_rect):
                    if dx > 0:
                        self.rect.right = plat_rect.left
                    elif dx < 0:
                        self.rect.left = plat_rect.right
                    self.pos.x = self.rect.centerx

        # ANIMACJA
        if dx != 0:
            if self.walk_anim:
                self.play(self.walk_anim, reset=False)
        else:
            if self.idle_anim:
                self.play(self.idle_anim, reset=False)

        # GRAWITACJA
        gravity = 1200
        self.vel_y += gravity * dt
        self.pos.y += self.vel_y * dt
        self.update_rect()

        # KOLIZJE PIONOWE
        self.is_grounded = False

        if platforms:
            for platform in platforms:
                plat_rect = platform.rect if hasattr(platform, "rect") else platform
                if self.rect.colliderect(plat_rect):
                    if self.vel_y > 0:
                        self.rect.bottom = plat_rect.top
                        self.pos.y = self.rect.centery
                        self.vel_y = 0
                        self.is_grounded = True
                        self.jumps_left = self.max_jumps  # Reset skoków na platformie
                    elif self.vel_y < 0:
                        self.rect.top = plat_rect.bottom
                        self.pos.y = self.rect.centery
                        self.vel_y = 0
                    break

        super().update(dt)


# =========================================================
# GHOST
# =========================================================
class GhostMouse(Character):

    def __init__(self, x=0, y=0, spritesheet_path=None):
        super().__init__(x, y, 30, spritesheet_path=spritesheet_path)
        self.hp = 50

    def update(self, dt, platforms=None, *args, **kwargs):
        self.last_pos = self.pos.copy()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        # ----------------------------------------------------
        # 1. RUCH I KOLIZJA POZIOMA (X)
        # ----------------------------------------------------
        dx = mouse_pos.x - self.pos.x
        self.pos.x += dx
        self.update_rect()

        if platforms:
            for platform in platforms:
                plat_rect = platform.rect if hasattr(platform, "rect") else platform
                if self.rect.colliderect(plat_rect):
                    if dx > 0:  # Ruch w prawo
                        self.rect.right = plat_rect.left
                    elif dx < 0:  # Ruch w lewo
                        self.rect.left = plat_rect.right
                    self.pos.x = self.rect.centerx

        # ----------------------------------------------------
        # 2. RUCH I KOLIZJA PIONOWA (Y)
        # ----------------------------------------------------
        dy = mouse_pos.y - self.pos.y
        self.pos.y += dy
        self.update_rect()

        if platforms:
            for platform in platforms:
                plat_rect = platform.rect if hasattr(platform, "rect") else platform
                if self.rect.colliderect(plat_rect):
                    if dy > 0:  # Ruch w dół
                        self.rect.bottom = plat_rect.top
                    elif dy < 0:  # Ruch w górę
                        self.rect.top = plat_rect.bottom
                    self.pos.y = self.rect.centery

        super().update(dt)


# =========================================================
# SHOOTING ENEMY
# =========================================================

class ShootingEnemy(Character):

    def __init__(self, x: float, y: float, spritesheet_path: Optional[str] = None):
        super().__init__(x, y, 50, spritesheet_path=spritesheet_path)
        self.hp = 30
        self.speed = 150
        self.shoot_cooldown = 0.0
        self.shoot_interval = 1.5
        self.projectile_speed = 300
        self.projectile_damage = 15

        self.detection_range = 300
        self.patrol_speed = 100
        self.move_direction = random.choice([-1, 1])
        self.direction = 1

        self.gravity = 2000
        self.vel_y = 0
        self.is_grounded = False

    def shoot(self, target_x: float, target_y: float):
        dx = target_x - self.pos.x
        dy = target_y - self.pos.y
        distance = (dx**2 + dy**2)**0.5

        if distance > 0:
            dx /= distance
            dy /= distance
        else:
            dx, dy = 1, 0

        self.shoot_cooldown = self.shoot_interval

        return Projectile(
            self.pos.x,
            self.pos.y,
            dx * self.projectile_speed,
            dy * self.projectile_speed,
            damage=self.projectile_damage,
            color="orange"
        )

    def take_damage(self, damage: int):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0

    def is_alive(self) -> bool:
        return self.hp > 0

    def update(self, dt: float, player_pos: pygame.Vector2 = None, platforms=None, *args, **kwargs):
        self.shoot_cooldown -= dt
        dx = 0

        if player_pos:
            dist_vec = player_pos - self.pos
            dist_to_player = dist_vec.length()
            if dist_to_player < self.detection_range and dist_to_player > 0:
                direction = dist_vec.normalize()
                dx = direction.x * self.speed * dt
                self.direction = 1 if dx >= 0 else -1
            else:
                dx = self.move_direction * self.patrol_speed * dt
                self.direction = self.move_direction
        else:
            dx = self.move_direction * self.patrol_speed * dt

        self.pos.x += dx
        self.update_rect()

        if platforms:
            for platform in platforms:
                plat_rect = platform.rect if hasattr(platform, "rect") else platform
                if self.rect.colliderect(plat_rect):
                    if dx > 0:
                        self.rect.right = plat_rect.left
                        self.move_direction = -1
                    elif dx < 0:
                        self.rect.left = plat_rect.right
                        self.move_direction = 1
                    self.pos.x = self.rect.centerx

        if self.pos.x < 50 or self.pos.x > 850:
            self.move_direction *= -1

        self.vel_y += self.gravity * dt
        self.pos.y += self.vel_y * dt
        self.update_rect()

        self.is_grounded = False
        if platforms:
            for platform in platforms:
                plat_rect = platform.rect if hasattr(platform, "rect") else platform
                if self.rect.colliderect(plat_rect):
                    if self.vel_y > 0:
                        self.rect.bottom = plat_rect.top
                        self.vel_y = 0
                        self.is_grounded = True
                    elif self.vel_y < 0:
                        self.rect.top = plat_rect.bottom
                        self.vel_y = 0
                    self.pos.y = self.rect.centery

        if abs(dx) > self.movement_threshold:
            if self.walk_anim:
                self.play(self.walk_anim, reset=False)
        else:
            if self.idle_anim:
                self.play(self.idle_anim, reset=False)

        super().update(dt)


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

    def update_all(self, dt, platforms=None, player_pos=None):
        for character in self.characters.values():
            if isinstance(character, ShootingEnemy):
                character.update(dt, player_pos=player_pos, platforms=platforms)
            elif isinstance(character, (Creature, GhostMouse)):
                character.update(dt, platforms=platforms)
            else:
                character.update(dt)

    def draw_all(self, surface):
        for character in self.characters.values():
            character.draw(surface)


# =========================================================
# PROJECTILE & MANAGER
# =========================================================

class Projectile:
    def __init__(self, x: float, y: float, vx: float, vy: float, damage: int = 10, color: str = "yellow", lifetime: float = 5.0):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vx, vy)
        self.radius = 4
        self.damage = damage
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.is_dead = False

        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt: float):
        self.age += dt
        self.pos += self.vel * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if self.age >= self.lifetime:
            self.is_dead = True

    def is_alive(self) -> bool:
        return not self.is_dead and self.age < self.lifetime

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)


class ProjectileManager:
    def __init__(self):
        self.projectiles = []

    def add(self, projectile):
        if projectile:
            self.projectiles.append(projectile)

    def update(self, dt: float, *args, **kwargs):
        """Aktualizuje pociski i usuwa nieaktywne/martwe."""
        for projectile in self.projectiles[:]:
            projectile.update(dt)

            if not projectile.is_alive() or getattr(projectile, "is_dead", False):
                self.projectiles.remove(projectile)

    def draw_all(self, surface):
        for projectile in self.projectiles:
            projectile.draw(surface)

    def get_projectiles(self):
        return self.projectiles.copy()

    def clear(self):
        self.projectiles.clear()

    # --- Metody Magiczne ---

    def __len__(self):
        return len(self.projectiles)

    def __iter__(self):
        return iter(self.projectiles)

    def __getitem__(self, index):
        return self.projectiles[index]

    def __bool__(self):
        return bool(self.projectiles)