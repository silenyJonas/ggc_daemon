import pyautogui
from services.base_tab import BaseTab
import time
from datetime import datetime


class DeliverySpamManager(BaseTab):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def Run(self, tasks, auto_reward, zeli_pos, zima_pos, pisek_pos, ohen_pos, tab_instance):
        """
        Hlavní spouštěcí metoda volaná z GUI vlákna.
        """
        tab_instance.log_message(status="info", message="--- Manager aktivní (DMS -> FWD) ---")

        # Mapování pozic pro DMS (všechny světy)
        dms_world_map = [
            ("ZELI", zeli_pos),
            ("ZIMA", zima_pos),
            ("PISEK", pisek_pos),
            ("OHEN", ohen_pos)
        ]

        # --- 1. VLNA: DMS (Suroviny) ---
        # Zde zůstává původní logika: Target 1 (všechny světy), Target 2 (všechny světy)...
        tab_instance.log_message(status="info", message="=== START: DMS Sekce (Všechny světy) ===")
        self._process_full_cycle(tasks, "dms", dms_world_map, auto_reward, tab_instance)

        if not tab_instance.is_running:
            return

        # --- 2. VLNA: FWD (Špionáže) ---
        # Zde se změnila logika: Pouze ZELENÝ svět, postupně všechny cíle
        tab_instance.log_message(status="info", message="=== START: FWD Sekce (Pouze ZELI) ===")

        # Pro FWD definujeme "mapu" pouze s jedním světem
        fwd_world_map = [("ZELI", zeli_pos)]
        self._process_full_cycle(tasks, "fwd", fwd_world_map, auto_reward, tab_instance)

        tab_instance.log_message(status="info", message="Všechny sekce dokončeny.")

    def _process_full_cycle(self, tasks, mode, world_map, auto_reward, tab_instance):
        """
        Univerzální procesor. U DMS projde 4 světy na úkol, u FWD jen ten, který mu Run předá (ZELI).
        """
        active_tasks = [t for t in tasks if t.get(f"{mode}_active")]

        if not active_tasks:
            tab_instance.log_message(status="info", message=f"Žádné aktivní úkoly pro {mode.upper()}.")
            return

        for task in active_tasks:
            if not tab_instance.is_running:
                break

            target_name = task.get("name")
            is_feather = task.get(f"{mode}_horse_feather")

            tab_instance.log_message(status="info", message=f"--- Úkol: {target_name} ---")

            # Pro každý target projedeme světy v dodané mapě
            for world_name, world_pos in world_map:
                if not tab_instance.is_running:
                    break

                # Změna světa (u FWD proběhne jen jednou na začátku nebo se potvrdí ZELI)
                tab_instance.log_message(status="info",
                                         message=f"[{mode.upper()}] Svět: {world_name} (Pozice: {world_pos})")
                self.ChangeWorl(world_pos)

                # Vyhledání cíle na mapě
                self.SelectCastle(target_name)

                # Volání specifické odesílací funkce
                if mode == "dms":
                    self.DMSSend(target_name, is_feather, 13, world_name, tab_instance, auto_reward)
                else:
                    self.FWDSend(target_name, is_feather, 29, world_name, tab_instance, auto_reward)

            # Aktualizace času po dokončení úkolu (u FWD po dokončení ZELI fáze)
            task[f"{mode}_last_wipe"] = datetime.now().strftime("%H:%M:%S")
            tab_instance._save_data()



    def DMSSend(self, target, is_feather, count, world_name, tab_instance, auto_reward):

        for i in range(1, count + 1):
            if not tab_instance.is_running: break
            time.sleep(0.5)
            c2_x = self.config_reader.get_value("actions_click_patter.find_by_name_world_map.click_2.x")
            c2_y = self.config_reader.get_value("actions_click_patter.find_by_name_world_map.click_2.y")
            pyautogui.click(c2_x, c2_y)
            time.sleep(0.1)
            pyautogui.moveTo(c2_x + 4, c2_y + 4)
            time.sleep(0.1)
            pyautogui.click(c2_x + 4, c2_y + 4)
            for cid in ["3", "4", "5"]:
                time.sleep(0.5)
                pyautogui.click(
                    self.config_reader.get_value(f"actions_click_patter.find_by_name_world_map.click_{cid}.x"),
                    self.config_reader.get_value(f"actions_click_patter.find_by_name_world_map.click_{cid}.y")
                )
            cid_horse = "6" if is_feather else "7"
            time.sleep(0.5)
            pyautogui.click(
                self.config_reader.get_value(f"actions_click_patter.find_by_name_world_map.click_{cid_horse}.x"),
                self.config_reader.get_value(f"actions_click_patter.find_by_name_world_map.click_{cid_horse}.y")
            )
            time.sleep(0.5)
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.find_by_name_world_map.click_8.x"),
                self.config_reader.get_value("actions_click_patter.find_by_name_world_map.click_8.y")
            )
            tab_instance.log_message(status="info", message=f"[{world_name}] DMS {i}/{count} odesláno na {target}")
            if auto_reward:
                self.CloseWindowsPopups()
                pyautogui.click(1200, 762)
                
    def FWDSend(self, target, is_feather, count, world_name, tab_instance, auto_reward):
        if auto_reward:
            self.CloseWindowsPopups()
            if auto_reward:
                self.CloseWindowsPopups()
                pyautogui.click(1200, 762)
        wait_interval = 6.5
        for i in range(1, count + 1):
            if not tab_instance.is_running: break
            start_time = time.perf_counter()
            time.sleep(0.5)
            c1_x = self.config_reader.get_value("actions_click_patter.send_spio_cycle.click_1.x")
            c1_y = self.config_reader.get_value("actions_click_patter.send_spio_cycle.click_1.y")
            pyautogui.click(c1_x, c1_y)
            time.sleep(0.1)
            pyautogui.moveTo(c1_x + 4, c1_y + 4)
            time.sleep(0.1)
            pyautogui.click(c1_x + 4, c1_y + 4)
            for cid in ["2", "3", "4"]:
                time.sleep(0.5)
                pyautogui.click(
                    self.config_reader.get_value(f"actions_click_patter.send_spio_cycle.click_{cid}.x"),
                    self.config_reader.get_value(f"actions_click_patter.send_spio_cycle.click_{cid}.y")
                )
            cid_horse = "5" if is_feather else "6"
            time.sleep(0.5)
            pyautogui.click(
                self.config_reader.get_value(f"actions_click_patter.send_spio_cycle.click_{cid_horse}.x"),
                self.config_reader.get_value(f"actions_click_patter.send_spio_cycle.click_{cid_horse}.y")
            )
            time.sleep(0.5)
            pyautogui.click(
                self.config_reader.get_value(f"actions_click_patter.send_spio_cycle.click_7.x"),
                self.config_reader.get_value(f"actions_click_patter.send_spio_cycle.click_7.y")
            )
            tab_instance.log_message(status="info", message=f"[{world_name}] FWD {i}/{count} odesláno na {target}")
            if i < count:
                elapsed = time.perf_counter() - start_time
                to_wait = wait_interval - elapsed
                if to_wait > 0: time.sleep(to_wait)

    def SelectCastle(self, castle_name):
        time.sleep(0.5)
        for _ in range(3):
            pos_x = self.config_reader.get_value("actions_click_patter.find_by_name_world_map.click_1.x")
            pos_y = self.config_reader.get_value("actions_click_patter.find_by_name_world_map.click_1.y")
            pyautogui.click(pos_x, pos_y)
            time.sleep(0.2)
            pyautogui.click(pos_x, pos_y)
            pyautogui.press('Del')
            time.sleep(0.1)
        pyautogui.typewrite(castle_name)
        time.sleep(0.2)
        pyautogui.press('Enter')
        time.sleep(1.0)

    def ChangeWorl(self, position):
        time.sleep(0.5)
        pyautogui.click(
            self.config_reader.get_value("settings.castle_list_cords.base_x"),
            self.config_reader.get_value("settings.castle_list_cords.base_y")
        )
        time.sleep(0.5)
        pyautogui.click(
            self.config_reader.get_value("settings.castle_list_cords.base_x"),
            self.config_reader.get_value("settings.castle_list_cords.castle_y_" + str(position))
        )
        time.sleep(2.0)