import pygame

from Interactive import (
    Lever,
    CodePanel,
    ScoringButton,
    Door,
    LevelGate,
    InteractiveManager
)


class LevelData:

    def __init__(self):

        # pygame.Rect objects used for collision
        self.platforms = []

        # Player starting position
        self.player_pos = (450, 300)

        # Interactive objects
        self.interactive_manager = InteractiveManager()

        # Named objects
        self.objects = {}


def load_level(filepath):

    level = LevelData()

    # Doors are loaded after levers because
    # doors can depend on levers.
    pending_doors = []

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            for line_number, line in enumerate(
                file,
                1
            ):

                line = line.strip()

                # Ignore comments and empty lines
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

                        if len(parts) < 3:
                            print(
                                f"Line {line_number}: "
                                f"p needs x y"
                            )
                            continue

                        x = float(parts[1])
                        y = float(parts[2])

                        level.player_pos = (
                            x,
                            y
                        )

                    # =================================================
                    # PLATFORM
                    # =================================================

                    elif object_type == "platform":

                        if len(parts) < 5:
                            print(
                                f"Line {line_number}: "
                                f"platform needs "
                                f"x y width height name"
                            )
                            continue

                        x = int(float(parts[1]))
                        y = int(float(parts[2]))
                        width = int(float(parts[3]))
                        height = int(float(parts[4]))

                        rect = pygame.Rect(
                            x,
                            y,
                            width,
                            height
                        )

                        level.platforms.append(rect)

                    # =================================================
                    # LEVER
                    # =================================================

                    elif object_type == "lever":

                        if len(parts) < 6:
                            print(
                                f"Line {line_number}: "
                                f"lever needs "
                                f"x y width height "
                                f"direction name"
                            )
                            continue

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

                        lever = Lever(
                            x,
                            y,
                            width,
                            height,
                            direction=direction
                        )

                        level.interactive_manager.add(
                            lever
                        )

                        if name:
                            level.objects[name] = lever

                    # =================================================
                    # DOOR
                    # =================================================

                    elif object_type == "door":

                        if len(parts) < 6:
                            print(
                                f"Line {line_number}: "
                                f"door needs "
                                f"x y width height "
                                f"trigger_name"
                            )
                            continue

                        x = float(parts[1])
                        y = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])

                        trigger_name = parts[5]

                        name = (
                            parts[6]
                            if len(parts) > 6
                            else None
                        )

                        pending_doors.append(
                            {
                                "x": x,
                                "y": y,
                                "width": width,
                                "height": height,
                                "trigger": trigger_name,
                                "name": name,
                                "line": line_number
                            }
                        )

                    # =================================================
                    # CODE PANEL
                    # =================================================

                    elif object_type == "codepanel":

                        if len(parts) < 4:
                            print(
                                f"Line {line_number}: "
                                f"codepanel needs "
                                f"x y code"
                            )
                            continue

                        x = float(parts[1])
                        y = float(parts[2])
                        code = parts[3]

                        name = (
                            parts[4]
                            if len(parts) > 4
                            else None
                        )

                        panel = CodePanel(
                            x,
                            y,
                            code=code
                        )

                        level.interactive_manager.add(
                            panel
                        )

                        if name:
                            level.objects[name] = panel

                    # =================================================
                    # SCORING BUTTON
                    # =================================================

                    elif object_type == "scoringbutton":

                        if len(parts) < 4:
                            print(
                                f"Line {line_number}: "
                                f"scoringbutton needs "
                                f"x y required_power"
                            )
                            continue

                        x = float(parts[1])
                        y = float(parts[2])
                        power = int(parts[3])

                        name = (
                            parts[4]
                            if len(parts) > 4
                            else None
                        )

                        button = ScoringButton(
                            x,
                            y,
                            required_power=power
                        )

                        level.interactive_manager.add(
                            button
                        )

                        if name:
                            level.objects[name] = button

                    # =================================================
                    # LEVEL GATE
                    # =================================================

                    elif object_type == "levelgate":

                        if len(parts) < 3:
                            print(
                                f"Line {line_number}: "
                                f"levelgate needs x y"
                            )
                            continue

                        x = float(parts[1])
                        y = float(parts[2])

                        name = (
                            parts[3]
                            if len(parts) > 3
                            else None
                        )

                        gate = LevelGate(
                            x,
                            y
                        )

                        level.interactive_manager.add(
                            gate
                        )

                        if name:
                            level.objects[name] = gate

                    # =================================================
                    # UNKNOWN
                    # =================================================

                    else:

                        print(
                            f"⚠️ Line {line_number}: "
                            f"Unknown object '{object_type}'"
                        )

                except (
                    ValueError,
                    IndexError
                ) as error:

                    print(
                        f"❌ Line {line_number}: "
                        f"{line}"
                    )

                    print(
                        f"   {error}"
                    )

        # =========================================================
        # CONNECT DOORS TO THEIR TRIGGERS
        # =========================================================

        for door_data in pending_doors:

            trigger_name = door_data["trigger"]

            trigger = level.objects.get(
                trigger_name
            )

            if trigger is None:

                print(
                    f"❌ Door on line "
                    f"{door_data['line']} "
                    f"references unknown "
                    f"object '{trigger_name}'"
                )

                continue

            door = Door(
                door_data["x"],
                door_data["y"],
                door_data["width"],
                door_data["height"],
                trigger_object=trigger
            )

            level.interactive_manager.add(
                door
            )

            if door_data["name"]:
                level.objects[
                    door_data["name"]
                ] = door

    except FileNotFoundError:

        print(
            f"❌ Level file not found: "
            f"{filepath}"
        )

    print(
        f"Level loaded: "
        f"{len(level.platforms)} platforms"
    )

    print(
        f"Player spawn: "
        f"{level.player_pos}"
    )

    return level
