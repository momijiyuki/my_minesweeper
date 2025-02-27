from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from . import params
from .mixins import DrawableMixin


if TYPE_CHECKING:
    from .settings import GameSettings


class MinePanel(DrawableMixin):
    bg_panel = None
    closed_panel = None
    mine_flag = None

    @classmethod
    def initialize_resource(cls, settings: GameSettings) -> None:
        if cls.bg_panel is None:
            try:
                cls.bg_panel = pygame.image.load(settings.img_paths["bg_panel"])
                cls.closed_panel = pygame.image.load(settings.img_paths["closed_panel"])
                cls.mine_flag = pygame.image.load(settings.img_paths["mine_flag"])
            except pygame.error as e:
                print(f"画像の読み込みに失敗しました: {e}")
                cls._create_alternative_images(settings)

    @classmethod
    def _create_alternative_images(cls, settings: GameSettings) -> None:
        size = (settings.panel_size, settings.panel_size)
        cls.bg_panel = pygame.Surface(size)
        cls.bg_panel.fill((200, 200, 200))

        cls.closed_panel = pygame.Surface(size)
        cls.closed_panel.fill((150, 150, 150))

        cls.mine_flag = pygame.Surface(size)
        cls.mine_flag.fill(params.RED)

    def __init__(self) -> None:
        self.has_mine = False
        self.is_flagged = False
        self.is_revealed = False
        self.pos_topleft = (0, 0)
        self.neighbor_mine = 0

    def set_mine(self) -> None:
        self.has_mine = True

    def get_in_mine(self) -> bool:
        return self.has_mine

    def set_nmine(self, num: int) -> None:
        self.neighbor_mine = num

    def set_pos(self, x: int, y: int) -> MinePanel:
        self.pos_topleft = (x, y)
        return self

    def get_is_revealed(self) -> bool:
        return self.is_revealed

    def toggle_flag(self) -> None:
        if self.is_revealed:
            return
        self.is_flagged ^= True

    def open_panel(self) -> None:
        if self.is_flagged:
            return
        self.is_revealed = True

    def update_panel(self, screen: pygame.Surface) -> None:
        self.__draw_panel(screen)
        self.__draw_flag(screen)
        self.__draw_number_panel(screen)

    def __draw_panel(self, screen: pygame.Surface) -> None:
        """パネルの描画"""
        if self.is_revealed:
            screen.blit(self.bg_panel, self.pos_topleft)
        else:
            screen.blit(self.closed_panel, self.pos_topleft)

    def __draw_flag(self, screen: pygame.Surface) -> None:
        """旗の描画"""
        if not self.is_revealed and self.is_flagged:
            screen.blit(self.mine_flag, self.pos_topleft)

    def __draw_number_panel(self, screen: pygame.Surface) -> None:
        """地雷数の表示"""
        if not self.is_revealed:
            return

        self.drawtext(
            screen,
            f"{self.neighbor_mine}",
            [i + 15 for i in list(self.pos_topleft)],
            color=params.FONT_COLOR.get(self.neighbor_mine, (191, 191, 191)),
        )
