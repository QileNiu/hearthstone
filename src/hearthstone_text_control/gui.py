from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .backends import Backend, PyAutoGuiBackend
from .config import Profile, load_default_profile, load_profile
from .engine import CommandEngine


class GuiBackend:
    def __init__(self, log: "LogWriter", live: bool) -> None:
        self._log = log
        self._live = live
        self._live_backend: Backend | None = None
        if live:
            self._live_backend = PyAutoGuiBackend()

    def click(self, x: int, y: int, label: str) -> None:
        prefix = "真实点击" if self._live else "模拟点击"
        self._log.write(f"{prefix}: ({x}, {y}) - {label}")
        if self._live_backend:
            self._live_backend.click(x, y, label)

    def wait(self, seconds: float) -> None:
        self._log.write(f"等待: {seconds:.2f} 秒")
        if self._live_backend:
            self._live_backend.wait(seconds)


class LogWriter:
    def __init__(self, text: tk.Text) -> None:
        self._text = text

    def write(self, message: str) -> None:
        self._text.configure(state="normal")
        self._text.insert("end", message.rstrip() + "\n")
        self._text.see("end")
        self._text.configure(state="disabled")

    def clear(self) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")


class HearthstoneControlApp:
    def __init__(self, root: tk.Tk, profile_path: str | None, live: bool) -> None:
        self.root = root
        self.root.title("炉石文字控制器")
        self.root.geometry("900x620")
        self.root.minsize(760, 520)

        self.profile_path = tk.StringVar(value=profile_path or "内置示例配置")
        self.live_mode = tk.BooleanVar(value=live)
        self.command_text = tk.StringVar()
        self.deck_name = tk.StringVar(value="法师")
        self.hand_slot = tk.StringVar(value="1")
        self.board_slot = tk.StringVar(value="1")
        self.target_name = tk.StringVar(value="对方英雄")

        self.profile = self._load_profile(profile_path)
        self.log: LogWriter

        self._build_layout()
        self._write_startup_log()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        header = ttk.Frame(self.root, padding=(12, 10, 12, 4))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="炉石文字控制器", font=("", 16, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Checkbutton(
            header,
            text="live 模式：真实控制鼠标",
            variable=self.live_mode,
            command=self._mode_changed,
        ).grid(row=0, column=2, sticky="e")

        profile_row = ttk.Frame(self.root, padding=(12, 4))
        profile_row.grid(row=1, column=0, sticky="ew")
        profile_row.columnconfigure(1, weight=1)
        ttk.Label(profile_row, text="坐标配置").grid(row=0, column=0, sticky="w")
        ttk.Entry(profile_row, textvariable=self.profile_path, state="readonly").grid(
            row=0, column=1, sticky="ew", padx=8
        )
        ttk.Button(profile_row, text="选择配置", command=self._choose_profile).grid(
            row=0, column=2, padx=(0, 6)
        )
        ttk.Button(profile_row, text="编辑配置", command=self._open_profile).grid(
            row=0, column=3
        )

        command_row = ttk.Frame(self.root, padding=(12, 8))
        command_row.grid(row=2, column=0, sticky="ew")
        command_row.columnconfigure(0, weight=1)
        entry = ttk.Entry(command_row, textvariable=self.command_text, font=("", 13))
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        entry.bind("<Return>", lambda _event: self.execute_current_command())
        ttk.Button(command_row, text="执行命令", command=self.execute_current_command).grid(
            row=0, column=1
        )

        body = ttk.PanedWindow(self.root, orient="horizontal")
        body.grid(row=3, column=0, sticky="nsew", padx=12, pady=(4, 8))

        controls = ttk.Frame(body, padding=8)
        body.add(controls, weight=1)
        self._build_controls(controls)

        log_frame = ttk.Frame(body, padding=8)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        body.add(log_frame, weight=2)

        log_text = tk.Text(log_frame, wrap="word", height=20, state="disabled")
        log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        log_text.configure(yscrollcommand=scrollbar.set)
        self.log = LogWriter(log_text)

        footer = ttk.Frame(self.root, padding=(12, 0, 12, 10))
        footer.grid(row=4, column=0, sticky="ew")
        ttk.Button(footer, text="清空日志", command=self._clear_log).pack(side="left")
        ttk.Button(footer, text="帮助", command=lambda: self.execute_command("帮助")).pack(
            side="left", padx=6
        )
        ttk.Button(footer, text="退出", command=self.root.destroy).pack(side="right")

        entry.focus_set()

    def _build_controls(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        deck = ttk.LabelFrame(parent, text="卡组和对局", padding=8)
        deck.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        deck.columnconfigure(1, weight=1)
        ttk.Label(deck, text="卡组名").grid(row=0, column=0, sticky="w")
        ttk.Entry(deck, textvariable=self.deck_name).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(deck, text="选择卡组", command=self._select_deck).grid(row=0, column=2)
        ttk.Button(deck, text="开始游戏", command=lambda: self.execute_command("开始游戏")).grid(
            row=1, column=0, sticky="ew", pady=(8, 0)
        )
        ttk.Button(deck, text="结束回合", command=lambda: self.execute_command("结束回合")).grid(
            row=1, column=1, columnspan=2, sticky="ew", padx=(6, 0), pady=(8, 0)
        )

        card = ttk.LabelFrame(parent, text="出牌", padding=8)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        card.columnconfigure(1, weight=1)
        ttk.Label(card, text="手牌编号").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(card, from_=1, to=10, textvariable=self.hand_slot, width=5).grid(
            row=0, column=1, sticky="w", padx=6
        )
        ttk.Label(card, text="目标").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(card, textvariable=self.target_name).grid(
            row=1, column=1, sticky="ew", padx=6, pady=(8, 0)
        )
        ttk.Button(card, text="出牌", command=self._play_card).grid(row=0, column=2)
        ttk.Button(card, text="出牌到目标", command=self._play_card_to_target).grid(
            row=1, column=2, pady=(8, 0)
        )

        attack = ttk.LabelFrame(parent, text="攻击", padding=8)
        attack.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        attack.columnconfigure(1, weight=1)
        ttk.Label(attack, text="我方随从编号").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(attack, from_=1, to=7, textvariable=self.board_slot, width=5).grid(
            row=0, column=1, sticky="w", padx=6
        )
        ttk.Button(attack, text="打脸", command=self._attack_face).grid(row=0, column=2)
        ttk.Button(attack, text="攻击目标", command=self._attack_target).grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0)
        )

        quick = ttk.LabelFrame(parent, text="快捷点击", padding=8)
        quick.grid(row=3, column=0, sticky="ew")
        for index, (label, command) in enumerate(
            [
                ("对方英雄", "点击 对方英雄"),
                ("我方英雄", "点击 我方英雄"),
                ("英雄技能", "点击 英雄技能"),
                ("确认", "点击 确认"),
            ]
        ):
            ttk.Button(quick, text=label, command=lambda value=command: self.execute_command(value)).grid(
                row=index // 2, column=index % 2, sticky="ew", padx=3, pady=3
            )
        quick.columnconfigure(0, weight=1)
        quick.columnconfigure(1, weight=1)

    def _load_profile(self, profile_path: str | None) -> Profile:
        if profile_path:
            return load_profile(profile_path)
        return load_default_profile()

    def _make_engine(self) -> CommandEngine:
        return CommandEngine(self.profile, GuiBackend(self.log, self.live_mode.get()))

    def execute_current_command(self) -> None:
        command = self.command_text.get().strip()
        if command:
            self.execute_command(command)
            self.command_text.set("")

    def execute_command(self, command: str) -> None:
        self.log.write(f"> {command}")
        try:
            result = self._make_engine().execute(command)
        except Exception as exc:  # Tkinter callback boundary: show actionable errors in UI.
            messagebox.showerror("执行失败", str(exc))
            self.log.write(f"错误: {exc}")
            return
        if result.message:
            self.log.write(result.message)
        if result.should_exit:
            self.root.destroy()

    def _select_deck(self) -> None:
        self.execute_command(f"选择卡组 {self.deck_name.get().strip()}")

    def _play_card(self) -> None:
        self.execute_command(f"出牌 {self.hand_slot.get().strip()}")

    def _play_card_to_target(self) -> None:
        self.execute_command(
            f"出牌 {self.hand_slot.get().strip()} 目标 {self.target_name.get().strip()}"
        )

    def _attack_face(self) -> None:
        self.execute_command(f"打脸 {self.board_slot.get().strip()}")

    def _attack_target(self) -> None:
        self.execute_command(
            f"攻击 {self.board_slot.get().strip()} {self.target_name.get().strip()}"
        )

    def _choose_profile(self) -> None:
        path = filedialog.askopenfilename(
            title="选择坐标配置文件",
            filetypes=[("JSON 配置", "*.json"), ("所有文件", "*.*")],
        )
        if not path:
            return
        try:
            self.profile = load_profile(path)
        except Exception as exc:
            messagebox.showerror("配置读取失败", str(exc))
            return
        self.profile_path.set(path)
        self.log.write(f"已加载配置: {path}")

    def _open_profile(self) -> None:
        path = self.profile_path.get()
        if path == "内置示例配置":
            messagebox.showinfo("无法编辑内置配置", "请先选择或安装目录中的 profile.json。")
            return
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
            return
        subprocess.Popen(["xdg-open", path])

    def _mode_changed(self) -> None:
        mode = "live：真实控制鼠标" if self.live_mode.get() else "dry-run：只显示动作"
        self.log.write(f"模式切换为 {mode}")

    def _clear_log(self) -> None:
        self.log.clear()

    def _write_startup_log(self) -> None:
        self.log.write("程序已启动。")
        self.log.write(f"当前配置: {self.profile_path.get()}")
        mode = "live：真实控制鼠标" if self.live_mode.get() else "dry-run：只显示动作"
        self.log.write(f"当前模式: {mode}")
        self.log.write("建议第一次先关闭 live 模式进行测试。")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = tk.Tk()
    HearthstoneControlApp(root, profile_path=args.profile, live=args.live)
    root.mainloop()
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="炉石文字控制器 GUI")
    parser.add_argument("--profile", help="坐标配置 JSON 文件路径。")
    parser.add_argument("--live", action="store_true", help="启动时启用 live 鼠标控制模式。")
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
