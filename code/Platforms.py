import pygame


class PlatformManager:

    def __init__(
        self,
        texture_left,
        texture_middle,
        texture_right,
        texture_wall,
        platforms=None,
        walls=None
    ):

        self.platforms = []
        self.walls = []

        # =====================================================
        # TEKSTURY PLATFORM
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

        except (
            pygame.error,
            FileNotFoundError
        ) as error:

            print(
                f"Nie można załadować tekstur platformy: "
                f"{error}"
            )

            self.left_image = pygame.Surface(
                (25, 50),
                pygame.SRCALPHA
            )

            self.middle_image = pygame.Surface(
                (50, 50),
                pygame.SRCALPHA
            )

            self.right_image = pygame.Surface(
                (25, 50),
                pygame.SRCALPHA
            )

            self.left_image.fill(
                (255, 0, 0)
            )

            self.middle_image.fill(
                (200, 0, 0)
            )

            self.right_image.fill(
                (255, 0, 0)
            )

        # =====================================================
        # TEKSTURA ŚCIANY
        # =====================================================

        try:

            self.wall_image = pygame.image.load(
                texture_wall
            ).convert_alpha()

        except (
            pygame.error,
            FileNotFoundError
        ) as error:

            print(
                f"Nie można załadować tekstury ściany: "
                f"{error}"
            )

            self.wall_image = pygame.Surface(
                (50, 50),
                pygame.SRCALPHA
            )

            self.wall_image.fill(
                (80, 80, 80)
            )

        # =====================================================
        # PLATFORMY
        # =====================================================

        if platforms is not None:

            self.platforms = platforms

        else:

            self.platforms = [
                pygame.Rect(
                    300,
                    500,
                    200,
                    20
                ),

                pygame.Rect(
                    600,
                    380,
                    200,
                    20
                ),

                pygame.Rect(
                    900,
                    250,
                    200,
                    20
                )
            ]

        # =====================================================
        # ŚCIANY
        # =====================================================

        if walls is not None:

            self.walls = walls

        # =====================================================
        # CACHE
        # =====================================================

        self.platform_textures = {}
        self.wall_textures = {}

        self._prepare_textures()

    # =====================================================
    # TEXTURE PREPARATION
    # =====================================================

    def _prepare_textures(self):

        self.platform_textures.clear()
        self.wall_textures.clear()

        for platform in self.platforms:

            self._cache_texture_for_platform(
                platform
            )

        for wall in self.walls:

            self._cache_texture_for_wall(
                wall
            )

    # =====================================================
    # PLATFORM TEXTURE CACHE
    # =====================================================

    def _cache_texture_for_platform(
        self,
        platform
    ):

        texture = self._create_platform_texture(
            platform.width,
            platform.height
        )

        self.platform_textures[
            id(platform)
        ] = texture

    # =====================================================
    # WALL TEXTURE CACHE
    # =====================================================

    def _cache_texture_for_wall(
        self,
        wall
    ):

        texture = self._create_wall_texture(
            wall.width,
            wall.height
        )

        self.wall_textures[
            id(wall)
        ] = texture

    # =====================================================
    # CREATE PLATFORM TEXTURE
    # =====================================================

    def _create_platform_texture(
        self,
        width,
        height
    ):

        width = max(
            1,
            int(width)
        )

        height = max(
            1,
            int(height)
        )

        left_width = self.left_image.get_width()
        right_width = self.right_image.get_width()

        if width < left_width + right_width:

            left_width = width // 2

            right_width = (
                width - left_width
            )

        surface = pygame.Surface(
            (width, height),
            pygame.SRCALPHA
        )

        # -------------------------------------------------
        # LEFT
        # -------------------------------------------------

        if left_width > 0:

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

            while x < (
                left_width
                + middle_width
            ):

                remaining = (
                    left_width
                    + middle_width
                    - x
                )

                tile_width = min(
                    middle.get_width(),
                    remaining
                )

                tile = middle

                if (
                    tile_width
                    != middle.get_width()
                ):

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

        if right_width > 0:

            right = pygame.transform.scale(
                self.right_image,
                (
                    right_width,
                    height
                )
            )

            surface.blit(
                right,
                (
                    width - right_width,
                    0
                )
            )

        return surface

    # =====================================================
    # CREATE WALL TEXTURE
    # =====================================================

    def _create_wall_texture(
        self,
        width,
        height
    ):

        width = max(
            1,
            int(width)
        )

        height = max(
            1,
            int(height)
        )

        return pygame.transform.scale(
            self.wall_image,
            (
                width,
                height
            )
        )

    # =====================================================
    # ADD PLATFORM
    # =====================================================

    def add(
        self,
        platform
    ):

        self.platforms.append(
            platform
        )

        self._cache_texture_for_platform(
            platform
        )

    # =====================================================
    # ADD WALL
    # =====================================================

    def add_wall(
        self,
        wall
    ):

        self.walls.append(
            wall
        )

        self._cache_texture_for_wall(
            wall
        )

    # =====================================================
    # REMOVE PLATFORM
    # =====================================================

    def remove(
        self,
        platform
    ):

        if platform in self.platforms:

            self.platforms.remove(
                platform
            )

            self.platform_textures.pop(
                id(platform),
                None
            )

    # =====================================================
    # REMOVE WALL
    # =====================================================

    def remove_wall(
        self,
        wall
    ):

        if wall in self.walls:

            self.walls.remove(
                wall
            )

            self.wall_textures.pop(
                id(wall),
                None
            )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self):

        self.platforms.clear()
        self.walls.clear()

        self.platform_textures.clear()
        self.wall_textures.clear()

    # =====================================================
    # GET ALL SOLID OBJECTS
    # =====================================================

    def get_obstacles(self):

        return (
            self.platforms
            + self.walls
        )

    # =====================================================
    # DRAW PLATFORM
    # =====================================================

    def _draw_platform(
        self,
        surface,
        platform
    ):

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
    # DRAW WALL
    # =====================================================

    def _draw_wall(
        self,
        surface,
        wall
    ):

        texture = self.wall_textures.get(
            id(wall)
        )

        if texture:

            surface.blit(
                texture,
                wall
            )

        else:

            pygame.draw.rect(
                surface,
                (100, 100, 100),
                wall
            )

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        surface
    ):

        for platform in self.platforms:

            self._draw_platform(
                surface,
                platform
            )

        for wall in self.walls:

            self._draw_wall(
                surface,
                wall
            )

    # =====================================================
    # PYTHONIC INTERFACE
    # =====================================================

    def __len__(self):

        return (
            len(self.platforms)
            + len(self.walls)
        )

    def __iter__(self):

        return iter(
            self.get_obstacles()
        )

    def __getitem__(
        self,
        index
    ):

        return self.get_obstacles()[index]

    def __contains__(
        self,
        item
    ):

        return (
            item in self.platforms
            or item in self.walls
        )

    def __repr__(self):

        return (
            f"<{self.__class__.__name__} "
            f"({len(self.platforms)} platforms, "
            f"{len(self.walls)} walls)>"
        )
