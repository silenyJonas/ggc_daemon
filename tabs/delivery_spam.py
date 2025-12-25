import tkinter as tk
from tkinter import ttk
import threading
import time
import json
import os
from services.base_tab import BaseTab
from managers.delivery_spam_manager import DeliverySpamManager


class DeliverySpamTab(BaseTab, ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.is_running = False
        self.manager = DeliverySpamManager()
        self.data_file = "data/delivery_tasks.json"

        # Načtení dat
        data = self._load_data()
        self.tasks = data.get("tasks", [])

        # Definice sledovaných světů a jejich výchozích pozic
        self.worlds = ["zeli", "zima", "pisek", "ohen"]
        self.castle_settings = data.get("castle_settings", {w: 1 for w in self.worlds})

        self.create_widgets()
        self._fill_table_from_tasks()

        self.tree.bind("<Button-1>", self._on_table_click)
        self.update_button_text()

    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"tasks": [], "castle_settings": {}}
        return {"tasks": [], "castle_settings": {}}

    def _save_data(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

        # Aktualizace pozic hradů z Entry polí před uložením
        for world in self.worlds:
            try:
                self.castle_settings[world] = int(self.castle_entries[world].get())
            except ValueError:
                self.castle_settings[world] = 1

        full_data = {"tasks": self.tasks, "castle_settings": self.castle_settings}
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=4, ensure_ascii=False)
        self._fill_table_from_tasks()

    def _on_table_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return
        column = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        idx = self.tree.index(item_id)

        if column == "#3":  # Active DMS
            self.tasks[idx]["dms_active"] = not self.tasks[idx].get("dms_active", False)
            self._save_data()
        elif column == "#6":  # Active FWD
            self.tasks[idx]["fwd_active"] = not self.tasks[idx].get("fwd_active", False)
            self._save_data()
        elif column == "#1":  # Target
            self._spawn_edit_entry(item_id, column, idx, "name")
        elif column == "#2":  # DMS Kůň
            self._spawn_edit_dropdown(item_id, column, idx, "dms_horse_feather")
        elif column == "#5":  # FWD Kůň
            self._spawn_edit_dropdown(item_id, column, idx, "fwd_horse_feather")

    def _spawn_edit_entry(self, item_id, column, task_idx, key):
        x, y, width, height = self.tree.bbox(item_id, column)
        entry = ttk.Entry(self.tree)
        entry.insert(0, self.tasks[task_idx].get(key, ""))
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus()
        entry.bind("<Return>", lambda e: [self.tasks[task_idx].update({key: entry.get().strip()}), entry.destroy(),
                                          self._save_data()])
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def _spawn_edit_dropdown(self, item_id, column, task_idx, key):
        x, y, width, height = self.tree.bbox(item_id, column)
        edit_combo = ttk.Combobox(self.tree, values=["Pírko", "Gold"], state="readonly")
        edit_combo.set("Pírko" if self.tasks[task_idx].get(key) else "Gold")
        edit_combo.place(x=x, y=y, width=width, height=height)
        edit_combo.focus()
        edit_combo.bind("<<ComboboxSelected>>",
                        lambda e: [self.tasks[task_idx].update({key: (edit_combo.get() == "Pírko")}),
                                   edit_combo.destroy(), self._save_data()])
        edit_combo.bind("<FocusOut>", lambda e: edit_combo.destroy())

    def create_widgets(self):
        # Horní ovládání
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=5, fill="x", padx=10)

        self.control_button = ttk.Button(top_frame, text="Spustit", command=self.toggle_loop)
        self.control_button.pack(side=tk.LEFT, padx=5)

        self.auto_reward_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top_frame, text="Auto odměny", variable=self.auto_reward_var).pack(side=tk.LEFT, padx=20)

        # Sekce pro nastavení pozic hradů (inty)
        settings_frame = ttk.LabelFrame(self, text="Pozice hradů (číslo v seznamu)", padding=10)
        settings_frame.pack(pady=5, fill="x", padx=10)

        self.castle_entries = {}
        for world in self.worlds:
            f = ttk.Frame(settings_frame)
            f.pack(side=tk.LEFT, padx=10)
            ttk.Label(f, text=f"{world.capitalize()}:").pack(side=tk.LEFT)
            ent = ttk.Entry(f, width=4)
            ent.insert(0, str(self.castle_settings.get(world, 1)))
            ent.pack(side=tk.LEFT, padx=2)
            self.castle_entries[world] = ent

        # Tabulka
        table_frame = ttk.Frame(self)
        table_frame.pack(pady=5, fill="both", expand=True, padx=10)
        self.cols = ("nazev", "dms_kun", "dms_act", "dms_last", "fwd_kun", "fwd_act", "fwd_last")
        self.tree = ttk.Treeview(table_frame, columns=self.cols, show="headings", height=12)
        headers = ["Target", "DMS Kůň", "DMS Akt", "DMS Wipe", "FWD Kůň", "FWD Akt", "FWD Wipe"]
        for col, head in zip(self.cols, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)

        # Přidávání úkolů
        add_frame = ttk.LabelFrame(self, text="Nový úkol", padding=10)
        add_frame.pack(pady=5, fill="x", padx=10)
        r1 = ttk.Frame(add_frame)
        r1.pack(fill="x")
        ttk.Label(r1, text="Název:").pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(r1, width=20)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(r1, text="Smazat vybrané", command=self.delete_task).pack(side=tk.RIGHT, padx=5)
        ttk.Button(r1, text="Přidat", command=self.add_task).pack(side=tk.RIGHT, padx=5)

    def _fill_table_from_tasks(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for task in self.tasks:
            self.tree.insert("", tk.END, values=(
                task["name"],
                "Pírko" if task.get("dms_horse_feather", True) else "Gold",
                "✅" if task.get("dms_active", False) else "❌",
                task.get("dms_last_wipe", "-"),
                "Pírko" if task.get("fwd_horse_feather", True) else "Gold",
                "✅" if task.get("fwd_active", False) else "❌",
                task.get("fwd_last_wipe", "-")
            ))

    def add_task(self):
        name = self.name_entry.get().strip()
        if not name: return
        self.tasks.append({
            "name": name, "dms_horse_feather": True, "dms_active": False, "dms_last_wipe": "-",
            "fwd_horse_feather": True, "fwd_active": False, "fwd_last_wipe": "-"
        })
        self._save_data()
        self.name_entry.delete(0, tk.END)

    def delete_task(self):
        for item in self.tree.selection():
            idx = self.tree.index(item)
            if idx < len(self.tasks): self.tasks.pop(idx)
        self._save_data()

    def toggle_loop(self):
        if self.is_running:
            self.is_running = False
        else:
            if not self.tasks: return
            self._save_data()  # Uloží aktuální inty z políček
            self.is_running = True
            threading.Thread(target=self._run_loop_in_thread, daemon=True).start()
        self.update_button_text()

    def _run_loop_in_thread(self):
        for x in range(3, 0, -1):
            if not self.is_running: break
            self.log_message(status="info", message=f"Spuštění za: {x}")
            time.sleep(1)

        if self.is_running:
            try:
                # Předání jako jednotlivé proměnné (inty)
                self.manager.Run(
                    tasks=self.tasks,
                    auto_reward=self.auto_reward_var.get(),
                    zeli_pos=int(self.castle_settings["zeli"]),
                    zima_pos=int(self.castle_settings["zima"]),
                    pisek_pos=int(self.castle_settings["pisek"]),
                    ohen_pos=int(self.castle_settings["ohen"]),
                    tab_instance=self
                )
            except Exception as e:
                self.log_message(status="error", message=f"Chyba: {e}")

        self.is_running = False
        self.after(0, self.update_button_text)

    def update_button_text(self):
        self.control_button.config(text="Zastavit (F1)" if self.is_running else "Spustit (F1)")