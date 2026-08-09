
import sys

import pygame

from LoadLevels import load_level
from Platforms import PlatformManager

from Characters import (
    Creature,
    GhostMouse,
    CharacterManager,
    ProjectileManager
)

from Interactive import CodePanel

from GUI import (
    MainMenu,
    LevelSelectMenu,
    OptionsMenu,
    CreditsMenu,
    FailureMenu,
    VictoryMenu
)

from pause_menu import PauseMenu


# =========================================================
# KONFIGURACJA
# =========================================================

FPS = 60

WIDTH = 900
HEIGHT = 600

player = Creature(
    450,
    300,
    speed=400,
    jump_force=-700,
    spritesheet_path="../pictures/ludzik.png"
)

# =========================================================
# STANY GRY
# =========================================================

MENU = 0
PLAYING = 1
OPTIONS = 2
CREDITS = 3
FAILURE = 4
VICTORY = 5
PAUSE = 6
LEVEL_SELECT = 7


# =========================================================
# PLAYER
# =========================================================
def create_player(start_pos):

    player = Creature(
        start_pos[0],
        start_pos[1],
        speed=400,
        jump_force=-700,
        spritesheet_path="../pictures/ludzik.png"
    )

    try:

        player.add_anim(
            "idle",
            [0],
            3,
            3,
            speed=100,
            priority=Creature.PRIORITY_IDLE,
            spritesheet_path="../pictures/ludzik.png",
            scale=2.0
        )

        player.add_anim(
            "walk",
            [0, 1, 2, 3, 4, 5],
            3,
            3,
            speed=150,
            priority=Creature.PRIORITY_WALK,
            spritesheet_path="../pictures/ludzik.png",
            scale=2.0
        )

        player.add_anim(
            "attack",
            list(range(19)),
            5,
            4,
            speed=35,
            loop=False,
            priority=Creature.PRIORITY_ATTACK,
            spritesheet_path="../pictures/Gracz_atak.png",
            scale=0.5
        )

    except Exception as error:

        print(
            "⚠️ Uwaga podczas ładowania "
            f"animacji gracza: {error}"
        )

    player.set_walk_idle(
        "walk",
        "idle"
    )

    player.play(
        "idle"
    )

    return player


# =========================================================
# RESET
# =========================================================

def reset_game(
    player,
    ghost,
    spawn_pos
):

    player.pos.update(
        spawn_pos[0],
        spawn_pos[1]
    )

    player.update_rect()

    player.hp = 100

    player.vel_x = 0
    player.vel_y = 0

    player.is_grounded = False

    player.jumps_left = (
        player.max_jumps
    )

    ghost.pos.update(
        spawn_pos[0],
        spawn_pos[1]
    )

    ghost.update_rect()

    ghost.last_pos = (
        ghost.pos.copy()
    )

    ghost.hp = 50


# =========================================================
# GHOST COLLISIONS
# =========================================================

def get_rect(obj):

    if hasattr(obj, "rect"):

        return obj.rect

    return obj


def move_ghost_with_collisions(
    ghost,
    dx,
    dy,
    obstacles
):

    """
    Poruszanie ducha myszką.

    POS ducha = środek hitboxa.

    last_pos musi zostać ustawione przed
    wywołaniem tej funkcji.
    """

    ghost_rect = (
        ghost.rect.copy()
    )

    # =====================================================
    # RUCH X
    # =====================================================

    ghost_rect.x += int(dx)

    for obstacle in obstacles:

        obstacle_rect = get_rect(
            obstacle
        )

        if not ghost_rect.colliderect(
            obstacle_rect
        ):

            continue

        if dx > 0:

            ghost_rect.right = (
                obstacle_rect.left
            )

        elif dx < 0:

            ghost_rect.left = (
                obstacle_rect.right
            )

    # =====================================================
    # RUCH Y
    # =====================================================

    ghost_rect.y += int(dy)

    for obstacle in obstacles:

        obstacle_rect = get_rect(
            obstacle
        )

        if not ghost_rect.colliderect(
            obstacle_rect
        ):

            continue

        if dy > 0:

            ghost_rect.bottom = (
                obstacle_rect.top
            )

        elif dy < 0:

            ghost_rect.top = (
                obstacle_rect.bottom
            )

    # =====================================================
    # SYNCHRONIZACJA
    # =====================================================

    ghost.rect = ghost_rect

    ghost.pos.x = (
        float(ghost_rect.centerx)
    )

    ghost.pos.y = (
        float(ghost_rect.centery)
    )


# =========================================================
# LOAD LEVEL
# =========================================================

