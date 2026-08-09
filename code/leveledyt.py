import pygame
import sys
import os

# ============================================================
# CONFIG
# ============================================================

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700

WORLD_WIDTH = 900
WORLD_HEIGHT = 600

SIDEBAR_WIDTH = SCREEN_WIDTH - WORLD_WIDTH

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("Alien Space - Level Editor")

clock = pygame.time.Clock()

FONT = pygame.font.Font(None, 24)
SMALL_FONT = pygame.font.Font(None, 20)
BIG_FONT = pygame.font.Font(None, 30)

# Default level file
# ============================================================
# LEVEL FILES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LEVELS_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "../levels")
)

os.makedirs(
    LEVELS_DIR,
    exist_ok=True
)

DEFAULT_LEVEL = os.path.join(
    LEVELS_DIR,
    "level.txt"
)



# ============================================================
# COLORS
# ============================================================

BG = (25, 25, 30)
GRID = (45, 45, 50)

WHITE = (240, 240, 240)
GRAY = (150, 150, 150)
DARK_GRAY = (70, 70, 75)

RED = (220, 60, 60)
GREEN = (60, 200, 100)
BLUE = (70, 140, 220)
YELLOW = (230, 200, 60)
ORANGE = (230, 130, 50)

PLATFORM_COLOR = (90, 130, 180)
PLAYER_COLOR = (80, 220, 100)
ENEMY_COLOR = (220, 70, 70)
LEVER_COLOR = (220, 180, 60)
DOOR_COLOR = (130, 80, 180)
PANEL_COLOR = (60, 170, 180)
BUTTON_COLOR = (220, 120, 50)
GATE_COLOR = (70, 220, 180)


# ============================================================
# OBJECT TYPES
# ============================================================

OBJECT_TYPES = [
    "platform",
    "enemy",
    "lever",
    "door",
    "codepanel",
    "scoringbutton",
    "levelgate",
    "player",
]


# ============================================================
# EDITABLE OBJECT
# ============================================================

