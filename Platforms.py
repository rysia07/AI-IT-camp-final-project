import pygame
import LoadLevels



class PlatformManager:
    def __init__(self, texture_path):
        # Ładowanie i zabezpieczenie tekstury
        try:
            self.raw_image = pygame.image.load(texture_path).convert_alpha()
        except pygame.error:
            self.raw_image = pygame.Surface((50, 50))
            self.raw_image.fill((139, 69, 19))

        # pobieranie rectów z Loadlevels.py
        manager, player_pos = LoadLevels.load_rects_from_file("level.txt")

        self.platforms = manager.get_rects()
        self.player_pos = player_pos
        print(self.player_pos)

        # Przygotowanie skalowanych tekstur

        self.platform_texture = pygame.transform.scale(self.raw_image, (200, 20))

    def draw(self, surface):
        # Rysowanie podłogi

        # Rysowanie pozostałych platform
        for platform in self.platforms[1:]:
            surface.blit(self.platform_texture, platform)