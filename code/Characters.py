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
        x,
        y,
        size,
        image=None,
        spritesheet_path=None
    ):

        self.pos = pygame.Vector2(
            x,
            y
        )

        self.last_pos = self.pos.copy()

        self.size = size
        self.image = image

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

        # =================================================
        # SPRITE
        # =================================================

        self.sprite = None

        if spritesheet_path:

            self.sprite = SpriteObject(
                "character",
                spritesheet_path,
                int(x),
                int(y)
            )

        # =================================================
        # ANIMATION
        # =================================================

        self.current_anim = None
        self.current_priority = 0

        self.anim_priority = {}

        self.walk_anim = None
        self.idle_anim = None

        self.is_paused = False
        self.movement_threshold = 0.5

    # =====================================================
    # ADD ANIMATION
    # =====================================================

    def add_anim(
        self,
        name,
        frames,
        cols,
        rows,
        speed=100,
        loop=True,
        priority=0,
        spritesheet_path=None,
        scale=1.0
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

    # =====================================================
    # WALK / IDLE
    # =====================================================

    def set_walk_idle(
        self,
        walk_anim_name,
        idle_anim_name
    ):

        self.walk_anim = walk_anim_name
        self.idle_anim = idle_anim_name

    # =====================================================
    # PLAY ANIMATION
    # =====================================================

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

        # Nie przerywamy ważniejszej animacji.
        if self.current_priority > priority:
            return False

        # -------------------------------------------------
        # NOWA ANIMACJA
        # -------------------------------------------------

        if self.current_anim != name:
            reset = True

        self.sprite.play(
            name,
            reset=reset
        )

        self.current_anim = name
        self.current_priority = priority

        return True

    # =====================================================
    # UPDATE RECT
    # =====================================================

    def update_rect(self):

        self.rect.center = (
            int(self.pos.x),
            int(self.pos.y)
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        self.update_rect()

        if self.sprite:

            # Najpierw aktualizujemy animację.
            self.sprite.update(dt)

            # Synchronizacja pozycji sprite.
            self.sprite.set_position(
                int(self.pos.x),
                int(self.pos.y)
            )

            # Jeżeli animacja się skończyła,
            # zwalniamy priorytet.
            if self.sprite.is_finished():

                self.current_priority = 0

                # Atak zakończony -> automatycznie
                # przechodzimy do idle/walk w następnym
                # update Creature.

    # =====================================================
    # DRAW
    # =====================================================

    def draw(self, surface):

        if (
            self.sprite
            and self.sprite.current
        ):

            self.sprite.draw(
                surface
            )

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
        spritesheet_path=None
    ):

        super().__init__(
            x=x,
            y=y,
            size=50,
            spritesheet_path=spritesheet_path
        )

        # =================================================
        # STATS
        # =================================================

        self.vel_y = 0

        self.hp = 100
        self.power = 0
        self.score = 0

        # =================================================
        # RUCH
        # =================================================

        self.speed = 400

        # =================================================
        # SKOK
        # =================================================

        self.max_jumps = 2
        self.jumps_left = self.max_jumps

        self.is_grounded = False

        self.jump_speed = 400

        # =================================================
        # ANIMACJE
        # =================================================

        self.walk_anim = "walk"
        self.idle_anim = "idle"

    # =====================================================
    # JUMP
    # =====================================================

    def jump(self):

        if self.jumps_left > 0:

            self.vel_y = -self.jump_speed

            self.jumps_left -= 1

            self.is_grounded = False

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt,
        platforms=None
    ):

        keys = pygame.key.get_pressed()

        # =================================================
        # RUCH POZIOMY
        # =================================================

        dx = 0

        if keys[pygame.K_a]:

            dx -= self.speed * dt

        if keys[pygame.K_d]:

            dx += self.speed * dt

        self.pos.x += dx

        self.update_rect()

        # =================================================
        # KOLIZJE X
        # =================================================

        if platforms:

            for platform in platforms:

                plat_rect = (
                    platform.rect
                    if hasattr(platform, "rect")
                    else platform
                )

                if self.rect.colliderect(
                    plat_rect
                ):

                    if dx > 0:

                        self.rect.right = (
                            plat_rect.left
                        )

                    elif dx < 0:

                        self.rect.left = (
                            plat_rect.right
                        )

                    self.pos.x = (
                        self.rect.centerx
                    )

        # =================================================
        # ANIMACJA RUCHU
        # =================================================
        #
        # WAŻNE:
        # Attack ma priority 3.
        # Walk/idle mają priority 1.
        #
        # Dzięki temu podczas ataku A/D nie
        # przerwie animacji ataku.
        # =================================================



        # =================================================
        # GRAWITACJA
        # =================================================

        gravity = 1200

        self.vel_y += (
            gravity * dt
        )

        self.pos.y += (
            self.vel_y * dt
        )

        self.update_rect()

        # =================================================
        # KOLIZJE Y
        # =================================================

        self.is_grounded = False

        if platforms:

            for platform in platforms:

                plat_rect = (
                    platform.rect
                    if hasattr(platform, "rect")
                    else platform
                )

                if self.rect.colliderect(
                    plat_rect
                ):

                    # SPADANIE
                    if self.vel_y > 0:

                        self.rect.bottom = (
                            plat_rect.top
                        )

                        self.pos.y = (
                            self.rect.centery
                        )

                        self.vel_y = 0

                        self.is_grounded = True

                        self.jumps_left = (
                            self.max_jumps
                        )

                    # UDERZENIE OD DOŁU
                    elif self.vel_y < 0:

                        self.rect.top = (
                            plat_rect.bottom
                        )

                        self.pos.y = (
                            self.rect.centery
                        )

                        self.vel_y = 0

                    break

        # =================================================
        # ANIMACJA
        # =================================================

        super().update(
            dt
        )


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

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt,
        platforms=None
    ):

        self.last_pos = (
            self.pos.copy()
        )

        mouse_pos = pygame.Vector2(
            pygame.mouse.get_pos()
        )

        # =================================================
        # X
        # =================================================

        dx = (
            mouse_pos.x
            - self.pos.x
        )

        self.pos.x += dx

        self.update_rect()

        if platforms:

            for platform in platforms:

                plat_rect = (
                    platform.rect
                    if hasattr(platform, "rect")
                    else platform
                )

                if self.rect.colliderect(
                    plat_rect
                ):

                    if dx > 0:

                        self.rect.right = (
                            plat_rect.left
                        )

                    elif dx < 0:

                        self.rect.left = (
                            plat_rect.right
                        )

                    self.pos.x = (
                        self.rect.centerx
                    )

        # =================================================
        # Y
        # =================================================

        dy = (
            mouse_pos.y
            - self.pos.y
        )

        self.pos.y += dy

        self.update_rect()

        if platforms:

            for platform in platforms:

                plat_rect = (
                    platform.rect
                    if hasattr(platform, "rect")
                    else platform
                )

                if self.rect.colliderect(
                    plat_rect
                ):

                    if dy > 0:

                        self.rect.bottom = (
                            plat_rect.top
                        )

                    elif dy < 0:

                        self.rect.top = (
                            plat_rect.bottom
                        )

                    self.pos.y = (
                        self.rect.centery
                    )

        super().update(
            dt
        )


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

        return self.characters.get(
            name
        )

    def update_all(
        self,
        dt,
        platforms=None
    ):

        for character in (
            self.characters.values()
        ):

            if isinstance(
                character,
                (Creature, GhostMouse)
            ):

                character.update(
                    dt,
                    platforms
                )

            else:

                character.update(
                    dt
                )

    def draw_all(
        self,
        surface
    ):

        for character in (
            self.characters.values()
        ):

            character.draw(
                surface
            )


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
        lifetime=5.0
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

        self.lifetime = lifetime
        self.age = 0.0

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

    def update(
        self,
        dt
    ):

        self.age += dt

        self.pos += (
            self.vel * dt
        )

        self.rect.center = (
            int(self.pos.x),
            int(self.pos.y)
        )

    def is_alive(self):

        return (
            self.age
            < self.lifetime
        )

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

    def add(
        self,
        projectile
    ):

        self.projectiles.append(
            projectile
        )

    def update(
        self,
        dt
    ):

        for projectile in self.projectiles:

            projectile.update(
                dt
            )

        self.projectiles = [
            projectile
            for projectile in self.projectiles
            if projectile.is_alive()
        ]

    def draw_all(
        self,
        surface
    ):

        for projectile in (
            self.projectiles
        ):

            projectile.draw(
                surface
            )

    def get_projectiles(self):

        return self.projectiles.copy()


