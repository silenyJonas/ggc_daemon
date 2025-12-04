import tkinter as tk
from tkinter import ttk
import threading
import time
from services.base_tab import BaseTab
from managers.berimond_green_manager import BerimondGreenManager


class BerimondGreenTab(BaseTab, ttk.Frame):
    """Záložka – Berimond Green."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.manager = BerimondGreenManager()

        # --- Default values ---
        self.is_running = False
        self.color_type = "all"
        self.feather_horses = True
        self.attack_count = 10
        self.delay_attack = 2

        # --- Default camp coordinates ---
        self.default_green = [
            [811, 339],
            [812, 340],
            [816, 343],
            [815, 345],
            [815, 347]
        ]
        self.default_red = [
            [810, 340],
            [807, 341],
            [806, 344],
            [816, 339],
            [817, 340]
        ]

        # arrays: budou naplněny Entry
        self.green_array = [[0, 0] for _ in range(5)]
        self.red_array = [[0, 0] for _ in range(5)]

        self.create_widgets()
        self._fill_default_entries()

    def create_widgets(self):
        """GUI prvky."""

        # --- COLOR TYPE ---
        color_frame = ttk.Frame(self)
        color_frame.pack(pady=10, anchor="w")
        ttk.Label(color_frame, text="Typ barvy:").pack(side=tk.LEFT, padx=(0, 10))

        self.color_var = tk.StringVar(value=self.color_type)
        ttk.Radiobutton(color_frame, text="Red", variable=self.color_var, value="red",
                        command=self._on_color_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(color_frame, text="Blue", variable=self.color_var, value="blue",
                        command=self._on_color_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(color_frame, text="All", variable=self.color_var, value="all",
                        command=self._on_color_changed).pack(side=tk.LEFT, padx=5)

        # --- HORSES ---
        horse_frame = ttk.Frame(self)
        horse_frame.pack(pady=10, anchor="w")
        ttk.Label(horse_frame, text="Typ koně:").pack(side=tk.LEFT, padx=(0, 10))

        self.feather_horses_var = tk.BooleanVar(value=self.feather_horses)
        ttk.Radiobutton(horse_frame, text="Gold koně", variable=self.feather_horses_var, value=False,
                        command=self._on_horse_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(horse_frame, text="Pírko koně", variable=self.feather_horses_var, value=True,
                        command=self._on_horse_changed).pack(side=tk.LEFT, padx=5)

        # --- ATTACK COUNT ---
        attack_frame = ttk.Frame(self)
        attack_frame.pack(pady=5, anchor="w")
        ttk.Label(attack_frame, text="Počet útoků:").pack(side=tk.LEFT, padx=(0, 5))
        self.attack_entry = ttk.Entry(attack_frame, width=10)
        self.attack_entry.insert(0, str(self.attack_count))
        self.attack_entry.pack(side=tk.LEFT)

        # --- DELAY ATTACK ---
        delay_frame = ttk.Frame(self)
        delay_frame.pack(pady=5, anchor="w")
        ttk.Label(delay_frame, text="Delay mezi útoky (s):").pack(side=tk.LEFT, padx=(0, 5))
        self.delay_entry = ttk.Entry(delay_frame, width=10)
        self.delay_entry.insert(0, str(self.delay_attack))
        self.delay_entry.pack(side=tk.LEFT)

        # --- GREEN CAMPS 1–5 ---
        ttk.Label(self, text="Green tábory (1–5):").pack(pady=(10, 3), anchor="w")
        self.green_entries = []
        for i in range(5):
            frame = ttk.Frame(self)
            frame.pack(pady=2, anchor="w")
            ttk.Label(frame, text=f"Tabor {i+1}: X").pack(side=tk.LEFT)
            x_entry = ttk.Entry(frame, width=6)
            x_entry.pack(side=tk.LEFT, padx=3)
            ttk.Label(frame, text="Y").pack(side=tk.LEFT)
            y_entry = ttk.Entry(frame, width=6)
            y_entry.pack(side=tk.LEFT, padx=3)
            self.green_entries.append((x_entry, y_entry))

        # --- RED CAMPS 1–5 ---
        ttk.Label(self, text="Red tábory (1–5):").pack(pady=(10, 3), anchor="w")
        self.red_entries = []
        for i in range(5):
            frame = ttk.Frame(self)
            frame.pack(pady=2, anchor="w")
            ttk.Label(frame, text=f"Tabor {i+1}: X").pack(side=tk.LEFT)
            x_entry = ttk.Entry(frame, width=6)
            x_entry.pack(side=tk.LEFT, padx=3)
            ttk.Label(frame, text="Y").pack(side=tk.LEFT)
            y_entry = ttk.Entry(frame, width=6)
            y_entry.pack(side=tk.LEFT, padx=3)
            self.red_entries.append((x_entry, y_entry))

        # --- START / STOP ---
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=15, anchor="center")
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_action)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_action)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def _fill_default_entries(self):
        """Předvyplní Entry pole defaultními souřadnicemi."""
        for i, (x, y) in enumerate(self.default_green):
            x_entry, y_entry = self.green_entries[i]
            x_entry.delete(0, "end")
            x_entry.insert(0, str(x))
            y_entry.delete(0, "end")
            y_entry.insert(0, str(y))

        for i, (x, y) in enumerate(self.default_red):
            x_entry, y_entry = self.red_entries[i]
            x_entry.delete(0, "end")
            x_entry.insert(0, str(x))
            y_entry.delete(0, "end")
            y_entry.insert(0, str(y))

    # ======================
    # CALLBACKS
    # ======================
    def _on_color_changed(self):
        self.color_type = self.color_var.get()
        self.log_message(status="info", message=f"Barva změněna na: {self.color_type}")

    def _on_horse_changed(self):
        self.feather_horses = bool(self.feather_horses_var.get())
        horse_type = "Pírko" if self.feather_horses else "Gold"
        self.log_message(status="info", message=f"Typ koně změněn na: {horse_type}")

    # ======================
    # START / STOP
    # ======================
    def start_action(self):
        if self.is_running:
            self.log_message(status="info", message="Akce již běží!")
            return

        # --- ALWAYS RESET ARRAYS, REMOVE OLD INVALID DATA ---
        self.green_array = [[0, 0] for _ in range(5)]
        self.red_array = [[0, 0] for _ in range(5)]

        try:
            self.attack_count = int(self.attack_entry.get())
            self.delay_attack = int(self.delay_entry.get())

            # --- read green camps ---
            for i in range(5):
                self.green_array[i] = [
                    int(self.green_entries[i][0].get()),
                    int(self.green_entries[i][1].get())
                ]

            # --- read red camps ---
            for i in range(5):
                self.red_array[i] = [
                    int(self.red_entries[i][0].get()),
                    int(self.red_entries[i][1].get())
                ]

        except ValueError:
            self.log_message(status="error", message="Chyba: zadejte platná čísla pro tábory a útoky.")
            return

        self.is_running = True
        self.log_message(status="info", message="Akce spuštěna!")

        threading.Thread(target=self._run_loop, daemon=True).start()

    def stop_action(self):
        if not self.is_running:
            self.log_message(status="info", message="Akce není spuštěna!")
            return
        self.is_running = False
        self.log_message(status="info", message="Akce zastavena.")

    def _run_loop(self):
        """Smyčka s odpočtem."""
        countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")

        for x in range(countdown, 0, -1):
            if not self.is_running:
                self.log_message(status="info", message="Akce přerušena během odpočtu.")
                return
            self.log_message(status="info", message=f"Spuštění za: {x}")
            time.sleep(1)

        self.log_message(status="info", message="Hlavní akce spuštěna!")

        try:
            self.manager.RunBerimondGreenManager(
                color_type=self.color_type,
                green_array=self.green_array,
                red_array=self.red_array,
                attack_count=self.attack_count,
                delay_attack=self.delay_attack,
                feather_horses=self.feather_horses
            )
        except Exception as e:
            self.log_message(status="error", message=f"Chyba při spuštění RunBerimondGreenManager: {e}")

        self.is_running = False
        self.log_message(status="info", message="Akce dokončena.")
