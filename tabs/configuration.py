import tkinter as tk
from tkinter import ttk


class ConfigurationTab(ttk.Frame):
    """Záložka pro úpravu konfigurace JSON."""

    def __init__(self, parent, config_manager, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_manager = config_manager
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):

        # Rámeček pro celý obsah, který bude obsahovat grid
        content_frame = ttk.Frame(self)
        content_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Načteme data z JSONu
        castle_data = self.config_manager.data.get("main_castle_cords", {})

        row = 0
        for color, coords in castle_data.items():
            # Nadpis pro barvu hradu
            color_label = ttk.Label(content_frame, text=f"{color.capitalize()}", font=("Arial", 12, "bold"))
            color_label.grid(row=row, column=0, columnspan=2, pady=(10, 5), sticky="w")
            row += 1

            # Vstupní pole pro X
            x_label = ttk.Label(content_frame, text="X:")
            x_label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
            x_entry = ttk.Entry(content_frame)
            x_entry.insert(0, str(coords.get("x", 0)))
            x_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            row += 1

            # Vstupní pole pro Y
            y_label = ttk.Label(content_frame, text="Y:")
            y_label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
            y_entry = ttk.Entry(content_frame)
            y_entry.insert(0, str(coords.get("y", 0)))
            y_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            row += 1

            # Uložíme reference na políčka
            self.entries[color] = {"x": x_entry, "y": y_entry}

        # Konfigurace sloupce pro roztažení
        content_frame.grid_columnconfigure(1, weight=1)

        # Tlačítko pro uložení změn
        save_button = ttk.Button(self, text="Uložit změny", command=self.save_changes)
        save_button.pack(pady=20)

    def save_changes(self):
        """
        Přečte data z inputů, aktualizuje data ve správci konfigurace
        a uloží je do JSON souboru.
        """
        try:
            for color, entry_pair in self.entries.items():
                x_val = int(entry_pair["x"].get())
                y_val = int(entry_pair["y"].get())

                self.config_manager.data["main_castle_cords"][color]["x"] = x_val
                self.config_manager.data["main_castle_cords"][color]["y"] = y_val

            self.config_manager.save_config()
            print("Konfigurace hradů byla uložena!")

        except ValueError:
            print("Chyba: Vstupní pole musí obsahovat platná celá čísla.")