def load_selected_level(
    level_filename
):

    try:

        level = load_level(
            f"../levels/{level_filename}"
        )

    except FileNotFoundError:

        level = load_level(
            level_filename
        )

    interactive_mgr = (
        level.interactive_manager
    )

    platform_mgr = PlatformManager(
        "../pictures/platforma.png",
        level.platforms
    )

    projectile_mgr = (
        ProjectileManager()
    )

    player = create_player(
        level.player_pos
    )

    ghost = GhostMouse(
        level.player_pos[0],
        level.player_pos[1]
    )

    ghost.update_rect()

    ghost.last_pos = (
        ghost.pos.copy()
    )

    char_mgr = CharacterManager()

    char_mgr.add(
        "player",
        player
    )

    char_mgr.add(
        "ghost",
        ghost
    )

    return (
        level,
        interactive_mgr,
        platform_mgr,
        projectile_mgr,
        player,
        ghost,
        char_mgr
    )


# =========================================================
# MAIN
# =========================================================

def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    pygame.display.set_caption(
        "Alien Space"
    )

    clock = pygame.time.Clock()

    # =====================================================
    # LEVEL
    # =====================================================

    current_level_file = (
        "level1.txt"
    )

    (
        level,
        interactive_mgr,
        platform_mgr,
        projectile_mgr,
        player,
        ghost,
        char_mgr
    ) = load_selected_level(
        current_level_file
    )

    # =====================================================
    # MENUS
    # =====================================================

    available_levels = [
        "level1.txt",
        "level2.txt"
    ]

    main_menu = MainMenu(
        WIDTH,
        HEIGHT
    )

    level_select_menu = LevelSelectMenu(
        WIDTH,
        HEIGHT,
        available_levels
    )

    options_menu = OptionsMenu(
        WIDTH,
        HEIGHT
    )

    credits_menu = CreditsMenu(
        WIDTH,
        HEIGHT
    )

    failure_menu = FailureMenu(
        WIDTH,
        HEIGHT
    )

    victory_menu = VictoryMenu(
        WIDTH,
        HEIGHT
    )

    pause_menu = PauseMenu(
        WIDTH,
        HEIGHT
    )

    # =====================================================
    # GAME STATE
    # =====================================================

    current_state = MENU

    previous_state = MENU

    running = True

    pygame.mouse.get_rel()

    # =====================================================
    # GAME LOOP
    # =====================================================

    while running:

        dt = (
            clock.tick(FPS)
            / 1000.0
        )

        mouse_dx = 0
        mouse_dy = 0

        # =================================================
        # INPUT
        # =================================================

        for event in pygame.event.get():

            # -------------------------------------------------
            # QUIT
            # -------------------------------------------------

            if event.type == pygame.QUIT:

                running = False

            # -------------------------------------------------
            # OPTIONS
            # -------------------------------------------------

            if current_state == OPTIONS:

                if hasattr(
                    options_menu,
                    "handle_event"
                ):

                    options_menu.handle_event(
                        event
                    )

            # -------------------------------------------------
            # KEYBOARD
            # -------------------------------------------------

            if event.type == pygame.KEYDOWN:

                # ESC
                if event.key == pygame.K_ESCAPE:

                    if current_state == PLAYING:

                        current_state = PAUSE

                        pause_menu.active = True

                        pygame.mouse.set_visible(
                            True
                        )

                        pygame.event.set_grab(
                            False
                        )

                    elif current_state == PAUSE:

                        current_state = PLAYING

                        pause_menu.active = False

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

                        pygame.mouse.get_rel()

                # Gameplay keys
                if current_state == PLAYING:

                    # Jump
                    if event.key in (
                        pygame.K_w,
                        pygame.K_UP,
                        pygame.K_SPACE
                    ):

                        player.jump()

                    # Attack
                    if (
                        event.key == pygame.K_2
                        and hasattr(
                            player,
                            "play"
                        )
                    ):

                        player.play(
                            "attack"
                        )

            # -------------------------------------------------
            # MOUSE MOTION
            # -------------------------------------------------

            elif event.type == pygame.MOUSEMOTION:

                if current_state == PLAYING:

                    dx, dy = event.rel

                    mouse_dx += dx
                    mouse_dy += dy

            # -------------------------------------------------
            # LEFT CLICK
            # -------------------------------------------------

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if current_state == PLAYING:

                    interactive_mgr.handle_event_all(
                        event
                    )

                elif current_state == MENU:

                    action = (
                        main_menu.handle_click(
                            event.pos,
                            (1, 0, 0)
                        )
                    )

                    if action == "level_select":

                        previous_state = MENU

                        current_state = (
                            LEVEL_SELECT
                        )

                    elif action == "options":

                        previous_state = MENU

                        current_state = (
                            OPTIONS
                        )

                    elif action == "credits":

                        current_state = CREDITS

                    elif action == "quit":

                        running = False

                elif current_state == LEVEL_SELECT:

                    action = (
                        level_select_menu.handle_input(
                            event.pos,
                            (1, 0, 0)
                        )
                    )

                    if action == "back":

                        current_state = (
                            previous_state
                        )

                    elif (
                        action
                        and action.startswith("load_")
                    ):

                        level_file = (
                            action.replace(
                                "load_",
                                ""
                            )
                        )

                        current_level_file = (
                            level_file
                        )

                        (
                            level,
                            interactive_mgr,
                            platform_mgr,
                            projectile_mgr,
                            player,
                            ghost,
                            char_mgr
                        ) = load_selected_level(
                            current_level_file
                        )

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

                        pygame.mouse.get_rel()

                        current_state = PLAYING

                elif current_state == PAUSE:

                    action = (
                        pause_menu.handle_input(
                            event.pos,
                            (1, 0, 0)
                        )
                    )

                    if action == "resume":

                        pause_menu.active = False

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

                        pygame.mouse.get_rel()

                        current_state = PLAYING

                    elif action == "level_select":

                        pause_menu.active = False

                        previous_state = PAUSE

                        current_state = (
                            LEVEL_SELECT
                        )

                    elif action == "options":

                        previous_state = PAUSE

                        current_state = OPTIONS

                    elif action == "main_menu":

                        pause_menu.active = False

                        pygame.mouse.set_visible(
                            True
                        )

                        pygame.event.set_grab(
                            False
                        )

                        current_state = MENU

                elif current_state == OPTIONS:

                    action = (
                        options_menu.handle_input(
                            event.pos,
                            (1, 0, 0)
                        )
                    )

                    if action == "back":

                        current_state = (
                            previous_state
                        )

                elif current_state == CREDITS:

                    action = (
                        credits_menu.handle_input(
                            event.pos,
                            (1, 0, 0)
                        )
                    )

                    if action == "back":

                        current_state = MENU

                elif current_state == FAILURE:

                    action = (
                        failure_menu.handle_input(
                            event.pos,
                            (1, 0, 0)
                        )
                    )

                    if action == "retry":

                        (
                            level,
                            interactive_mgr,
                            platform_mgr,
                            projectile_mgr,
                            player,
                            ghost,
                            char_mgr
                        ) = load_selected_level(
                            current_level_file
                        )

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

                        pygame.mouse.get_rel()

                        current_state = PLAYING

                    elif action == "menu":

                        current_state = MENU

                elif current_state == VICTORY:

                    action = (
                        victory_menu.handle_input(
                            event.pos,
                            (1, 0, 0)
                        )
                    )

                    if action == "level_select":

                        previous_state = MENU

                        current_state = (
                            LEVEL_SELECT
                        )

                    elif action == "menu":

                        current_state = MENU

            # -------------------------------------------------
            # INTERACTIVE EVENTS
            # -------------------------------------------------

            if current_state == PLAYING:

                interactive_mgr.handle_event(
                    event
                )

        # =====================================================
        # UPDATE
        # =====================================================

        if current_state == MENU:

            main_menu.update()

        elif current_state == LEVEL_SELECT:

            level_select_menu.update()

        elif current_state == PAUSE:

            pause_menu.update()

        elif current_state == OPTIONS:

            options_menu.update()

        elif current_state == CREDITS:

            credits_menu.update()

        elif current_state == FAILURE:

            failure_menu.update()

        elif current_state == VICTORY:

            victory_menu.update()

        # =====================================================
        # PLAYING
        # =====================================================

        elif current_state == PLAYING:

            # =================================================
            # PLAYER INPUT
            # =================================================

            keys = pygame.key.get_pressed()

            move_x = 0

            if (
                keys[pygame.K_a]
                or keys[pygame.K_LEFT]
            ):

                move_x -= 1

            if (
                keys[pygame.K_d]
                or keys[pygame.K_RIGHT]
            ):

                move_x += 1

            player.move(
                move_x
            )

            # =================================================
            # OBSTACLES
            # =================================================

            interactive_objs = (
                interactive_mgr.objects
            )

            solid_interactive = [

                obj

                for obj in interactive_objs

                if (
                    hasattr(
                        obj,
                        "is_open"
                    )

                    and not obj.is_open

                    and not isinstance(
                        obj,
                        CodePanel
                    )
                )
            ]

            all_obstacles = (
                platform_mgr.platforms
                + solid_interactive
            )

            # =================================================
            # GHOST
            # =================================================

            # WAŻNE:
            # last_pos = pozycja z poprzedniej klatki
            ghost.last_pos = (
                ghost.pos.copy()
            )

            if (
                mouse_dx != 0
                or mouse_dy != 0
            ):

                move_ghost_with_collisions(
                    ghost,
                    mouse_dx,
                    mouse_dy,
                    all_obstacles
                )

            else:

                # Upewnij się, że hitbox
                # nadal jest zsynchronizowany.
                ghost.update_rect()

            # =================================================
            # PLAYER
            # =================================================

            char_mgr.update_all(
                dt,
                platforms=all_obstacles
            )

            # Duch NIE jest aktualizowany przez manager,
            # ale musimy zaktualizować jego sprite.
            ghost.update(
                dt
            )

            # =================================================
            # ENEMIES
            # =================================================

            for enemy in level.enemies:

                enemy.update(
                    dt,
                    player_pos=player.pos,
                    platforms=platform_mgr
                )

                if (
                    getattr(
                        enemy,
                        "shoot_cooldown",
                        0
                    ) <= 0
                ):

                    if hasattr(
                        enemy,
                        "shoot"
                    ):

                        projectile = enemy.shoot(
                            player.pos.x,
                            player.pos.y
                        )

                        if projectile:

                            projectile_mgr.add(
                                projectile
                            )

            # =================================================
            # PROJECTILES
            # =================================================

            projectile_mgr.update(
                dt
            )

            # =================================================
            # PROJECTILE COLLISION
            # =================================================

            for projectile in (
                projectile_mgr.get_projectiles()
            ):

                if player.rect.colliderect(
                    projectile.rect
                ):

                    player.hp -= getattr(
                        projectile,
                        "damage",
                        10
                    )

                    projectile.is_dead = True

                    print(
                        "💥 Trafienie! "
                        f"HP gracza: {player.hp}"
                    )

            # =================================================
            # DEATH
            # =================================================

            if player.hp <= 0:

                pygame.mouse.set_visible(
                    True
                )

                pygame.event.set_grab(
                    False
                )

                current_state = FAILURE

            # =================================================
            # INTERACTIVE OBJECTS
            # =================================================

            interactive_mgr.update_all(
                player,
                ghost,
                dt
            )

            # =================================================
            # LEVEL GATE
            # =================================================

            for obj in interactive_mgr:

                if getattr(
                    obj,
                    "triggered",
                    False
                ):

                    pygame.mouse.set_visible(
                        True
                    )

                    pygame.event.set_grab(
                        False
                    )

                    current_state = VICTORY

                    obj.triggered = False

                    break

        # =====================================================
        # DRAW
        # =====================================================

        screen.fill(
            (30, 30, 40)
        )

        # =====================================================
        # GAME
        # =====================================================

        if current_state in (
            PLAYING,
            PAUSE
        ):

            # Platformy
            platform_mgr.draw(
                screen
            )

            # Interactive
            interactive_mgr.draw_all(
                screen
            )

            # Characters
            char_mgr.draw_all(
                screen
            )

            # Enemies
            for enemy in level.enemies:

                if (
                    hasattr(
                        enemy,
                        "is_alive"
                    )
                    and enemy.is_alive()
                ):

                    enemy.draw(
                        screen
                    )

                elif not hasattr(
                    enemy,
                    "is_alive"
                ):

                    enemy.draw(
                        screen
                    )

            # Projectiles
            projectile_mgr.draw_all(
                screen
            )

            # =================================================
            # HUD
            # =================================================

            font = pygame.font.Font(
                None,
                32
            )

            player_power = getattr(
                player,
                "power",
                0
            )

            hud_text = font.render(
                (
                    f"Player HP: {player.hp} "
                    f"| Ghost HP: {ghost.hp} "
                    f"| Power: {player_power}"
                ),
                True,
                (255, 255, 255)
            )

            screen.blit(
                hud_text,
                (10, 10)
            )

            info = font.render(
                (
                    "A/D = Move, "
                    "W/Space = Jump, "
                    "2 = Attack, "
                    "ESC = Pause"
                ),
                True,
                (200, 200, 200)
            )

            screen.blit(
                info,
                (10, 50)
            )

            if current_state == PAUSE:

                pause_menu.draw(
                    screen
                )

        # =====================================================
        # MENUS
        # =====================================================

        elif current_state == MENU:

            main_menu.draw(
                screen
            )

        elif current_state == LEVEL_SELECT:

            level_select_menu.draw(
                screen
            )

        elif current_state == OPTIONS:

            options_menu.draw(
                screen
            )

        elif current_state == CREDITS:

            credits_menu.draw(
                screen
            )

        elif current_state == FAILURE:

            failure_menu.draw(
                screen
            )

        elif current_state == VICTORY:

            victory_menu.draw(
                screen
            )

        # =====================================================
        # DISPLAY
        # =====================================================

        pygame.display.flip()

    pygame.quit()

    sys.exit()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()
