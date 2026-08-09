import pygame
from GUI import BaseMenu, Button


class PauseMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "PAUZA")
        self.active = False

        btn_w, btn_h = 220, 50
        center_x = width // 2 - btn_w // 2
        start_y = 180
        spacing = 65

        self.buttons = [
            Button(center_x, start_y, btn_w, btn_h, "Wznów", "resume"),
            Button(center_x, start_y + spacing, btn_w, btn_h, "Wybór poziomu", "level_select"),
            Button(center_x, start_y + spacing * 2, btn_w, btn_h, "Opcje", "options"),
            Button(center_x, start_y + spacing * 3, btn_w, btn_h, "Menu Główna", "main_menu")
        ]

    def toggle(self):
        self.active = not self.active