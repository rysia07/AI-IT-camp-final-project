import pygame


class PlatformManager:

    def __init__(self, texture_left, texture_middle, texture_right, platforms=None):

        self.platforms = []

        # =====================================================
        # TEXTURY
        # =====================================================

        try:
            self.left_image = pygame.image.load(
                texture_left
            ).convert_alpha()

            self.middle_image = pygame.image.load(
                texture_middle
            ).convert_alpha()

            self.right_image = pygame.image.load(
                texture_right
            ).convert_alpha()

        except (pygame.error, FileNotFoundError) as error:

            print(
                f"Nie można załadować tekstur platformy: {error}"
            )

            # Tekstury zastępcze
            self.left_image = pygame.Surface((25, 50))
            self.middle_image = pygame.Surface((50, 50))
            self.right_image = pygame.Surface((25, 50))

            self.left_image.fill((255, 0, 0))
            self.middle_image.fill((200, 0, 0))
            self.right_image.fill((255, 0, 0))

        # =====================================================
        # PLATFORMY
        # =====================================================

        if platforms is not None:

            self.platforms = platforms

        else:

            self.floor = pygame.Rect(
                0,
                550,
                900,
                50
            )

            self.platforms = [
                pygame.Rect(300, 500, 200, 20),
                pygame.Rect(600, 380, 200, 20),
                pygame.Rect(900, 250, 200, 20)
            ]

        # =====================================================
        # CACHE
        # =====================================================

        self.platform_textures = {}

        self._prepare_textures()

    # =====================================================
    # TEXTURE PREPARATION
    # =====================================================

    def _prepare_textures(self):

        self.platform_textures.clear()

        for platform in self.platforms:

            self._cache_texture_for_platform(
                platform
            )

    def _cache_texture_for_platform(self, platform):

        texture = self._create_platform_texture(
            platform.width,
            platform.height
        )

        self.platform_textures[id(platform)] = texture

    # =====================================================
    # CREATE PLATFORM
    # =====================================================

    def _create_platform_texture(self, width, height):

        # -------------------------------------------------
        # Szerokość końcówek
        # -------------------------------------------------

        left_width = self.left_image.get_width()
        right_width = self.right_image.get_width()

        # Jeżeli platforma jest bardzo mała,
        # zabezpieczamy się przed zbyt dużymi końcówkami.

        if width < left_width + right_width:

            left_width = width // 2
            right_width = width - left_width

        # -------------------------------------------------
        # Powierzchnia wynikowa
        # -------------------------------------------------

        surface = pygame.Surface(
            (width, height),
            pygame.SRCALPHA
        )

        # -------------------------------------------------
        # LEFT
        # -------------------------------------------------

        left = pygame.transform.scale(
            self.left_image,
            (
                left_width,
                height
            )
        )

        surface.blit(
            left,
            (0, 0)
        )

        # -------------------------------------------------
        # RIGHT
        # -------------------------------------------------

        right = pygame.transform.scale(
            self.right_image,
            (
                right_width,
                height
            )
        )

        # -------------------------------------------------
        # MIDDLE
        # -------------------------------------------------

        middle_width = (
            width
            - left_width
            - right_width
        )

        if middle_width > 0:

            middle = pygame.transform.scale(
                self.middle_image,
                (
                    self.middle_image.get_width(),
                    height
                )
            )

            x = left_width

            while x < left_width + middle_width:

                remaining = (
                    left_width
                    + middle_width
                    - x
                )

                tile_width = min(
                    middle.get_width(),
                    remaining
                )

                # Jeżeli ostatni tile jest krótszy,
                # przycinamy go.

                tile = middle

                if tile_width != middle.get_width():

                    tile = middle.subsurface(
                        pygame.Rect(
                            0,
                            0,
                            tile_width,
                            height
                        )
                    )

                surface.blit(
                    tile,
                    (x, 0)
                )

                x += tile_width

        # -------------------------------------------------
        # RIGHT
        # -------------------------------------------------

        surface.blit(
            right,
            (
                width - right_width,
                0
            )
        )

        return surface

    # =====================================================
    # ADD
    # =====================================================

    def add(self, platform):

        self.platforms.append(
            platform
        )

        self._cache_texture_for_platform(
            platform
        )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self):

        self.platforms.clear()
        self.platform_textures.clear()

    # =====================================================
    # DRAW
    # =====================================================

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

            else:

                pygame.draw.rect(
                    surface,
                    (100, 100, 100),
                    platform
                )

    # =====================================================
    # PYTHONIC INTERFACE
    # =====================================================

    def __len__(self):

        return len(
            self.platforms
        )

    def __iter__(self):

        return iter(
            self.platforms
        )

    def __getitem__(self, index):

        return self.platforms[index]

    def __contains__(self, item):

        return item in self.platforms

    def __repr__(self):

        return (
            f"<{self.__class__.__name__} "
            f"({len(self.platforms)} items)>"
        )
