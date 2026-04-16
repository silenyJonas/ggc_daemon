import time
import pyautogui

from services.base_tab import BaseTab


class BaronManager(BaseTab):
    """Manager pro logiku útoku na Barony."""

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def ChangeWorld(self, castle_pos):
        """Přepne svět podle pozice hradu v seznamu."""
        base_x = self.config_reader.get_value("settings.castle_list_cords.base_x")
        base_y = self.config_reader.get_value("settings.castle_list_cords.base_y")

        self.log_message(status="info", message=f"Přepínám svět na pozici: {castle_pos}")
        time.sleep(1)
        pyautogui.click(base_x, base_y)
        time.sleep(2)

        target_y = self.config_reader.get_value(f"settings.castle_list_cords.castle_y_{castle_pos}")
        pyautogui.click(base_x, target_y)
        time.sleep(5)  # Pauza na načtení mapy světa

    def RunAllBarons(self, max_attacks, feather_horses, delay, wait_minutes, positions, tab_instance):
        """
        Nekonečná smyčka: Oheň -> Písek -> Zima. (Zelí odstraněno)
        Nyní se nejprve přepne svět a až poté čeká pauza (kromě úplně prvního startu).
        """
        order = [
            ("fire", positions.get("fire", 9)),
            ("sand", positions.get("sand", 8)),
            ("winter", positions.get("winter", 7))
        ]

        self.log_message(status="info", message="Spouštím NONSTOP režim (Oheň, Písek, Zima).")

        first_run = True  # Příznak pro první spuštění

        ali_click_state = True

        while tab_instance.is_running:
            for world_name, world_pos in order:
                if not tab_instance.is_running:
                    break

                # 1. KROK: Přepnutí světa
                self.log_message(status="info", message=f"--- PŘEPÍNÁM NA SVĚT: {world_name.upper()} ---")
                self.ChangeWorld(world_pos)

                # 2. KROK: Pokud to NENÍ první spuštění, odpočítej pauzu po přepnutí
                if not first_run:
                    self.log_message(status="info", message=f"Svět přepnut. Nyní pauza {wait_minutes} min před útoky.")
                    for min_rem in range(wait_minutes, 0, -1):
                        for sec_rem in range(60):
                            if not tab_instance.is_running: return
                            if sec_rem == 0:
                                self.log_message(status="info",
                                                 message=f"Odpočinek na světě {world_name.upper()}: {min_rem} min zbývá.")
                            time.sleep(1)

                # Po prvním světě (Oheň) už příznak vypneme, aby se u dalších čekalo
                first_run = False

                # 3. KROK: Samotné útoky
                config_path_prefix = f"entity_list.barons.{world_name}"

                for i in range(1, max_attacks + 1):
                    if not tab_instance.is_running:
                        return

                    target_x = self.config_reader.get_value(f"{config_path_prefix}.target_{i}.x")
                    target_y = self.config_reader.get_value(f"{config_path_prefix}.target_{i}.y")

                    if target_x and target_y:
                        start_time = time.time()

                        self.log_message(status="info",
                                         message=f"[{world_name.upper()}] Posílám útok {i}/{max_attacks}")

                        self.SendAttackFirstWaveAuto(
                            target_x=target_x,
                            target_y=target_y,
                            feather_horse=feather_horses,
                            note=f"Nonstop {world_name} #{i}"
                        )

                        #odkliknout pokud zautocite na hrace popup
                        time.sleep(1)
                        pyautogui.click(1136, 364)

                        #kdyby to kliklo na hrace tak odkliknbout jednou to klikne jednou a pak dvakrat a pak jednou kolo od kola:
                        time.sleep(1)
                        if ali_click_state:
                            pyautogui.click(1200, 750)
                            ali_click_state = False
                        else:
                            pyautogui.click(1200, 750)
                            time.sleep(1)
                            pyautogui.click(1200, 750)
                            ali_click_state = True

                        # Výpočet čekání do dalšího útoku v rámci světa
                        elapsed = time.time() - start_time
                        wait = delay - elapsed

                        if wait > 0:
                            for remaining in range(int(wait), 0, -1):
                                if not tab_instance.is_running: return
                                if remaining % 5 == 0 or remaining <= 3:
                                    self.log_message(status="info", message=f"Další útok za: {remaining}s")
                                time.sleep(1)
                            time.sleep(wait % 1)
                    else:
                        self.log_message(status="info", message=f"Na světě {world_name} není více cílů v configu.")
                        break

                self.log_message(status="info", message=f"Útoky na světě {world_name.upper()} dokončeny.")

    def SendBaronAttacks(
            self,
            start_index: int,
            end_index: int,
            selected_world: str,
            feather_horses: bool,
            tab_instance
    ):
        """Klasická smyčka pro jeden vybraný svět."""
        self.log_message(status="info", message=f"Baron manager: Jednorázová jízda {selected_world}.")

        config_path_prefix = f"entity_list.barons.{selected_world}"

        for x in range(start_index, end_index + 1):
            if not tab_instance.is_running:
                return

            target_x = self.config_reader.get_value(f"{config_path_prefix}.target_{x}.x")
            target_y = self.config_reader.get_value(f"{config_path_prefix}.target_{x}.y")

            if target_x and target_y:
                self.SendAttackFirstWaveAuto(
                    target_x=target_x,
                    target_y=target_y,
                    feather_horse=feather_horses,
                    note=f"Target: {x}"
                )
                time.sleep(self.config_reader.get_value("settings.offsets.default_time_delay_offset") or 1)

        tab_instance.is_running = False
        self.log_message(status="info", message="Jednorázová jízda dokončena.")