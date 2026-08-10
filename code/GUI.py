import pygame


class Button:
    """Uniwersalna klasa przycisku dla wszystkich menu."""

    def __init__(self, x, y, width, height, text, action, idle_color=(70, 70, 70), active_color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.idle_color = idle_color
        self.active_color = active_color
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font):
        color = self.active_color if self.hovered else self.idle_color

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=8)

        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class Slider:
    """Klasa interaktywnego suwaka (np. do regulacji głośności)."""

    def __init__(self, x, y, width, height, min_val=0.0, max_val=1.0, initial_val=0.5):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False

        handle_x = x + int((initial_val - min_val) / (max_val - min_val) * width)
        self.handle_rect = pygame.Rect(handle_x - 10, y - 5, 20, height + 10)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])

    def update_value(self, mouse_x):
        rel_x = max(self.rect.left, min(mouse_x, self.rect.right))
        self.handle_rect.centerx = rel_x
        ratio = (rel_x - self.rect.left) / self.rect.width
        self.value = round(self.min_val + ratio * (self.max_val - self.min_val), 2)

    def draw(self, surface, font, label="Głośność"):
        txt_surf = font.render(f"{label}: {int(self.value * 100)}%", True, (255, 255, 255))
        surface.blit(txt_surf, (self.rect.x, self.rect.y - 35))

        pygame.draw.rect(surface, (50, 50, 50), self.rect, border_radius=4)
        fill_width = self.handle_rect.centerx - self.rect.left
        fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_width, self.rect.height)
        pygame.draw.rect(surface, (100, 180, 255), fill_rect, border_radius=4)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=4)

        color = (220, 220, 220) if self.dragging else (170, 170, 170)
        pygame.draw.rect(surface, color, self.handle_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255), self.handle_rect, 2, border_radius=6)


