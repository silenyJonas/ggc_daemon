# tabs/baron.py
import tkinter as tk
from tkinter import ttk
import threading
import time
from services.base_tab import BaseTab
from managers.baron_manager import BaronManager  # NOVÝ IMPORT


class BaronTab(BaseTab, ttk.Frame):
    """Třída pro záložku Baronů, která dědí z BaseTab."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Initialize start_index and end_index with default values
        self.start_index = 1
        self.end_index = 49
        self.is_running = False  # HLÍDACÍ PROMĚNNÁ
        self.feather_horses = True
        self.manager = BaronManager()  # Inicializace Manageru

        self.create_widgets()
        self.update_button_text()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""
        self.control_button = ttk.Button(
            self,
            text="Spustit",
            command=self.toggle_loop
        )
        self.control_button.pack(pady=10)

        # Rámeček pro uspořádání vstupních polí
        index_frame = ttk.Frame(self)
        index_frame.pack(pady=10)

        # Vstupní pole pro startovní index
        start_index_label = ttk.Label(index_frame, text="Startovní index:")
        start_index_label.pack(side=tk.LEFT, padx=(0, 5))
        self.start_index_entry = ttk.Entry(index_frame, width=5)
        self.start_index_entry.insert(0, str(self.start_index))
        self.start_index_entry.pack(side=tk.LEFT)

        # Vstupní pole pro koncový index
        end_index_label = ttk.Label(index_frame, text="Koncový index:")
        end_index_label.pack(side=tk.LEFT, padx=(15, 5))
        self.end_index_entry = ttk.Entry(index_frame, width=5)
        self.end_index_entry.insert(0, str(self.end_index))
        self.end_index_entry.pack(side=tk.LEFT)

        # Tlačítko pro uložení hodnot
        save_button = ttk.Button(
            self,
            text="Uložit indexy",
            command=self.save_indices
        )
        save_button.pack(pady=5)

        # Rámeček pro uspořádání radio buttonů (svět + typ koně)
        world_frame = ttk.Frame(self)
        world_frame.pack(pady=10, fill="x")

        world_label = ttk.Label(world_frame, text="Vybrat svět:")
        world_label.pack(side=tk.LEFT, padx=(0, 10))

        # Proměnná pro ukládání hodnoty vybraného Radiobutton (svět)
        self.world_variable = tk.StringVar(value="green")

        # Vytvoření Radiobuttonů pro každý svět s navázaným příkazem
        ttk.Radiobutton(world_frame, text="Green", variable=self.world_variable, value="green",
                        command=self.world_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(world_frame, text="Winter", variable=self.world_variable, value="winter",
                        command=self.world_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(world_frame, text="Sand", variable=self.world_variable, value="sand",
                        command=self.world_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(world_frame, text="Fire", variable=self.world_variable, value="fire",
                        command=self.world_changed).pack(side=tk.LEFT, padx=5)

        # --- Radiobuttony pro typ koně (mění bool feather_horses) ---
        self.feather_horses_var = tk.BooleanVar(value=self.feather_horses)

        horse_frame = ttk.Frame(self)
        horse_frame.pack(pady=5, fill="x")

        horse_label = ttk.Label(horse_frame, text="Typ koně:")
        horse_label.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(horse_frame, text="Gold koně", variable=self.feather_horses_var, value=False,
                        command=self._on_feather_horses_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(horse_frame, text="Pírko koně", variable=self.feather_horses_var, value=True,
                        command=self._on_feather_horses_changed).pack(side=tk.LEFT, padx=5)

    def _on_feather_horses_changed(self):
        """Callback při změně typu koně - aktualizuje self.feather_horses."""
        self.feather_horses = bool(self.feather_horses_var.get())
        horse_type = "Pírko" if self.feather_horses else "Gold"
        try:
            self.log_message(
                status="info",
                message=f"Typ koně byl změněn na: {horse_type}"
            )
        except Exception:
            pass

    def world_changed(self):
        """Zaznamená změnu vybraného světa do GUI logu."""
        selected_world = self.world_variable.get()
        self.log_message(
            status="info",
            message=f"Svět byl změněn na: {selected_world}"
        )

    def save_indices(self):
        """Uloží hodnoty ze vstupních polí do proměnných a vypíše je do GUI logu."""
        try:
            self.start_index = int(self.start_index_entry.get())
            self.end_index = int(self.end_index_entry.get())
            self.log_message(
                status="info",
                message=f"Indexy byly uloženy: start={self.start_index}, end={self.end_index}"
            )
        except ValueError:
            self.log_message(
                status="error",
                message="Chyba: Zadejte prosím platná celá čísla pro indexy."
            )

    def toggle_loop(self):
        """Spustí nebo zastaví smyčku útoku."""
        if self.is_running:
            self.is_running = False
            self.log_message(status="info", message="Smyčka Baronů zastavena.")
        else:
            self.save_indices()  # Uložení aktuálních hodnot před startem
            if self.start_index > self.end_index:
                self.log_message(status="error", message="Chyba: Startovní index je větší než koncový.")
                return

            self.is_running = True
            self.log_message(status="info", message="Smyčka Baronů spuštěna!")
            threading.Thread(target=self._run_loop_in_thread, daemon=True).start()

        self.update_button_text()

    def _run_loop_in_thread(self):
        """Zajistí odpočet a volání Manageru v odděleném vlákně."""

        # --- 1. Odpočítávání s kontrolou zastavení ---
        countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
        for x in range(countdown, 0, -1):
            if not self.is_running:
                self.log_message(status="info", message="Spuštění Baronů přerušeno během odpočtu.")
                self.update_button_text()
                return
            self.log_message(
                status="info",
                message="Spuštění za: " + str(x)
            )
            time.sleep(1)

        # --- 2. Volání manageru ---
        try:
            self.manager.SendBaronAttacks(
                start_index=self.start_index,
                end_index=self.end_index,
                selected_world=self.world_variable.get(),
                feather_horses=self.feather_horses,
                tab_instance=self  # 🔥 KLÍČOVÉ: Předání reference na instanci záložky 🔥
            )
        except Exception as e:
            self.log_message(status="error", message=f"Kritická chyba v Baron Manageru: {e}")

        # Po dokončení smyčky v manageru (ať už úspěšně nebo chybou) se is_running změní na False
        # (nastavuje Manager), nebo jej zde zkontrolujeme, pokud došlo k chybě.
        self.is_running = False
        self.update_button_text()

    def update_button_text(self):
        """Aktualizuje text tlačítka podle stavu smyčky."""
        if self.is_running:
            self.control_button.config(text="Zastavit (F1)")
        else:
            self.control_button.config(text="Spustit (F1)")