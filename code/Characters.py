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

        # POS = środek postaci / hitboxa
        self.pos = pygame.Vector2(x, y)

        # Poprzednia pozycja
        self.last_pos = self.pos.copy()

        self.size = size
        self.image = image

        # =====================================================
        # HITBOX
        # =====================================================

        self.rect = pygame.Rect(
            0,
            0,
            int(size),
            int(size)
        )

        self.rect.center = (
            int(x),
            int(y)
        )

        # =====================================================
        # ANIMACJE
        # =====================================================

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

    # =========================================================
    # ANIMATIONS
    # =========================================================

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
                self.sprite = SpriteObject(
                    "character",
                    spritesheet_path,
                    int(self.pos.x),
                    int(self.pos.y)
                )

            else:
                raise ValueError(
                    "Brak spritesheet_path"
                )

        self.sprite.add_frames(
            name=name,
            indices=frames,
            cols=cols,
            rows=rows,
            frame_duration=speed,
            loop=loop,
            spritesheet_path=spritesheet_path,
            scale=scale
        )

        self.anim_priority[name] = priority

    def set_walk_idle(
        self,
        walk_anim_name,
        idle_anim_name
    ):

        self.walk_anim = walk_anim_name
        self.idle_anim = idle_anim_name

    def play(
        self,
        name,
        reset=True
    ):

        if not self.sprite:
            return False

        if name not in self.sprite.animations:
            return False

        priority = self.anim_priority.get(
            name,
            0
        )

        if self.current_priority > priority:
            return False

        self.sprite.play(
            name,
            reset
        )

        self.current_anim = name
        self.current_priority = priority

        return True

    # =========================================================
    # HITBOX
    # =========================================================

    def update_rect(self):

        self.rect.center = (
            int(self.pos.x),
            int(self.pos.y)
        )

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        dt,
        *args,
        **kwargs
    ):

        # UWAGA:
        # Nie aktualizujemy tutaj rect.
        #
        # Creature robi to po zakończeniu
        # całej fizyki i kolizji.

        if self.sprite:

            if self.sprite.is_finished():
                self.current_priority = 0

            self.sprite.update(dt)

            self.sprite.set_position(
                int(self.pos.x),
                int(self.pos.y)
            )

    # =========================================================
    # DRAW
    # =========================================================

    def draw(
        self,
        surface
    ):

        if (
            self.sprite
            and self.sprite.current
        ):

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


# =========================================================
# CREATURE
# =========================================================

