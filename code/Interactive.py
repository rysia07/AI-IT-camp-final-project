import random
from typing import Optional
import pygame
from animations import SpriteObject
# =========================================================
# INTERACTIVE & ENVIRONMENT
# =========================================================

class Interactive:

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.active = True
        self.color = (150, 150, 150)
        self.sprite = None
        self.current_anim = None

    def add_anim(
            self,
            name,
            frames,
            cols,
            rows,
            speed=100,
            loop=True,
            spritesheet_path=None,
            scale=1.0
    ):
        if self.sprite is None:
            if spritesheet_path is None:
                raise ValueError("spritesheet_path is required for the first animation.")

            self.sprite = SpriteObject(
                "interactive",
                spritesheet_path,
                self.rect.centerx,
                self.rect.centery
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

    def play(self, name, reset=True):
        if self.sprite is None or name not in self.sprite.animations:
            return False

        self.sprite.play(name, reset)
        self.current_anim = name
        return True

    def update_animation(self, dt):
        if self.sprite is None:
            return

        self.sprite.update(dt)
        self.sprite.set_position(self.rect.centerx, self.rect.centery)

    def update(self, creature, ghost):
        pass

    def handle_event(self, event):
        pass

    def draw(self, surface):
        if self.sprite and self.sprite.current:
            self.sprite.draw(surface)
        else:
            pygame.draw.rect(surface, self.color, self.rect)


class Lever(Interactive):
    def __init__(self, x, y, w=100, h=20, direction="left"):
        super().__init__(x, y, w, h)
        self.enabled = False
        self.direction = direction
        self.enter_side = None

    def update(self, creature, ghost):
        prev_x, prev_y = ghost.last_pos.x, ghost.last_pos.y
        curr_x, curr_y = ghost.pos.x, ghost.pos.y

        if self.direction in ("left", "right"):
            y_in_bounds = self.rect.top <= curr_y <= self.rect.bottom or self.rect.top <= prev_y <= self.rect.bottom

            if y_in_bounds:
                if self.enter_side is None:
                    if prev_x <= self.rect.left < curr_x:
                        self.enter_side = "left"
                    elif prev_x >= self.rect.right > curr_x:
                        self.enter_side = "right"

                elif self.enter_side == "left" and curr_x >= self.rect.right:
                    self.enabled = (self.direction == "right")
                    self.enter_side = None

                elif self.enter_side == "right" and curr_x <= self.rect.left:
                    self.enabled = (self.direction == "left")
                    self.enter_side = None
            else:
                self.enter_side = None

        elif self.direction in ("top", "bottom"):
            x_in_bounds = self.rect.left <= curr_x <= self.rect.right or self.rect.left <= prev_x <= self.rect.right

            if x_in_bounds:
                if self.enter_side is None:
                    if prev_y <= self.rect.top < curr_y:
                        self.enter_side = "top"
                    elif prev_y >= self.rect.bottom > curr_y:
                        self.enter_side = "bottom"

                elif self.enter_side == "top" and curr_y >= self.rect.bottom:
                    self.enabled = (self.direction == "bottom")
                    self.enter_side = None

                elif self.enter_side == "bottom" and curr_y <= self.rect.top:
                    self.enabled = (self.direction == "top")
                    self.enter_side = None
            else:
                self.enter_side = None

    def draw(self, surface):
        self.color = (46, 204, 113) if self.enabled else (231, 76, 60)
        super().draw(surface)


class CodePanel(Interactive):
    def __init__(self, x, y, code="1234"):
        super().__init__(x, y, 60, 60)
        self.code = str(code)
        self.current = ""
        self.is_unlocked = False
        self.is_open = False
        self.player_near = False
        self.color = (70, 130, 180)

    def update(self, creature, ghost):
        self.player_near = creature.rect.colliderect(self.rect)
        if not self.player_near and self.is_open:
            self.is_open = False
            self.current = ""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and self.player_near:
                self.is_open = not self.is_open
                self.current = ""
            elif event.key == pygame.K_ESCAPE and self.is_open:
                self.is_open = False
                self.current = ""
            elif self.is_open:
                if event.unicode.isdigit():
                    self.current += event.unicode
                elif event.key == pygame.K_BACKSPACE:
                    self.current = self.current[:-1]

                if len(self.current) > len(self.code):
                    self.current = ""

                if self.current == self.code:
                    self.is_unlocked = True
                    self.is_open = False
                    self.current = ""

    def draw(self, surface):
        super().draw(surface)

        if self.player_near and not self.is_open:
            font = pygame.font.Font(None, 24)
            hint = font.render("[Q] Code", True, (255, 255, 255))
            surface.blit(hint, (self.rect.x - 10, self.rect.y - 25))

        if self.is_open:
            popup_rect = pygame.Rect(self.rect.x - 30, self.rect.y - 70, 120, 50)
            pygame.draw.rect(surface, (40, 40, 40), popup_rect)

            font = pygame.font.Font(None, 32)
            display_text = self.current + "_" * (len(self.code) - len(self.current))
            text_surf = font.render(display_text, True, (0, 255, 0))
            text_rect = text_surf.get_rect(center=popup_rect.center)
            surface.blit(text_surf, text_rect)


class ScoringButton(Interactive):
    def __init__(self, x, y, required_power=1):
        super().__init__(x, y, 80, 20)
        self.required_power = required_power
        self.points = 100
        self.used = False
        self.color = (241, 196, 15)

    def update(self, creature, ghost):
        if creature.rect.colliderect(self.rect):
            current_power = getattr(creature, 'power', 0)
            if not self.used and current_power >= self.required_power:
                if hasattr(creature, 'score'):
                    creature.score += self.points
                self.used = True
                self.color = (127, 140, 141)

            # Obsługa kolizji jako platforma i reset skoków
            overlap_left = creature.rect.right - self.rect.left
            overlap_right = self.rect.right - creature.rect.left
            overlap_top = creature.rect.bottom - self.rect.top
            overlap_bottom = self.rect.bottom - creature.rect.top

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_top and creature.vel_y >= 0:
                creature.rect.bottom = self.rect.top
                creature.vel_y = 0
                creature.pos.y = creature.rect.centery
                creature.is_grounded = True
                creature.jumps_left = creature.max_jumps  # RESET DOUBLE JUMP

            elif min_overlap == overlap_bottom and creature.vel_y < 0:
                creature.rect.top = self.rect.bottom
                creature.vel_y = 0
                creature.pos.y = creature.rect.centery

            elif min_overlap == overlap_left:
                creature.rect.right = self.rect.left
                creature.pos.x = creature.rect.centerx

            elif min_overlap == overlap_right:
                creature.rect.left = self.rect.right
                creature.pos.x = creature.rect.centerx


class Door(Interactive):
    def __init__(self, x, y, w=30, h=120, trigger_object=None):
        super().__init__(x, y, w, h)
        self.is_open = False
        self.trigger_object = trigger_object
        self.color = (139, 69, 19)

    def update(self, creature, ghost):
        if self.trigger_object:
            if hasattr(self.trigger_object, 'enabled'):
                self.is_open = self.trigger_object.enabled
            elif hasattr(self.trigger_object, 'is_unlocked'):
                self.is_open = self.trigger_object.is_unlocked

        # Jeśli drzwi są ZAMKNIĘTE, działają jak kolizyjna ściana/platforma
        if not self.is_open and creature.rect.colliderect(self.rect):
            overlap_left = creature.rect.right - self.rect.left
            overlap_right = self.rect.right - creature.rect.left
            overlap_top = creature.rect.bottom - self.rect.top
            overlap_bottom = self.rect.bottom - creature.rect.top

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left:
                creature.rect.right = self.rect.left
                creature.pos.x = creature.rect.centerx
            elif min_overlap == overlap_right:
                creature.rect.left = self.rect.right
                creature.pos.x = creature.rect.centerx
            elif min_overlap == overlap_top and creature.vel_y >= 0:
                creature.rect.bottom = self.rect.top
                creature.vel_y = 0
                creature.pos.y = creature.rect.centery
                creature.is_grounded = True
                creature.jumps_left = creature.max_jumps  # RESET DOUBLE JUMP
            elif min_overlap == overlap_bottom and creature.vel_y < 0:
                creature.rect.top = self.rect.bottom
                creature.vel_y = 0
                creature.pos.y = creature.rect.centery

    def draw(self, surface):
        if not self.is_open:
            super().draw(surface)


class LevelGate(Interactive):
    def __init__(self, x, y):
        super().__init__(x, y, 100, 120)
        self.triggered = False
        self.color = (142, 68, 173)

    def update(self, creature, ghost):
        if self.triggered:
            return

        if creature.rect.colliderect(self.rect) and ghost.rect.colliderect(self.rect):
            print("NEXT LEVEL")
            self.triggered = True


class SafeZone(Interactive):
    """
    Strefa (np. schron, pole siłowe), w której postać oraz duszka chroni status bezpieczny.
    Możesz w łatwy sposób sprawdzać, czy postać jest w SafeZone i blokować obrażenia.
    """

    def __init__(self, x, y, w=150, h=150):
        super().__init__(x, y, w, h)
        self.color = (46, 204, 113, 100)  # Półprzezroczysty zielony
        self.is_ghost_inside = False
        self.is_creature_inside = False

    def update(self, creature, ghost):
        self.is_creature_inside = self.rect.colliderect(creature.rect)

    def draw(self, surface):
        # Rysowanie półprzezroczystego obszaru
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill((46, 204, 113, 80))
        surface.blit(s, (self.rect.x, self.rect.y))
        pygame.draw.rect(surface, (46, 204, 113), self.rect, 2)


# =========================================================
# INTERACTIVE MANAGER
# =========================================================

class InteractiveManager:

    def __init__(self):
        self.objects = []

    def add(self, obj: Interactive):
        self.objects.append(obj)

    def update_all(self, creature, ghost, dt):
        for obj in self.objects:
            if obj.active:
                obj.update(creature, ghost)
                obj.update_animation(dt)

    def handle_event_all(self, event):
        for obj in self.objects:
            if obj.active:
                obj.handle_event(event)

    def draw_all(self, surface):
        for obj in self.objects:
            if obj.active:
                obj.draw(surface)