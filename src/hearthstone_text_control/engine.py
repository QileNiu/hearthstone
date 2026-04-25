from __future__ import annotations

from dataclasses import dataclass

from .backends import Backend
from .config import Point, Profile


HELP_TEXT = """Available commands:
  帮助
  选择卡组 <名称>
  开始游戏
  出牌 <手牌编号>
  出牌 <手牌编号> 目标 <目标>
  打脸
  打脸 <己方随从编号>
  攻击 <己方随从编号> <目标>
  结束回合
  点击 <配置点名称>
  等待 <秒数>
  退出
"""


@dataclass
class CommandResult:
    message: str | None = None
    should_exit: bool = False


class CommandEngine:
    def __init__(self, profile: Profile, backend: Backend) -> None:
        self.profile = profile
        self.backend = backend

    def execute(self, line: str) -> CommandResult:
        text = line.strip()
        if not text:
            return CommandResult()

        parts = text.split()
        verb = parts[0]

        if verb in {"帮助", "help", "?"}:
            return CommandResult(HELP_TEXT)
        if verb in {"退出", "quit", "exit"}:
            return CommandResult("Bye.", should_exit=True)
        if verb in {"选择卡组", "选卡组"}:
            return self._select_deck(parts)
        if verb in {"开始游戏", "开始"}:
            return self._click_point("play_button", "开始游戏")
        if verb in {"结束回合", "结束"}:
            return self._click_point("end_turn", "结束回合")
        if verb == "出牌":
            return self._play_card(parts)
        if verb == "打脸":
            return self._attack_face(parts)
        if verb == "攻击":
            return self._attack(parts)
        if verb == "点击":
            return self._manual_click(parts)
        if verb == "等待":
            return self._wait(parts)

        return CommandResult(f"Unknown command: {text}")

    def _select_deck(self, parts: list[str]) -> CommandResult:
        if len(parts) < 2:
            return CommandResult("Usage: 选择卡组 <名称>")
        deck_name = " ".join(parts[1:])
        point = self.profile.decks.get(deck_name)
        if point is None:
            known = ", ".join(sorted(self.profile.decks))
            return CommandResult(f"Unknown deck '{deck_name}'. Known decks: {known}")
        self._click(point, f"deck:{deck_name}")
        return CommandResult(f"Selected deck: {deck_name}")

    def _play_card(self, parts: list[str]) -> CommandResult:
        if len(parts) < 2:
            return CommandResult("Usage: 出牌 <手牌编号> [目标 <目标>]")
        hand_slot = parts[1]
        point = self.profile.hand_slots.get(hand_slot)
        if point is None:
            known = ", ".join(sorted(self.profile.hand_slots, key=int))
            return CommandResult(f"Unknown hand slot '{hand_slot}'. Known slots: {known}")

        self._click(point, f"hand:{hand_slot}")
        if len(parts) >= 4 and parts[2] == "目标":
            target_name = " ".join(parts[3:])
            try:
                target = self.profile.resolve_target(target_name)
            except ValueError as exc:
                return CommandResult(str(exc))
            self._click(target, f"target:{target_name}")
        elif len(parts) > 2:
            target_name = " ".join(parts[2:])
            try:
                target = self.profile.resolve_target(target_name)
            except ValueError as exc:
                return CommandResult(str(exc))
            self._click(target, f"target:{target_name}")

        return CommandResult(f"Played hand slot: {hand_slot}")

    def _attack_face(self, parts: list[str]) -> CommandResult:
        if len(parts) == 1:
            return self._click_point("enemy_hero", "打脸")
        source = parts[1]
        point = self.profile.board_slots.get(source)
        if point is None:
            known = ", ".join(sorted(self.profile.board_slots, key=int))
            return CommandResult(f"Unknown board slot '{source}'. Known slots: {known}")
        self._click(point, f"board:{source}")
        self._click(self.profile.resolve_point("enemy_hero"), "enemy_hero")
        return CommandResult(f"Attacked enemy hero with board slot: {source}")

    def _attack(self, parts: list[str]) -> CommandResult:
        if len(parts) < 3:
            return CommandResult("Usage: 攻击 <己方随从编号> <目标>")
        source = parts[1]
        target_name = " ".join(parts[2:])
        source_point = self.profile.board_slots.get(source)
        if source_point is None:
            known = ", ".join(sorted(self.profile.board_slots, key=int))
            return CommandResult(f"Unknown board slot '{source}'. Known slots: {known}")
        try:
            target = self.profile.resolve_target(target_name)
        except ValueError as exc:
            return CommandResult(str(exc))
        self._click(source_point, f"board:{source}")
        self._click(target, f"target:{target_name}")
        return CommandResult(f"Attacked {target_name} with board slot: {source}")

    def _manual_click(self, parts: list[str]) -> CommandResult:
        if len(parts) < 2:
            return CommandResult("Usage: 点击 <配置点名称>")
        point_name = " ".join(parts[1:])
        try:
            point = self.profile.resolve_point(point_name)
        except ValueError as exc:
            return CommandResult(str(exc))
        self._click(point, f"point:{point_name}")
        return CommandResult(f"Clicked point: {point_name}")

    def _wait(self, parts: list[str]) -> CommandResult:
        if len(parts) != 2:
            return CommandResult("Usage: 等待 <秒数>")
        try:
            seconds = float(parts[1])
        except ValueError:
            return CommandResult("Wait seconds must be a number.")
        if seconds < 0:
            return CommandResult("Wait seconds must be non-negative.")
        self.backend.wait(seconds)
        return CommandResult(f"Waited {seconds:.2f}s")

    def _click_point(self, point_name: str, label: str) -> CommandResult:
        self._click(self.profile.resolve_point(point_name), label)
        return CommandResult(f"Clicked: {label}")

    def _click(self, point: Point, label: str) -> None:
        self.backend.click(point.x, point.y, label)
        if self.profile.wait_after_action_seconds > 0:
            self.backend.wait(self.profile.wait_after_action_seconds)