# =========================================================
# SHOOTING ENEMY
# =========================================================

class ShootingEnemy(Character):

    def __init__(
        self,
        x,
        y,
        spritesheet_path=None
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

        self.move_direction = (
            random.choice([-1, 1])
        )

        self.direction = 1

        self.gravity = 2000

        self.vel_y = 0

        self.is_grounded = False

    # =====================================================
    # SHOOT
    # =====================================================

    def shoot(
        self,
        target_x,
        target_y
    ):

        dx = (
            target_x
            - self.pos.x
        )

        dy = (
            target_y
            - self.pos.y
        )

        distance = (
            dx ** 2
            + dy ** 2
        ) ** 0.5

        if distance > 0:

            dx /= distance
            dy /= distance

        return Projectile(
            self.pos.x,
            self.pos.y,
            dx * self.projectile_speed,
            dy * self.projectile_speed,
            damage=self.projectile_damage,
            color="orange"
        )

    # =====================================================
    # DAMAGE
    # =====================================================

    def take_damage(
        self,
        damage
    ):

        self.hp -= damage

        if self.hp < 0:

            self.hp = 0

    def is_alive(self):

        return self.hp > 0

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt,
        player_pos=None,
        platforms=None
    ):

        self.shoot_cooldown -= dt

        dx = 0

        # =================================================
        # RUCH X
        # =================================================

        if player_pos:

            dist_to_player = (
                self.pos - player_pos
            ).length()

            if (
                dist_to_player
                < self.detection_range
            ):

                direction = (
                    player_pos
                    - self.pos
                )

                if direction.length() > 0:

                    direction = (
                        direction.normalize()
                    )

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

                self.direction = (
                    self.move_direction
                )

        else:

            dx = (
                self.move_direction
                * self.patrol_speed
                * dt
            )

        self.pos.x += dx

        self.update_rect()

        # =================================================
        # KOLIZJE X
        # =================================================

        if platforms:

            for platform in platforms:

                plat_rect = (
                    platform.rect
                    if hasattr(platform, "rect")
                    else platform
                )

                if self.rect.colliderect(
                    plat_rect
                ):

                    if dx > 0:

                        self.rect.right = (
                            plat_rect.left
                        )

                        self.move_direction = -1

                    elif dx < 0:

                        self.rect.left = (
                            plat_rect.right
                        )

                        self.move_direction = 1

                    self.pos.x = (
                        self.rect.centerx
                    )

        # =================================================
        # GRANICE EKRANU
        # =================================================

        if (
            self.pos.x < 50
            or self.pos.x > 850
        ):

            self.move_direction *= -1

        # =================================================
        # GRAWITACJA
        # =================================================

        self.vel_y += (
            self.gravity * dt
        )

        self.pos.y += (
            self.vel_y * dt
        )

        self.update_rect()

        self.is_grounded = False

        # =================================================
        # KOLIZJE Y
        # =================================================

        if platforms:

            for platform in platforms:

                plat_rect = (
                    platform.rect
                    if hasattr(platform, "rect")
                    else platform
                )

                if self.rect.colliderect(
                    plat_rect
                ):

                    if self.vel_y > 0:

                        self.rect.bottom = (
                            plat_rect.top
                        )

                        self.vel_y = 0

                        self.is_grounded = True

                    elif self.vel_y < 0:

                        self.rect.top = (
                            plat_rect.bottom
                        )

                        self.vel_y = 0

                    self.pos.y = (
                        self.rect.centery
                    )

        # =================================================
        # ANIMACJA
        # =================================================

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

        super().update(
            dt
        )
