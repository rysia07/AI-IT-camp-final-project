class OptionsMenu(BaseMenu):

    def __init__(self, width, height, audio_manager=None):

        super().__init__(
            width,
            height,
            "OPCJE"
        )

        self.audio_manager = audio_manager

        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2

        # =================================================
        # VOLUME
        # =================================================

        slider_w = 300
        slider_h = 16

        slider_x = (
            width // 2
            - slider_w // 2
        )

        self.volume_slider = Slider(
            slider_x,
            180,
            slider_w,
            slider_h,
            min_val=0.0,
            max_val=1.0,
            initial_val=(
                audio_manager.master_volume
                if audio_manager is not None
                else 0.7
            )
        )

        # =================================================
        # CONTROLS
        # =================================================

        self.controls_info = [
            "--- STEROWANIE ---",
            "A / D  lub  Strzałki:  Ruch w lewo / prawo",
            "W / Spacja:  Skok",
            "S / Strzałka w dół:  Szybkie opadanie",
            "Klawisz 2:  Atak postaci",
            "Ruch myszą:  Ruch Duchem (Ghost)",
            "ESC:  Pauza"
        ]

        # =================================================
        # BUTTONS
        # =================================================

        self.buttons = [
            Button(
                center_x,
                480,
                btn_w,
                btn_h,
                "Powrót",
                "back"
            )
        ]

    # =====================================================
    # EVENTS
    # =====================================================

    def handle_event(self, event):

        old_value = self.volume_slider.value

        self.volume_slider.handle_event(
            event
        )

        new_value = self.volume_slider.value

        # =================================================
        # ZMIANA GŁOŚNOŚCI
        # =================================================

        if (
            new_value != old_value
            and self.audio_manager is not None
        ):

            self.audio_manager.set_master_volume(
                new_value
            )

    # =====================================================
    # DRAW
    # =====================================================

    def draw(self, surface):

        super().draw(
            surface
        )

        self.volume_slider.draw(
            surface,
            self.btn_font,
            "Głośność"
        )

        # =================================================
        # CONTROLS
        # =================================================

        start_y = 240

        for i, line in enumerate(
            self.controls_info
        ):

            color = (
                (255, 215, 0)
                if i == 0
                else (220, 220, 220)
            )

            txt_surf = self.info_font.render(
                line,
                True,
                color
            )

            txt_rect = txt_surf.get_rect(
                center=(
                    self.width // 2,
                    start_y + i * 28
                )
            )

            surface.blit(
                txt_surf,
                txt_rect
            )