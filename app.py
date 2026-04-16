# app.py
import tkinter as tk
from tkinter import ttk
import queue
import threading
import datetime
import time
import pyautogui
import cv2
import numpy as np
import easyocr
import os

from tabs import BaronTab, BerimondTab, ConfigurationTab, DiscordTab, FortressTab, NomadTab, ScanTab, TutorialTab, \
    BerimondGreenTab, BulkBuyTab, RiftTab, DeliverySpamTab, ElementPVPTab
from services.config_manager import ConfigManager
from services.shared_data import message_queue, LogMessage


class App(tk.Tk):
    """Hlavní třída aplikace."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Joncluv mega OP OP nejlepsi program na svete")
        self.geometry("1300x800")

        # Inicializace OCR
        self.reader = easyocr.Reader(['en'])

        # Proměnné pro sledování rubínů
        self.last_ruby_value = None
        self.total_gained_rubies = 0
        self.is_monitoring = True

        self.config_manager = ConfigManager(filepath="configuration.json")
        self.after(100, self.process_messages)
        self.create_widgets()

        threading.Thread(target=self._monitor_rubies_loop, daemon=True).start()

    def create_widgets(self):
        """Vytváří hlavní widgety aplikace."""
        main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(main_pane)
        main_pane.add(notebook, weight=3)

        messages_frame = ttk.Frame(main_pane)
        main_pane.add(messages_frame, weight=1)

        ruby_bar = ttk.Frame(messages_frame)
        ruby_bar.pack(fill=tk.X, padx=5, pady=2)

        self.ruby_label = ttk.Label(ruby_bar, text="Vyježděno rubínů za session: 0", font=("Arial", 10, "bold"))
        self.ruby_label.pack(side=tk.LEFT, padx=5)

        reset_btn = ttk.Button(ruby_bar, text="Resetovat Session", command=self.reset_ruby_session)
        reset_btn.pack(side=tk.LEFT, padx=10)

        log_label = ttk.Label(messages_frame, text="Log hlášek", font=("Arial", 12, "bold"))
        log_label.pack(fill=tk.X, padx=5, pady=2)

        self.log_text = tk.Text(messages_frame, wrap="word", bg="black", fg="white", height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state="disabled")

        # Inicializace záložek
        self.fortessTab = FortressTab(notebook)
        self.baronTab = BaronTab(notebook)
        self.nomadTab = NomadTab(notebook)
        self.berimondTab = BerimondTab(notebook)
        self.scanTab = ScanTab(notebook)
        self.configurationTab = ConfigurationTab(notebook, self.config_manager)
        self.discordTab = DiscordTab(notebook)
        self.tutorialTab = TutorialTab(notebook)
        self.beriGreenlTab = BerimondGreenTab(notebook)
        self.bulkBuyTab = BulkBuyTab(notebook)
        self.riftTab = RiftTab(notebook)
        self.spamTab = DeliverySpamTab(notebook)
        self.elementPVPTab = ElementPVPTab(notebook)

        notebook.add(self.fortessTab, text="Fort")
        notebook.add(self.baronTab, text="Baron")
        notebook.add(self.nomadTab, text="Nom")
        notebook.add(self.berimondTab, text="Beri")
        notebook.add(self.beriGreenlTab, text="Beri Green")
        notebook.add(self.scanTab, text="Scan")
        notebook.add(self.configurationTab, text="Conf")
        notebook.add(self.discordTab, text="DC")
        notebook.add(self.bulkBuyTab, text="Item Buy")
        notebook.add(self.riftTab, text="Rift")
        notebook.add(self.spamTab, text="Spam")
        notebook.add(self.tutorialTab, text="Help")
        notebook.add(self.elementPVPTab, text="ElementPVP")

    def reset_ruby_session(self):
        self.last_ruby_value = None
        self.total_gained_rubies = 0
        self.ruby_label.config(text="Vyježděno rubínů za session: 0")
        message_queue.put(LogMessage(time.time(), "ok", "App", "Počítadlo rubínů bylo vynulováno."))

    def _get_current_rubies_from_screen(self):
        """Opravené OCR pro zamezení 'vypálení' obrazu."""
        try:
            # Region necháme, jak jsi ho měl, vypadá že míří správně
            region = (30, 165, 52, 12)
            screenshot = pyautogui.screenshot(region=region)

            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # Zvětšení je super, to necháme
            img = cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_LANCZOS4)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # --- KLÍČOVÁ ZMĚNA ZDE ---
            # Místo 210 zkusíme 120. Čím nižší číslo, tím méně "vypálené" to bude.
            # THRESH_BINARY_INV udělá černé číslice na bílém pozadí (OCR to miluje)
            _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)

            # Pokud by to bylo pořád moc tlusté, zkusíme odstranit šum
            kernel = np.ones((2, 2), np.uint8)
            thresh = cv2.dilate(thresh, kernel, iterations=1) # Trochu ztenčí čáry
            thresh = cv2.erode(thresh, kernel, iterations=1)

            # Ulož si to a uvidíš ten rozdíl!
            cv2.imwrite("ocr_ruby_input.png", thresh)

            results = self.reader.readtext(thresh, detail=0, allowlist='0123456789')
            text = "".join(results)
            digits_only = "".join(filter(str.isdigit, text))

            if digits_only:
                return int(digits_only)
            return None
        except Exception as e:
            return None

    def _monitor_rubies_loop(self):
        """Sleduje přírůstky rubínů."""
        while self.is_monitoring:
            current_val = self._get_current_rubies_from_screen()

            if current_val is not None:
                if self.last_ruby_value is not None:
                    # Pokud se hodnota zvedla, přičteme zisk
                    if current_val > self.last_ruby_value:
                        gain = current_val - self.last_ruby_value
                        self.total_gained_rubies += gain
                        self.ruby_label.config(text=f"Vyježděno rubínů za session: {self.total_gained_rubies}")

                    # Pokud klesla (útrata), jen se adaptujeme na novou hladinu

                self.last_ruby_value = current_val

            # Interval 10s pro rychlou odezvu
            time.sleep(10)

    def process_messages(self):
        while not message_queue.empty():
            log_object = message_queue.get()
            formatted_time = datetime.datetime.fromtimestamp(log_object.time).strftime("%H:%M:%S.%f")[:-3]
            formatted_message = f"[{formatted_time}] [{log_object.status.upper()}] <{log_object.module}> {log_object.message}"

            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, formatted_message + "\n")
            self.log_text.config(state="disabled")
            self.log_text.see(tk.END)

        self.after(100, self.process_messages)


if __name__ == "__main__":
    app = App()
    app.mainloop()