import tkinter as tk
from tkinter import ttk
import threading
import time
from services.base_tab import BaseTab
from managers.baron_manager import BaronManager


class BaronTab(BaseTab, ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.start_index = 1
        self.end_index = 49
        self.is_running = False
        self.feather_horses = True
        self.manager = BaronManager()

        # Proměnné pro nonstop režim
        self.nonstop_all = tk.BooleanVar(value=False)
        self.attack_delay = tk.IntVar(value=30)  # Změněno na 25s
        self.wait_after_world = tk.IntVar(value=16)  # Změněno na 15 minut
        self.max_attacks_per_world = tk.IntVar(value=100)  # Nová kolonka

        # Pozice v seznamu hradů (Zelí odstraněno)
        self.pos_winter = tk.IntVar(value=7)
        self.pos_sand = tk.IntVar(value=8)
        self.pos_fire = tk.IntVar(value=9)

        self.create_widgets()
        self.update_button_text()

    def create_widgets(self):
        self.control_button = ttk.Button(self, text="Spustit", command=self.toggle_loop)
        self.control_button.pack(pady=10)

        # Checkbox pro NONSTOP
        self.nonstop_check = ttk.Checkbutton(
            self,
            text="Jezdit nonstop vše (všechny světy)",
            variable=self.nonstop_all,
            command=self._toggle_nonstop_layout
        )
        self.nonstop_check.pack(pady=5)

        # --- KONTEJNER PRO NASTAVENÍ NONSTOPU ---
        self.nonstop_settings_frame = ttk.LabelFrame(self, text="Nastavení Nonstop jízdy")

        # Řádek pro Časy (Delay, Pauza, Max útoků)
        time_row = ttk.Frame(self.nonstop_settings_frame)
        time_row.pack(fill="x", padx=5, pady=5)

        ttk.Label(time_row, text="Delay útok (s):").pack(side=tk.LEFT)
        ttk.Entry(time_row, textvariable=self.attack_delay, width=5).pack(side=tk.LEFT, padx=5)

        ttk.Label(time_row, text="Pauza po světě (min):").pack(side=tk.LEFT, padx=(15, 5))
        ttk.Entry(time_row, textvariable=self.wait_after_world, width=5).pack(side=tk.LEFT)

        ttk.Label(time_row, text="Max útoků:").pack(side=tk.LEFT, padx=(15, 5))
        ttk.Entry(time_row, textvariable=self.max_attacks_per_world, width=5).pack(side=tk.LEFT)

        # Pozice hradů řádek (Zelí odstraněno)
        pos_row = ttk.Frame(self.nonstop_settings_frame)
        pos_row.pack(fill="x", padx=5, pady=5)

        worlds_pos = [("Zima:", self.pos_winter),
                      ("Písek:", self.pos_sand), ("Oheň:", self.pos_fire)]

        for text, var in worlds_pos:
            ttk.Label(pos_row, text=text).pack(side=tk.LEFT, padx=(5, 2))
            ttk.Entry(pos_row, textvariable=var, width=3).pack(side=tk.LEFT, padx=(0, 5))

        # --- Rámeček pro INDEXY a SVĚTY (klasický režim) ---
        self.index_frame = ttk.Frame(self)
        self.index_frame.pack(pady=10)

        ttk.Label(self.index_frame, text="Start:").pack(side=tk.LEFT)
        self.start_index_entry = ttk.Entry(self.index_frame, width=5)
        self.start_index_entry.insert(0, "1")
        self.start_index_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(self.index_frame, text="End:").pack(side=tk.LEFT)
        self.end_index_entry = ttk.Entry(self.index_frame, width=5)
        self.end_index_entry.insert(0, "49")
        self.end_index_entry.pack(side=tk.LEFT, padx=5)

        self.world_frame = ttk.Frame(self)
        self.world_frame.pack(pady=10, fill="x")
        self.world_variable = tk.StringVar(value="winter") # Změněno default na winter
        for w in ["winter", "sand", "fire"]: # Green odstraněno
            ttk.Radiobutton(self.world_frame, text=w.capitalize(), variable=self.world_variable, value=w).pack(
                side=tk.LEFT, padx=5)

        # --- Radiobuttony pro typ koně ---
        horse_frame = ttk.Frame(self)
        horse_frame.pack(pady=5, fill="x")
        self.feather_horses_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(horse_frame, text="Gold koně", variable=self.feather_horses_var, value=False).pack(side=tk.LEFT,
                                                                                                           padx=5)
        ttk.Radiobutton(horse_frame, text="Pírko koně", variable=self.feather_horses_var, value=True).pack(side=tk.LEFT,
                                                                                                           padx=5)

    def _toggle_nonstop_layout(self):
        """Přepíná viditelnost prvků."""
        if self.nonstop_all.get():
            self.index_frame.pack_forget()
            self.world_frame.pack_forget()
            self.nonstop_settings_frame.pack(pady=10, padx=10, fill="x")
        else:
            self.nonstop_settings_frame.pack_forget()
            self.index_frame.pack(pady=10)
            self.world_frame.pack(pady=10)

    def toggle_loop(self):
        if self.is_running:
            self.is_running = False
            self.log_message("info", "Smyčka Baronů zastavena.")
        else:
            self.is_running = True
            self.log_message("info", "Smyčka Baronů spuštěna!")
            threading.Thread(target=self._run_loop_in_thread, daemon=True).start()
        self.update_button_text()

    def _run_loop_in_thread(self):
        default_wait = self.config_reader.get_value("settings.offsets.default_time_before_run") or 3
        time.sleep(default_wait)

        try:
            if self.nonstop_all.get():
                # Volání nonstop metody bez green
                self.manager.RunAllBarons(
                    feather_horses=self.feather_horses_var.get(),
                    delay=self.attack_delay.get(),
                    wait_minutes=self.wait_after_world.get(),
                    max_attacks=self.max_attacks_per_world.get(),
                    positions={
                        "winter": self.pos_winter.get(),
                        "sand": self.pos_sand.get(),
                        "fire": self.pos_fire.get()
                    },
                    tab_instance=self
                )
            else:
                self.manager.SendBaronAttacks(
                    start_index=int(self.start_index_entry.get()),
                    end_index=int(self.end_index_entry.get()),
                    selected_world=self.world_variable.get(),
                    feather_horses=self.feather_horses_var.get(),
                    tab_instance=self
                )
        except Exception as e:
            self.log_message("error", f"Kritická chyba v Baron Manageru: {e}")

        self.is_running = False
        self.update_button_text()

    def update_button_text(self):
        txt = "Zastavit (F1)" if self.is_running else "Spustit (F1)"
        self.control_button.config(text=txt)