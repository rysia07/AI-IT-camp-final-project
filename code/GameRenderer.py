import pygame


class GameRenderer:

    def __init__(self, game):

        self.game = game

        self.screen = game.screen
        self.width = game.width
        self.height = game.height

    def draw(self):

        game = self.game


        self.screen.fill((30, 30, 40))
    # =====================================================
    # MAIN DRAW
    # =====================================================



        # =================================================
        # GAME
        # =================================================

        if game.current_state in (
            1,  # PLAYING
            6   # PAUSE
        ):

            self.draw_game()

        # =================================================
        # MENU
        # =================================================

        elif game.current_state == 0:

            game.main_menu.draw(
                self.screen
            )

        # =================================================
        # LEVEL SELECT
        # =================================================

        elif game.current_state == 7:

            game.level_select_menu.draw(
                self.screen
            )

        # =================================================
        # OPTIONS
        # =================================================

        elif game.current_state == 2:

            game.options_menu.draw(
                self.screen
            )

        # =================================================
        # CREDITS
        # =================================================

        elif game.current_state == 3:

            game.credits_menu.draw(
                self.screen
            )

        # =================================================
        # FAILURE
        # =================================================

        elif game.current_state == 4:

            game.failure_menu.draw(
                self.screen
            )

        # =================================================
        # VICTORY
        # =================================================

        elif game.current_state == 5:

            game.victory_menu.draw(
                self.screen
            )

        pygame.display.flip()

    # =====================================================
    # GAME DRAW
    # =====================================================

    def draw_game(self):

        game = self.game

        # =================================================
        # PLATFORMY
        # =================================================

        game.platform_mgr.draw(
            self.screen
        )

        # =================================================
        # OBIEKTY INTERAKTYWNE
        # =================================================

        game.interactive_mgr.draw_all(
            self.screen
        )

        # =================================================
        # POSTACIE
        # =================================================

        game.char_mgr.draw_all(
            self.screen
        )

        # =================================================
        # WROGOWIE
        # =================================================

        for enemy in game.level.enemies:

            # Wróg posiada is_alive()

            if hasattr(
                enemy,
                "is_alive"
            ):

                if enemy.is_alive():

                    enemy.draw(
                        self.screen
                    )

            # Wróg nie posiada is_alive()

            else:

                enemy.draw(
                    self.screen
                )

        # =================================================
        # POCISKI
        # =================================================

        game.projectile_mgr.draw_all(
            self.screen
        )

        # =================================================
        # HUD
        # =================================================

        self.draw_hud()

        # =================================================
        # PAUSE
        # =================================================

        if game.current_state == 6:

            game.pause_menu.draw(
                self.screen
            )

    # =====================================================
    # HUD
    # =====================================================

    def draw_hud(self):

        game = self.game

        font = pygame.font.Font(
            None,
            32
        )

        # =================================================
        # PLAYER POWER
        # =================================================

        player_power = getattr(
            game.player,
            "power",
            0
        )

        # =================================================
        # HUD
        # =================================================

        hud_text = font.render(
            (
                f"Player HP: {game.player.hp} "
                f"| Ghost HP: {game.ghost.hp} "
                f"| Power: {player_power}"
            ),
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            hud_text,
            (10, 10)
        )

        # =================================================
        # CONTROLS
        # =================================================

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

        self.screen.blit(
            info,
            (10, 50)
        )