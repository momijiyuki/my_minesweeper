# !/usr/bin/env python3
import pygame

from minesweeper.screens import Fields
from minesweeper.screens import MineField
from minesweeper.screens import Result
from minesweeper.screens import Title
from minesweeper.settings import GameSettings
from minesweeper.settings import State


__all__ = ["MineSweeper"]


class MineSweeper:
    def __init__(self, settings: GameSettings = None) -> None:
        self.settings = settings if settings is not None else GameSettings()
        self.controller: dict[State, Fields] = {
            State.TITLE: Title(self.settings),
            State.GAME: MineField(self.settings),
            State.RESULT: Result(self.settings),
        }
        self.state = State.GAME
        self.game_state = False

    def screen_update(self, screen: pygame.Surface) -> None:
        if self.state == State.GAME:
            self.controller[self.state].screen_update(screen)

        if self.state == State.RESULT:
            self.controller[self.state].screen_update(
                screen,
                gamestate=self.controller[State.GAME].is_cleared,
            )

    def clicked(
        self,
        pos: tuple[int, int],
        event_button: int,
    ) -> None:
        if event_button == self.settings.LEFTCLICK:
            # cliked
            result = self.controller[self.state].left_click(pos)
            if result is not None:
                self.state = result
                if self.state == State.GAME:
                    self.controller[self.state].reset()
        elif event_button == self.settings.RIGHTCLICK:
            # right clicked
            self.controller[self.state].right_click(pos)
