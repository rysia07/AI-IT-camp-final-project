import pygame

from Interactive import ScoringButton


class GameUpdate:

    def __init__(
        self,
        game
    ):

        self.game = game

    # =====================================================
    # GET RECT
    # =====================================================

    @staticmethod
    def get_rect(
        obj
    ):

        if hasattr(
            obj,
            "rect"
        ):

            return obj.rect

        return obj

    # =====================================================
    # GHOST COLLISIONS
    # =====================================================

    def move_ghost_with_collisions(
        self,
        ghost,
        dx,
        dy,
        obstacles
    ):

        if dx >= 25:
            dx = 25
        if dy >= 25:
            dy = 25

        if dx <= -25:
            dx = -25
        if dy <= -25:
            dy = -25

        ghost_rect = (
            ghost.rect.copy()
        )

        # -------------------------------------------------
        # X
        # -------------------------------------------------

        ghost_rect.x += int(dx)

        for obstacle in obstacles:

            obstacle_rect = (
                self.get_rect(
                    obstacle
                )
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

        # -------------------------------------------------
        # Y
        # -------------------------------------------------

        ghost_rect.y += int(dy)

        for obstacle in obstacles:

            obstacle_rect = (
                self.get_rect(
                    obstacle
                )
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

        # -------------------------------------------------
        # SCREEN BOUNDS
        # -------------------------------------------------

        ghost_rect.clamp_ip(
            pygame.Rect(
                0,
                0,
                self.game.width,
                self.game.height
            )
        )

        # -------------------------------------------------
        # SYNCHRONIZACJA
        # -------------------------------------------------

        ghost.rect = (
            ghost_rect
        )

        ghost.pos.x = float(
            ghost_rect.centerx
        )

        ghost.pos.y = float(
            ghost_rect.centery
        )

    # =====================================================
    # OBSTACLES
    # =====================================================

    def get_obstacles(
        self
    ):

        game = self.game

        # =================================================
        # PLATFORMY + ŚCIANY
        # =================================================

        if hasattr(
            game.platform_mgr,
            "get_obstacles"
        ):

            obstacles = (
                game.platform_mgr
                .get_obstacles()
                .copy()
            )

        else:

            obstacles = (
                game.platform_mgr
                .platforms
                .copy()
            )

        # =================================================
        # INTERACTIVE SOLID
        # =================================================

        interactive_objs = (
            game.interactive_mgr.objects
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
                    ScoringButton
                )
            )
        ]

        obstacles.extend(
            solid_interactive
        )

        return obstacles

    # =====================================================
    # PLAYER
    # =====================================================

    def update_player(
        self,
        dt,
        obstacles
    ):

        game = self.game

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

        game.player.move(
            move_x
        )

        game.char_mgr.update_all(
            dt,
            platforms=obstacles
        )

        # -------------------------------------------------
        # SCREEN CLAMP
        # -------------------------------------------------

        game.player.rect.clamp_ip(
            pygame.Rect(
                0,
                0,
                game.width,
                game.height
            )
        )

        game.player.pos.x = float(
            game.player.rect.centerx
        )

        game.player.pos.y = float(
            game.player.rect.centery
        )

    # =====================================================
    # PLAYER OUT OF BOUNDS
    # =====================================================

    def check_player_out_of_bounds(
        self
    ):

        game = self.game

        if (
            game.player.rect.bottom
            >= game.height
        ):

            game.player.hp = 0

    # =====================================================
    # GHOST
    # =====================================================

    def update_ghost(
        self,
        obstacles
    ):

        game = self.game

        game.ghost.last_pos = (
            game.ghost.pos.copy()
        )

        if (
            game.mouse_dx != 0
            or game.mouse_dy != 0
        ):

            self.move_ghost_with_collisions(
                game.ghost,
                game.mouse_dx,
                game.mouse_dy,
                obstacles
            )

        else:

            game.ghost.update_rect()

        game.ghost.update(
            game.clock.get_time()
            / 1000.0
        )

    # =====================================================
    # ENEMIES
    # =====================================================

    def update_enemies(
        self,
        dt
    ):

        game = self.game

        # =================================================
        # PLATFORMY + ŚCIANY
        # =================================================

        obstacles = (
            game.platform_mgr
            .get_obstacles()
        )

        # =================================================
        # ENEMIES
        # =================================================

        for enemy in game.level.enemies:

            enemy.update(
                dt,
                player_pos=game.player.pos,
                platforms=obstacles
            )

            # -------------------------------------------------
            # SHOOT
            # -------------------------------------------------

            if (
                getattr(
                    enemy,
                    "shoot_cooldown",
                    0
                )
                <= 0
            ):

                if hasattr(
                    enemy,
                    "shoot"
                ):

                    projectile = enemy.shoot(
                        game.player.pos.x,
                        game.player.pos.y
                    )

                    if projectile:

                        game.projectile_mgr.add(
                            projectile
                        )

    # =====================================================
    # PROJECTILES
    # =====================================================
    def update_projectiles(
            self,
            dt
    ):

        game = self.game

        # =================================================
        # AKTUALIZACJA POCISKÓW + ŚCIANY
        # =================================================

        game.projectile_mgr.update(
            dt,
            game.platform_mgr.platforms
        )

        # =================================================
        # TRAFIENIA
        # =================================================

        for projectile in (
                game.projectile_mgr.get_projectiles()
        ):

            # -------------------------------------------------
            # POCISK WROGA -> GRACZ
            # -------------------------------------------------

            if projectile.owner == "enemy":

                if (
                        game.player is not None
                        and game.player.rect.colliderect(
                    projectile.rect
                )
                ):
                    game.player.hp -= getattr(
                        projectile,
                        "damage",
                        10
                    )

                    projectile.is_dead = True

                    print(
                        "💥 Pocisk wroga trafił gracza! "
                        f"HP: {game.player.hp}"
                    )

            # -------------------------------------------------
            # POCISK GRACZA -> WRÓG
            # -------------------------------------------------

            elif projectile.owner == "player":

                for enemy in game.char_mgr.characters.values():

                    # Tylko ShootingEnemy / obiekty
                    # posiadające take_damage
                    if not hasattr(
                            enemy,
                            "take_damage"
                    ):
                        continue

                    if not hasattr(
                            enemy,
                            "is_alive"
                    ):
                        continue

                    if not enemy.is_alive():
                        continue

                    if enemy.rect.colliderect(
                            projectile.rect
                    ):
                        enemy.take_damage(
                            getattr(
                                projectile,
                                "damage",
                                10
                            )
                        )

                        projectile.is_dead = True

                        print(
                            "💥 Pocisk gracza trafił wroga! "
                            f"HP wroga: {enemy.hp}"
                        )

                        break

    # =====================================================
    # GAMEPLAY UPDATE
    # =====================================================

    def update_game(
        self,
        dt
    ):

        game = self.game

        # =================================================
        # OBSTACLES
        # =================================================

        obstacles = (
            self.get_obstacles()
        )

        # =================================================
        # PLAYER
        # =================================================

        self.update_player(
            dt,
            obstacles
        )

        self.check_player_out_of_bounds()

        # =================================================
        # GHOST
        # =================================================

        self.update_ghost(
            obstacles
        )

        # =================================================
        # ENEMIES
        # =================================================

        self.update_enemies(
            dt
        )

        # =================================================
        # PROJECTILES
        # =================================================

        self.update_projectiles(
            dt
        )

        # =================================================
        # DEATH
        # =================================================

        if game.player.hp <= 0:

            game.stop_game_mouse()

            game.set_state(
                game.FAILURE
            )

            return

        # =================================================
        # INTERACTIVE
        # =================================================

        game.interactive_mgr.update_all(
            game.player,
            game.ghost,
            dt
        )

        # =================================================
        # PLAYER OUTSIDE LEVEL
        # =================================================

        if (
            game.player.pos.y
            > game.height

            or game.player.rect.top
            > game.height
        ):

            print(
                "⚠️ GRACZ SPADŁ:",
                game.player.pos,
                game.player.rect
            )

            game.player.hp = 0

            game.stop_game_mouse()

            game.set_state(
                game.FAILURE
            )

            return

        # =================================================
        # LEVEL GATE
        # =================================================

        self.check_level_gate()

    # =====================================================
    # LEVEL GATE
    # =====================================================

    def check_level_gate(
        self
    ):

        game = self.game

        for obj in game.interactive_mgr:

            if not getattr(
                obj,
                "triggered",
                False
            ):

                continue

            # =================================================
            # CURRENT LEVEL INDEX
            # =================================================

            try:

                current_index = (
                    game.available_levels.index(
                        game.current_level_file
                    )
                )

            except ValueError:

                current_index = -1

            # =================================================
            # NEXT LEVEL
            # =================================================

            if (
                current_index >= 0

                and current_index + 1
                < len(game.available_levels)
            ):

                next_level = (
                    game.available_levels[
                        current_index + 1
                    ]
                )

                print(
                    f"➡️ Przejście: "
                    f"{game.current_level_file} "
                    f"-> "
                    f"{next_level}"
                )

                game.current_level_file = (
                    next_level
                )

                game.load_selected_level(
                    game.current_level_file
                )

                obj.triggered = False

                game.start_game_mouse()

                game.set_state(
                    game.PLAYING
                )

            # =================================================
            # KONIEC GRY
            # =================================================

            else:

                print(
                    "🏆 Ukończono "
                    "wszystkie poziomy!"
                )

                game.stop_game_mouse()

                obj.triggered = False

                game.set_state(
                    game.VICTORY
                )

            break

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt
    ):

        game = self.game

        if (
            game.current_state
            == game.MENU
        ):

            game.main_menu.update()

        elif (
            game.current_state
            == game.LEVEL_SELECT
        ):

            game.level_select_menu.update()

        elif (
            game.current_state
            == game.PAUSE
        ):

            game.pause_menu.update()

        elif (
            game.current_state
            == game.OPTIONS
        ):

            game.options_menu.update()

        elif (
            game.current_state
            == game.CREDITS
        ):

            game.credits_menu.update()

        elif (
            game.current_state
            == game.FAILURE
        ):

            game.failure_menu.update()

        elif (
            game.current_state
            == game.VICTORY
        ):

            game.victory_menu.update()

        elif (
            game.current_state
            == game.PLAYING
        ):

            self.update_game(
                dt
            )
