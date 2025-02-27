import sys

import minesweeper as ms
import pygame
from minesweeper.params import WHITE
from pygame.locals import MOUSEBUTTONDOWN
from pygame.locals import QUIT


def main() -> None:
    pygame.display.init()
    pygame.font.init()
    settings = ms.GameSettings()
    ms_master = ms.MineSweeper(settings)

    screen = pygame.display.set_mode(settings.window_size)

    clock = pygame.time.Clock()

    while True:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                ms_master.clicked(event.pos, event.button)

        ms_master.screen_update(screen)
        pygame.display.update()
        clock.tick(600)


if __name__ == "__main__":
    main()