class Creature(Character):

    def __init__(
        self,
        x,
        y,
        speed=400,
        jump_force=-150,
        spritesheet_path=None
    ):

        super().__init__(
            x=x,
            y=y,
            size=50,
            spritesheet_path=spritesheet_path
        )

        # =====================================================
        # RUCH
        # =====================================================

        self.vel_x = 0.0
        self.vel_y = 0.0

        self.speed = speed

        # =====================================================
        # SKOK
        # =====================================================

        self.max_jumps = 2
        self.jumps_left = self.max_jumps

        self.is_grounded = False

        # jump_force jest ujemny,
        # bo Y rośnie w dół
        self.jump_force = jump_force

        # =====================================================
        # FIZYKA
        # =====================================================

        self.gravity = 1200

        # =====================================================
        # STATYSTYKI
        # =====================================================

        self.hp = 100
        self.power = 0
        self.score = 0

        # =====================================================
        # ANIMACJE
        # =====================================================

        self.walk_anim = "walk"
        self.idle_anim = "idle"

        self.projectile_speed = 500
        self.projectile_damage = 10
        self.shoot_cooldown = 0.0
        self.shoot_interval = 0.2

    # =========================================================
    # JUMP
    # =========================================================

    def jump(self):

        if self.jumps_left <= 0:
            return False

        self.vel_y = self.jump_force

        self.jumps_left -= 1

        self.is_grounded = False

        return True

    # =========================================================
    # MOVE
    # =========================================================

    def move(
        self,
        direction
    ):

        self.vel_x = (
            direction * self.speed
        )

    def shoot(
            self,
            direction_x,
            direction_y
    ):

        if self.shoot_cooldown > 0:
            return None

        direction = pygame.Vector2(
            direction_x,
            direction_y
        )

        if direction.length_squared() == 0:
            return None

        direction = direction.normalize()

        self.shoot_cooldown = self.shoot_interval

        return Projectile(
            self.pos.x,
            self.pos.y,
            direction.x * self.projectile_speed,
            direction.y * self.projectile_speed,
            damage=self.projectile_damage,
            color="cyan",
            owner="player"
        )
    # =========================================================
    # COLLISION RECT
    # =========================================================

    @staticmethod
    def get_rect(obj):

        if hasattr(obj, "rect"):
            return obj.rect

        return obj

    def check_screen_bounds(self, width=900, height=600):

        if (
                self.rect.right <= 0
                or self.rect.left >= width
                or self.rect.bottom >= height
                or self.rect.top <= 0
        ):
            print(
                f"PLAYER OUT OF SCREEN: "
                f"{self.rect} / SCREEN: {width}x{height}"
            )

            self.hp = 0
            return False

        return True

    # =========================================================
    # COLLISION X
    # =========================================================

    def _move_horizontal(
        self,
        dt,
        platforms
    ):

        dx = self.vel_x * dt

        if dx == 0:
            return

        self.pos.x += dx

        self.update_rect()
        self.check_screen_bounds(
            width=900,
            height=600
        )

        for platform in platforms:

            platform_rect = self.get_rect(platform)

            if not self.rect.colliderect(platform_rect):
                continue

            if dx > 0:

                self.rect.right = platform_rect.left

            elif dx < 0:

                self.rect.left = platform_rect.right

            self.pos.x = self.rect.centerx

    # =========================================================
    # COLLISION Y
    # =========================================================

    def _move_vertical(
        self,
        dt,
        platforms
    ):

        # Zapamiętujemy poprzedni rect.
        old_rect = self.rect.copy()

        # =====================================================
        # GRAWITACJA
        # =====================================================

        self.vel_y += self.gravity * dt

        # =====================================================
        # RUCH PIONOWY
        # =====================================================

        self.pos.y += self.vel_y * dt

        self.update_rect()

        landed = False

        for platform in platforms:

            platform_rect = self.get_rect(platform)

            if not self.rect.colliderect(platform_rect):
                continue

            # =================================================
            # SPADANIE / LĄDOWANIE
            # =================================================

            if self.vel_y >= 0:

                if old_rect.bottom <= platform_rect.top:

                    self.rect.bottom = platform_rect.top

                    self.pos.y = self.rect.centery

                    self.vel_y = 0

                    landed = True

            # =================================================
            # SKOK / UDERZENIE GŁOWĄ
            # =================================================

            else:

                if old_rect.top >= platform_rect.bottom:

                    self.rect.top = platform_rect.bottom

                    self.pos.y = self.rect.centery

                    self.vel_y = 0

        # =====================================================
        # IS GROUNDED
        # =====================================================

        self.is_grounded = landed

        if landed:
            self.jumps_left = self.max_jumps

    # =========================================================
    # CHECK GROUND
    # =========================================================

    def _check_ground(
        self,
        platforms
    ):

        ground_check = pygame.Rect(
            self.rect.left + 2,
            self.rect.bottom,
            max(1, self.rect.width - 4),
            2
        )

        for platform in platforms:

            platform_rect = self.get_rect(platform)

            if ground_check.colliderect(platform_rect):

                if abs(
                    self.rect.bottom
                    - platform_rect.top
                ) <= 2:

                    return True

        return False

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        dt,
        platforms=None,
        *args,
        **kwargs
    ):

        if platforms is None:
            platforms = []

        # =====================================================
        # POPRZEDNIA POZYCJA
        # =====================================================

        self.last_pos = self.pos.copy()

        # =====================================================
        # RUCH POZIOMY
        # =====================================================

        self._move_horizontal(
            dt,
            platforms
        )

        # =====================================================
        # ANIMACJA RUCHU
        # =====================================================

        if abs(self.vel_x) > self.movement_threshold:

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

        # =====================================================
        # RUCH PIONOWY + GRAWITACJA
        # =====================================================

        self._move_vertical(
            dt,
            platforms
        )

        # =====================================================
        # DODATKOWE SPRAWDZENIE PODŁOŻA
        # =====================================================

        if not self.is_grounded:

            if self._check_ground(platforms):

                self.is_grounded = True

                self.vel_y = 0

                self.jumps_left = self.max_jumps

                # Dociśnięcie postaci do platformy
                for platform in platforms:

                    platform_rect = self.get_rect(platform)

                    if (
                        self.rect.bottom
                        >= platform_rect.top
                        and
                        self.rect.bottom
                        <= platform_rect.top + 3
                        and
                        self.rect.right
                        > platform_rect.left
                        and
                        self.rect.left
                        < platform_rect.right
                    ):

                        self.rect.bottom = platform_rect.top

                        self.pos.y = self.rect.centery

                        break

        # =====================================================
        # FINALNA SYNCHRONIZACJA
        # =====================================================
        #
        # Po wszystkich ruchach i kolizjach
        # rect musi odpowiadać dokładnie self.pos.
        #

        self.update_rect()

        # =====================================================
        # SPRITE
        # =====================================================

        super().update(dt)


# =========================================================
# GHOST
# =========================================================