class LevelObject:

    def __init__(
        self,
        object_type,
        x,
        y,
        width=50,
        height=50,
        name=None,
        extra=None
    ):

        self.type = object_type

        self.x = float(x)
        self.y = float(y)

        self.width = float(width)
        self.height = float(height)

        self.name = name

        self.extra = extra or {}

        self.selected = False

    # --------------------------------------------------------
    # RECT
    # --------------------------------------------------------

    def get_rect(self):

        return pygame.Rect(
            int(self.x),
            int(self.y),
            max(1, int(self.width)),
            max(1, int(self.height))
        )

    # --------------------------------------------------------
    # COLOR
    # --------------------------------------------------------

    def get_color(self):

        colors = {

            "platform": PLATFORM_COLOR,
            "player": PLAYER_COLOR,
            "enemy": ENEMY_COLOR,
            "lever": LEVER_COLOR,
            "door": DOOR_COLOR,
            "codepanel": PANEL_COLOR,
            "scoringbutton": BUTTON_COLOR,
            "levelgate": GATE_COLOR,

        }

        return colors.get(
            self.type,
            WHITE
        )

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    def draw(self, surface):

        rect = self.get_rect()

        color = self.get_color()

        # Player is drawn as a circle
        if self.type == "player":

            pygame.draw.circle(
                surface,
                color,
                rect.center,
                max(5, min(rect.width, rect.height) // 2)
            )

        else:

            pygame.draw.rect(
                surface,
                color,
                rect
            )

        # Selection outline

        if self.selected:

            pygame.draw.rect(
                surface,
                RED,
                rect.inflate(6, 6),
                3
            )

        # Object label

        label = self.type

        if self.name:
            label += f" ({self.name})"

        text = SMALL_FONT.render(
            label,
            True,
            WHITE
        )

        surface.blit(
            text,
            (
                rect.x,
                rect.y - 18
            )
        )


# ============================================================
# LEVEL EDITOR
# ============================================================

class LevelEditor:

    def __init__(self):

        self.objects = []

        self.selected = None

        self.dragging = False

        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.level_path = DEFAULT_LEVEL
        self.level_name = "level"

        self.player = None

        self.message = ""
        self.message_timer = 0

        # ----------------------------------------------------
        # Text input
        # ----------------------------------------------------

        self.active_field = None

        self.field_values = {}

        self.field_rects = {}

        # Field for selecting the level file
        self.file_field_rect = pygame.Rect(
            WORLD_WIDTH + 85,
            40,
            SIDEBAR_WIDTH - 100,
            25
        )

        self.replace_field = False

        # ----------------------------------------------------
        # New object type
        # ----------------------------------------------------

        self.new_object_type = "platform"

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        self.buttons = []

        self.create_buttons()

        # ----------------------------------------------------
        # Load existing level
        # ----------------------------------------------------

        self.load_level(
            self.level_path
        )

    # ========================================================
    # BUTTONS
    # ========================================================

    def create_buttons(self):

        self.buttons = []

        x = WORLD_WIDTH + 15

        y = 75


        button_width = SIDEBAR_WIDTH - 30

        for object_type in OBJECT_TYPES:

            rect = pygame.Rect(
                x,
                y,
                button_width,
                30
            )

            self.buttons.append(
                (
                    rect,
                    object_type
                )
            )

            y += 35

    # ========================================================
    # LOAD LEVEL
    # ========================================================

    def load_level(self, filepath):

        self.objects.clear()

        self.player = None

        if not os.path.exists(filepath):

            self.show_message(
                "Level file does not exist"
            )

            return

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:

                for line in file:

                    line = line.strip()

                    if not line:
                        continue

                    if line.startswith("#"):
                        continue

                    parts = line.replace(
                        ",",
                        " "
                    ).split()

                    if not parts:
                        continue

                    object_type = parts[0].lower()

                    try:

                        # =================================================
                        # PLAYER
                        # =================================================

                        if object_type == "p":

                            x = float(parts[1])
                            y = float(parts[2])

                            obj = LevelObject(
                                "player",
                                x,
                                y,
                                50,
                                50
                            )

                            self.objects.append(obj)

                            self.player = obj

                        # =================================================
                        # PLATFORM
                        # =================================================

                        elif object_type == "platform":

                            x = float(parts[1])
                            y = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])

                            name = (
                                parts[5]
                                if len(parts) > 5
                                else None
                            )

                            obj = LevelObject(
                                "platform",
                                x,
                                y,
                                width,
                                height,
                                name
                            )

                            self.objects.append(obj)

                        # =================================================
                        # LEVER
                        # =================================================

                        elif object_type == "lever":

                            x = float(parts[1])
                            y = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])

                            direction = parts[5]

                            name = (
                                parts[6]
                                if len(parts) > 6
                                else None
                            )

                            obj = LevelObject(
                                "lever",
                                x,
                                y,
                                width,
                                height,
                                name,
                                {
                                    "direction": direction
                                }
                            )

                            self.objects.append(obj)

                        # =================================================
                        # DOOR
                        # =================================================

                        elif object_type == "door":

                            x = float(parts[1])
                            y = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])

                            trigger = parts[5]

                            name = (
                                parts[6]
                                if len(parts) > 6
                                else None
                            )

                            obj = LevelObject(
                                "door",
                                x,
                                y,
                                width,
                                height,
                                name,
                                {
                                    "trigger": trigger
                                }
                            )

                            self.objects.append(obj)

                        # =================================================
                        # CODE PANEL
                        # =================================================

                        elif object_type == "codepanel":

                            x = float(parts[1])
                            y = float(parts[2])

                            code = parts[3]

                            name = (
                                parts[4]
                                if len(parts) > 4
                                else None
                            )

                            obj = LevelObject(
                                "codepanel",
                                x,
                                y,
                                60,
                                40,
                                name,
                                {
                                    "code": code
                                }
                            )

                            self.objects.append(obj)

                        # =================================================
                        # SCORING BUTTON
                        # =================================================

                        elif object_type == "scoringbutton":

                            x = float(parts[1])
                            y = float(parts[2])

                            power = int(parts[3])

                            name = (
                                parts[4]
                                if len(parts) > 4
                                else None
                            )

                            obj = LevelObject(
                                "scoringbutton",
                                x,
                                y,
                                40,
                                40,
                                name,
                                {
                                    "required_power": power
                                }
                            )

                            self.objects.append(obj)

                        # =================================================
                        # LEVEL GATE
                        # =================================================

                        elif object_type == "levelgate":

                            x = float(parts[1])
                            y = float(parts[2])

                            name = (
                                parts[3]
                                if len(parts) > 3
                                else None
                            )

                            obj = LevelObject(
                                "levelgate",
                                x,
                                y,
                                60,
                                80,
                                name
                            )

                            self.objects.append(obj)

                        # =================================================
                        # ENEMY
                        # =================================================

                        elif object_type in (
                            "enemy",
                            "shootingenemy"
                        ):

                            x = float(parts[1])
                            y = float(parts[2])

                            spritesheet = (
                                parts[3]
                                if len(parts) > 3
                                else None
                            )

                            name = (
                                parts[4]
                                if len(parts) > 4
                                else None
                            )

                            obj = LevelObject(
                                "enemy",
                                x,
                                y,
                                50,
                                50,
                                name,
                                {
                                    "spritesheet": spritesheet
                                }
                            )

                            self.objects.append(obj)

                    except (
                        ValueError,
                        IndexError
                    ):

                        print(
                            "Could not read:",
                            line
                        )

            self.show_message(
                f"Loaded {len(self.objects)} objects"
            )

        except Exception as error:

            print(error)

            self.show_message(
                "Could not load level"
            )

    # ========================================================
    # SAVE LEVEL
    # ========================================================

    def save_level(self):

        try:

            with open(
                    self.level_path,
                    "w",
                    encoding="utf-8"
            ) as file:

                file.write("# ==================================\n")
                file.write("# GENERATED BY LEVEL EDITOR\n")
                file.write("# ==================================\n\n")

                # ------------------------------------------------
                # PLAYER
                # ------------------------------------------------

                for obj in self.objects:

                    if obj.type == "player":
                        file.write(
                            f"p {self.clean(obj.x)} "
                            f"{self.clean(obj.y)}\n"
                        )

                file.write("\n")

                # ------------------------------------------------
                # OTHER OBJECTS
                # ------------------------------------------------

                for obj in self.objects:

                    if obj.type == "player":
                        continue

                    if obj.type == "platform":

                        line = (
                            f"platform "
                            f"{self.clean(obj.x)} "
                            f"{self.clean(obj.y)} "
                            f"{self.clean(obj.width)} "
                            f"{self.clean(obj.height)}"
                        )

                        if obj.name:
                            line += f" {obj.name}"

                        file.write(line + "\n")

                    elif obj.type == "lever":

                        line = (
                            f"lever "
                            f"{self.clean(obj.x)} "
                            f"{self.clean(obj.y)} "
                            f"{self.clean(obj.width)} "
                            f"{self.clean(obj.height)} "
                            f"{obj.extra.get('direction', 'left')}"
                        )

                        if obj.name:
                            line += f" {obj.name}"

                        file.write(line + "\n")

                    elif obj.type == "door":

                        line = (
                            f"door "
                            f"{self.clean(obj.x)} "
                            f"{self.clean(obj.y)} "
                            f"{self.clean(obj.width)} "
                            f"{self.clean(obj.height)} "
                            f"{obj.extra.get('trigger', '')}"
                        )

                        if obj.name:
                            line += f" {obj.name}"

                        file.write(line + "\n")

                    elif obj.type == "codepanel":

                        line = (
                            f"codepanel "
                            f"{self.clean(obj.x)} "
                            f"{self.clean(obj.y)} "
                            f"{obj.extra.get('code', '1234')}"
                        )

                        if obj.name:
                            line += f" {obj.name}"

                        file.write(line + "\n")

                    elif obj.type == "scoringbutton":

                        line = (
                            f"scoringbutton "
                            f"{self.clean(obj.x)} "
                            f"{self.clean(obj.y)} "
                            f"{obj.extra.get('required_power', 0)}"
                        )

                        if obj.name:
                            line += f" {obj.name}"

                        file.write(line + "\n")

                    elif obj.type == "levelgate":

                        line = (
                            f"levelgate "
                            f"{self.clean(obj.x)} "
                            f"{self.clean(obj.y)}"
                        )

                        if obj.name:
                            line += f" {obj.name}"

                        file.write(line + "\n")

                    elif obj.type == "enemy":

                        line = (
                            f"enemy "
                            f"{self.clean(obj.x)} "
                            f"{self.clean(obj.y)}"
                        )

                        spritesheet = obj.extra.get(
                            "spritesheet"
                        )

                        if spritesheet:

                            line += f" {spritesheet}"

                            if obj.name:
                                line += f" {obj.name}"

                        elif obj.name:

                            line += f" none {obj.name}"

                        file.write(line + "\n")

            self.show_message(
                f"SAVED: {self.level_name}.txt"
            )

        except Exception as error:

            print(error)

            self.show_message(
                "SAVE ERROR"
            )

    # ========================================================
    # NEW LEVEL
    # ========================================================

    def new_level(self):

        numbers = []

        if os.path.exists(LEVELS_DIR):

            for filename in os.listdir(LEVELS_DIR):

                if not filename.startswith("level"):
                    continue

                if not filename.endswith(".txt"):
                    continue

                number = filename[5:-4]

                if number.isdigit():
                    numbers.append(
                        int(number)
                    )

        # ----------------------------------------------------
        # level.txt = podstawowy level
        # następny = level2
        # ----------------------------------------------------

        if numbers:

            next_number = max(numbers) + 1

        else:

            next_number = 2

        self.level_name = f"level{next_number}"

        self.level_path = os.path.join(
            LEVELS_DIR,
            f"{self.level_name}.txt"
        )

        # ----------------------------------------------------
        # Wyczyść edytor
        # ----------------------------------------------------

        self.objects.clear()

        self.selected = None
        self.player = None

        self.dragging = False

        self.active_field = None

        self.field_values.clear()
        self.field_rects.clear()

        self.show_message(
            f"NEW LEVEL: {self.level_name}"
        )

    # ========================================================
    # NUMBER CLEANUP
    # ========================================================

    def clean(self, value):

        try:
            value = float(value)

            if value.is_integer():
                return str(int(value))

            return str(value)

        except (ValueError, TypeError):
            return str(value)

    # ========================================================
    # MESSAGE
    # ========================================================

    def show_message(self, text):

        self.message = text

        self.message_timer = 2.0

    # ========================================================
    # SELECT OBJECT
    # ========================================================

    def select_object(self, mouse_pos):

        # Objects are checked backwards so that the last
        # object is considered to be on top.

        for obj in reversed(self.objects):

            if obj.get_rect().collidepoint(mouse_pos):

                self.set_selected(obj)

                return obj

        self.set_selected(None)

        return None

    # ========================================================
    # SET SELECTED
    # ========================================================

    def set_selected(self, obj):

        # Usuń zaznaczenie ze wszystkich obiektów
        for item in self.objects:
            item.selected = False

        self.selected = obj

        if obj:
            obj.selected = True

        # Zakończ edycję pola
        self.active_field = None

        # Wyczyść tymczasowe wartości
        self.field_values.clear()

        # Wyczyść prostokąty pól
        self.field_rects.clear()

        # Wyłącz tryb zastępowania
        self.replace_field = False

    # ========================================================
    # ADD OBJECT
    # ========================================================

    def add_object(self, object_type):

        x = 200
        y = 200

        if object_type == "player":

            # Only one player

            if self.player:

                self.show_message(
                    "There is already a player"
                )

                return

            obj = LevelObject(
                "player",
                x,
                y,
                50,
                50
            )

            self.player = obj

        elif object_type == "platform":

            obj = LevelObject(
                "platform",
                x,
                y,
                150,
                30,
                "new_platform"
            )

        elif object_type == "enemy":

            obj = LevelObject(
                "enemy",
                x,
                y,
                50,
                50,
                "new_enemy",
                {
                    "spritesheet": None
                }
            )

        elif object_type == "lever":

            obj = LevelObject(
                "lever",
                x,
                y,
                100,
                20,
                "new_lever",
                {
                    "direction": "left"
                }
            )

        elif object_type == "door":

            obj = LevelObject(
                "door",
                x,
                y,
                30,
                120,
                "new_door",
                {
                    "trigger": "button1"
                }
            )

        elif object_type == "codepanel":

            obj = LevelObject(
                "codepanel",
                x,
                y,
                60,
                40,
                "new_panel",
                {
                    "code": "1234"
                }
            )

        elif object_type == "scoringbutton":

            obj = LevelObject(
                "scoringbutton",
                x,
                y,
                40,
                40,
                "new_button",
                {
                    "required_power": 0
                }
            )

        elif object_type == "levelgate":

            obj = LevelObject(
                "levelgate",
                x,
                y,
                60,
                80,
                "new_gate"
            )

        else:

            return

        self.objects.append(obj)

        self.set_selected(obj)

        self.show_message(
            f"Added {object_type}"
        )

    # ========================================================
    # DELETE
    # ========================================================

    def delete_selected(self):

        if not self.selected:
            return

        if self.selected == self.player:
            self.player = None

        self.objects.remove(
            self.selected
        )

        self.selected = None

        self.show_message(
            "Object deleted"
        )

    # ========================================================
    # DRAW GRID
    # ========================================================

    def draw_grid(self):

        for x in range(
            0,
            WORLD_WIDTH,
            50
        ):

            pygame.draw.line(
                screen,
                GRID,
                (x, 0),
                (x, WORLD_HEIGHT)
            )

        for y in range(
            0,
            WORLD_HEIGHT,
            50
        ):

            pygame.draw.line(
                screen,
                GRID,
                (0, y),
                (WORLD_WIDTH, y)
            )

    # ========================================================
    # DRAW SIDEBAR
    # ========================================================

    def draw_sidebar(self):

        self.field_rects.clear()

        pygame.draw.rect(
            screen,
            (35, 35, 40),
            (
                WORLD_WIDTH,
                0,
                SIDEBAR_WIDTH,
                SCREEN_HEIGHT
            )
        )

        title = BIG_FONT.render(
            "LEVEL EDITOR",
            True,
            WHITE
        )

        screen.blit(
            title,
            (
                WORLD_WIDTH + 15,
                5
            )
        )

        # ----------------------------------------------------
        # FILE TO EDIT
        # ----------------------------------------------------

        file_label = SMALL_FONT.render(
            "File",
            True,
            WHITE
        )

        screen.blit(
            file_label,
            (
                WORLD_WIDTH + 15,
                43
            )
        )

        # File name field
        self.file_field_rect = pygame.Rect(
            WORLD_WIDTH + 85,
            40,
            SIDEBAR_WIDTH - 100,
            25
        )

        file_color = (
            (90, 90, 110)
            if self.active_field == "level_file"
            else (70, 70, 80)
        )

        pygame.draw.rect(
            screen,
            file_color,
            self.file_field_rect
        )

        pygame.draw.rect(
            screen,
            GRAY,
            self.file_field_rect,
            1
        )

        if self.active_field == "level_file":

            display_file = self.field_values.get(
                "level_file",
                self.get_file_name()
            )

        else:

            display_file = self.get_file_name()

        file_text = SMALL_FONT.render(
            display_file,
            True,
            WHITE
        )

        screen.blit(
            file_text,
            (
                self.file_field_rect.x + 5,
                self.file_field_rect.y + 4
            )
        )

        # ----------------------------------------------------
        # Add buttons
        # ----------------------------------------------------

        for rect, object_type in self.buttons:


            color = (
                BLUE
                if object_type == self.new_object_type
                else DARK_GRAY
            )

            pygame.draw.rect(
                screen,
                color,
                rect
            )

            text = SMALL_FONT.render(
                "+ " + object_type,
                True,
                WHITE
            )

            screen.blit(
                text,
                (
                    rect.x + 8,
                    rect.y + 7
                )
            )

        # ----------------------------------------------------
        # Properties
        # ----------------------------------------------------

        property_y = 365


        pygame.draw.line(
            screen,
            GRAY,
            (
                WORLD_WIDTH + 10,
                property_y
            ),
            (
                SCREEN_WIDTH - 10,
                property_y
            )
        )

        property_y += 15

        prop_title = BIG_FONT.render(
            "PROPERTIES",
            True,
            WHITE
        )

        screen.blit(
            prop_title,
            (
                WORLD_WIDTH + 15,
                property_y
            )
        )

        property_y += 40

        if not self.selected:

            text = SMALL_FONT.render(
                "Click an object",
                True,
                GRAY
            )

            screen.blit(
                text,
                (
                    WORLD_WIDTH + 15,
                    property_y
                )
            )

            return

        obj = self.selected

        # ----------------------------------------------------
        # Fields
        # ----------------------------------------------------

        fields = [
            ("type", obj.type),
            ("x", self.clean(obj.x)),
            ("y", self.clean(obj.y)),
            ("width", self.clean(obj.width)),
            ("height", self.clean(obj.height)),
            ("name", obj.name or "")
        ]

        for field_name, value in fields:

            property_y = self.draw_field(
                field_name,
                value,
                property_y
            )

        # ----------------------------------------------------
        # Extra properties
        # ----------------------------------------------------

        if obj.type == "lever":

            property_y = self.draw_field(
                "direction",
                obj.extra.get(
                    "direction",
                    "left"
                ),
                property_y
            )

        elif obj.type == "door":

            property_y = self.draw_field(
                "trigger",
                obj.extra.get(
                    "trigger",
                    ""
                ),
                property_y
            )

        elif obj.type == "codepanel":

            property_y = self.draw_field(
                "code",
                obj.extra.get(
                    "code",
                    "1234"
                ),
                property_y
            )

        elif obj.type == "scoringbutton":

            property_y = self.draw_field(
                "power",
                str(
                    obj.extra.get(
                        "required_power",
                        0
                    )
                ),
                property_y
            )

        elif obj.type == "enemy":

            property_y = self.draw_field(
                "spritesheet",
                obj.extra.get(
                    "spritesheet"
                ) or "",
                property_y
            )

    # ========================================================
    # DRAW FIELD
    # ========================================================

    def draw_field(
            self,
            name,
            value,
            y
    ):

        label = SMALL_FONT.render(
            name,
            True,
            WHITE
        )

        screen.blit(
            label,
            (
                WORLD_WIDTH + 15,
                y
            )
        )

        rect = pygame.Rect(
            WORLD_WIDTH + 85,
            y - 3,
            SIDEBAR_WIDTH - 100,
            25
        )

        color = (
            (70, 70, 80)
            if self.active_field != name
            else (90, 90, 110)
        )

        pygame.draw.rect(
            screen,
            color,
            rect
        )

        pygame.draw.rect(
            screen,
            GRAY,
            rect,
            1
        )

        # ----------------------------------------------------
        # Show text currently being edited
        # ----------------------------------------------------

        if self.active_field == name:

            display_value = self.field_values.get(
                name,
                str(value)
            )

        else:

            display_value = str(value)

        text = SMALL_FONT.render(
            display_value,
            True,
            WHITE
        )

        screen.blit(
            text,
            (
                rect.x + 5,
                rect.y + 4
            )
        )

        self.field_rects[name] = rect

        return y + 32

    # ========================================================
    # FIELD CLICK
    # ========================================================

    def click_field(self, mouse_pos):

        # ----------------------------------------------------
        # FILE FIELD
        # ----------------------------------------------------

        if self.file_field_rect.collidepoint(mouse_pos):

            # Apply currently edited field first
            if self.active_field:
                self.apply_field()

            self.active_field = "level_file"

            self.field_values["level_file"] = (
                self.get_file_name()
            )

            self.replace_field = True

            return

        # ----------------------------------------------------
        # OBJECT PROPERTIES
        # ----------------------------------------------------

        if not self.selected:
            return

        # Szukamy pola klikniętego myszką
        for name, rect in self.field_rects.items():

            if rect.collidepoint(mouse_pos):

                # TYPE jest tylko informacyjne
                if name == "type":
                    self.active_field = None
                    return

                # Jeśli klikamy inne pole podczas edycji,
                # zastosuj poprzednie pole
                if (
                        self.active_field
                        and self.active_field != name
                ):
                    self.apply_field()

                # Ustaw nowe aktywne pole
                # Ustaw nowe aktywne pole
                self.active_field = name

                # Pobierz aktualną wartość
                current_value = self.get_field_value(name)

                # Załaduj ją do bufora
                self.field_values[name] = current_value

                # Pierwszy wpisany znak zastąpi starą wartość
                self.replace_field = True

                return

        # Kliknięto poza polami
        if self.active_field:
            self.apply_field()

        self.active_field = None

    # ========================================================
    # EDIT FIELD
    # ========================================================

    def handle_text_input(self, event):

        if not self.active_field:
            return

        # File name can be edited without selecting an object
        if self.active_field == "level_file":

            field = self.active_field

            if field not in self.field_values:
                self.field_values[field] = self.get_file_name()

            # ENTER = load file
            if event.key == pygame.K_RETURN:
                value = self.field_values.get(
                    field,
                    ""
                )

                self.set_file_name(value)

                self.active_field = None
                self.field_values.pop(field, None)
                self.replace_field = False

                return

            # ESC = cancel
            if event.key == pygame.K_ESCAPE:
                self.active_field = None
                self.field_values.pop(field, None)
                self.replace_field = False

                return

            # BACKSPACE
            if event.key == pygame.K_BACKSPACE:
                current = self.field_values.get(
                    field,
                    ""
                )

                self.field_values[field] = current[:-1]

                self.replace_field = False

                return

            # Normal text
            if not event.unicode.isprintable():
                return

            current = self.field_values.get(
                field,
                ""
            )

            if self.replace_field:
                current = ""
                self.replace_field = False

            self.field_values[field] = (
                    current + event.unicode
            )

            return

        # ----------------------------------------------------
        # NORMAL OBJECT FIELD
        # ----------------------------------------------------

        if not self.selected:
            return

        field = self.active_field

        if field not in self.field_values:
            self.field_values[field] = self.get_field_value(field)

        # ----------------------------------------------------
        # ENTER
        # ----------------------------------------------------

        if event.key == pygame.K_RETURN:
            self.apply_field()

            self.active_field = None
            self.replace_field = False

            return

        # ----------------------------------------------------
        # ESC
        # ----------------------------------------------------

        if event.key == pygame.K_ESCAPE:
            self.active_field = None
            self.field_values.pop(field, None)
            self.replace_field = False

            return

        # ----------------------------------------------------
        # BACKSPACE
        # ----------------------------------------------------

        if event.key == pygame.K_BACKSPACE:
            current = self.field_values.get(
                field,
                ""
            )

            self.field_values[field] = current[:-1]

            self.replace_field = False

            return

        # ----------------------------------------------------
        # NORMAL TEXT
        # ----------------------------------------------------

        if not event.unicode.isprintable():
            return

        current = self.field_values.get(
            field,
            ""
        )

        # Pierwszy znak po kliknięciu
        # zastępuje starą wartość
        if self.replace_field:
            current = ""
            self.replace_field = False

        # ----------------------------------------------------
        # NUMERIC FIELDS
        # ----------------------------------------------------

        if field in (
                "x",
                "y",
                "width",
                "height",
                "power"
        ):

            if event.unicode.isdigit():

                self.field_values[field] = (
                        current + event.unicode
                )

            elif (
                    field != "power"
                    and event.unicode == "."
                    and "." not in current
            ):

                self.field_values[field] = (
                        current + event.unicode
                )

        # ----------------------------------------------------
        # TEXT FIELDS
        # ----------------------------------------------------

        else:

            self.field_values[field] = (
                    current + event.unicode
            )
    # ========================================================
    # FILE NAME
    # ========================================================

    def get_file_name(self):

        return os.path.basename(self.level_path)

    def set_file_name(self, value):

        value = value.strip()

        if not value:
            return

        # Add .txt automatically
        if not value.lower().endswith(".txt"):
            value += ".txt"

        # Prevent paths from escaping the levels directory
        value = os.path.basename(value)

        self.level_name = os.path.splitext(value)[0]

        self.level_path = os.path.join(
            LEVELS_DIR,
            value
        )

        self.load_level(
            self.level_path
        )

        self.show_message(
            f"EDITING: {value}"
        )

    # ========================================================
    # GET FIELD
    # ========================================================

    def get_field_value(self, field):

        obj = self.selected

        if field == "x":
            return self.clean(obj.x)

        if field == "y":
            return self.clean(obj.y)

        if field == "width":
            return self.clean(obj.width)

        if field == "height":
            return self.clean(obj.height)

        if field == "name":
            return obj.name or ""

        if field == "direction":
            return obj.extra.get(
                "direction",
                "left"
            )

        if field == "trigger":
            return obj.extra.get(
                "trigger",
                ""
            )

        if field == "code":
            return obj.extra.get(
                "code",
                "1234"
            )

        if field == "power":
            return str(
                obj.extra.get(
                    "required_power",
                    0
                )
            )

        if field == "spritesheet":
            return obj.extra.get(
                "spritesheet"
            ) or ""

        return ""

    # ========================================================
    # SET FIELD
    # ========================================================

    def set_field_value(
        self,
        field,
        value
    ):

        obj = self.selected

        if field == "x":

            try:
                obj.x = float(value)
            except ValueError:
                pass

        elif field == "y":

            try:
                obj.y = float(value)
            except ValueError:
                pass

        elif field == "width":

            try:
                obj.width = max(
                    0,
                    float(value)
                )
            except ValueError:
                pass

        elif field == "height":

            try:
                obj.height = max(
                    0,
                    float(value)
                )
            except ValueError:
                pass

        elif field == "name":

            obj.name = value

        elif field == "direction":

            obj.extra["direction"] = value

        elif field == "trigger":

            obj.extra["trigger"] = value

        elif field == "code":

            obj.extra["code"] = value

        elif field == "power":

            try:
                obj.extra[
                    "required_power"
                ] = int(value)
            except ValueError:
                pass

        elif field == "spritesheet":

            obj.extra[
                "spritesheet"
            ] = value if value else None

    # ========================================================
    # APPLY FIELD
    # ========================================================

    def apply_field(self):

        if not self.active_field:
            return

        # ----------------------------------------------------
        # FILE FIELD
        # ----------------------------------------------------

        if self.active_field == "level_file":

            value = self.field_values.get(
                "level_file",
                ""
            )

            if value:
                self.set_file_name(value)

            return

        # ----------------------------------------------------
        # OBJECT FIELD
        # ----------------------------------------------------

        if not self.selected:
            return

        field = self.active_field

        value = self.field_values.get(
            field,
            ""
        )

        # ----------------------------------------------------
        # Empty numeric fields
        # ----------------------------------------------------

        if field in ("x", "y", "width", "height", "power"):

            if value == "":
                return

        # Apply
        self.set_field_value(
            field,
            value
        )

        # Keep the buffer synchronized
        self.field_values[field] = (
            self.get_field_value(field)
        )

    # ========================================================
    # UPDATE DRAG
    # ========================================================

    def update_drag(self, mouse_pos):

        if not self.selected:
            return

        if not self.dragging:
            return

        self.selected.x = (
            mouse_pos[0]
            - self.drag_offset_x
        )

        self.selected.y = (
            mouse_pos[1]
            - self.drag_offset_y
        )

        # Keep inside world

        self.selected.x = max(
            0,
            min(
                WORLD_WIDTH - self.selected.width,
                self.selected.x
            )
        )

        self.selected.y = max(
            0,
            min(
                WORLD_HEIGHT - self.selected.height,
                self.selected.y
            )
        )

    # ========================================================
    # MOUSE DOWN
    # ========================================================

    def mouse_down(self, pos):

        # ----------------------------------------------------
        # Sidebar
        # ----------------------------------------------------

        if pos[0] >= WORLD_WIDTH:

            # Object buttons

            for rect, object_type in self.buttons:

                if rect.collidepoint(pos):

                    self.add_object(
                        object_type
                    )

                    return

            # Properties

            self.click_field(pos)

            return

        # ----------------------------------------------------
        # World
        # ----------------------------------------------------

        obj = self.select_object(pos)

        if obj:

            self.dragging = True

            self.drag_offset_x = (
                pos[0] - obj.x
            )

            self.drag_offset_y = (
                pos[1] - obj.y
            )

    # ========================================================
    # MOUSE UP
    # ========================================================

    def mouse_up(self):

        self.dragging = False

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):

        if self.message_timer > 0:

            self.message_timer -= dt

            if self.message_timer <= 0:
                self.message = ""

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self):

        screen.fill(
            BG
        )

        # World

        pygame.draw.rect(
            screen,
            (20, 20, 25),
            (
                0,
                0,
                WORLD_WIDTH,
                WORLD_HEIGHT
            )
        )

        self.draw_grid()

        # Objects

        for obj in self.objects:

            obj.draw(screen)

        # Border

        pygame.draw.rect(
            screen,
            WHITE,
            (
                0,
                0,
                WORLD_WIDTH,
                WORLD_HEIGHT
            ),
            2
        )

        # Sidebar

        self.draw_sidebar()

        # Message

        if self.message:

            text = BIG_FONT.render(
                self.message,
                True,
                GREEN
            )

            screen.blit(
                text,
                (
                    10,
                    WORLD_HEIGHT - 35
                )
            )

        # Controls

        controls = SMALL_FONT.render(
            "LMB drag | DEL delete | S save | L load | ESC quit",
            True,
            GRAY
        )

        screen.blit(
            controls,
            (
                10,
                WORLD_HEIGHT + 5
            )
        )


# ============================================================
# MAIN
# ============================================================

editor = LevelEditor()

running = True

while running:

    dt = clock.tick(60) / 1000.0

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():

        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if event.type == pygame.QUIT:

            running = False

        # ----------------------------------------------------
        # KEYBOARD
        # ----------------------------------------------------

        elif event.type == pygame.KEYDOWN:

            # Text field active?

            if editor.active_field:

                editor.handle_text_input(
                    event
                )

                continue

            # Delete

            if event.key == pygame.K_DELETE:

                editor.delete_selected()

            # Save

            elif event.key == pygame.K_s:

                editor.save_level()

            # New level


            elif event.key == pygame.K_n:

                editor.new_level()

            # Load


            elif event.key == pygame.K_l:

                editor.load_level(

                editor.level_path

            )

            # Escape

            elif event.key == pygame.K_ESCAPE:

                running = False

        # ----------------------------------------------------
        # MOUSE
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                editor.mouse_down(
                    event.pos
                )

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                editor.mouse_up()

    # --------------------------------------------------------
    # Drag
    # --------------------------------------------------------

    editor.update_drag(
        mouse_pos
    )

    editor.update(
        dt
    )

    editor.draw()

    pygame.display.flip()


pygame.quit()
sys.exit()
