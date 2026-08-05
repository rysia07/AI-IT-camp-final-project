import pygame
from ClickableBox import ClickableBox
from Characters import Characters
pygame.init()

creature = Creature(400,300)
ghost = GhostMouse(600,300)

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

box1 = ClickableBox(100, 100, 200, 200, (255, 0, 0), (255, 100, 100), (200, 0, 0))
box2 = ClickableBox(400, 400, 200, 200, (0, 255, 0), (100, 255, 100), (0, 200, 0))

creature = Character(
    500,
    300,
    40
)

mouse = Character(
    700,
    300,
    20
)

running = True
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        box1.handle_event(event)
        box2.handle_event(event)

    screen.fill((30, 30, 30))

    box1.draw(screen)
    box2.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()