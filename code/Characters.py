import pygame
from typing import Optional
from animations import SpriteObject
import random

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
        priority=0,
        spritesheet_path: Optional[str] = None,
        scale: float = 1.0
    ):
        # If no default SpriteObject exists, allow providing a spritesheet_path per-animation.
        if not self.sprite:
            if spritesheet_path:
                # Create a SpriteObject using the provided spritesheet for this character.
                self.sprite = SpriteObject("character", spritesheet_path, int(self.pos.x), int(self.pos.y))
            else:
                raise ValueError("Brak spritesheet_path")

        # Delegate to SpriteObject.add_frames which supports per-animation spritesheet and scaling.
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


# =========================================================
# CREATURE
# =========================================================
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

        # =========================
        # MOVEMENT
        # =========================

        self.speed = 400

        # =========================
        # JUMP
        # =========================

        self.max_jumps = 2
        self.jumps_left = self.max_jumps

        self.is_grounded = False

        self.jump_speed = 400

        # =========================
        # ANIMATIONS
        # =========================

        self.walk_anim = "walk"
        self.idle_anim = "idle"

    # =====================================================
    # JUMP
    # =====================================================

    def jump(self):

        if self.jumps_left > 0:

            # Move upward
            self.vel_y = -self.jump_speed

            self.jumps_left -= 1

            self.is_grounded = False

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt, platforms=None):

        keys = pygame.key.get_pressed()

        # =================================================
        # HORIZONTAL MOVEMENT
        # =================================================

        dx = 0

        if keys[pygame.K_a]:
            dx -= self.speed * dt

        if keys[pygame.K_d]:
            dx += self.speed * dt

        # Move player
        self.pos.x += dx

        # Update hitbox
        self.update_rect()

        # =================================================
        # HORIZONTAL COLLISIONS
        # =================================================

        if platforms:

            for platform in platforms:

                plat_rect = (
                    platform.rect
                    if hasattr(platform, "rect")
                    else platform
                )

                if self.rect.colliderect(plat_rect):

                    if dx > 0:
                        # Moving right
                        self.rect.right = plat_rect.left

                    elif dx < 0:
                        # Moving left
                        self.rect.left = plat_rect.right

                    self.pos.x = self.rect.centerx

        # =================================================
        # ANIMATION
        # =================================================

        if dx != 0:

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
        # GRAVITY
        # =================================================

        gravity = 1200

        self.vel_y += gravity * dt

        self.pos.y += self.vel_y * dt

        self.update_rect()

        # =================================================
        # VERTICAL COLLISIONS
        # =================================================

        self.is_grounded = False

        if platforms:

            for platform in platforms:

                plat_rect = (
                    platform.rect
                    if hasattr(platform, "rect")
                    else platform
                )

                if self.rect.colliderect(plat_rect):

                    # -----------------------------
                    # FALLING / LANDING
                    # -----------------------------

                    if self.vel_y > 0:

                        self.rect.bottom = plat_rect.top

                        self.pos.y = self.rect.centery

                        self.vel_y = 0

                        self.is_grounded = True

                        # Reset double jump
                        self.jumps_left = self.max_jumps

                    # -----------------------------
                    # HITTING CEILING
                    # -----------------------------

                    elif self.vel_y < 0:

                        self.rect.top = plat_rect.bottom

                        self.pos.y = self.rect.centery

                        self.vel_y = 0

                    break

        # =================================================
        # CHARACTER / SPRITE UPDATE
        # =================================================

        super().update(dt)

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


# =========================================================
# PROJECTILE
# =========================================================

