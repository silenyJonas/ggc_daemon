from services.base_tab import BaseTab
import json
import threading
import pyautogui
import re
import os
import time
from datetime import datetime, timedelta
import cv2
import numpy as np
import os
import pyautogui
from datetime import datetime, timedelta

class ScanManager(BaseTab):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.can_continue = False

    def ReuturnCanContinue(self):
        return self.can_continue


    def ChangeWorld(self, current_pos):
        base_x = self.config_reader.get_value("settings.castle_list_cords.base_x")
        base_y = self.config_reader.get_value("settings.castle_list_cords.base_y")

        castle_y = self.config_reader.get_value("settings.castle_list_cords.castle_y_"+str(current_pos))

        sleep_time = self.config_reader.get_value("settings.offsets.default_click_delay")

        time.sleep(2)
        pyautogui.click(base_x,base_y)
        time.sleep(2)

        pyautogui.click(base_x, castle_y)
        time.sleep(2)

    def ScanFort_save(self, json_name: str, scan_distance=50, dismiss_popups=True, scan_both_worlds=False, sand_pos=4, fire_pos=5):
        """Provede scan pevností. Pokud je scan_both_worlds True, ignoruje json_name a projede Písek i Oheň."""

        self.can_continue = False

        def _scan_loop():
            # Určení světů ke scanování
            worlds_to_scan = []
            if scan_both_worlds:
                worlds_to_scan = ["sand", "fire"]
            else:
                worlds_to_scan = [json_name]

            # Společný odpočet na začátku
            countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
            for x in range(countdown, 0, -1):
                if self.stop_event.is_set():
                    self.log_message(status="info", message="ScanFort zastaven uživatelem během odpočtu")
                    self.can_continue = True
                    return
                self.log_message(status="info", message=f"Spuštění ScanFort za: {x}")
                time.sleep(1)

            # Iterace přes vybrané světy
            for current_world in worlds_to_scan:
                if self.stop_event.is_set():
                    break

                self.log_message(status="info", message=f"Začínám scan světa: {current_world}")

                # Vymazání DB pro daný svět před startem
                self.ClearFortArray(current_world)

                # Přepnutí světa (pokud je implementováno)
                self.ChangeWorld(current_world, sand_pos, fire_pos)

                # --- Nastavení souřadnic hradu a načtení JSON dat ---
                castle_x = self.config_reader.get_value(f"main_castle_cords.{current_world}.x")
                castle_y = self.config_reader.get_value(f"main_castle_cords.{current_world}.y")

                base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "fortress_data_storage")
                json_path = os.path.join(base_dir, f"{current_world}.json")

                with open(json_path, "r", encoding="utf-8") as f:
                    fort_data = json.load(f)

                forts_sorted = sorted(fort_data.items(), key=lambda kv: int(kv[0].split("_")[1]))
                counter = 1
                ocr_threads = []

                # --- Samotný průchod pevnostmi (Logika zůstává stejná) ---
                for fort_key, target in forts_sorted:
                    if self.stop_event.is_set():
                        self.log_message(status="info",
                                         message=f"ScanFort zastaven uživatelem během světa {current_world}")
                        break

                    if dismiss_popups and counter % 10 == 0:
                        self.CloseWindowsPopups()

                    private_click_offset_01 = 0.1
                    private_click_offset_02 = 0.2
                    private_click_offset_05 = 0.2
                    target_x, target_y = target["x"], target["y"]
                    distance = self.GetDistance(castle_x, castle_y, target_x, target_y)

                    if distance > scan_distance:
                        self.log_message(
                            status="info",
                            message=f"Sken {current_world}: [{target_x}:{target_y}] přeskočen (vzdálenost {distance:.2f} > {scan_distance})"
                        )
                        counter += 1
                        continue

                    try:
                        # Klikací sekvence (beze změny)
                        pyautogui.click(self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                                        self.config_reader.get_value(
                                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.y"))
                        pyautogui.click(self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                                        self.config_reader.get_value(
                                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.y"))
                        time.sleep(private_click_offset_01)
                        pyautogui.typewrite(str(target_x))
                        pyautogui.press("Tab")
                        pyautogui.typewrite(str(target_y))
                        pyautogui.press("Enter")
                        time.sleep(private_click_offset_05)
                        pyautogui.moveTo(
                            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
                            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y"))
                        time.sleep(private_click_offset_01)
                        pyautogui.click(self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_1.x") + 5,
                                        self.config_reader.get_value(
                                            "actions_click_patter.send_attack_first_wave_auto.click_1.y") + 5)
                        time.sleep(private_click_offset_01)
                        pyautogui.moveTo(
                            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.x"),
                            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.y"))
                        time.sleep(0.1)

                        # OCR vlákno
                        cords = f"{target_x}:{target_y}"
                        kingdom = "ZIM" if current_world == "winter" else "PSK" if current_world == "sand" else "OHN"
                        t = threading.Thread(target=self.AnalyzeScreenFort,
                                             kwargs={"kingdom": kingdom, "cords": cords, "json_name": current_world,
                                                     "stop_event": self.stop_event}, daemon=True, )
                        t.start()
                        ocr_threads.append(t)

                    except Exception as e:
                        self.log_message(status="error",
                                         message=f"Chyba při scanu {current_world} [{target_x}:{target_y}]: {e}")

                    counter += 1
                    time.sleep(private_click_offset_02)

                # Počkání na OCR a seřazení pro aktuální svět
                for t in ocr_threads:
                    t.join()

                self.SortFortArray(json_name=current_world)
                self.log_message(status="info", message=f"Svět {current_world} dokončen.")

            self.log_message(status="info", message="Scanování všech vybraných světů dokončeno.")
            self.can_continue = True

        thread = threading.Thread(target=_scan_loop, daemon=True)
        thread.start()
        return thread

    def ScanFort(self, json_name: str, positions, scan_distance=50, dismiss_popups=True, scan_both_worlds=False):
        """Provede scan pevností. Pokud je scan_both_worlds True, ignoruje json_name a projede Písek i Oheň."""

        self.can_continue = False

        winter_pos = positions.get("winter")
        sand_pos = positions.get("sand")
        fire_pos = positions.get("fire")

        def _scan_loop():
            # Určení světů ke scanování
            worlds_to_scan = []
            if scan_both_worlds:
                worlds_to_scan = ["sand", "fire"]
            else:
                worlds_to_scan = [json_name]

            # Společný odpočet na začátku
            countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
            for x in range(countdown, 0, -1):
                if self.stop_event.is_set():
                    self.log_message(status="info", message="ScanFort zastaven uživatelem během odpočtu")
                    self.can_continue = True
                    return
                self.log_message(status="info", message=f"Spuštění ScanFort za: {x}")
                time.sleep(1)

            # Iterace přes vybrané světy
            for current_world in worlds_to_scan:
                if self.stop_event.is_set():
                    break

                self.log_message(status="info", message=f"Začínám scan světa: {current_world}")

                # Vymazání DB pro daný svět před startem
                self.ClearFortArray(current_world)

                current_pos = None
                if current_world == "winter":
                    current_pos = winter_pos
                elif current_world == "sand":
                    current_pos = sand_pos
                elif current_world == "fire":
                    current_pos = fire_pos

                # Přepnutí světa
                self.ChangeWorld(current_pos)

                # --- Nastavení souřadnic hradu a načtení JSON dat ---
                castle_x = self.config_reader.get_value(f"main_castle_cords.{current_world}.x")
                castle_y = self.config_reader.get_value(f"main_castle_cords.{current_world}.y")

                base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "fortress_data_storage")
                json_path = os.path.join(base_dir, f"{current_world}.json")

                with open(json_path, "r", encoding="utf-8") as f:
                    fort_data = json.load(f)

                forts_sorted = sorted(fort_data.items(), key=lambda kv: int(kv[0].split("_")[1]))

                # Celkový počet pevností pro dynamický výpis progresu
                total_forts = len(forts_sorted)
                counter = 1
                ocr_threads = []

                # --- Samotný průchod pevnostmi ---
                for fort_key, target in forts_sorted:
                    if self.stop_event.is_set():
                        self.log_message(status="info",
                                         message=f"ScanFort zastaven uživatelem během světa {current_world}")
                        break

                    # Dynamický výpis progresu do logu
                    self.log_message(status="info", message=f"Scan {current_world}: {counter}/{total_forts} pevností.")

                    if dismiss_popups and counter % 10 == 0:
                        self.CloseWindowsPopups()

                    private_click_offset_01 = 0.1
                    private_click_offset_02 = 0.2
                    private_click_offset_05 = 0.2
                    target_x, target_y = target["x"], target["y"]
                    distance = self.GetDistance(castle_x, castle_y, target_x, target_y)

                    if distance > scan_distance:
                        self.log_message(
                            status="info",
                            message=f"Přeskočeno: [{target_x}:{target_y}] (vzdálenost {distance:.2f} > {scan_distance})"
                        )
                        counter += 1
                        continue

                    try:
                        # Klikací sekvence
                        pyautogui.click(self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                            self.config_reader.get_value(
                                "actions_click_patter.send_attack_first_wave_auto.click_select_cords.y"))
                        pyautogui.click(self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                            self.config_reader.get_value(
                                "actions_click_patter.send_attack_first_wave_auto.click_select_cords.y"))
                        time.sleep(private_click_offset_01)
                        pyautogui.typewrite(str(target_x))
                        pyautogui.press("Tab")
                        pyautogui.typewrite(str(target_y))
                        pyautogui.press("Enter")
                        time.sleep(private_click_offset_05)
                        pyautogui.moveTo(
                            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
                            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y"))
                        time.sleep(private_click_offset_01)
                        pyautogui.click(self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_1.x") + 5,
                                        self.config_reader.get_value(
                                            "actions_click_patter.send_attack_first_wave_auto.click_1.y") + 5)
                        time.sleep(private_click_offset_01)
                        pyautogui.moveTo(
                            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.x"),
                            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.y"))
                        time.sleep(0.1)

                        # OCR vlákno
                        cords = f"{target_x}:{target_y}"
                        kingdom = "ZIM" if current_world == "winter" else "PSK" if current_world == "sand" else "OHN"
                        t = threading.Thread(target=self.AnalyzeScreenFort,
                                             kwargs={"kingdom": kingdom, "cords": cords, "json_name": current_world,
                                                     "stop_event": self.stop_event}, daemon=True, )
                        t.start()
                        ocr_threads.append(t)

                    except Exception as e:
                        self.log_message(status="error",
                                         message=f"Chyba při scanu {current_world} [{target_x}:{target_y}]: {e}")

                    counter += 1
                    time.sleep(private_click_offset_02)

                # Počkání na OCR a seřazení pro aktuální svět
                for t in ocr_threads:
                    t.join()

                self.SortFortArray(json_name=current_world)
                self.log_message(status="info", message=f"Svět {current_world} dokončen.")

            self.log_message(status="info", message="Scanování všech vybraných světů dokončeno.")
            self.can_continue = True

        thread = threading.Thread(target=_scan_loop, daemon=True)
        thread.start()
        return thread
    def AnalyzeScreenFort_save(self, json_name: str, kingdom="", cords="", stop_event=None):
        """Analyzuje oblast obrazovky, vytáhne čas z OCR a uloží do DB."""
        # okamžitá kontrola, zda bylo vlákno zastaveno
        if stop_event is not None and stop_event.is_set():
            return

        # načtení pozice a rozměrů snímku z configu
        x = int(self.config_reader.get_value("settings.scan_screen_size.x"))
        y = int(self.config_reader.get_value("settings.scan_screen_size.y"))
        width = int(self.config_reader.get_value("settings.scan_screen_size.width"))
        height = int(self.config_reader.get_value("settings.scan_screen_size.height"))

        # vytvoření screenshotu
        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        # cesta pro uložení screenshotu
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_dir, "images", "scan_cooldown_screen_save.png")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        screenshot.save(image_path)

        # OCR čtení textu
        result = self.reader.readtext(image_path, detail=0)
        extracted_text = " ".join(result).strip()

        if not extracted_text:
            self.log_message(status="warn", message="OCR nenašlo žádný text")
            return

        # převedení textu na budoucí čas
        future_time = self.calculate_future_time(extracted_text)
        if not future_time:
            self.log_message(status="warn", message=f"Nepodařilo se extrahovat čas z textu: {extracted_text}")
            return

        # spojení informací do formátu: kingdom;cords;čas
        record = f"{kingdom};{cords};{future_time}"

        # zápis do DB
        self.db_writer.WriteToDb(record, json_name)

        # logování
        self.log_message(status="ok", message=f"Načtený text: {record}")

    def AnalyzeScreenFort(self, json_name: str, kingdom="", cords="", stop_event=None):
        """Analyzuje oblast obrazovky, vylepší obraz pro OCR a uloží čas do DB."""
        # Okamžitá kontrola, zda bylo vlákno zastaveno
        if stop_event is not None and stop_event.is_set():
            return

        # Načtení pozice a rozměrů snímku z configu
        x = int(self.config_reader.get_value("settings.scan_screen_size.x"))
        y = int(self.config_reader.get_value("settings.scan_screen_size.y"))
        width = int(self.config_reader.get_value("settings.scan_screen_size.width"))
        height = int(self.config_reader.get_value("settings.scan_screen_size.height"))

        # Vytvoření screenshotu
        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        # --- PŘEDZPRACOVÁNÍ OBRAZU (Pre-processing) ---
        # Převod PIL obrázku na formát pro OpenCV (NumPy array)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # 1. Zvětšení obrázku (3x) - zásadní pro detekci malých číslic a dvojteček
        img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        # 2. Převod na šedotón a aplikování prahování (Thresholding)
        # Vytvoříme černý text na bílém pozadí pro maximální kontrast
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Cesta pro uložení upraveného screenshotu
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_dir, "images", "scan_cooldown_screen_processed.png")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        # Uložíme upravený obrázek
        cv2.imwrite(image_path, thresh)

        # OCR čtení textu z upraveného obrázku
        result = self.reader.readtext(image_path, detail=0)
        extracted_text = " ".join(result).strip()

        if not extracted_text:
            self.log_message(status="warn", message="OCR nenašlo žádný text na upraveném snímku")
            return

        # Převedení textu na budoucí čas
        future_time = self.calculate_future_time(extracted_text)
        if not future_time:
            self.log_message(status="warn", message=f"Nepodařilo se extrahovat čas z: {extracted_text}")
            return

        # Spojení informací a zápis do DB
        record = f"{kingdom};{cords};{future_time}"
        self.db_writer.WriteToDb(record, json_name)

    def calculate_future_time_save(self, text: str):
        """
        Extrahuje čas z textu (např. 'Lze napadnout za: 09:35', '16.56.38')
        a převede ho na absolutní čas (YYYY-MM-DD HH:MM:SS).
        """
        # nahraď tečky dvojtečkami – OCR často zaměňuje
        cleaned = text.replace(".", ":")

        # najdi první výskyt časového údaje (např. 09:35 nebo 10:22:12)
        #match = re.search(r"(\d{1,2}:\d{1,2}(?::\d{1,2})?)", cleaned)
        match = re.search(r"(\d+:\d{1,2}(?::\d{1,2})?)", cleaned)
        if not match:
            return None

        time_str = match.group(1)
        parts = time_str.split(":")

        try:
            # různé varianty formátu
            if len(parts) == 3:
                h, m, s = map(int, parts)
            elif len(parts) == 2:
                h = 0
                m, s = map(int, parts)
            elif len(parts) == 1:
                h, m, s = 0, 0, int(parts[0])
            else:
                return None
        except ValueError:
            return None

        # výpočet budoucího času
        delta = timedelta(hours=h, minutes=m, seconds=s)
        future_time = datetime.now() + delta

        # vrátí formátovaný čas
        return future_time.strftime("%Y-%m-%d %H:%M:%S")

    def calculate_future_time(self, text: str):
        """
        Extrahuje čas z OCR textu a převede ho na YYYY-MM-DD HH:MM:SS.
        Ošetřuje chyby OCR v separátorech (tečky, čárky, mezery).
        """
        # 1. Čištění textu: Nahradíme tečky, čárky a mezery mezi čísly dvojtečkami
        # To pomůže regexu najít čas, i když OCR přečte "16.22 42"
        cleaned = re.sub(r"[:\.,\s]+", ":", text)

        # 2. Robustní Regex:
        # Hledá formáty HH:MM:SS nebo HH:MM
        # \d{1,3} dovoluje zachytit i případně chybně přečtená trojciferná čísla pro hlášení chyby
        match = re.search(r"(\d{1,2}:\d{1,2}:\d{1,2})|(\d{1,2}:\d{1,2})", cleaned)

        if not match:
            # Nouzový pokus: Najít všechna čísla a zkusit je spojit
            nums = re.findall(r"\d+", cleaned)
            if len(nums) >= 2:
                time_str = ":".join(nums[:3])
            else:
                return None
        else:
            time_str = match.group(0)

        parts = time_str.split(":")

        try:
            # Rozřazení částí času
            if len(parts) == 3:
                h, m, s = map(int, parts)
            elif len(parts) == 2:
                # Pokud jsou jen dvě části, bereme to jako MM:SS (dle vaší původní logiky)
                h, m, s = 0, int(parts[0]), int(parts[1])
            else:
                return None

            # Logická pojistka pro validitu času
            if m >= 60 or s >= 60:
                return None

        except (ValueError, IndexError):
            return None

        # Výpočet absolutního času v budoucnosti
        delta = timedelta(hours=h, minutes=m, seconds=s)
        future_time = datetime.now() + delta

        return future_time.strftime("%Y-%m-%d %H:%M:%S")
    def SortFortArray(self, json_name):
        # cesta k db.txt
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "fortress_data_storage", json_name + "_db.txt")

        if not os.path.exists(db_path):
            self.log_message(status="error", message="Soubor db.txt nebyl nalezen")
            return []

        # načteme řádky
        with open(db_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        def parse_line(line: str):
            try:
                parts = line.split(";")
                kingdom, cords, dt_str = parts
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                return (kingdom, cords, dt)
            except Exception as e:
                self.log_message(status="error", message=f"Chyba při parsování řádku: {line} ({e})")
                return None

        parsed = [p for p in (parse_line(line) for line in lines) if p]

        # seřadíme podle datetime od nejbližšího po nejvzdálenější
        sorted_data = sorted(parsed, key=lambda x: x[2])

        # pokud chceš, můžeš to vrátit zpět jako stringy
        result_lines = [f"{k};{c};{dt.strftime('%Y-%m-%d %H:%M:%S')}" for k, c, dt in sorted_data]

        # přepíšeme db.txt seřazeným obsahem
        with open(db_path, "w", encoding="utf-8") as f:
            f.write("\n".join(result_lines) + "\n")

        self.log_message(status="ok", message=f"Seřazeno {len(result_lines)} záznamů podle času.")
        return result_lines

    def ClearFortArray(self, json_name):
        #json name je winter/sand/fire
        """Vymaže celý obsah fortress_data_storage/db.txt"""

        # sestavení cesty k db.txt relativně k umístění tohoto souboru
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "fortress_data_storage", json_name+"_db.txt")

        # otevření v režimu 'w' přepíše soubor prázdným obsahem
        with open(db_path, "w", encoding="utf-8") as f:
            f.write("")

        # pro jistotu log
        self.log_message(status="ok", message="Soubor db.txt byl vymazán.")