class GhostMouse(Character):

    def __init__(
        self,
        x=0,
        y=0,
        spritesheet_path=None
    ):

        super().__init__(
            x,
            y,
            30,
            spritesheet_path=spritesheet_path
        )

        self.hp = 50

    def update(
        self,
        dt,
        platforms=None,
        *args,
        **kwargs
    ):

        # Duch jest sterowany przez main.py.
        # Nie zmieniamy tutaj jego pozycji.

        self.update_rect()

        super().update(dt)


# =========================================================
# SHOOTING ENEMY
# =========================================================

class ShootingEnemy(Character):

    def __init__(
        self,
        x: float,
        y: float,
        spritesheet_path: Optional[str] = None
    ):

        super().__init__(
            x,
            y,
            50,
            spritesheet_path=spritesheet_path
        )

        self.hp = 30

        self.speed = 150

        self.shoot_cooldown = 0.0
        self.shoot_interval = 1.5

        self.projectile_speed = 300
        self.projectile_damage = 15

        self.detection_range = 300

        self.patrol_speed = 100

        self.move_direction = random.choice(
            [-1, 1]
        )

        self.direction = 1

        # =====================================================
        # FIZYKA WROGA
        # =====================================================

        self.gravity = 2000
        self.vel_y = 0.0

        self.is_grounded = False

    # =========================================================
    # SHOOT
    # =========================================================

    def shoot(
        self,
        target_x: float,
        target_y: float
    ):

        dx = target_x - self.pos.x
        dy = target_y - self.pos.y

        distance = (
            dx ** 2 + dy ** 2
        ) ** 0.5

        if distance > 0:

            dx /= distance
            dy /= distance

        else:

            dx = 1
            dy = 0

        self.shoot_cooldown = self.shoot_interval

        return Projectile(
            self.pos.x,
            self.pos.y,
            dx * self.projectile_speed,
            dy * self.projectile_speed,
            damage=self.projectile_damage,
            color="orange",
            owner="enemy"
        )

    # =========================================================
    # DAMAGE
    # =========================================================

    def take_damage(
        self,
        damage: int
    ):

        self.hp -= damage

        if self.hp <= 0:
            self.hp = 0

    def is_alive(self):

        return self.hp > 0

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        dt: float,
        player_pos: pygame.Vector2 = None,
        platforms=None,
        *args,
        **kwargs
    ):

        if platforms is None:
            platforms = []

        self.shoot_cooldown -= dt

        # =====================================================
        # RUCH X
        # =====================================================

        dx = 0

        if player_pos:

            dist_vec = (
                player_pos - self.pos
            )

            dist_to_player = (
                dist_vec.length()
            )

            if (
                dist_to_player
                < self.detection_range
                and dist_to_player > 0
            ):

                direction = dist_vec.normalize()

                dx = (
                    direction.x
                    * self.speed
                    * dt
                )

                self.direction = (
                    1 if dx >= 0
                    else -1
                )

            else:

                dx = (
                    self.move_direction
                    * self.patrol_speed
                    * dt
                )

                self.direction = self.move_direction

        else:

            dx = (
                self.move_direction
                * self.patrol_speed
                * dt
            )

        self.pos.x += dx

        self.update_rect()

        # =====================================================
        # KOLIZJE X
        # =====================================================

        for platform in platforms:

            platform_rect = (
                platform.rect
                if hasattr(platform, "rect")
                else platform
            )

            if self.rect.colliderect(platform_rect):

                if dx > 0:

                    self.rect.right = platform_rect.left

                    self.move_direction = -1

                elif dx < 0:

                    self.rect.left = platform_rect.right

                    self.move_direction = 1

                self.pos.x = self.rect.centerx

        # =====================================================
        # GRANICE EKRANU
        # =====================================================

        if self.pos.x < 50:

            self.pos.x = 50

            self.move_direction = 1

        elif self.pos.x > 850:

            self.pos.x = 850

            self.move_direction = -1

        # =====================================================
        # GRAWITACJA
        # =====================================================

        old_rect = self.rect.copy()

        self.vel_y += self.gravity * dt

        self.pos.y += self.vel_y * dt

        self.update_rect()

        self.is_grounded = False

        # =====================================================
        # KOLIZJE Y
        # =====================================================

        for platform in platforms:

            platform_rect = (
                platform.rect
                if hasattr(platform, "rect")
                else platform
            )

            if not self.rect.colliderect(platform_rect):
                continue

            # Lądowanie
            if self.vel_y >= 0:

                if old_rect.bottom <= platform_rect.top:

                    self.rect.bottom = platform_rect.top

                    self.pos.y = self.rect.centery

                    self.vel_y = 0

                    self.is_grounded = True

            # Uderzenie głową
            else:

                if old_rect.top >= platform_rect.bottom:

                    self.rect.top = platform_rect.bottom

                    self.pos.y = self.rect.centery

                    self.vel_y = 0

            break

        # =====================================================
        # ANIMACJA
        # =====================================================

        if abs(dx) > self.movement_threshold:

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

        # =====================================================
        # FINALNA SYNCHRONIZACJA
        # =====================================================

        self.update_rect()

        super().update(dt)