class Projectile:
    """Pocisk wystrzelony przez wroga."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, damage: int = 10, color: str = "yellow", lifetime: float = 5.0):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vx, vy)
        self.radius = 4
        self.damage = damage
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
    
    def update(self, dt: float):
        self.age += dt
        self.pos += self.vel * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
    
    def is_alive(self) -> bool:
        return self.age < self.lifetime
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
    
    def draw_hitbox(self, surface, color="yellow"):
        pygame.draw.rect(surface, color, self.rect, 2)


# =========================================================
# PROJECTILE MANAGER
# =========================================================

class ProjectileManager:
    """Zarządza wszystkimi pociskami w grze."""
    
    def __init__(self):
        self.projectiles = []
    
    def add(self, projectile: Projectile):
        self.projectiles.append(projectile)
    
    def update(self, dt: float):
        self.projectiles = [p for p in self.projectiles if p.is_alive()]
        for projectile in self.projectiles:
            projectile.update(dt)
    
    def draw_all(self, surface):
        for projectile in self.projectiles:
            projectile.draw(surface)
    
    def get_projectiles(self):
        return self.projectiles.copy()


# =========================================================
# SHOOTING ENEMY
# =========================================================

class ShootingEnemy(Character):
    """Wróg, który się porusza i strzela do gracza."""
    
    PRIORITY_IDLE = 1
    PRIORITY_WALK = 1
    PRIORITY_SHOOT = 3
    
    def __init__(self, x: float, y: float, spritesheet_path: Optional[str] = None):
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
        
        # Inteligencja wroga
        self.detection_range = 300
        self.patrol_speed = 100
        self.move_direction = random.choice([-1, 1])
        self.direction = 1
        
        # Grawitacja
        self.gravity = 2000
        self.vel_y = 0
        self.is_grounded = False
    
    def shoot(self, target_x: float, target_y: float) -> Projectile:
        """Strzela w kierunku celu."""
        # Kierunek do celu
        dx = target_x - self.pos.x
        dy = target_y - self.pos.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Tworzenie pocisku
        projectile = Projectile(
            self.pos.x,
            self.pos.y,
            dx * self.projectile_speed,
            dy * self.projectile_speed,
            damage=self.projectile_damage,
            color="orange"
        )
        return projectile
    
    def take_damage(self, damage: int):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
    
    def is_alive(self) -> bool:
        """Sprawdza, czy wróg żyje."""
        return self.hp > 0
    
    def update(self, dt: float, player_pos: pygame.Vector2 = None, platforms=None):
        """Aktualizuje pozycję i logikę wroga."""
        
        # Zmniejsz cooldown
        self.shoot_cooldown -= dt
        
        # Ruch
        dx = 0
        
        if player_pos:
            # Odległość do gracza
            dist_to_player = (self.pos - player_pos).length()
            
            if dist_to_player < self.detection_range:
                # Widzi gracza - podchodzi
                direction = (player_pos - self.pos).normalize()
                dx = direction.x * self.speed * dt
                self.direction = 1 if dx >= 0 else -1
            else:
                # Patrolu
                dx = self.move_direction * self.patrol_speed * dt
                self.direction = self.move_direction
        else:
            # Patrolu, jeśli brak pozycji gracza
            dx = self.move_direction * self.patrol_speed * dt
        
        # Ruch X
        self.pos.x += dx
        self.update_rect()
        
        # Kolizje z platformami (poziomo)
        if platforms:
            for platform in platforms:
                if self.rect.colliderect(platform):
                    if dx > 0:
                        self.rect.right = platform.left
                        self.move_direction = -1
                    elif dx < 0:
                        self.rect.left = platform.right
                        self.move_direction = 1
                    self.pos.x = self.rect.centerx
        
        # Zmiana kierunku patrolu na krawędziach
        if self.pos.x < 50 or self.pos.x > 850:
            self.move_direction *= -1
        
        # ========== GRAWITACJA ==========
        self.vel_y += self.gravity * dt
        self.pos.y += self.vel_y * dt
        self.update_rect()
        
        # Kolizje z platformami (pionowo)
        self.is_grounded = False
        if platforms:
            for platform in platforms:
                if self.rect.colliderect(platform):
                    if self.vel_y > 0:
                        # Lądowanie
                        self.rect.bottom = platform.top
                        self.vel_y = 0
                        self.is_grounded = True
                    elif self.vel_y < 0:
                        # Uderzenie od dołu
                        self.rect.top = platform.bottom
                        self.vel_y = 0
                    self.pos.y = self.rect.centery
        
        # Animacje
        if abs(dx) > self.movement_threshold:
            if self.walk_anim:
                self.play(self.walk_anim, reset=False)
        else:
            if self.idle_anim:
                self.play(self.idle_anim, reset=False)
        
        # Update animacji
        super().update(int(dt * 1000))