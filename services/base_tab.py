import json
import math
from tkinter import ttk
import threading
from .config_reader import ConfigReader
from .shared_data import message_queue, LogMessage
import pyautogui
from .db_writer import DbWriter
import easyocr
import re
import keyboard
import os
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import tkinter as tk
class BaseTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_reader = ConfigReader(filepath="configuration.json")
        self.is_running = False
        self.db_writer = DbWriter()
        self.click_delay_offset = self.config_reader.get_value("settings.offsets.default_click_delay")
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.stop_event = threading.Event()

    def GetDistance(self, castle_x, castle_y, target_x, target_y):

        dx = target_x - castle_x
        dy = target_y - castle_y
        return math.sqrt(dx * dx + dy * dy)


    # SCAN_PEVNOSTI_KONEC_____________________________________________
    # POSLAT_BASIC_UTOK_______________________________________________
    def SelectCode(self, selected_code):
        print(type(selected_code))
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.select_attack_code.base_click.x"),
            self.config_reader.get_value("actions_click_patter.select_attack_code.base_click.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.select_attack_code.code_"+str(selected_code)+".x"),
            self.config_reader.get_value("actions_click_patter.select_attack_code.code_"+str(selected_code)+".y"),
        )
        time.sleep(self.click_delay_offset)
    def SendAttackFirstWaveAuto(self,close_popups=True,skip_samu_nomad_cd = False, target_x=None, target_y=None, send_with_cords = True, kingdom=None, feather_horse=None, note=None, attack_code=None):
        if send_with_cords:
            #pyautogui.press("Tab")
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.y")
            )
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.y")
            )
            time.sleep(self.click_delay_offset)
            pyautogui.typewrite(str(target_x))
            pyautogui.press("Tab")
            pyautogui.typewrite(str(target_y))
            pyautogui.press("Enter")
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.y")
        )
        time.sleep(self.click_delay_offset)
        #skip cd
        if skip_samu_nomad_cd:
            self.SkipNomadSamuCooldown()

        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_3.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_3.y")
        )

        #close windows
        if close_popups:
            self.CloseWindowsPopups()
        #close windows end
        time.sleep(self.click_delay_offset)
        if attack_code != None:
            print(type(attack_code))
            self.SelectCode(attack_code)

        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_4.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_4.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_5.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_5.y")
        )
        time.sleep(self.click_delay_offset)
        #kone:
        if(feather_horse):
            pyautogui.click(
                self.config_reader.get_value("horses.feather.x"),
                self.config_reader.get_value("horses.feather.y")
            )
        else:
            pyautogui.click(
                self.config_reader.get_value("horses.gold.x"),
                self.config_reader.get_value("horses.gold.y")
            )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_6.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_6.y")
        )
        time.sleep(self.click_delay_offset)

        if send_with_cords:
            self.log_message(
                status="ok",
                message="Útok poslán na: ["+str(target_x)+":"+str(target_y)+"] | Note: "+note
            )
    def SkipNomadSamuCooldown(self):
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.skip_samu_nomad_cd.click_1.x"),
            self.config_reader.get_value("actions_click_patter.skip_samu_nomad_cd.click_1.y")
        )
        time.sleep(self.click_delay_offset + 0.5)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.skip_samu_nomad_cd.click_2.x"),
            self.config_reader.get_value("actions_click_patter.skip_samu_nomad_cd.click_2.y")
        )
        time.sleep(self.click_delay_offset)
    def CloseWindowsPopups(self):
        sleep_time = 0.15

        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.map_found.x"),
            self.config_reader.get_value("close_all_windows.map_found.y")
        )
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.prime_time.x"),
            self.config_reader.get_value("close_all_windows.prime_time.y")
        )

        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.free_outpost.x"),
            self.config_reader.get_value("close_all_windows.free_outpost.y")
        )
        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.triple_action.x"),
            self.config_reader.get_value("close_all_windows.triple_action.y")
        )
        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.info_dialog.x"),
            self.config_reader.get_value("close_all_windows.info_dialog.y")
        )
        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.close_ali.x"),
            self.config_reader.get_value("close_all_windows.close_ali.y")
        )
    # POSLAT_BASIC_UTOK_KONEC_________________________________________
    # JEZDENI_PEVNOSTI________________________________________________

    # JEZDENI_PEVNOSTI_START__________________________________________
    def toggle_loop(self, event=None):
        """Spustí nebo zastaví smyčku pro útok na základě stavu."""
        if self.is_running:
            self.is_running = False
            self.log_message(
                status="stopped",
                message="Smyčka byla zastavena."
            )
            self.update_button_text()
        else:
            self.is_running = True
            self.log_message(
                status="running",
                message="Smyčka byla spuštěna."
            )
            self.update_button_text()
            self.start_attack_loop()

    def start_attack_loop(self):
        """Spustí smyčku útoku v samostatném vlákně."""
        thread = threading.Thread(target=self._attack_loop)
        thread.daemon = True
        thread.start()

    def log_message(self, status: str, message: str):
        log = LogMessage(
            time=time.time(),
            status=status,
            module=self.__class__.__name__,
            message=message
        )
        message_queue.put(log)

    def _attack_loop(self):
        """Abstraktní metoda, která musí být implementována v podtřídě."""
        raise NotImplementedError("Tato metoda musí být implementována v podtřídě.")

    def update_button_text(self):
        """Abstraktní metoda pro aktualizaci textu tlačítka."""
        raise NotImplementedError("Tato metoda musí být implementována v podtřídě.")

    def ReturnConfigValue(self, key_path):
        return self.config_reader.get_value(key_path)

    def SendAttackMultiWaveAuto(self,skip_samu_nomad_cd=False, target_x=None, target_y=None, send_with_cords=True,
                                feather_horse=None, note=None, first_wave_from_bottom=None,other_waves_from_bottom=None, auto_fill_waves=None ):
        if send_with_cords:
            # pyautogui.press("Tab")
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.y")
            )
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.y")
            )
            time.sleep(self.click_delay_offset)
            pyautogui.typewrite(str(target_x))
            pyautogui.press("Tab")
            pyautogui.typewrite(str(target_y))
            pyautogui.press("Enter")
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.y")
        )
        time.sleep(self.click_delay_offset)
        # skip cd
        if skip_samu_nomad_cd:
            self.SkipNomadSamuCooldown()
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_3.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_3.y")
        )

        # close windows
        self.CloseWindowsPopups()
        # close windows end
        time.sleep(self.click_delay_offset)
        #fillnout vlny celkove
        #vychozi pozice je NIC NEVYBRANO
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_1.x"),
            self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_1.y")
        )
        time.sleep(self.click_delay_offset)

        self.SelectCode(first_wave_from_bottom)

        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_4.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_4.y")
        )
        time.sleep(self.click_delay_offset)

        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_2.x"),
            self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_2.y")
        )
        time.sleep(self.click_delay_offset)

        self.SelectCode(other_waves_from_bottom)
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_4.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_4.y")
        )
        if auto_fill_waves:
            time.sleep(self.click_delay_offset)
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_3.x"),
                self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_3.y")
            )

        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_1.x"),
            self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_1.x"),
            self.config_reader.get_value("actions_click_patter.fill_all_waves_atk.click_1.y")
        )
        time.sleep(self.click_delay_offset)


        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_5.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_5.y")
        )
        time.sleep(self.click_delay_offset)
        # kone:
        if (feather_horse):
            pyautogui.click(
                self.config_reader.get_value("horses.feather.x"),
                self.config_reader.get_value("horses.feather.y")
            )
        else:
            pyautogui.click(
                self.config_reader.get_value("horses.gold.x"),
                self.config_reader.get_value("horses.gold.y")
            )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_6.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_6.y")
        )
        time.sleep(self.click_delay_offset)

