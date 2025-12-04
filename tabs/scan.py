import tkinter as tk
from tkinter import ttk
from services.base_tab import BaseTab
from managers.scan_manager import ScanManager

class ScanTab(BaseTab, ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.manager = ScanManager()
        self.selected_json = tk.StringVar(value="sand")  # výchozí hodnota
        self.scan_distance_var = tk.StringVar(value="999999")  # výchozí hodnota v poli
        self.confirm_overwrite = tk.BooleanVar(value=False)  # checkbutton stav
        self.dismiss_popups = tk.BooleanVar(value=False)     # nový radiobutton stav
        self.create_widgets()

    def create_widgets(self):
        # rámec pro radiobuttony pro výběr světa
        frame_radios = ttk.Frame(self)
        frame_radios.pack(pady=10, anchor="w")

        ttk.Radiobutton(frame_radios, text="Zima", variable=self.selected_json, value="winter").pack(side="left", padx=5)
        ttk.Radiobutton(frame_radios, text="Písek", variable=self.selected_json, value="sand").pack(side="left", padx=5)
        ttk.Radiobutton(frame_radios, text="Oheň", variable=self.selected_json, value="fire").pack(side="left", padx=5)

        # rámec pro scan distance
        frame_distance = ttk.Frame(self)
        frame_distance.pack(pady=5, anchor="w")

        ttk.Label(frame_distance, text="Scan vzdálenost:").pack(side="left", padx=(0, 5))
        self.distance_entry = ttk.Entry(frame_distance, textvariable=self.scan_distance_var, width=10)
        self.distance_entry.pack(side="left")

        # checkbutton potvrzení
        self.confirm_check = ttk.Checkbutton(
            self,
            text="Spuštění scanu přepíše seznam pevností",
            variable=self.confirm_overwrite,
            command=self.update_button_state
        )
        self.confirm_check.pack(pady=5, anchor="w")

        # --- Nový radiobutton pro odklikávání popupů ---
        frame_dismiss = ttk.Frame(self)
        frame_dismiss.pack(pady=5, anchor="w")

        ttk.Label(frame_dismiss, text="Použít odklikávání popupů během scanu:").pack(side="left", padx=(0, 5))
        ttk.Radiobutton(frame_dismiss, text="Ano", variable=self.dismiss_popups, value=True,
                        command=self._on_dismiss_changed).pack(side="left", padx=5)
        ttk.Radiobutton(frame_dismiss, text="Ne", variable=self.dismiss_popups, value=False,
                        command=self._on_dismiss_changed).pack(side="left", padx=5)

        # tlačítko pro spuštění scanu (na začátku disabled)
        self.button = ttk.Button(self, text="Spustit Scan", command=self.button_action, state="disabled")
        self.button.pack(pady=20, anchor="w")

    def update_button_state(self):
        """Povolí nebo zakáže tlačítko podle checkboxu."""
        if self.confirm_overwrite.get():
            self.button.config(state="normal")
        else:
            self.button.config(state="disabled")

    def _on_dismiss_changed(self):
        state = "Ano" if self.dismiss_popups.get() else "Ne"
        self.log_message(status="info", message=f"Použít odklikávání popupů během scanu: {state}")

    def button_action(self):
        """Akce, která se provede po stisknutí tlačítka."""
        if not self.confirm_overwrite.get():
            self.log_message(status="warn", message="Musíš potvrdit přepsání seznamu pevností.")
            return

        chosen = self.selected_json.get()

        try:
            scan_distance = int(self.scan_distance_var.get())
        except ValueError:
            scan_distance = 999999  # fallback, pokud je špatný vstup

        dismiss = self.dismiss_popups.get()

        self.manager.ScanFort(chosen, scan_distance=scan_distance, dismiss_popups=dismiss)