# managers/baron_manager.py
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

    def RunAllBarons(self, feather_horses, delay, wait_minutes, positions, tab_instance):
        """
        Nekonečná smyčka: Oheň -> Písek -> Zima -> Zelí.
        Loguje progress útoků, odpočet mezi nimi a čeká custom čas po každém světě.
        """
        order = [
            ("fire", positions.get("fire", 5)),
            ("sand", positions.get("sand", 4)),
            ("winter", positions.get("winter", 3)),
            ("green", positions.get("green", 1))
        ]

        self.log_message(status="info", message="Spouštím NONSTOP režim všech světů.")

        while tab_instance.is_running:
            for world_name, world_pos in order:
                if not tab_instance.is_running:
                    break

                self.log_message(status="info", message=f"--- PŘEPÍNÁM NA SVĚT: {world_name.upper()} ---")
                self.ChangeWorld(world_pos)

                config_path_prefix = f"entity_list.barons.{world_name}"

                # PRO TESTOVÁNÍ: range(1, 6) = 5 útoků. Pro ostrou verzi změň na (1, 151)
                for i in range(1, 151):
                    if not tab_instance.is_running:
                        return

                    target_x = self.config_reader.get_value(f"{config_path_prefix}.target_{i}.x")
                    target_y = self.config_reader.get_value(f"{config_path_prefix}.target_{i}.y")

                    if target_x and target_y:
                        start_time = time.time()

                        self.log_message(status="info", message=f"[{world_name.upper()}] Posílám útok {i}/150")

                        self.SendAttackFirstWaveAuto(
                            target_x=target_x,
                            target_y=target_y,
                            feather_horse=feather_horses,
                            note=f"Nonstop {world_name} #{i}"
                        )

                        # Výpočet čekání do dalšího útoku
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

                # Pauza po dojetí světa (používá hodnotu z GUI)
                if not tab_instance.is_running: break

                self.log_message(status="info", message=f"Svět {world_name} hotov. Pauza {wait_minutes} min.")

                # Odpočet pauzy po minutách
                for min_rem in range(wait_minutes, 0, -1):
                    for sec_rem in range(60):
                        if not tab_instance.is_running: return
                        if sec_rem == 0:
                            self.log_message(status="info", message=f"Zbývá {min_rem} min do dalšího světa.")
                        time.sleep(1)

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