class BaseMenu:
    """Bazowa klasa dla wszystkich menu."""

    def __init__(self, width, height, title_text):
        self.width = width
        self.height = height
        self.title_text = title_text
        self.title_font = pygame.font.Font(None, 64)
        self.credits_font = pygame.font.Font(None, 16)
        self.btn_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 28)
        self.buttons = []

    def handle_input(self, pos, mouse_buttons=None):
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                return button.action
        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)

    def draw_background_and_title(self, surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title_surf = self.title_font.render(self.title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.width // 2, 80))
        surface.blit(title_surf, title_rect)

    def draw(self, surface):
        self.draw_background_and_title(surface)
        for button in self.buttons:
            button.draw(surface, self.btn_font)


class MainMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "ALIEN SPACE")
        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2
        start_y = 180
        spacing = 65

        # "Graj" kieruje do wyboru poziomów ("level_select")
        self.buttons = [
            Button(center_x, start_y, btn_w, btn_h, "Graj", "level_select"),
            Button(center_x, start_y + spacing, btn_w, btn_h, "Opcje", "options"),
            Button(center_x, start_y + spacing * 2, btn_w, btn_h, "Autorzy", "credits"),
            Button(center_x, start_y + spacing * 3, btn_w, btn_h, "Wyjście", "quit")
        ]

    def handle_click(self, pos, mouse_buttons=None):
        return self.handle_input(pos, mouse_buttons)


class LevelSelectMenu(BaseMenu):
    """Menu wyboru poziomu."""

    def __init__(self, width, height, level_list=None):
        super().__init__(width, height, "WYBÓR POZIOMU")
        if level_list is None:
            level_list = [
                "level1.txt",
                "level2.txt",
                "level3.txt",
                "level4.txt",
                "level5.txt"
            ]

        self.buttons = []
        btn_w, btn_h = 220, 50
        center_x = width // 2 - btn_w // 2
        start_y = 180
        spacing = 60

        for i, lvl_name in enumerate(level_list):
            action_name = f"load_{lvl_name}"
            display_name = f"Poziom {i + 1}"
            self.buttons.append(
                Button(center_x, start_y + i * spacing, btn_w, btn_h, display_name, action_name)
            )

        # Przyciski Powrót na dole
        self.buttons.append(
            Button(center_x, start_y + len(level_list) * spacing + 20, btn_w, btn_h, "Powrót", "back")
        )

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
        # MUSIC SLIDER
        # =================================================

        slider_w = 300
        slider_h = 16
        slider_x = width // 2 - slider_w // 2

        music_value = (
            audio_manager.music_volume
            if audio_manager is not None
            else 1.0
        )

        self.music_slider = Slider(
            slider_x,
            170,
            slider_w,
            slider_h,
            min_val=0.0,
            max_val=1.0,
            initial_val=music_value
        )

        # =================================================
        # SFX SLIDER
        # =================================================

        sfx_value = (
            audio_manager.sfx_volume
            if audio_manager is not None
            else 1.0
        )

        self.sfx_slider = Slider(
            slider_x,
            250,
            slider_w,
            slider_h,
            min_val=0.0,
            max_val=1.0,
            initial_val=sfx_value
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
        # BACK BUTTON
        # =================================================

        self.buttons = [
            Button(
                center_x,
                500,
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

        old_music = self.music_slider.value
        old_sfx = self.sfx_slider.value

        # -------------------------------------------------
        # MUSIC
        # -------------------------------------------------

        self.music_slider.handle_event(
            event
        )

        # -------------------------------------------------
        # SFX
        # -------------------------------------------------

        self.sfx_slider.handle_event(
            event
        )

        # -------------------------------------------------
        # UPDATE AUDIO
        # -------------------------------------------------

        if self.audio_manager is not None:

            if self.music_slider.value != old_music:

                self.audio_manager.set_music_volume(
                    self.music_slider.value
                )

            if self.sfx_slider.value != old_sfx:

                self.audio_manager.set_sfx_volume(
                    self.sfx_slider.value
                )

    # =====================================================
    # DRAW
    # =====================================================

    def draw(self, surface):

        super().draw(
            surface
        )

        # -------------------------------------------------
        # MUSIC
        # -------------------------------------------------

        self.music_slider.draw(
            surface,
            self.btn_font,
            "Muzyka"
        )

        # -------------------------------------------------
        # SFX
        # -------------------------------------------------

        self.sfx_slider.draw(
            surface,
            self.btn_font,
            "Efekty dźwiękowe"
        )

        # -------------------------------------------------
        # CONTROLS
        # -------------------------------------------------

        start_y = 320

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

class CreditsMenu(BaseMenu):

    def __init__(self, width, height, audio_manager=None):

        super().__init__(
            width,
            height,
            "AKTORZÓY"
        )

        self.audio_manager = audio_manager
        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2

        self.credits_lines = [
            '''
            Gra stworzona przez 'AIAIAI STUDIOS'
            
            Jakub :
                wczytywanie animacji, ładowanie leveli,
                edytor leveli
                
            Rafał : 
                Główna pętla gry,
                mechanika postaci
                
            Mati : 
                level design,
                menu opcji,
            
            Ala : 
                grafika gry,
                level design,
                wsparcie psychiczne,
                motywator
                
            Steve J*bs :
                audio design,
                trailer
                
        ''']
                
            
            
            
            
            
            

        self.buttons = [
            Button(center_x, 480, btn_w, btn_h, "Powrót", "back")
        ]

    def draw(self, surface):
        super().draw(surface)
        start_y = 180
        for i, line in enumerate(self.credits_lines):
            txt_surf = self.info_font.render(line, True, (220, 220, 220))
            txt_rect = txt_surf.get_rect(center=(self.width // 2, start_y + i * 32))
            surface.blit(txt_surf, txt_rect)


class FailureMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "PORAŻKA")
        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2
        start_y = 220
        spacing = 70

        self.buttons = [
            Button(center_x, start_y, btn_w, btn_h, "Spróbuj ponownie", "retry"),
            Button(center_x, start_y + spacing, btn_w, btn_h, "Menu Główna", "menu")
        ]


class VictoryMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "ZWYCIĘSTWO!")
        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2
        start_y = 220
        spacing = 70

        self.buttons = [
            Button(center_x, start_y, btn_w, btn_h, "Wybór Poziomu", "level_select"),
            Button(center_x, start_y + spacing, btn_w, btn_h, "Menu Główna", "menu")
        ]