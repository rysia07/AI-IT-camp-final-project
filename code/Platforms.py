import pygame


class PlatformManager:

    def __init__(self, texture_path, platforms=None):
        self.platforms = []
        try:
            self.raw_image = pygame.image.load(texture_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            # Tworzymy domyślną czerwoną teksturę zastępczą
            self.raw_image = pygame.Surface((50, 50))
            self.raw_image.fill((255, 0, 0))

        # Przypisanie domyślnych lub przekazanych platform
        if platforms is not None:
            self.platforms = platforms
        else:
            self.floor = pygame.Rect(0, 550, 900, 50)
            self.platforms = [
                self.floor,
                pygame.Rect(300, 500, 200, 20),
                pygame.Rect(600, 380, 200, 20),
                pygame.Rect(900, 250, 200, 20)
            ]

        # Przygotowanie tekstur dla wszystkich platform
        self.platform_textures = {}
        self._prepare_textures()

    def _prepare_textures(self):
        """Przygotowuje przeskalowane tekstury dla wszystkich obecnych platform."""
        self.platform_textures.clear()
        for platform in self.platforms:
            self._cache_texture_for_platform(platform)

    def _cache_texture_for_platform(self, platform):
        """Pomocnicza metoda tworząca skalowaną teksturę dla pojedynczej platformy."""
        size = (platform.width, platform.height)
        self.platform_textures[id(platform)] = pygame.transform.scale(
            self.raw_image, size
        )

    def add(self, platform):
        """Dodaje nową platformę i automatycznie generuje dla niej teksturę."""
        self.platforms.append(platform)
        self._cache_texture_for_platform(platform)

    def clear(self):
        """Czyści listę platform (np. przy zmianie poziomu)."""
        self.platforms.clear()
        self.platform_textures.clear()

    def draw(self, surface):
        """Rysuje wszystkie platformy na podanej powierzchni."""
        for platform in self.platforms:
            texture = self.platform_textures.get(id(platform))
            if texture:
                surface.blit(texture, platform)
            else:
                # W razie braku tekstury rysujemy prostokąt
                pygame.draw.rect(surface, (100, 100, 100), platform)

    # --- Metody Magiczne (Pythonic Interface) ---

    def __len__(self):
        """Pozwala na: len(platform_mgr)"""
        return len(self.platforms)

    def __iter__(self):
        """Pozwala na: for p in platform_mgr:"""
        return iter(self.platforms)

    def __getitem__(self, index):
        """Pozwala na: platform_mgr[0] lub platform_mgr[1:3]"""
        return self.platforms[index]

    def __contains__(self, item):
        """Pozwala na: if platform in platform_mgr:"""
        return item in self.platforms

    def __repr__(self):
        return f"<{self.__class__.__name__} ({len(self.platforms)} items)>"