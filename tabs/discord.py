import tkinter as tk
from tkinter import ttk

class DiscordTab(ttk.Frame):
    """Sedmá záložka - ukázka."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""
        label = ttk.Label(self, text="Toto je obsah sedmé záložky.")
        label.pack(padx=20, pady=20)

        button = ttk.Button(self, text="Tlačítko 7", command=self.button_action)
        button.pack(pady=10)

    def button_action(self):
        """Akce, která se provede po stisknutí tlačítka."""
        print("Akce z Tab7 byla provedena.")