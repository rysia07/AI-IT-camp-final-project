import pygame
from GUI import BaseMenu, Button


class PauseMenu(BaseMenu):
    def __init__(self, width, height):
        super().__init__(width, height, "PAUZA")
        self.active = False

        btn_w, btn_h = 200, 50
        center_x = width // 2 - btn_w // 2
        start_y = 200
        spacing = 70

        self.buttons = [
            Button(center_x, start_y, btn_w, btn_h, "Wznów", "resume"),
            Button(center_x, start_y + spacing, btn_w, btn_h, "Opcje", "options"),
            Button(center_x, start_y + spacing * 2, btn_w, btn_h, "Główne Menu", "main_menu")
        ]

    def toggle(self):
        self.active = not self.active