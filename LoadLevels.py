# LoadLevels.py
import pygame
import random
from typing import List, Dict, Tuple, Optional


global player_pos
player_pos = (0,0)


class RectObject:
    """Represents a drawable rectangle."""

    def __init__(self, x: float, y: float, width: float, height: float,
                 color: Optional[Tuple[int, int, int]] = None,
                 name: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color if color else self._random_color()
        self.name = name

    @staticmethod
    def _random_color() -> Tuple[int, int, int]:
        """Generate random bright color."""
        return (random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw rectangle on surface."""
        pygame.draw.rect(surface, self.color, self.rect)

    def contains(self, x: float, y: float) -> bool:
        """Check if point is inside rect."""
        return self.rect.collidepoint(x, y)


class RectManager:
    """Manage and draw multiple rectangles."""

    def __init__(self):
        self.rects: List[RectObject] = []
        self.rects_by_name: Dict[str, RectObject] = {}

    def add(self, rect_obj: RectObject) -> None:
        """Add rectangle to manager."""
        self.rects.append(rect_obj)
        if rect_obj.name:
            self.rects_by_name[rect_obj.name] = rect_obj

    def remove(self, name: str) -> None:
        """Remove rectangle by name."""
        if name in self.rects_by_name:
            rect = self.rects_by_name[name]
            self.rects.remove(rect)
            del self.rects_by_name[name]

    def get(self, name: str) -> Optional[RectObject]:
        """Get rectangle by name."""
        return self.rects_by_name.get(name)

    def draw_all(self, surface: pygame.Surface) -> None:
        """Draw all rectangles."""
        for rect in self.rects:
            rect.draw(surface)

    def get_rects(self) -> List[pygame.Rect]:
        """Get all pygame.Rect objects (for collision detection)."""
        return [r.rect for r in self.rects]


def load_rects_from_file(filepath: str) -> RectManager:
    """
    Load rectangles from a .txt file.

    File format (space or comma separated):
    x y width height name
    100 100 50 50 platform1
    200 200 100 50 platform2

    Colors are random for each rect!

    Args:
        filepath: Path to .txt file

    Returns:
        RectManager with loaded rectangles
    """
    manager = RectManager()

    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                if line.startswith('p'):
                    print("aaa")
                else:
                    pass


                # Split by space or comma
                    parts = line.replace(',', ' ').split()

                if len(parts) < 4:
                    print(f"⚠️ Line {line_num}: Invalid format (need at least x y width height)")
                    continue

                try:
                    if not parts[0] == 'p':
                        x = float(parts[0])
                        y = float(parts[1])
                        width = float(parts[2])
                        height = float(parts[3])

                        # Optional: name
                        name = parts[4] if len(parts) > 4 else ""

                        # Color is now random!
                        rect_obj = RectObject(x, y, width, height, name=name)
                        manager.add(rect_obj)
                    else:
                        player_pos = (float(parts[0]), float(parts[1]))
                except (ValueError, IndexError) as e:
                    print(f"⚠️ Line {line_num}: {line} - Error: {e}")
                    continue

        print(f"✅ Loaded {len(manager.rects)} rectangles from {filepath}")
        return manager

    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return manager

def get_player_pos():
    return player_pos


# ============= DEMO =============
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    clock = pygame.time.Clock()

    # Load rects from file
    manager2 = load_rects_from_file('level.txt')

    # Add some rects manually if file doesn't exist
    if len(manager2.rects) == 0:
        manager2.add(RectObject(50, 500, 800, 50, name="ground"))
        manager2.add(RectObject(200, 400, 100, 50, name="platform1"))
        manager2.add(RectObject(500, 300, 150, 50, name="platform2"))

    running = True
    while running:
        dt = clock.tick(60)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))
        manager2.draw_all(screen)

        # Display info
        font = pygame.font.Font(None, 32)
        text = font.render(f"Rects loaded: {len(manager2.rects)}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()