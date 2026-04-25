from __future__ import annotations

import unittest

from hearthstone_text_control.backends import DryRunBackend
from hearthstone_text_control.config import Point, Profile
from hearthstone_text_control.engine import CommandEngine


class RecordingBackend(DryRunBackend):
    def __init__(self) -> None:
        self.events: list[tuple[str, int | float, int | None, str | None]] = []

    def click(self, x: int, y: int, label: str) -> None:
        self.events.append(("click", x, y, label))

    def wait(self, seconds: float) -> None:
        self.events.append(("wait", seconds, None, None))


class CommandEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = RecordingBackend()
        profile = Profile(
            name="test",
            points={
                "play_button": Point(10, 20),
                "end_turn": Point(30, 40),
                "enemy_hero": Point(50, 60),
            },
            decks={"法师": Point(70, 80)},
            hand_slots={"1": Point(90, 100)},
            board_slots={"1": Point(110, 120)},
            aliases={"对方英雄": "enemy_hero"},
            wait_after_action_seconds=0,
        )
        self.engine = CommandEngine(profile, self.backend)

    def test_select_deck(self) -> None:
        result = self.engine.execute("选择卡组 法师")

        self.assertEqual(result.message, "Selected deck: 法师")
        self.assertEqual(self.backend.events, [("click", 70, 80, "deck:法师")])

    def test_play_card_with_target(self) -> None:
        result = self.engine.execute("出牌 1 目标 对方英雄")

        self.assertEqual(result.message, "Played hand slot: 1")
        self.assertEqual(
            self.backend.events,
            [
                ("click", 90, 100, "hand:1"),
                ("click", 50, 60, "target:对方英雄"),
            ],
        )

    def test_attack_face_with_board_slot(self) -> None:
        result = self.engine.execute("打脸 1")

        self.assertEqual(result.message, "Attacked enemy hero with board slot: 1")
        self.assertEqual(
            self.backend.events,
            [
                ("click", 110, 120, "board:1"),
                ("click", 50, 60, "enemy_hero"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
