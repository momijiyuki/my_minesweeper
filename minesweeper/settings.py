from enum import Enum
from typing import NamedTuple


class State(Enum):
    TITLE = "title"
    GAME = "game"
    RESULT = "result"


class Idx(NamedTuple):
    row: int
    column: int


class GameSettings:
    LEFTCLICK = 1
    RIGHTCLICK = 3

    def __init__(
        self,
        rows: int = 16,
        cols: int = 16,
        mine_count: int = 40,
        margin: int = 10,
        header_height: int = 20,
    ) -> None:
        self.rows = max(8, rows)
        self.cols = max(8, cols)
        if (self.rows - 1) * (self.cols - 1) < mine_count:
            self.mine_count = (self.rows - 1) * (self.cols - 1)
        elif mine_count < 10:  # noqa: PLR2004
            self.mine_count = 10
        else:
            self.mine_count = mine_count

        self.margin = margin
        self.header_margin = header_height
        self.panel_size = 30
        self.font_size = 26

        self.img_paths = {
            "bg_panel": "./img/bg_panel.png",
            "closed_panel": "./img/panel.png",
            "mine_flag": "./img/30pxflag.png",
        }

    @property
    def screen_width(self) -> int:
        return self.panel_size * self.cols + 2 * self.margin

    @property
    def screen_height(self) -> int:
        return self.panel_size * self.rows + 2 * self.margin + self.header_margin

    @property
    def window_size(self) -> tuple[int, int]:
        return self.screen_width, self.screen_height
