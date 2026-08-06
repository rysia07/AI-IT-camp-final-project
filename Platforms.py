import pygame

class PlatformManager:
    def __init__(self, texture_path):
        # Ładowanie i zabezpieczenie tekstury
        try:
            self.raw_image = pygame.image.load(texture_path).convert_alpha()
        except pygame.error:
            self.raw_image = pygame.Surface((50, 50))
            self.raw_image.fill((139, 69, 19))

        # Definicja podłogi i platform
        self.floor = pygame.Rect(0, 550, 900, 50)
        self.platforms = [
            self.floor,
            pygame.Rect(300, 500, 200, 20),
            pygame.Rect(600, 380, 200, 20),
            pygame.Rect(900, 250, 200, 20)
        ]

        # Przygotowanie skalowanych tekstur
        self.floor_texture = pygame.transform.scale(self.raw_image, self.floor.size)
        self.platform_texture = pygame.transform.scale(self.raw_image, (200, 20))

    def draw(self, surface):
        # Rysowanie podłogi
        surface.blit(self.floor_texture, self.floor)
        # Rysowanie pozostałych platform
        for platform in self.platforms[1:]:
            surface.blit(self.platform_texture, platform)