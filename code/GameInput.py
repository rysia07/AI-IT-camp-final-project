import pygame


class GameInput:

    def __init__(self, game):
        self.game = game

    # =====================================================
    # KEYBOARD
    # =====================================================

    def handle_keydown(self, event):

        game = self.game

        # -------------------------------------------------
        # ESC
        # -------------------------------------------------

        if event.key == pygame.K_ESCAPE:

            # PLAYING -> PAUSE
            if game.state.is_playing():

                game.state.pause()

                return

            # PAUSE -> PLAYING
            elif game.state.is_pause():

                game.state.resume()

                return

        # -------------------------------------------------
        # TYLKO GAMEPLAY
        # -------------------------------------------------

        if not game.state.is_playing():
            return

        # -------------------------------------------------
        # JUMP
        # -------------------------------------------------

        if event.key in (
            pygame.K_w,
            pygame.K_SPACE
        ):

            if game.player.jump():

                game.jump_audio.stop()
                game.jump_audio.play()

        # -------------------------------------------------
        # ATTACK
        # -------------------------------------------------

        elif event.key == pygame.K_2:

            if hasattr(
                game.player,
                "play"
            ):

                game.attack_audio.stop()
                game.attack_audio.play()

                game.player.play(
                    "attack"
                )

    # =====================================================
    # MOUSE MOTION
    # =====================================================

    def handle_mouse_motion(self, event):

        game = self.game

        if not game.state.is_playing():
            return

        dx, dy = event.rel

        game.mouse_dx += dx
        game.mouse_dy += dy

    # =====================================================
    # LEFT CLICK
    # =====================================================

    def handle_left_click(self, event):

        game = self.game

        # =================================================
        # PLAYING
        # =================================================

        if game.state.is_playing():

            if game.interactive_mgr is not None:

                game.interactive_mgr.handle_event_all(
                    event
                )

            return

        # =================================================
        # MENU
        # =================================================

        if game.state.is_menu():

            action = game.main_menu.handle_click(
                event.pos,
                (1, 0, 0)
            )

            if action == "level_select":

                game.state.level_select(
                    previous=game.MENU
                )

            elif action == "options":

                game.state.options(
                    previous=game.MENU
                )

            elif action == "credits":

                game.state.credits()

                game.audio_manager.play(
                    "credits"
                )

            elif action == "quit":

                game.running = False

            return

        # =================================================
        # LEVEL SELECT
        # =================================================

        if game.state.is_level_select():

            action = (
                game.level_select_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            # ---------------------------------------------
            # BACK
            # ---------------------------------------------

            if action == "back":

                previous = game.state.previous

                game.state.set_direct(
                    previous
                )

                if game.state.is_playing():

                    game.start_game_mouse()

                else:

                    game.stop_game_mouse()

                return

            # ---------------------------------------------
            # LOAD LEVEL
            # ---------------------------------------------

            if (
                action
                and action.startswith("load_")
            ):

                level_file = action.replace(
                    "load_",
                    "",
                    1
                )

                game.current_level_file = (
                    level_file
                )

                game.level_manager.load_level(
                    level_file
                )

                game.state.start_game()

            return

        # =================================================
        # PAUSE
        # =================================================

        if game.state.is_pause():

            action = (
                game.pause_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            # ---------------------------------------------
            # RESUME
            # ---------------------------------------------

            if action == "resume":

                game.state.resume()

            # ---------------------------------------------
            # LEVEL SELECT
            # ---------------------------------------------

            elif action == "level_select":

                game.pause_menu.active = False

                game.state.level_select(
                    previous=game.PAUSE
                )

                game.stop_game_mouse()

            # ---------------------------------------------
            # OPTIONS
            # ---------------------------------------------

            elif action == "options":

                game.state.options(
                    previous=game.PAUSE
                )

                game.stop_game_mouse()

            # ---------------------------------------------
            # MAIN MENU
            # ---------------------------------------------

            elif action == "main_menu":

                game.state.main_menu()

            return

        # =================================================
        # OPTIONS
        # =================================================

        if game.state.is_options():

            action = (
                game.options_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            if action == "back":

                previous = game.state.previous

                game.state.set_direct(
                    previous
                )

                if game.state.is_playing():

                    game.start_game_mouse()

                else:

                    game.stop_game_mouse()

            return

        # =================================================
        # CREDITS
        # =================================================

        if game.state.is_credits():

            action = (
                game.credits_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            if action == "back":

                game.state.main_menu()

            return

        # =================================================
        # FAILURE
        # =================================================

        if game.state.is_failure():

            action = (
                game.failure_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            # ---------------------------------------------
            # RETRY
            # ---------------------------------------------

            if action == "retry":

                game.level_manager.load_level(
                    game.current_level_file
                )

                game.state.start_game()

            # ---------------------------------------------
            # MENU
            # ---------------------------------------------

            elif action == "menu":

                game.state.main_menu()

            return

        # =================================================
        # VICTORY
        # =================================================

        if game.state.is_victory():

            action = (
                game.victory_menu.handle_input(
                    event.pos,
                    (1, 0, 0)
                )
            )

            # ---------------------------------------------
            # LEVEL SELECT
            # ---------------------------------------------

            if action == "level_select":

                game.state.level_select(
                    previous=game.MENU
                )

            # ---------------------------------------------
            # MENU
            # ---------------------------------------------

            elif action == "menu":

                game.state.main_menu()

    # =====================================================
    # EVENTS
    # =====================================================

    def handle_events(self):

        game = self.game

        # -------------------------------------------------
        # RESET MOUSE DELTA
        # -------------------------------------------------

        game.mouse_dx = 0
        game.mouse_dy = 0

        # -------------------------------------------------
        # EVENT LOOP
        # -------------------------------------------------

        for event in pygame.event.get():

            # ---------------------------------------------
            # QUIT
            # ---------------------------------------------

            if event.type == pygame.QUIT:

                game.running = False

                continue

            # ---------------------------------------------
            # OPTIONS EVENTS
            # ---------------------------------------------

            if game.state.is_options():

                if hasattr(
                    game.options_menu,
                    "handle_event"
                ):

                    game.options_menu.handle_event(
                        event
                    )

            # ---------------------------------------------
            # KEYBOARD
            # ---------------------------------------------

            if event.type == pygame.KEYDOWN:

                self.handle_keydown(
                    event
                )

            # ---------------------------------------------
            # MOUSE MOTION
            # ---------------------------------------------

            elif event.type == pygame.MOUSEMOTION:

                self.handle_mouse_motion(
                    event
                )

            # ---------------------------------------------
            # LEFT CLICK
            # ---------------------------------------------

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                self.handle_left_click(
                    event
                )

            # ---------------------------------------------
            # INTERACTIVE OBJECTS
            # ---------------------------------------------

            if game.state.is_playing():

                if game.interactive_mgr is not None:

                    game.interactive_mgr.handle_event(
                        event
                    )