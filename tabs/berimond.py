import tkinter as tk
from tkinter import ttk
import threading
import time
from services.base_tab import BaseTab  # dedeno z BaseTab, aby bylo možné logovat
from managers.berimond_continent_manager import BerimondContinentManager

class BerimondTab(BaseTab, ttk.Frame):
    """Čtvrtá záložka - Berimond."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.manager = BerimondContinentManager()
        # --- Výchozí hodnoty ---
        self.is_running = False
        self.feather_horses = True
        self.max_attacks = 10
        self.attacks_between_refill = 3
        self.units_from_left = 1  # nové pole jednotky na plnění z leva
        self.delay_between_attacks = 2

        self.create_widgets()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""

        # --- Typ koně ---
        horse_frame = ttk.Frame(self)
        horse_frame.pack(pady=10, anchor="w")
        ttk.Label(horse_frame, text="Typ koně:").pack(side=tk.LEFT, padx=(0, 10))

        self.feather_horses_var = tk.BooleanVar(value=self.feather_horses)
        ttk.Radiobutton(horse_frame, text="Gold koně", variable=self.feather_horses_var, value=False,
                        command=self._on_horse_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(horse_frame, text="Pírko koně", variable=self.feather_horses_var, value=True,
                        command=self._on_horse_changed).pack(side=tk.LEFT, padx=5)

        # --- Kolik max útoků ---
        attacks_frame = ttk.Frame(self)
        attacks_frame.pack(pady=5, anchor="w")
        ttk.Label(attacks_frame, text="Kolik max útoků:").pack(side=tk.LEFT, padx=(0, 5))
        self.max_attacks_entry = ttk.Entry(attacks_frame, width=10)
        self.max_attacks_entry.insert(0, str(self.max_attacks))
        self.max_attacks_entry.pack(side=tk.LEFT)

        # --- Kolik útoků mezi doplněním ---
        refill_frame = ttk.Frame(self)
        refill_frame.pack(pady=5, anchor="w")
        ttk.Label(refill_frame, text="Kolik útoků mezi doplněním:").pack(side=tk.LEFT, padx=(0, 5))
        self.refill_attacks_entry = ttk.Entry(refill_frame, width=10)
        self.refill_attacks_entry.insert(0, str(self.attacks_between_refill))
        self.refill_attacks_entry.pack(side=tk.LEFT)

        # --- Jednotky na plnění z leva ---
        units_frame = ttk.Frame(self)
        units_frame.pack(pady=5, anchor="w")
        ttk.Label(units_frame, text="Jednotky na plnění z leva:").pack(side=tk.LEFT, padx=(0, 5))
        self.units_entry = ttk.Entry(units_frame, width=10)
        self.units_entry.insert(0, str(self.units_from_left))
        self.units_entry.pack(side=tk.LEFT)

        # --- Delay mezi útoky ---
        delay_frame = ttk.Frame(self)
        delay_frame.pack(pady=5, anchor="w")
        ttk.Label(delay_frame, text="Delay mezi útoky (s):").pack(side=tk.LEFT, padx=(0, 5))
        self.delay_entry = ttk.Entry(delay_frame, width=10)
        self.delay_entry.insert(0, str(self.delay_between_attacks))
        self.delay_entry.pack(side=tk.LEFT)

        # --- Ovládací tlačítka Start / Stop ---
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=15, anchor="center")
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_action)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_action)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    # --- Callbacky ---
    def _on_horse_changed(self):
        self.feather_horses = bool(self.feather_horses_var.get())
        horse_type = "Pírko" if self.feather_horses else "Gold"
        self.log_message(status="info", message=f"Typ koně byl změněn na: {horse_type}")

    # --- Start / Stop ---
    def start_action(self):
        if self.is_running:
            self.log_message(status="info", message="Akce již běží!")
            return
        try:
            self.max_attacks = int(self.max_attacks_entry.get())
            self.attacks_between_refill = int(self.refill_attacks_entry.get())
            self.units_from_left = int(self.units_entry.get())
            self.delay_between_attacks = int(self.delay_entry.get())
        except ValueError:
            self.log_message(status="error", message="Chyba: zadejte platná čísla pro útoky a jednotky.")
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
        """Smyčka, která spouští děděnou funkci BerimondOnContinent."""
        countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
        for x in range(countdown, 0, -1):
            if not self.is_running:
                self.log_message(status="info", message="Akce přerušena během odpočtu.")
                return
            self.log_message(status="info", message=f"Spuštění za: {x}")
            time.sleep(1)

        self.log_message(status="info", message="Hlavní akce spuštěna!")
        try:
            self.manager.BerimondOnContinent(
                max_attacks=self.max_attacks,
                horses=self.feather_horses,
                attacks_between_refill=self.attacks_between_refill,
                troops_from_left=self.units_from_left,
                delay_between_attacks=self.delay_between_attacks)  # děděná metoda, implementace není zde
        except Exception as e:
            self.log_message(status="error", message=f"Chyba při spuštění BerimondOnContinent: {e}")

        self.is_running = False
        self.log_message(status="info", message="Akce dokončena.")
