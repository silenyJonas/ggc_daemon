# tabs/baron.py
import tkinter as tk
from tkinter import ttk
import threading
import time
from services.base_tab import BaseTab


class TutorialTab(BaseTab, ttk.Frame):
    """Třída pro záložku Baronů, která dědí z BaseTab."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Initialize start_index and end_index with default values
        self.nodes = [
            "PISEK BARONI - [samu;zebriky;pirkokone] tak jet indexy 1-135 [34minut], 136-150 [3minuty]",
            "PISEK BARONI - [samu;zebriky;zlatokone]xxxx ",
            "OHEN BARONI - [samu;zebriky;pirkokone] tak jet indexy 1-127 [32minut], 128-150 [2miunty]",
            "OHEN BARONI - [samu;zebriky;pirkokone] tak jet indexy 1-85, 86-120, 121-150",

        ]

        self.create_widgets()


    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""

        test_frame = ttk.Frame(self)
        test_frame.pack(pady=20, fill="x")

        for x in range(len(self.nodes)):
            ttk.Label(test_frame, text=self.nodes[x]).pack(anchor="w", fill="x")




