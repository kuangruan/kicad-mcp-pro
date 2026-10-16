"""KiCad 10 IPC toolbar action for KiCad MCP Pro Companion.

KiCad launches this file in its plugin-specific Python environment.
"""

from __future__ import annotations

import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import ttk

from companion_core import backend_status, board_summary, dashboard_url, sync_board_context

BG = "#0d121d"
SURFACE = "#171f2d"
BORDER = "#303c4d"
TEXT = "#e5edf8"
MUTED = "#9aaac0"
ACCENT = "#80bfff"
GREEN = "#54d6a1"


def label(
    parent: tk.Misc,
    value: str,
    *,
    size: int = 11,
    color: str = TEXT,
    weight: str = "normal",
) -> tk.Label:
    return tk.Label(
        parent,
        text=value,
        bg=parent.cget("bg"),
        fg=color,
        font=("Segoe UI", size, weight),
        anchor="w",
        justify="left",
    )


def section(parent: tk.Misc, title: str) -> tk.Frame:
    frame = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
    frame.pack(fill="x", pady=(0, 12))
    label(frame, title, color=ACCENT, weight="bold").pack(fill="x", padx=18, pady=(14, 8))
    return frame


class CompanionWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("KiCad MCP Pro · Companion")
        root.geometry("560x605")
        root.minsize(490, 580)
        root.configure(bg=BG)

        style = ttk.Style(root)
        style.configure("Companion.TButton", font=("Segoe UI", 10), padding=(14, 9))
        container = tk.Frame(root, bg=BG, padx=22, pady=18)
        container.pack(fill="both", expand=True)

        label(container, "KiCad MCP Pro", size=20, weight="bold").pack(fill="x")
        label(
            container,
            "PCB Editor companion · read-only preview",
            color=MUTED,
        ).pack(fill="x", pady=(1, 18))

        card = section(container, "ACTIVE PCB")
        self.board_text = label(card, "Connecting to KiCad…", size=12, weight="bold")
        self.board_text.pack(fill="x", padx=18, pady=(0, 5))
        self.details_text = label(card, "Footprints · Nets · Selection", color=MUTED)
        self.details_text.pack(fill="x", padx=18, pady=(0, 17))

        service = section(container, "ENGINEERING SERVICE")
        self.service_text = label(service, "Checking local backend…", color=MUTED)
        self.service_text.pack(fill="x", padx=18, pady=(0, 17))

        actions = section(container, "WORKSPACE")
        label(
            actions,
            "Use the installed MCP Pro dashboard for tools and design reviews.",
            color=MUTED,
        ).pack(fill="x", padx=18, pady=(0, 10))
        row = tk.Frame(actions, bg=SURFACE)
        row.pack(fill="x", padx=18, pady=(0, 16))
        self.open_button = ttk.Button(
            row,
            text="Open dashboard",
            style="Companion.TButton",
            command=self.open_dashboard,
        )
        self.open_button.pack(side="left", padx=(0, 8))
        self.tools_button = ttk.Button(
            row,
            text="Review tools",
            style="Companion.TButton",
            command=lambda: self.open_dashboard("#tools-catalog"),
        )
        self.tools_button.pack(side="left")

        ttk.Button(
            container,
            text="Refresh KiCad and backend status",
            style="Companion.TButton",
            command=self.refresh,
        ).pack(fill="x", pady=(0, 12))
        self.sync_button = ttk.Button(
            container,
            text="Sync active PCB context to MCP Pro",
            style="Companion.TButton",
            command=self.sync_context,
        )
        self.sync_button.pack(fill="x", pady=(0, 12))
        label(
            container,
            "Sync shares board context only. No PCB edits are performed.",
            color=MUTED,
        ).pack(fill="x")

        self.ready = False
        self.board = None
        root.after(50, self.refresh)

    def refresh(self) -> None:
        try:
            board = board_summary()
        except Exception:
            self.board = None
            self.board_text.config(text="KiCad PCB context unavailable", fg=MUTED)
            self.details_text.config(text="Open a PCB in KiCad 10 and enable the IPC API.")
        else:
            self.board = board
            self.board_text.config(text=board.name or "Untitled board", fg=TEXT)
            self.details_text.config(
                text=f"{board.project}   ·   {board.footprints} footprints   ·   "
                f"{board.nets} nets   ·   {board.selected} selected"
            )

        self.ready, status = backend_status()
        self.service_text.config(text=status, fg=GREEN if self.ready else MUTED)
        state = "normal" if self.ready else "disabled"
        self.open_button.configure(state=state)
        self.tools_button.configure(state=state)
        self.sync_button.configure(
            state="normal" if self.ready and self.board is not None else "disabled"
        )

    def sync_context(self) -> None:
        if not self.ready or self.board is None:
            return
        snapshot = self.board
        self.sync_button.configure(state="disabled")
        self.service_text.config(text="Syncing context...", fg=MUTED)

        def work() -> None:
            try:
                sync_board_context(snapshot)
            except Exception:
                self.root.after(
                    0,
                    lambda: self._sync_done("Context sync failed; check backend access.", False),
                )
            else:
                self.root.after(0, lambda: self._sync_done("PCB context synced.", True))

        threading.Thread(target=work, daemon=True, name="kicad-mcp-context-sync").start()

    def _sync_done(self, message: str, success: bool) -> None:
        self.service_text.config(text=message, fg=GREEN if success else MUTED)
        self.sync_button.configure(state="normal" if self.ready else "disabled")

    def open_dashboard(self, fragment: str = "") -> None:
        if self.ready:
            try:
                url = dashboard_url(fragment)
            except ValueError:
                self.service_text.config(text="Dashboard URL must use loopback.", fg=MUTED)
            else:
                webbrowser.open(url)


def main() -> int:
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"KiCad MCP Pro Companion needs a graphical desktop: {exc}", file=sys.stderr)
        return 1
    CompanionWindow(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
