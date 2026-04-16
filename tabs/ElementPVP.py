import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from services.base_tab import BaseTab
from managers.element_pvp_manager import ElementPVPManager


class ElementPVPTab(BaseTab, ttk.Frame):
    """Záložka pro Element PVP s dynamickou tabulkou cílů a validací duplicit."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.manager = ElementPVPManager()
        self.json_path = "data/element_targets.json"

        # --- Výchozí hodnoty ---
        self.is_running = False
        self.feather_horses = True
        self.first_wave_from_bottom = "11"
        self.auto_fill_waves = True
        self.max_attacks = "10"
        self.targets = []

        self.create_widgets()
        self.load_targets()

    def create_widgets(self):
        # --- Horní nastavení ---
        settings_frame = ttk.LabelFrame(self, text=" Nastavení útoku ")
        settings_frame.pack(fill="x", padx=10, pady=5)

        self.feather_horses_var = tk.BooleanVar(value=self.feather_horses)
        ttk.Checkbutton(settings_frame, text="Pírko koně (jinak Gold)",
                        variable=self.feather_horses_var).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.auto_fill_var = tk.BooleanVar(value=self.auto_fill_waves)
        ttk.Checkbutton(settings_frame, text="Automaticky doplnit vlny",
                        variable=self.auto_fill_var).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        inputs_frame = ttk.Frame(settings_frame)
        inputs_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ttk.Label(inputs_frame, text="První vlna od spodu:").pack(side=tk.LEFT)
        self.first_wave_entry = ttk.Entry(inputs_frame, width=5)
        self.first_wave_entry.insert(0, self.first_wave_from_bottom)
        self.first_wave_entry.pack(side=tk.LEFT, padx=(5, 15))

        ttk.Label(inputs_frame, text="Max kol útoků:").pack(side=tk.LEFT)
        self.max_attacks_entry = ttk.Entry(inputs_frame, width=5)
        self.max_attacks_entry.insert(0, self.max_attacks)
        self.max_attacks_entry.pack(side=tk.LEFT, padx=(5, 15))

        # --- Tabulka cílů ---
        table_frame = ttk.LabelFrame(self, text=" Cíle (PVP Seznam) ")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "name", "x", "y")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.tree.heading("id", text="#")
        self.tree.heading("name", text="Jméno")
        self.tree.heading("x", text="X")
        self.tree.heading("y", text="Y")

        self.tree.column("id", width=30, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("x", width=50, anchor="center")
        self.tree.column("y", width=50, anchor="center")
        self.tree.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # --- Editor cílů ---
        edit_frame = ttk.Frame(self)
        edit_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(edit_frame, text="Jméno:").pack(side=tk.LEFT)
        self.ent_name = ttk.Entry(edit_frame, width=15)
        self.ent_name.pack(side=tk.LEFT, padx=5)

        ttk.Label(edit_frame, text="X:").pack(side=tk.LEFT, padx=(10, 2))
        self.ent_x = ttk.Entry(edit_frame, width=5)
        self.ent_x.pack(side=tk.LEFT)

        ttk.Label(edit_frame, text="Y:").pack(side=tk.LEFT, padx=(10, 2))
        self.ent_y = ttk.Entry(edit_frame, width=5)
        self.ent_y.pack(side=tk.LEFT)

        ttk.Button(edit_frame, text="Přidat", command=self.add_target).pack(side=tk.LEFT, padx=10)
        ttk.Button(edit_frame, text="Smazat", command=self.remove_target).pack(side=tk.LEFT)

        # --- Ovládání ---
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=15)
        self.start_button = ttk.Button(control_frame, text="Spustit PVP", command=self.start_action)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Zastavit", command=self.stop_action)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def _refresh_ids(self):
        """Přepočítá ID v tabulce po smazání nebo přidání."""
        for i, item in enumerate(self.tree.get_children(), start=1):
            values = list(self.tree.item(item, "values"))
            values[0] = i
            self.tree.item(item, values=values)

    def add_target(self):
        """Přidá cíl pouze pokud kombinace X a Y už v tabulce neexistuje."""
        name = self.ent_name.get().strip()
        new_x = self.ent_x.get().strip()
        new_y = self.ent_y.get().strip()

        # Základní validace vstupů
        if not (name and new_x.isdigit() and new_y.isdigit()):
            messagebox.showwarning("Chyba", "Vyplňte jméno a číselné souřadnice.")
            return

        # Kontrola duplicity (shoda X i Y zároveň)
        for item in self.tree.get_children():
            existing_values = self.tree.item(item, "values")
            # existing_values[2] je X, existing_values[3] je Y
            if str(existing_values[2]) == new_x and str(existing_values[3]) == new_y:
                messagebox.showwarning("Duplicita", f"Cíl na souřadnicích [{new_x}:{new_y}] již v seznamu existuje.")
                return

        # Pokud projde kontrolou, přidáme
        count = len(self.tree.get_children()) + 1
        self.tree.insert("", tk.END, values=(count, name, new_x, new_y))
        self.save_targets()

        # Vyčištění polí
        self.ent_name.delete(0, tk.END)
        self.ent_x.delete(0, tk.END)
        self.ent_y.delete(0, tk.END)

    def remove_target(self):
        for item in self.tree.selection():
            self.tree.delete(item)
        self._refresh_ids()
        self.save_targets()

    def save_targets(self):
        data = []
        for item in self.tree.get_children():
            v = self.tree.item(item)["values"]
            data.append({"name": v[1], "x": int(v[2]), "y": int(v[3])})
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        self.targets = data

    def load_targets(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.targets = json.load(f)
                    for i, t in enumerate(self.targets, start=1):
                        self.tree.insert("", tk.END, values=(i, t["name"], t["x"], t["y"]))
            except Exception as e:
                self.log_message(status="error", message=f"Chyba JSON: {e}")

    def start_action(self):
        if self.is_running: return
        if not self.tree.get_children(): return
        try:
            self.feather_horses = self.feather_horses_var.get()
            self.auto_fill_waves = self.auto_fill_var.get()
            self.first_wave_from_bottom = int(self.first_wave_entry.get())
            self.max_attacks = int(self.max_attacks_entry.get())
            self.save_targets()
            self.is_running = True
            threading.Thread(target=self._run_loop, daemon=True).start()
        except ValueError:
            self.log_message(status="error", message="Chyba ve vstupech!")

    def stop_action(self):
        self.is_running = False

    def _run_loop(self):
        time.sleep(1)
        if not self.is_running: return
        try:
            self.manager.Run(
                targets=self.targets,
                horses=self.feather_horses,
                first_wave_from_bottom=self.first_wave_from_bottom,
                auto_fill_waves=self.auto_fill_waves,
                max_attacks=self.max_attacks,
                tab_instance=self
            )
        except Exception as e:
            self.log_message(status="error", message=f"PVP Error: {e}")
        self.is_running = False
        self.log_message(status="info", message="Akce dokončena.")