# =========================================================
# CHARACTER MANAGER
# =========================================================

class CharacterManager:

    def __init__(self):

        self.characters = {}

    def add(
        self,
        name,
        character
    ):

        self.characters[name] = character

    def remove(
        self,
        name
    ):

        if name in self.characters:
            del self.characters[name]

    def get(
        self,
        name
    ):

        return self.characters.get(name)

    def update_all(
        self,
        dt,
        platforms=None,
        player_pos=None
    ):

        for name, character in (
            self.characters.items()
        ):

            # =================================================
            # DUCH
            # =================================================

            if isinstance(
                character,
                GhostMouse
            ):

                continue

            # =================================================
            # CREATURE
            # =================================================

            if isinstance(
                character,
                Creature
            ):

                character.update(
                    dt,
                    platforms=platforms
                )

            # =================================================
            # WRÓG
            # =================================================

            elif isinstance(
                character,
                ShootingEnemy
            ):

                character.update(
                    dt,
                    player_pos=player_pos,
                    platforms=platforms
                )

            # =================================================
            # INNE
            # =================================================

            else:

                character.update(dt)

    def update(
        self,
        dt,
        platforms=None,
        player_pos=None
    ):

        self.update_all(
            dt,
            platforms=platforms,
            player_pos=player_pos
        )

    def draw_all(
        self,
        surface
    ):

        for character in (
            self.characters.values()
        ):

            character.draw(surface)

    def draw(
        self,
        surface
    ):

        self.draw_all(surface)


# =========================================================
# PROJECTILE
# =========================================================

class Projectile:

    def __init__(
        self,
        x,
        y,
        vx,
        vy,
        damage=10,
        color="yellow",
        lifetime=5.0,
        owner=None
    ):

        self.pos = pygame.Vector2(
            x,
            y
        )

        self.vel = pygame.Vector2(
            vx,
            vy
        )

        self.radius = 4

        self.damage = damage
        self.color = color
        self.owner = owner

        self.lifetime = lifetime
        self.age = 0.0

        self.is_dead = False

        self.rect = pygame.Rect(
            0,
            0,
            self.radius * 2,
            self.radius * 2
        )

        self.rect.center = (
            int(self.pos.x),
            int(self.pos.y)
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt
    ):

        self.age += dt

        self.pos += self.vel * dt

        self.rect.center = (
            int(self.pos.x),
            int(self.pos.y)
        )

        if self.age >= self.lifetime:

            self.is_dead = True

    # =====================================================
    # ALIVE
    # =====================================================

    def is_alive(self):

        return (
            not self.is_dead
            and self.age < self.lifetime
        )

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        surface
    ):

        pygame.draw.circle(
            surface,
            self.color,
            (
                int(self.pos.x),
                int(self.pos.y)
            ),
            self.radius
        )


# =========================================================
# PROJECTILE MANAGER
# =========================================================

class ProjectileManager:

    def __init__(self):

        self.projectiles = []


    def update(
            self,
            dt,
            platforms
    ):

        for projectile in self.projectiles[:]:

            projectile.update(dt)

            # =============================================
            # POCISK JUŻ NIE ŻYJE
            # =============================================

            if not projectile.is_alive():
                self.projectiles.remove(
                    projectile
                )

                continue

            # =============================================
            # KOLIZJA ZE ŚCIANĄ / PLATFORMĄ
            # =============================================

            hit_wall = False

            for platform in platforms:

                platform_rect = (
                    platform.rect
                    if hasattr(platform, "rect")
                    else platform
                )

                if projectile.rect.colliderect(
                        platform_rect
                ):
                    hit_wall = True
                    break

            # =============================================
            # USUNIĘCIE POCISKU
            # =============================================

            if hit_wall:
                self.projectiles.remove(
                    projectile
                )

    def add(
        self,
        projectile
    ):

        if projectile:
            self.projectiles.append(
                projectile
            )
    def draw_all(
        self,
        surface
    ):

        for projectile in self.projectiles:

            projectile.draw(surface)

    def draw(
        self,
        surface
    ):

        self.draw_all(surface)

    def get_projectiles(self):

        return self.projectiles.copy()

    def clear(self):

        self.projectiles.clear()

    def __len__(self):

        return len(self.projectiles)

    def __iter__(self):

        return iter(
            self.projectiles
        )

    def __getitem__(
        self,
        index
    ):

        return self.projectiles[index]

    def __bool__(self):

        return bool(
            self.projectiles
        )