from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Protocol, TextIO


class Backend(Protocol):
    def click(self, x: int, y: int, label: str) -> None:
        """Click a screen coordinate."""

    def wait(self, seconds: float) -> None:
        """Wait for a number of seconds."""


@dataclass
class DryRunBackend:
    stream: TextIO = sys.stdout

    def click(self, x: int, y: int, label: str) -> None:
        print(f"CLICK {x} {y} # {label}", file=self.stream)

    def wait(self, seconds: float) -> None:
        print(f"WAIT {seconds:.2f}s", file=self.stream)


class PyAutoGuiBackend:
    def __init__(self) -> None:
        try:
            import pyautogui
        except ImportError as exc:
            raise RuntimeError(
                "Live mode requires pyautogui. Install with: python -m pip install -e \".[windows]\""
            ) from exc

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.02
        self._pyautogui = pyautogui

    def click(self, x: int, y: int, label: str) -> None:
        self._pyautogui.click(x=x, y=y)

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)
