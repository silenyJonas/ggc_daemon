from services.base_tab import BaseTab
import pyautogui
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import tkinter as tk
import threading
class FortressManager(BaseTab):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.closing_windows_allowed = True
        self.send_with_cords = True

    def MultitaskingFortressRider(
            self,
            winter_atk_code,
            sand_atk_code,
            fire_atk_code,
            winter_castle_list_pos=2,
            sand_castle_list_pos=3,
            fire_castle_list_pos=4,
            feather_forse=True,
            distance=99999,
            closing_popups=True,
            scan_before_run=False,
            world_scan=None,
            auto_buy_speed_bonus=False
    ):
        self.log_message(status="info", message="Multi-tasking rotace spuštěna.")

        if closing_popups:
            threading.Thread(target=self.close_popups_loop, daemon=True).start()

        records = self.ReturnSortedFortressList()
        records = self.FilterFortressListByDistance(records=records, max_distance=distance)

        # stav přípravy pro každý záznam
        prepared_world = {}  # rec -> bool (byl přepnut svět)
        prepared_cords = {}  # rec -> {"atk_code": str, "cords_found": bool}

        ali_swap = True

        while True:
            now = datetime.now()

            if auto_buy_speed_bonus:
                current_time = datetime.now().strftime("%H:%M:%S")
                if "11:03:00" <= current_time <= "11:03:30":
                    self.BuySpeedBonus()

            if not records:
                self.log_message(status="info", message="Žádné budoucí záznamy v DB.")
                time.sleep(1)
                continue

            try:
                expired_records = []
                skipped_any = False

                for rec in list(records):
                    world_code, coords, time_part = rec.split(";")
                    next_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
                    delta = (next_time - now).total_seconds()

                    castle_x = castle_y = 0
                    if world_code == "ZIM":
                        castle_x = self.config_reader.get_value("main_castle_cords.winter.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.winter.y")
                    elif world_code == "PSK":
                        castle_x = self.config_reader.get_value("main_castle_cords.sand.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.sand.y")
                    elif world_code == "OHN":
                        castle_x = self.config_reader.get_value("main_castle_cords.fire.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.fire.y")

                    target_x_str, target_y_str = coords.split(":")
                    target_x = int(target_x_str)
                    target_y = int(target_y_str)

                    dist = self.GetDistance(
                        castle_x=castle_x,
                        castle_y=castle_y,
                        target_x=target_x,
                        target_y=target_y
                    )

                    if dist > distance:
                        self.log_message(
                            status="info",
                            message=f"Přeskočeno (daleko): {world_code} | [{coords}] | vzdálenost {dist}"
                        )
                        records.remove(rec)
                        prepared_world.pop(rec, None)
                        prepared_cords.pop(rec, None)
                        skipped_any = True
                        continue

                    if delta <= 0:
                        expired_records.append(rec)
                    else:



                        # --- ROZDÍL OD SINGLE: přepni svět 5s před expirací ---
                        if int(delta) == 5 and not prepared_world.get(rec, False):

                            # co dva utoky odkliknout ali
                            if (ali_swap):
                                ali_swap = False
                                pyautogui.click(1225, 267)
                            else:
                                ali_swap = True

                            selected_atk_code = ""
                            if world_code == "ZIM":
                                selected_atk_code = str(winter_atk_code)
                            elif world_code == "PSK":
                                selected_atk_code = str(sand_atk_code)
                            elif world_code == "OHN":
                                selected_atk_code = str(fire_atk_code)

                            self.ChangeWorld(
                                world_code=world_code,
                                winter_castle_list_pos=winter_castle_list_pos,
                                sand_castle_list_pos=sand_castle_list_pos,
                                fire_castle_list_pos=fire_castle_list_pos
                            )
                            prepared_world[rec] = True
                            prepared_cords[rec] = {"atk_code": selected_atk_code, "cords_found": False}

                        # --- stejné jako single: najdi věž 3s před expirací ---
                        if int(delta) == 3 and prepared_world.get(rec, False):
                            cords_data = prepared_cords.get(rec, {})
                            if not cords_data.get("cords_found", False):
                                self.FindByCords(target_x=target_x, target_y=target_y)
                                prepared_cords[rec]["cords_found"] = True

                        self.log_message(
                            status="info",
                            message=f"Čeká: {world_code} | [{coords}] | Dist: {round(dist)} | Za: {int(delta)} s"
                        )
                        break  # stejné jako single – break na prvním čekajícím

                if skipped_any and not expired_records:
                    self.log_message(status="info", message="Žádný vhodný záznam v dosahu, čekám...")

                # --- Spuštění expirovaných útoků ---
                for rec in expired_records:
                    world_code, coords, _ = rec.split(";")
                    target_x, target_y = coords.split(":")

                    cords_data = prepared_cords.get(rec, {})
                    send_with_cords = not cords_data.get("cords_found", False)



                    # --- ROZDÍL OD SINGLE: vyber atk_code a přepni svět pokud ještě nebyl přepnut ---
                    if not prepared_world.get(rec, False):
                        selected_atk_code = ""
                        if world_code == "ZIM":
                            selected_atk_code = str(winter_atk_code)
                        elif world_code == "PSK":
                            selected_atk_code = str(sand_atk_code)
                        elif world_code == "OHN":
                            selected_atk_code = str(fire_atk_code)

                        self.ChangeWorld(
                            world_code=world_code,
                            winter_castle_list_pos=winter_castle_list_pos,
                            sand_castle_list_pos=sand_castle_list_pos,
                            fire_castle_list_pos=fire_castle_list_pos
                        )
                    else:
                        selected_atk_code = cords_data.get("atk_code", "")

                    self.log_message(status="info", message=f"Spouštím útok: {world_code} | [{coords}]")
                    self.closing_windows_allowed = False
                    time.sleep(2.5)  # stejné jako single




                    self.SendAttackFirstWaveAuto(
                        attack_code=selected_atk_code,
                        target_x=int(target_x),
                        target_y=int(target_y),
                        feather_horse=feather_forse,
                        note="Útok poslán",
                        close_popups=True,
                        send_with_cords=send_with_cords
                    )
                    self.closing_windows_allowed = True

                    prepared_world.pop(rec, None)
                    prepared_cords.pop(rec, None)
                    records.remove(rec)

            except Exception as e:
                msg = f"Chyba při čtení záznamů (Multitasking): {e}"
                self.log_message(status="error", message=msg)

            time.sleep(1)
    def MultitaskingFortressRider_save(
            self,
            winter_atk_code,
            sand_atk_code,
            fire_atk_code,
            winter_castle_list_pos=2,
            sand_castle_list_pos=3,
            fire_castle_list_pos=4,
            feather_forse=True,
            distance=99999,
            closing_popups=True,
            scan_before_run=False,
            world_scan=None,
            auto_buy_speed_bonus=False
    ):
        self.log_message(status="info", message="Multi-tasking rotace spuštěna.")
        if scan_before_run:
            # udela se scan na world_scan
            pass

        if closing_popups:
            # proběhne self.CloseWindowsPopups()
            pass

        if closing_popups:
            threading.Thread(target=self.close_popups_loop, daemon=True).start()

        records = self.ReturnSortedFortressList()
        records = self.FilterFortressListByDistance(records=records, max_distance=distance)

        while True:

            now = datetime.now()

            if auto_buy_speed_bonus:
                current_time = datetime.now().strftime("%H:%M:%S")
                if "11:03:00" <= current_time <= "11:03:30":
                    self.BuySpeedBonus()

            if not records:
                self.log_message(status="info", message="Žádné budoucí záznamy v DB.")
                time.sleep(1)
                continue

            try:
                expired_records = []  # seznam expirovaných a validních záznamů
                skipped_any = False

                for rec in list(records):  # kopie, protože budeme mazat
                    world_code, coords, time_part = rec.split(";")
                    next_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
                    delta = (next_time - now).total_seconds()

                    # souřadnice hlavního hradu
                    castle_x = castle_y = 0
                    if world_code == "ZIM":
                        castle_x = self.config_reader.get_value("main_castle_cords.winter.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.winter.y")
                    elif world_code == "PSK":
                        castle_x = self.config_reader.get_value("main_castle_cords.sand.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.sand.y")
                    elif world_code == "OHN":
                        castle_x = self.config_reader.get_value("main_castle_cords.fire.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.fire.y")

                    target_x_str, target_y_str = coords.split(":")
                    target_x = int(target_x_str)
                    target_y = int(target_y_str)

                    dist = self.GetDistance(
                        castle_x=castle_x,
                        castle_y=castle_y,
                        target_x=target_x,
                        target_y=target_y
                    )

                    if dist > distance:
                        self.log_message(
                            status="info",
                            message=f"Přeskočeno (daleko): {world_code} | [{coords}] | vzdálenost {round(dist)}"
                        )
                        records.remove(rec)
                        skipped_any = True
                        continue

                    if delta <= 0:
                        expired_records.append(rec)
                    else:
                        self.log_message(
                            status="info",
                            message=f"Čeká: {world_code} | [{coords}] | Dist: {round(dist)} | Za: {int(delta)} s"
                        )
                        break

                if skipped_any and not expired_records:
                    self.log_message(status="info", message="Žádný vhodný záznam v dosahu, čekám...")

                # všechny expirované útoky spustíme
                for rec in expired_records:
                    world_code, coords, _ = rec.split(";")
                    target_x, target_y = coords.split(":")

                    selected_atk_code = ""
                    if world_code == "ZIM":
                        selected_atk_code = str(winter_atk_code)
                    elif world_code == "PSK":
                        selected_atk_code = str(sand_atk_code)
                    elif world_code == "OHN":
                        selected_atk_code = str(fire_atk_code)

                    self.ChangeWorld(
                        world_code=world_code,
                        winter_castle_list_pos=winter_castle_list_pos,
                        sand_castle_list_pos=sand_castle_list_pos,
                        fire_castle_list_pos=fire_castle_list_pos
                    )
                    self.closing_windows_allowed = False
                    self.SendAttackFirstWaveAuto(
                        attack_code=selected_atk_code,
                        target_x=int(target_x),
                        target_y=int(target_y),
                        feather_horse=feather_forse,
                        note="Útok poslán",
                        close_popups=True
                    )
                    self.closing_windows_allowed = True
                    records.remove(rec)

            except Exception as e:
                msg = f"Chyba při čtení záznamů (Multitasking): {e}"
                self.log_message(status="error", message=msg)

            time.sleep(1)

    def GenerateFortressGraph(self):
        try:
            self.db_writer.UpdateBaseDb("all")

            data = self.db_writer.getSortedDb("db")
            if not data:
                self.log_message(status="info", message="DB je prázdná, není co zobrazit.")
                return

            records: list[tuple[str, datetime]] = []
            for rec in data:
                try:
                    world_code, _, time_part = rec.split(";")
                    record_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
                    records.append((world_code, record_time))
                except Exception:
                    self.log_message(status="error", message=f"Chybný záznam v DB: {rec}")

            if not records:
                self.log_message(status="info", message="Žádné validní záznamy.")
                return

            start_time = min(r[1] for r in records)
            end_time = max(r[1] for r in records)

            # Zaokrouhlení startu na nejbližších 6h zpět
            start_time = start_time.replace(minute=0, second=0, microsecond=0)
            start_time = start_time - timedelta(hours=start_time.hour % 6)

            intervals = []
            current = start_time
            while current <= end_time:
                intervals.append(current)
                current += timedelta(hours=6)

            # --- napočítat počty ---
            zim_counts = [0] * (len(intervals))
            psk_counts = [0] * (len(intervals))
            ohn_counts = [0] * (len(intervals))

            for world, t in records:
                idx = int((t - start_time).total_seconds() // (6 * 3600))
                if 0 <= idx < len(intervals):
                    if world == "ZIM":
                        zim_counts[idx] += 1
                    elif world == "PSK":
                        psk_counts[idx] += 1
                    elif world == "OHN":
                        ohn_counts[idx] += 1

            labels = [dt.strftime("%d.%m\n%H:%M") for dt in intervals]

            # --- vytvoření okna ---
            graph_window = tk.Toplevel(self)
            graph_window.title("Graf obnovy pevností (6h intervaly)")
            graph_window.geometry("1200x600")

            fig, ax = plt.subplots(figsize=(10, 6))

            bar1 = ax.bar(labels, zim_counts, color="blue", label="Zima (ZIM)")
            bar2 = ax.bar(labels, psk_counts, bottom=zim_counts, color="red", label="Písek (PSK)")
            bar3 = ax.bar(labels, ohn_counts,
                          bottom=[zim_counts[i] + psk_counts[i] for i in range(len(zim_counts))],
                          color="black", label="Oheň (OHN)")

            # --- přidání počtů na sloupce ---
            for i in range(len(labels)):
                if zim_counts[i] > 0:
                    ax.text(i, zim_counts[i] / 2, str(zim_counts[i]), ha='center', va='center', color='white',
                            fontsize=9)
                if psk_counts[i] > 0:
                    ax.text(i, zim_counts[i] + psk_counts[i] / 2, str(psk_counts[i]), ha='center', va='center',
                            color='white', fontsize=9)
                if ohn_counts[i] > 0:
                    ax.text(i, zim_counts[i] + psk_counts[i] + ohn_counts[i] / 2, str(ohn_counts[i]), ha='center',
                            va='center', color='white', fontsize=9)

            ax.set_title("Obnova pevností po 6 hodinách")
            ax.set_xlabel("Časové intervaly")
            ax.set_ylabel("Počet obnovených pevností")
            ax.legend()
            ax.grid(axis="y", linestyle="--", alpha=0.7)

            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.log_message(status="info", message="Sloupcový graf obnovy pevností zobrazen s počty.")

        except Exception as e:
            self.log_message(status="error", message=f"Chyba při generování grafu: {e}")

    def SingletaskingFortressRider_save(self, feather_forse=True, distance=99999, closing_popups=True, scan_before_run=False,
                                   world_scan=None,auto_buy_speed_bonus=False):

        self.log_message(status="info", message="Single-tasking rotace spuštěna.")
        if scan_before_run:
            # udela se scan na world_scan
            pass

        if closing_popups:
            # proběhne self.CloseWindowsPopups()
            pass

        records = self.ReturnSortedFortressList()
        records = self.FilterFortressListByDistance(records=records, max_distance=distance)

        while True:
            now = datetime.now()

            if auto_buy_speed_bonus:
                current_time = datetime.now().strftime("%H:%M:%S")
                if "11:03:00" <= current_time <= "11:03:30":
                    self.BuySpeedBonus()

            if not records:
                self.log_message(status="info", message="Žádné budoucí záznamy v DB.")
                time.sleep(1)
                continue

            try:
                expired_records = []  # seznam expirovaných a validních záznamů
                skipped_any = False  # jestli jsme něco přeskočili

                for rec in list(records):  # kopie seznamu, protože ho můžeme měnit
                    world_code, coords, time_part = rec.split(";")
                    next_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
                    delta = (next_time - now).total_seconds()

                    # souřadnice hlavního hradu podle světa
                    castle_x = castle_y = 0
                    if world_code == "ZIM":
                        castle_x = self.config_reader.get_value("main_castle_cords.winter.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.winter.y")
                    elif world_code == "PSK":
                        castle_x = self.config_reader.get_value("main_castle_cords.sand.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.sand.y")
                    elif world_code == "OHN":
                        castle_x = self.config_reader.get_value("main_castle_cords.fire.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.fire.y")

                    target_x_str, target_y_str = coords.split(":")
                    target_x = int(target_x_str)
                    target_y = int(target_y_str)

                    dist = self.GetDistance(
                        castle_x=castle_x,
                        castle_y=castle_y,
                        target_x=target_x,
                        target_y=target_y
                    )

                    if dist > distance:
                        self.log_message(status="info",
                                         message=f"Přeskočeno (daleko): {world_code} | [{coords}] | vzdálenost {dist}")
                        records.remove(rec)
                        skipped_any = True
                        continue

                    if delta <= 0:
                        expired_records.append(rec)
                    else:
                        # tento je validní, ale ještě neexpiroval → počkáme
                        self.log_message(
                            status="info",
                            message=f"Čeká: {world_code} | [{coords}] | Dist: {round(dist)} | Za: {int(delta)} s"
                        )
                        break

                # pokud jsme něco přeskočili a nemáme expired_records → oznámíme
                if skipped_any and not expired_records:
                    self.log_message(status="info", message="Žádný vhodný záznam v dosahu, čekám...")

                # všechny expirované útoky spustíme
                for rec in expired_records:
                    world_code, coords, _ = rec.split(";")
                    target_x, target_y = coords.split(":")
                    self.log_message(status="info", message=f"Spouštím útok: {world_code} | [{coords}]")
                    self.SendAttackFirstWaveAuto(
                        target_x=int(target_x),
                        target_y=int(target_y),
                        feather_horse=feather_forse,
                        note="Útok poslán",
                        close_popups=False
                    )
                    records.remove(rec)

            except Exception as e:
                msg = f"Chyba při čtení záznamů: {e}"
                self.log_message(status="error", message=msg)

            time.sleep(1)

    def close_popups_loop(self):
        while True:
            if self.closing_windows_allowed:
                #self.CloseWindowsPopups()
                time.sleep(30)  # každých 30 sekund

    def SingletaskingFortressRider(self, feather_forse=True, distance=99999, closing_popups=True, scan_before_run=False,
                                   world_scan=None, auto_buy_speed_bonus=False):
        self.log_message(status="info", message="Single-tasking rotace spuštěna.")

        if scan_before_run:
            # udela se scan na world_scan
            pass

        # Spustíme vlákno, které bude pravidelně zavírat pop-up okna

        if closing_popups:
            threading.Thread(target=self.close_popups_loop, daemon=True).start()

        records = self.ReturnSortedFortressList()
        records = self.FilterFortressListByDistance(records=records, max_distance=distance)

        while True:
            now = datetime.now()

            if auto_buy_speed_bonus:
                current_time = datetime.now().strftime("%H:%M:%S")
                if "11:03:00" <= current_time <= "11:03:30":
                    self.BuySpeedBonus()

            if not records:
                self.log_message(status="info", message="Žádné budoucí záznamy v DB.")
                time.sleep(1)
                continue

            try:
                expired_records = []  # seznam expirovaných a validních záznamů
                skipped_any = False  # jestli jsme něco přeskočili

                for rec in list(records):  # kopie seznamu, protože ho můžeme měnit
                    world_code, coords, time_part = rec.split(";")
                    next_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
                    delta = (next_time - now).total_seconds()

                    # souřadnice hlavního hradu podle světa
                    castle_x = castle_y = 0
                    if world_code == "ZIM":
                        castle_x = self.config_reader.get_value("main_castle_cords.winter.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.winter.y")
                    elif world_code == "PSK":
                        castle_x = self.config_reader.get_value("main_castle_cords.sand.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.sand.y")
                    elif world_code == "OHN":
                        castle_x = self.config_reader.get_value("main_castle_cords.fire.x")
                        castle_y = self.config_reader.get_value("main_castle_cords.fire.y")

                    target_x_str, target_y_str = coords.split(":")
                    target_x = int(target_x_str)
                    target_y = int(target_y_str)

                    dist = self.GetDistance(
                        castle_x=castle_x,
                        castle_y=castle_y,
                        target_x=target_x,
                        target_y=target_y
                    )

                    if dist > distance:
                        self.log_message(status="info",
                                         message=f"Přeskočeno (daleko): {world_code} | [{coords}] | vzdálenost {dist}")
                        records.remove(rec)
                        skipped_any = True
                        continue

                    if delta <= 0:
                        expired_records.append(rec)
                    else:
                        # tento je validní, ale ještě neexpiroval → počkáme
                        if int(delta)==3:
                            self.send_with_cords=False
                            self.FindByCords(target_x=target_x,target_y=target_y)
                        self.log_message(
                            status="info",
                            message=f"Čeká: {world_code} | [{coords}] | Dist: {round(dist)} | Za: {int(delta)} s"
                        )
                        break

                # pokud jsme něco přeskočili a nemáme expired_records → oznámíme
                if skipped_any and not expired_records:
                    self.log_message(status="info", message="Žádný vhodný záznam v dosahu, čekám...")

                # všechny expirované útoky spustíme
                for rec in expired_records:
                    world_code, coords, _ = rec.split(";")
                    target_x, target_y = coords.split(":")
                    self.log_message(status="info", message=f"Spouštím útok: {world_code} | [{coords}]")
                    self.closing_windows_allowed = False
                    time.sleep(2.5) # TOTO URCUJE DOBU PRED UTOPKEM CD
                    self.SendAttackFirstWaveAuto(
                        target_x=int(target_x),
                        target_y=int(target_y),
                        feather_horse=feather_forse,
                        note="Útok poslán",
                        close_popups=True,
                        send_with_cords=self.send_with_cords
                    )
                    self.send_with_cords = True
                    self.closing_windows_allowed = True
                    records.remove(rec)

            except Exception as e:
                msg = f"Chyba při čtení záznamů: {e}"
                self.log_message(status="error", message=msg)

            time.sleep(1)

    def FindByCords(self, target_x, target_y):
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
    def FilterFortressListByDistance(self, records, max_distance):
        """
        Vrátí seznam záznamů, které vyhovují vzdálenosti od hlavního hradu.

        :param records: seznam záznamů ve formátu "OHN;575:575;2025-09-21 18:08:43"
        :param max_distance: maximální vzdálenost
        :return: filtrovaný seznam záznamů
        """
        filtered = []
        for record in records:
            try:
                world_code, coords, _ = record.split(";")
                target_x, target_y = map(int, coords.split(":"))

                # nastavení souřadnic hradu podle světa
                if world_code == "ZIM":
                    castle_x = self.config_reader.get_value("main_castle_cords.winter.x")
                    castle_y = self.config_reader.get_value("main_castle_cords.winter.y")
                elif world_code == "PSK":
                    castle_x = self.config_reader.get_value("main_castle_cords.sand.x")
                    castle_y = self.config_reader.get_value("main_castle_cords.sand.y")
                else:  # OHN
                    castle_x = self.config_reader.get_value("main_castle_cords.fire.x")
                    castle_y = self.config_reader.get_value("main_castle_cords.fire.y")

                # pokud některá souřadnice není nastavena, přeskočíme záznam
                if castle_x is None or castle_y is None:
                    continue

                # vzdálenost
                distance = self.GetDistance(int(castle_x), int(castle_y), target_x, target_y)
                if distance <= max_distance:
                    filtered.append(record)
            except Exception as e:
                self.log_message(status="error", message=f"Chybný záznam: {record} | {e}")

        return filtered

    def BuySpeedBonus(self):
        print("BuySpeedBonus")
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_1.x"),
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_1.y"),
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_2.x"),
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_2.y"),
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_3.x"),
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_3.y"),
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_4.x"),
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_4.y"),
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_5.x"),
            self.config_reader.get_value("actions_click_patter.buy_speed_bonus.clicl_5.y"),
        )

    def ChangeWorld(self, world_code, winter_castle_list_pos, sand_castle_list_pos, fire_castle_list_pos):
        print(world_code)
        base_x = self.config_reader.get_value("settings.castle_list_cords.base_x")
        base_y = self.config_reader.get_value("settings.castle_list_cords.base_y")
        suffix_winter = self.config_reader.get_value("settings.castle_list_cords.castle_y_"+str(winter_castle_list_pos))
        suffix_sand = self.config_reader.get_value("settings.castle_list_cords.castle_y_"+str(sand_castle_list_pos))
        suffix_fire = self.config_reader.get_value("settings.castle_list_cords.castle_y_"+str(fire_castle_list_pos))

        sleep_time = self.config_reader.get_value("settings.offsets.default_click_delay")

        print(suffix_winter)
        print(suffix_sand)
        print(suffix_fire)

        time.sleep(sleep_time)
        pyautogui.click(
            base_x,
            base_y
        )
        time.sleep(sleep_time)
        if world_code == "ZIM":
            pyautogui.click(
                base_x,
                suffix_winter
            )
        if world_code == "PSK":
            pyautogui.click(
                base_x,
                suffix_sand
            )
        if world_code == "OHN":
            pyautogui.click(
                base_x,
                suffix_fire
            )

        self.log_message(
            status="ok",
            message="Svět změněn na: "+ world_code
        )

        time.sleep(sleep_time)

    def ReturnSortedFortressList(self):
        if not hasattr(self, "db_writer"):
            self.log_message(status="error", message="DbWriter není inicializován!")
            return []

        # předpokládáme, že JSON název = "db" nebo podle potřeby
        return self.db_writer.getSortedDb("db")
