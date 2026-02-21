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
        self.scan_both_worlds = tk.BooleanVar(value=False)  # Nový bool pro Písek + Oheň

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

        # Checkbox pro hromadný scan (Písek + Oheň)
        self.check_both = ttk.Checkbutton(
            self,
            text="Scanovat Písek + Oheň zároveň",
            variable=self.scan_both_worlds,
            command=self._on_both_worlds_toggled
        )
        self.check_both.pack(pady=5, anchor="w")

        # --- Rámec pro scan distance ---
        frame_distance = ttk.Frame(self)
        frame_distance.pack(pady=5, anchor="w")

        ttk.Label(frame_distance, text="Scan vzdálenost:").pack(side="left", padx=(0, 5))
        self.distance_entry = ttk.Entry(frame_distance, textvariable=self.scan_distance_var, width=10)
        self.distance_entry.pack(side="left")

        # --- Popup nastavení ---
        frame_dismiss = ttk.Frame(self)
        frame_dismiss.pack(pady=5, anchor="w")

        ttk.Label(frame_dismiss, text="Odklikávat popupy:").pack(side="left", padx=(0, 5))
        ttk.Radiobutton(frame_dismiss, text="Ano", variable=self.dismiss_popups, value=True,
                        command=self._on_dismiss_changed).pack(side="left", padx=5)
        ttk.Radiobutton(frame_dismiss, text="Ne", variable=self.dismiss_popups, value=False,
                        command=self._on_dismiss_changed).pack(side="left", padx=5)

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
        """Deaktivuje výběr jednotlivých světů, pokud je vybrán hromadný scan."""
        if self.scan_both_worlds.get():
            self.rb_winter.config(state="disabled")
            self.rb_sand.config(state="disabled")
            self.rb_fire.config(state="disabled")
            self.log_message(status="info", message="Vybrán kombinovaný scan: Písek + Oheň")
        else:
            self.rb_winter.config(state="normal")
            self.rb_sand.config(state="normal")
            self.rb_fire.config(state="normal")

    def update_button_state(self):
        """Povolí nebo zakáže tlačítko podle checkboxu."""
        state = "normal" if self.confirm_overwrite.get() else "disabled"
        self.button.config(state=state)

    def _on_dismiss_changed(self):
        state = "Ano" if self.dismiss_popups.get() else "Ne"
        self.log_message(status="info", message=f"Odklikávání popupů: {state}")

    def button_action(self):
        """Akce, která se provede po stisknutí tlačítka."""
        if not self.confirm_overwrite.get():
            return

        try:
            scan_distance = int(self.scan_distance_var.get())
        except ValueError:
            scan_distance = 999999

        dismiss = self.dismiss_popups.get()
        both_worlds = self.scan_both_worlds.get()
        chosen_world = self.selected_json.get()

        # Volání manageru s novým parametrem scan_both_worlds
        self.manager.ScanFort(
            chosen_world,
            scan_distance=scan_distance,
            dismiss_popups=dismiss,
            scan_both_worlds=both_worlds
        )