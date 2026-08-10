import pygame; from Game import Game
def main():
    game = Game(width=900,height=600,fps=60); game.run(); pygame.quit()
if __name__ == "__main__":
    main()