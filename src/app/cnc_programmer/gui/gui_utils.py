from __future__ import annotations

from tkinter import ttk, NORMAL


def _generate_label_entry_pair(frame: ttk.Frame | ttk.LabelFrame, label_text: str, row: int, column: int, padx: tuple[float, float], pady: tuple[float, float], state=NORMAL) -> (ttk.Label, ttk.Entry):
    label = ttk.Label(frame, text=label_text)
    label.grid(row=row, column=column, padx=padx, pady=pady, sticky="nsew")
    entry = ttk.Entry(frame, state=state)
    entry.grid(row=row, column=column + 1, padx=padx, pady=pady, sticky="nsew")
    return label, entry


def set_column_weights(frame: ttk.Frame | ttk.LabelFrame, column_weights):
    for index, weight in enumerate(column_weights):
        frame.columnconfigure(index, weight=weight)

