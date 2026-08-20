from collections.abc import Callable
from tkinter import StringVar, ttk
from typing import Any

from millify import millify


def format_views(views: str) -> str:
    num, _ = views.split()
    return f"{millify(int(num.replace(',', '')))}"


def create_entry_with_button(
    frame: ttk.Frame,
    button_text: str,
    button_command: Callable[[], Any],
    label_text: str,
    entry_var: StringVar,
    entry_state: str = "normal",
) -> None:
    label = ttk.Label(frame, text=label_text)
    label.pack(anchor="w", padx=10)

    row = ttk.Frame(frame)
    row.pack(fill="x", padx=10, pady=5)

    input = ttk.Entry(row, textvariable=entry_var, state=entry_state)
    input.pack(side="left", fill="x", expand=True)
    button = ttk.Button(row, text=button_text, command=button_command)
    button.pack(side="left", padx=(5, 0))
