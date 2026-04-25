from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class Profile:
    name: str
    points: dict[str, Point]
    decks: dict[str, Point]
    hand_slots: dict[str, Point]
    board_slots: dict[str, Point]
    aliases: dict[str, str]
    wait_after_action_seconds: float = 0.15

    def resolve_point(self, name: str) -> Point:
        key = self.aliases.get(name, name)
        if key not in self.points:
            known = ", ".join(sorted(self.points | self.aliases))
            raise ValueError(f"Unknown point '{name}'. Known points: {known}")
        return self.points[key]

    def resolve_target(self, name: str) -> Point:
        if name in self.board_slots:
            return self.board_slots[name]
        return self.resolve_point(name)


def load_profile(path: str | Path) -> Profile:
    profile_path = Path(path)
    with profile_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    return profile_from_data(data, str(data.get("name") or profile_path.stem))


def load_default_profile() -> Profile:
    profile_file = resources.files("hearthstone_text_control.profiles").joinpath(
        "example_profile.json"
    )
    with profile_file.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    return profile_from_data(data, str(data.get("name") or "bundled-example"))


def profile_from_data(data: dict[str, Any], fallback_name: str) -> Profile:
    return Profile(
        name=str(data.get("name") or fallback_name),
        points=_load_points(data.get("points", {}), "points"),
        decks=_load_points(data.get("decks", {}), "decks"),
        hand_slots=_load_points(data.get("hand_slots", {}), "hand_slots"),
        board_slots=_load_points(data.get("board_slots", {}), "board_slots"),
        aliases={str(k): str(v) for k, v in data.get("aliases", {}).items()},
        wait_after_action_seconds=float(data.get("wait_after_action_seconds", 0.15)),
    )


def _load_points(raw: dict[str, Any], section: str) -> dict[str, Point]:
    points: dict[str, Point] = {}
    for name, value in raw.items():
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError(f"{section}.{name} must be a two-item [x, y] coordinate")
        points[str(name)] = Point(int(value[0]), int(value[1]))
    return points
