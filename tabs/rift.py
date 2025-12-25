import tkinter as tk
from tkinter import ttk
import threading
import time
from services.base_tab import BaseTab
from managers.rift_manager import RiftManager


class RiftTab(BaseTab, ttk.Frame):
    """Záložka pro Rift (Hromadný nákup), dědící z BaseTab."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Výchozí hodnoty
        self.max_attacks = 45
        self.feather_horses = True
        self.is_running = False

        # Výchozí souřadnice
        self.pos_x = 481
        self.pos_y = 1074

        self.manager = RiftManager()

        self.create_widgets()
        self.update_button_text()

    def create_widgets(self):
        """Vytváří widgety pro záložku Rift."""

        # Hlavní ovládací tlačítko (Spustit/Zastavit)
        self.control_button = ttk.Button(
            self,
            text="Spustit",
            command=self.toggle_loop
        )
        self.control_button.pack(pady=10)

        # --- Rámeček pro souřadnice X a Y ---
        coords_frame = ttk.Frame(self)
        coords_frame.pack(pady=5)

        ttk.Label(coords_frame, text="X:").pack(side=tk.LEFT, padx=(0, 5))
        self.x_entry = ttk.Entry(coords_frame, width=6)
        self.x_entry.insert(0, str(self.pos_x))
        self.x_entry.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(coords_frame, text="Y:").pack(side=tk.LEFT, padx=(0, 5))
        self.y_entry = ttk.Entry(coords_frame, width=6)
        self.y_entry.insert(0, str(self.pos_y))
        self.y_entry.pack(side=tk.LEFT)

        # --- Nastavení počtu útoků ---
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)

        ttk.Label(input_frame, text="Max. počet útoků:").pack(side=tk.LEFT, padx=(0, 5))
        self.max_attacks_entry = ttk.Entry(input_frame, width=8)
        self.max_attacks_entry.insert(0, str(self.max_attacks))
        self.max_attacks_entry.pack(side=tk.LEFT)

        # --- Nastavení typu koně ---
        self.feather_horses_var = tk.BooleanVar(value=self.feather_horses)

        horse_frame = ttk.Frame(self)
        horse_frame.pack(pady=10)

        ttk.Label(horse_frame, text="Typ koně:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            horse_frame, text="Gold koně",
            variable=self.feather_horses_var, value=False,
            command=self._on_settings_changed
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            horse_frame, text="Pírko koně",
            variable=self.feather_horses_var, value=True,
            command=self._on_settings_changed
        ).pack(side=tk.LEFT, padx=5)

    def _on_settings_changed(self):
        """Callback při změně typu koně v GUI."""
        self.feather_horses = bool(self.feather_horses_var.get())
        horse_type = "Pírko" if self.feather_horses else "Gold"
        self.log_message(status="info", message=f"Změna nastavení: {horse_type} koně")

    def save_inputs(self):
        """Načte a validuje hodnoty z GUI polí před spuštěním."""
        try:
            self.max_attacks = int(self.max_attacks_entry.get())
            self.pos_x = int(self.x_entry.get())
            self.pos_y = int(self.y_entry.get())
            return True
        except ValueError:
            self.log_message(status="error", message="Chyba: Souřadnice a počet útoků musí být celá čísla.")
            return False

    def toggle_loop(self):
        """Přepíná stav běhu Rift manageru."""
        if self.is_running:
            self.is_running = False
            self.log_message(status="info", message="Rift proces zastaven uživatelem.")
        else:
            if not self.save_inputs():
                return

            self.is_running = True
            self.log_message(status="info",
                             message=f"Startuji Rift na [{self.pos_x}, {self.pos_y}] (Cíl: {self.max_attacks} útoků)")
            threading.Thread(target=self._run_loop_in_thread, daemon=True).start()

        self.update_button_text()

    def _run_loop_in_thread(self):
        """Vlákno pro obsluhu odpočtu a volání manageru."""
        countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
        for x in range(countdown, 0, -1):
            if not self.is_running:
                self.after(0, self.update_button_text)
                return
            self.log_message(status="info", message=f"Spuštění za: {x}")
            time.sleep(1)

        try:
            # Volání manageru s novými parametry pro souřadnice
            self.manager.Run(
                max_attacks=self.max_attacks,
                feather_horses=self.feather_horses,
                x=self.pos_x,
                y=self.pos_y,
                tab_instance=self
            )
        except Exception as e:
            self.log_message(status="error", message=f"Kritická chyba v Rift Manageru: {e}")
        finally:
            self.is_running = False
            self.after(0, self.update_button_text)

    def update_button_text(self):
        """Aktualizuje text na hlavním tlačítku."""
        if self.is_running:
            self.control_button.config(text="Zastavit (F1)")
        else:
            self.control_button.config(text="Spustit (F1)")