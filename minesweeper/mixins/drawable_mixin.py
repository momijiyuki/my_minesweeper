import pygame

from minesweeper import params


class DrawableMixin:
    @staticmethod
    def drawbutton(
        screen: pygame.Surface,
        rect: tuple[int, int, int, int],
        color: tuple[int, int, int] = (191, 191, 191),
    ) -> None:
        button = pygame.Rect(rect)
        pygame.draw.rect(screen, color, button)

    @staticmethod
    def drawtext(
        screen: pygame.surface,
        text: str,
        center_pos: list[int, int],
        color: tuple[int, int, int] = params.BLACK,
        font_size: int = 26,
    ) -> None:
        font = pygame.font.Font(None, font_size)
        text = font.render(text, True, color)  # noqa: FBT003
        text_rect = text.get_rect()
        text_rect.center = center_pos
        screen.blit(text, text_rect)
