import pygame


class PlatformManager:

    def __init__(self, texture_path, platforms=None):
        # Load texture
        try:
            self.raw_image = pygame.image.load(
                texture_path
            ).convert_alpha()

        except pygame.error:
            self.raw_image = pygame.Surface((50, 50))
            self.raw_image.fill((255, 0, 0))

        # Use loaded platforms if provided
        if platforms is not None:
            self.platforms = platforms

        else:
            # Default platforms
            self.floor = pygame.Rect(
                0, 550, 900, 50
            )

            self.platforms = [
                self.floor,
                pygame.Rect(300, 500, 200, 20),
                pygame.Rect(600, 380, 200, 20),
                pygame.Rect(900, 250, 200, 20)
            ]

        # Prepare textures
        self._prepare_textures()

    def _prepare_textures(self):

        self.platform_textures = {}

        for platform in self.platforms:

            size = platform.width, platform.height

            self.platform_textures[id(platform)] = (
                pygame.transform.scale(
                    self.raw_image,
                    size
                )
            )

    def draw(self, surface):

        for platform in self.platforms:

            texture = self.platform_textures.get(
                id(platform)
            )

            if texture:
                surface.blit(
                    texture,
                    platform
                )
