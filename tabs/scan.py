import tkinter as tk
from tkinter import ttk
from services.base_tab import BaseTab
from managers.scan_manager import ScanManager


class ScanTab(BaseTab, ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.manager = ScanManager()

        # Proměnné
        self.selected_json = tk.StringVar(value="sand")
        self.scan_distance_var = tk.StringVar(value="999999")
        self.confirm_overwrite = tk.BooleanVar(value=False)
        self.dismiss_popups = tk.BooleanVar(value=False)
        self.scan_both_worlds = tk.BooleanVar(value=False)

        # Pozice hradů (Default: Fire 9, Sand 8, Winter 7)
        self.fire_pos_var = tk.StringVar(value="4")
        self.sand_pos_var = tk.StringVar(value="3")
        self.winter_pos_var = tk.StringVar(value="2")

        self.create_widgets()

    def create_widgets(self):
        # --- Rámec pro výběr světů ---
        self.frame_radios = ttk.LabelFrame(self, text="Výběr světa k prohledání", padding=10)
        self.frame_radios.pack(pady=10, fill="x", anchor="w")

        self.rb_winter = ttk.Radiobutton(self.frame_radios, text="Zima", variable=self.selected_json, value="winter")
        self.rb_winter.pack(side="left", padx=5)

        self.rb_sand = ttk.Radiobutton(self.frame_radios, text="Písek", variable=self.selected_json, value="sand")
        self.rb_sand.pack(side="left", padx=5)

        self.rb_fire = ttk.Radiobutton(self.frame_radios, text="Oheň", variable=self.selected_json, value="fire")
        self.rb_fire.pack(side="left", padx=5)

        # Checkbox pro hromadný scan
        self.check_both = ttk.Checkbutton(
            self,
            text="Scanovat Oheň + Písek zároveň",
            variable=self.scan_both_worlds,
            command=self._on_both_worlds_toggled
        )
        self.check_both.pack(pady=5, anchor="w")

        # --- RÁMEC PRO POZICE HRADŮ ---
        self.frame_positions = ttk.LabelFrame(self, text=" Pozice hradů v seznamu ", padding=5)
        # Ve výchozím stavu viditelný, nebo jej můžeš ovládat v _on_both_worlds_toggled
        self.frame_positions.pack(pady=5, fill="x", anchor="w")

        # Grid pro hezké uspořádání pozic
        ttk.Label(self.frame_positions, text="Oheň:").grid(row=0, column=0, padx=5, pady=2)
        ttk.Entry(self.frame_positions, textvariable=self.fire_pos_var, width=5).grid(row=0, column=1, padx=5)

        ttk.Label(self.frame_positions, text="Písek:").grid(row=0, column=2, padx=5, pady=2)
        ttk.Entry(self.frame_positions, textvariable=self.sand_pos_var, width=5).grid(row=0, column=3, padx=5)

        ttk.Label(self.frame_positions, text="Zima:").grid(row=0, column=4, padx=5, pady=2)
        ttk.Entry(self.frame_positions, textvariable=self.winter_pos_var, width=5).grid(row=0, column=5, padx=5)

        # --- Rámec pro scan distance ---
        frame_distance = ttk.Frame(self)
        frame_distance.pack(pady=10, anchor="w")

        ttk.Label(frame_distance, text="Scan vzdálenost:").pack(side="left", padx=(0, 5))
        self.distance_entry = ttk.Entry(frame_distance, textvariable=self.scan_distance_var, width=10)
        self.distance_entry.pack(side="left")

        # --- Popup nastavení ---
        frame_dismiss = ttk.Frame(self)
        frame_dismiss.pack(pady=5, anchor="w")

        ttk.Label(frame_dismiss, text="Odklikávat popupy:").pack(side="left", padx=(0, 5))
        ttk.Radiobutton(frame_dismiss, text="Ano", variable=self.dismiss_popups, value=True).pack(side="left", padx=5)
        ttk.Radiobutton(frame_dismiss, text="Ne", variable=self.dismiss_popups, value=False).pack(side="left", padx=5)

        # --- Potvrzení a tlačítko ---
        self.confirm_check = ttk.Checkbutton(
            self,
            text="Spuštění scanu přepíše seznam pevností",
            variable=self.confirm_overwrite,
            command=self.update_button_state
        )
        self.confirm_check.pack(pady=15, anchor="w")

        self.button = ttk.Button(self, text="Spustit Scan", command=self.button_action, state="disabled")
        self.button.pack(pady=10, anchor="w")

    def _on_both_worlds_toggled(self):
        """Deaktivuje výběr světů při hromadném scanu."""
        if self.scan_both_worlds.get():
            self.selected_json.set("")
            self.rb_winter.config(state="disabled")
            self.rb_sand.config(state="disabled")
            self.rb_fire.config(state="disabled")
            self.log_message(status="info", message="Vybrán kombinovaný scan všech světů")
        else:
            self.selected_json.set("sand")
            self.rb_winter.config(state="normal")
            self.rb_sand.config(state="normal")
            self.rb_fire.config(state="normal")

    def update_button_state(self):
        state = "normal" if self.confirm_overwrite.get() else "disabled"
        self.button.config(state=state)

    def button_action(self):
        if not self.confirm_overwrite.get():
            return

        try:
            scan_distance = int(self.scan_distance_var.get())
            # Získání pozic z UI
            f_pos = int(self.fire_pos_var.get())
            s_pos = int(self.sand_pos_var.get())
            w_pos = int(self.winter_pos_var.get())
        except ValueError:
            scan_distance = 999999
            f_pos, s_pos, w_pos = 9, 8, 7

        # Volání manageru s předáním slovníku pozic
        self.manager.ScanFort(
            self.selected_json.get(),
            scan_distance=scan_distance,
            dismiss_popups=self.dismiss_popups.get(),
            scan_both_worlds=self.scan_both_worlds.get(),
            positions={
                "fire": f_pos,
                "sand": s_pos,
                "winter": w_pos
            }
        )