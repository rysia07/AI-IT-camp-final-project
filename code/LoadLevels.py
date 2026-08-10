
import pygame

from Characters import ShootingEnemy
from Interactive import (
    Lever,
    ScoringButton,
    CodePanel,
    Door,
    LevelGate,
    InteractiveManager
)


class LevelData:

    def __init__(self):
        # Platformy będące obiektami pygame.Rect
        self.platforms = []

        # Wrogowie
        self.enemies = []

        # Pozycja startowa gracza
        self.player_pos = (450, 300)

        # Menedżer obiektów interaktywnych
        self.interactive_manager = InteractiveManager()

        # Nazwane obiekty:
        # np. lever1, door1, panel1
        self.objects = {}


def load_level(filepath):

    level = LevelData()

    # Drzwi mogą wskazywać na obiekt zdefiniowany
    # wcześniej albo później w pliku.
    pending_doors = []

    try:

        with open(filepath, "r", encoding="utf-8") as file:

            for line_number, line in enumerate(file, 1):

                line = line.strip()

                # Puste linie i komentarze
                if not line or line.startswith("#"):
                    continue

                parts = line.replace(",", " ").split()

                if not parts:
                    continue

                object_type = parts[0].lower()

                try:

                    # =================================================
                    # PLAYER
                    #
                    # p x y
                    # =================================================

                    if object_type == "p":

                        if len(parts) < 3:
                            print(
                                f"❌ Line {line_number}: "
                                "'p' requires 'x y'"
                            )
                            continue

                        level.player_pos = (
                            float(parts[1]),
                            float(parts[2])
                        )

                    # =================================================
                    # PLATFORM
                    #
                    # platform x y width height [name]
                    # =================================================

                    elif object_type == "platform":

                        if len(parts) < 5:
                            print(
                                f"❌ Line {line_number}: "
                                "'platform' requires "
                                "'x y width height [name]'"
                            )
                            continue

                        rect = pygame.Rect(
                            int(float(parts[1])),
                            int(float(parts[2])),
                            int(float(parts[3])),
                            int(float(parts[4]))
                        )

                        level.platforms.append(rect)

                        if len(parts) > 5:
                            level.objects[parts[5]] = rect

                    # =================================================
                    # LEVER
                    #
                    # lever x y width height direction [name]
                    # =================================================

                    elif object_type == "lever":

                        if len(parts) < 6:
                            print(
                                f"❌ Line {line_number}: "
                                "'lever' requires "
                                "'x y width height direction [name]'"
                            )
                            continue

                        x = float(parts[1])
                        y = float(parts[2])
                        width = 23
                        height = 21

                        direction = parts[5]

                        name = (
                            parts[6]
                            if len(parts) > 6
                            else None
                        )

                        lever = Lever(
                            float(parts[1]),
                            float(parts[2]),
                            float(parts[3]),
                            float(parts[4]),
                            direction=parts[5].lower()
                        )

                        level.interactive_manager.add(lever)

                        if len(parts) > 6:
                            level.objects[parts[6]] = lever
                            
                    # =================================================
                    # CODE PANEL
                    #
                    # codepanel x y width height code [name]
                    # =================================================

                    elif object_type == "codepanel":

                        if len(parts) < 6:
                            print(
                                f"❌ Line {line_number}: "
                                "'codepanel' requires "
                                "'x y width height code [name]'"
                            )
                            continue

                        panel = CodePanel(
                            float(parts[1]),
                            float(parts[2]),
                            float(parts[3]),
                            float(parts[4]),
                            code=parts[5]
                        )

                        level.interactive_manager.add(
                            panel
                        )

                        if len(parts) > 6:
                            level.objects[
                                parts[6]
                            ] = panel

                    # =================================================
                    # DOOR
                    #
                    # door x y width height trigger_name [name]
                    # =================================================

                    elif object_type == "door":

                        if len(parts) < 6:
                            print(
                                f"❌ Line {line_number}: "
                                "'door' requires "
                                "'x y width height trigger_name [name]'"
                            )
                            continue

                        pending_doors.append({
                            "x": float(parts[1]),
                            "y": float(parts[2]),
                            "width": float(parts[3]),
                            "height": float(parts[4]),
                            "trigger": parts[5],
                            "name": (
                                parts[6]
                                if len(parts) > 6
                                else None
                            ),
                            "line": line_number
                        })

                    # =================================================
                    # SCORING BUTTON
                    #
                    # scoringbutton x y power [name]
                    # =================================================

                    elif object_type == "scoringbutton":

                        if len(parts) < 4:
                            print(
                                f"❌ Line {line_number}: "
                                "'scoringbutton' requires "
                                "'x y required_power [name]'"
                            )
                            continue

                        button = ScoringButton(
                            float(parts[1]),
                            float(parts[2]),
                            required_power=int(parts[3])
                        )

                        level.interactive_manager.add(button)

                        if len(parts) > 4:
                            level.objects[parts[4]] = button

                    # =================================================
                    # LEVEL GATE
                    #
                    # levelgate x y [name]
                    # =================================================

                    elif object_type == "levelgate":

                        if len(parts) < 3:
                            print(
                                f"❌ Line {line_number}: "
                                "'levelgate' requires 'x y [name]'"
                            )
                            continue

                        gate = LevelGate(
                            float(parts[1]),
                            float(parts[2])
                        )

                        level.interactive_manager.add(gate)

                        if len(parts) > 3:
                            level.objects[parts[3]] = gate

                    # =================================================
                    # ENEMY
                    #
                    # enemy x y
                    # enemy x y enemy_1
                    # enemy x y spritesheet.png
                    # enemy x y spritesheet.png enemy_1
                    # =================================================

                    elif object_type in (
                        "enemy",
                        "shootingenemy"
                    ):

                        if len(parts) < 3:
                            print(
                                f"❌ Line {line_number}: "
                                "'enemy' requires "
                                "'x y [spritesheet] [name]'"
                            )
                            continue

                        spritesheet = None
                        enemy_name = None

                        if len(parts) == 4:

                            value = parts[3]

                            if (
                                "." in value
                                or "/" in value
                                or "\\" in value
                            ):
                                spritesheet = value
                            else:
                                enemy_name = value

                        elif len(parts) > 4:

                            spritesheet = parts[3]
                            enemy_name = parts[4]

                        enemy = ShootingEnemy(
                            float(parts[1]),
                            float(parts[2]),
                            spritesheet_path=spritesheet
                        )

                        level.enemies.append(enemy)

                        if enemy_name:
                            level.objects[enemy_name] = enemy

                    # =================================================
                    # NIEZNANY OBIEKT
                    # =================================================

                    else:

                        print(
                            f"⚠️ Line {line_number}: "
                            f"Unknown object '{object_type}'"
                        )

                except (ValueError, IndexError) as error:

                    print(
                        f"❌ Line {line_number}: {line}\n"
                        f"   {error}"
                    )

        # =============================================================
        # ŁĄCZENIE DRZWI Z TRIGGERAMI
        # =============================================================

        for door_data in pending_doors:

            trigger = level.objects.get(
                door_data["trigger"]
            )

            if trigger is None:

                print(
                    f"❌ Door on line "
                    f"{door_data['line']} references "
                    f"unknown object "
                    f"'{door_data['trigger']}'"
                )

                continue

            door = Door(
                door_data["x"],
                door_data["y"],
                door_data["width"],
                door_data["height"],
                trigger_object=trigger
            )

            level.interactive_manager.add(door)

            if door_data["name"]:

                level.objects[
                    door_data["name"]
                ] = door

    except FileNotFoundError:

        print(
            f"❌ Level file not found: {filepath}"
        )

    print(
        f"Level loaded: "
        f"{len(level.platforms)} platforms, "
        f"{len(level.enemies)} enemies, "
        f"{len(level.interactive_manager)} "
        f"interactive objects"
    )

    print(
        f"Player spawn: {level.player_pos}"
    )

    return level
