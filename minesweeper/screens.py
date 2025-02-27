from __future__ import annotations

import itertools
import random
import sys
from abc import ABC
from abc import abstractmethod

import pygame

from .mixins import DrawableMixin
from .panel import MinePanel
from .settings import GameSettings
from .settings import Idx
from .settings import State


class Fields(ABC):
    def __init__(self, settings: GameSettings) -> None:
        self.settings = settings

    @abstractmethod
    def screen_update(self, screen: pygame.surface) -> None: ...

    @abstractmethod
    def left_click(self, pos: tuple[int, int]) -> State | None: ...

    @abstractmethod
    def right_click(self, pos: tuple[int, int]) -> None: ...


class Title(Fields):
    def __init__(self, settings: GameSettings) -> None:
        super().__init__(settings)

    def screen_update(self, screen: pygame.Surface) -> None:  # noqa:ARG002
        return

    def left_click(self, pos: tuple[int, int]) -> State | None:  # noqa:ARG002
        return

    def right_click(self, pos: tuple[int, int]) -> None:  # noqa:ARG002
        return


class Result(Fields, DrawableMixin):
    def __init__(self, settings: GameSettings) -> None:
        super().__init__(settings)

        lower_center = (
            self.settings.screen_width // 2,
            self.settings.screen_height
            - (self.settings.panel_size * 3 + self.settings.margin),
        )  # x, y

        self.restart_button = (lower_center[0] - 90, lower_center[1] - 20, 60, 20)
        self.restart_text = [lower_center[0] - 60, lower_center[1] - 10]
        self.quit_button = (lower_center[0] + 30, lower_center[1] - 20, 60, 20)
        self.quit_text = [lower_center[0] + 60, lower_center[1] - 10]

    def screen_update(self, screen: pygame.Surface, *, gamestate: bool) -> None:
        result = "game clear!!!" if gamestate else "game over"
        self.drawtext(screen, result, (self.settings.screen_width // 2, 50))

        self.drawbutton(screen, self.restart_button)
        self.drawbutton(screen, self.quit_button)
        self.drawtext(screen, "restart", self.restart_text)
        self.drawtext(screen, "quit", self.quit_text)

    def left_click(self, pos: tuple[int, int]) -> State | None:
        if self.is_valid(pos, self.restart_button):
            return State.GAME
        if self.is_valid(pos, self.quit_button):
            pygame.quit()
            sys.exit()
        return None

    def right_click(self, pos: tuple[int, int]) -> None:  # noqa:ARG002
        return

    @staticmethod
    def is_valid(pos: tuple[int, int], box: tuple[int, int, int, int]) -> bool:
        column, row = pos
        left, top, width, height = box
        return left <= column < left + width and top <= row < top + height


class MineField(Fields, DrawableMixin):
    def __init__(self, settings: GameSettings) -> None:
        super().__init__(settings)
        self.is_initialized = False
        MinePanel.initialize_resource(settings)
        self.panels = [
            [
                MinePanel().set_pos(
                    self.settings.margin + self.settings.panel_size * j,
                    self.settings.margin
                    + self.settings.header_margin
                    + self.settings.panel_size * i,
                )
                for j in range(self.settings.cols)
            ]
            for i in range(self.settings.rows)
        ]

    def screen_update(self, screen: pygame.Surface) -> None:
        flags = 0
        for i, j in itertools.product(
            list(range(self.settings.rows)),
            list(range(self.settings.cols)),
        ):
            self.panels[i][j].update_panel(screen)
            if self.panels[i][j].is_flagged:
                flags += 1
        self.drawtext(
            screen,
            f"{flags} / {self.settings.mine_count}",
            [self.settings.screen_width - 60, 20],
        )

    def left_click(self, pos: tuple[int, int]) -> State | None:
        idx = self.pos_to_grid_index(pos)
        if self.is_within_bounds(idx):
            if not self.is_initialized:
                self.place_mine(idx)
                self.is_initialized = True
            self.open(idx)

        if self.is_cleared or self.is_game_over:
            return State.RESULT
        return None

    def right_click(self, pos: tuple[int, int]) -> None:
        idx = self.pos_to_grid_index(pos)
        if self.is_within_bounds(idx):
            self.panels[idx.row][idx.column].toggle_flag()

    @property
    def is_cleared(self) -> None:
        for i, j in itertools.product(
            list(range(self.settings.rows)),
            list(range(self.settings.cols)),
        ):
            if (
                not self.panels[i][j].get_in_mine()
                and not self.panels[i][j].get_is_revealed()
            ):
                return False
        return True

    @property
    def is_game_over(self) -> None:
        for i, j in itertools.product(
            list(range(self.settings.rows)),
            list(range(self.settings.cols)),
        ):
            if self.panels[i][j].get_in_mine() and self.panels[i][j].get_is_revealed():
                return True
        return False

    def reset(self) -> None:
        self.is_initialized = False
        self.panels = [
            [
                MinePanel().set_pos(
                    self.settings.margin + self.settings.panel_size * j,
                    self.settings.margin
                    + self.settings.header_margin
                    + self.settings.panel_size * i,
                )
                for j in range(self.settings.cols)
            ]
            for i in range(self.settings.rows)
        ]

    def peripheral_panels(self, row: int, column: int) -> list[tuple[int, int]]:
        return [
            item
            for item in itertools.product(
                [row - 1, row, row + 1],
                [column - 1, column, column + 1],
            )
            if 0 <= item[0] < self.settings.rows and 0 <= item[1] < self.settings.cols
        ]

    def pos_to_grid_index(self, pos: tuple[int, int]) -> Idx:
        x_axis, y_axis = pos
        row = (y_axis - self.settings.margin - self.settings.header_margin) // 30
        column = (x_axis - self.settings.margin) // 30
        return Idx(row, column)

    def is_within_bounds(self, idx: Idx) -> bool:
        return (
            0 <= idx.row < self.settings.rows and 0 <= idx.column < self.settings.cols
        )

    def open(self, idx: Idx, visited: set | None = None) -> None:
        if visited is None:
            visited = set()
        visited.add((idx.row, idx.column))
        if self.panels[idx.row][idx.column].neighbor_mine == 0:
            for i, j in self.peripheral_panels(idx.row, idx.column):
                if not self.panels[i][j].is_revealed and (i, j) not in visited:
                    self.open(Idx(i, j), visited)
        self.panels[idx.row][idx.column].open_panel()

    def place_mine(self, idx: Idx) -> None:
        def is_valid(num: int) -> bool:
            return 0 <= num < self.settings.rows * self.settings.cols

        mine_set = list(range(self.settings.rows * self.settings.cols))
        drop_set = (
            idx.row * self.settings.cols + idx.column,
            idx.row * self.settings.cols + idx.column - 1,
            idx.row * self.settings.cols + idx.column + 1,
            (idx.row - 1) * self.settings.cols + idx.column,
            (idx.row + 1) * self.settings.cols + idx.column,
        )
        for i in drop_set:
            if is_valid(i):
                mine_set.remove(i)

        mine_list = sorted(random.sample(mine_set, self.settings.mine_count))
        for i in mine_list:
            row, column = divmod(i, self.settings.cols)
            self.panels[row][column].set_mine()

        for i, j in itertools.product(
            list(range(self.settings.rows)),
            list(range(self.settings.cols)),
        ):
            num = 0
            for row, column in self.peripheral_panels(i, j):
                if self.panels[row][column].has_mine:
                    num += 1
            self.panels[i][j].set_nmine(num)
