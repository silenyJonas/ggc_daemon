# app.py
import tkinter as tk
from tkinter import ttk
import queue
import threading
import datetime  # Importujeme modul datetime


# Import všech tříd záložek z balíčku 'tabs'
from tabs import BaronTab, BerimondTab, ConfigurationTab, DiscordTab, FortressTab, NomadTab, ScanTab, TutorialTab, BerimondGreenTab, BulkBuyTab
from services.config_manager import ConfigManager
from services.shared_data import message_queue, LogMessage


class App(tk.Tk):
    """Hlavní třída aplikace."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Joncluv mega OP OP nejlepsi program na svete")
        self.geometry("1300x800")

        self.config_manager = ConfigManager(filepath="configuration.json")
        self.after(100, self.process_messages)
        self.create_widgets()

    def create_widgets(self):
        """Vytváří hlavní widgety aplikace, včetně notebooku."""
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(main_pane)
        main_pane.add(notebook)

        messages_frame = ttk.Frame(main_pane)
        main_pane.add(messages_frame)

        log_label = ttk.Label(messages_frame, text="Log hlášek", font=("Arial", 12, "bold"))
        log_label.pack(fill=tk.X, padx=5, pady=5)

        self.log_text = tk.Text(messages_frame, wrap="word", bg="black", fg="white")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state="disabled")

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

        notebook.add(self.fortessTab, text="Fort")
        notebook.add(self.baronTab, text="Baron")
        notebook.add(self.nomadTab, text="Nom")
        notebook.add(self.berimondTab, text="Beri")
        notebook.add(self.beriGreenlTab, text="Beri Green")
        notebook.add(self.scanTab, text="Scan")
        notebook.add(self.configurationTab, text="Conf")
        notebook.add(self.discordTab, text="DC")
        notebook.add(self.tutorialTab, text="Help")
        notebook.add(self.bulkBuyTab, text="Item Buy")


    def process_messages(self):
        """Pravidelně kontroluje frontu zpráv a vypisuje je do textového pole."""
        while not message_queue.empty():
            log_object = message_queue.get()

            # Formátujeme výstup
            formatted_time = datetime.datetime.fromtimestamp(log_object.time).strftime("%H:%M:%S.%f")[:-3]

            formatted_message = f"[{formatted_time}] [{log_object.status.upper()}] <{log_object.module}> {log_object.message}"

            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, formatted_message + "\n")
            self.log_text.config(state="disabled")
            self.log_text.see(tk.END)

        self.after(100, self.process_messages)