import pygame
import sys

pygame.init()

size = 600

screen = pygame.display.set_mode((size, size), pygame.RESIZABLE)
pygame.display.set_caption("Resizable Pygame Window")

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:
            size = min(event.w, event.h)
            screen = pygame.display.set_mode((size, size), pygame.RESIZABLE)

    screen.fill((30, 30, 30))

    pygame.draw.rect(
        screen,
        (0, 200, 0),
        (size // 4, size // 4, size // 2, size // 2),
    )

    pygame.display.flip()
    clock.tick(60)
