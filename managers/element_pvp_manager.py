import time
import pyautogui
from services.base_tab import BaseTab


class ElementPVPManager(BaseTab):
    """Manažer pro logiku Element PVP útoků."""

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def Run(self, targets, horses, first_wave_from_bottom, auto_fill_waves, max_attacks, tab_instance):
        """Hlavní smyčka přes všechna kola a cíle."""

        self.log_message(status="info", message=f"Manager: Startuji PVP na {len(targets)} cílů.")

        for i in range(max_attacks):
            if not tab_instance.is_running:
                self.log_message(status="info", message="Manager: Zastaveno uživatelem.")
                break

            self.log_message(status="info", message=f"--- KOLO ÚTOKŮ Č. {i + 1} ---")

            for target in targets:
                if not tab_instance.is_running:
                    break

                # Volání funkce attack pro každý cíl
                self.attack(
                    target=target,
                    horses=horses,
                    first_wave_from_bottom=first_wave_from_bottom,
                    auto_fill_waves=auto_fill_waves
                )

                # Krátká pauza mezi cíli
                time.sleep(1)

        self.log_message(status="info", message="Manager: Všechny útoky dokončeny.")

    def attack(self, target, horses, first_wave_from_bottom, auto_fill_waves):
        """
        Pomocná funkce pro provedení jednoho útoku.
        Zatím pouze vypisuje hodnoty do logu.
        """
        name = target.get("name")
        tx = target.get("x")
        ty = target.get("y")
        h_type = "Pírka" if horses else "Gold"
        fill = "ANO" if auto_fill_waves else "NE"

        log_text = (f"[ATTACK] Cíl: {name} [{tx}:{ty}] | "
                    f"Kůň: {h_type} | "
                    f"Vlna od spodu: {first_wave_from_bottom} | "
                    f"Auto-fill: {fill}")

        self.log_message(status="info", message=log_text)

        sleep_time = 0.5

        #najit hrad pres souradnice
        pyautogui.click(851,9)
        time.sleep(0.1)
        pyautogui.click(851,9)
        pyautogui.typewrite(str(tx))
        time.sleep(sleep_time)
        pyautogui.press('Tab')
        pyautogui.typewrite(str(ty))
        time.sleep(sleep_time)
        pyautogui.press('Enter')
        time.sleep(sleep_time)

        #vyvoalt attack dialo (elementals)
        pyautogui.click(950,540)
        time.sleep(sleep_time)
        pyautogui.move(955,545)
        time.sleep(sleep_time)
        pyautogui.click(950,540)
        time.sleep(sleep_time)
        pyautogui.click(1015,612)
        time.sleep(sleep_time)
        pyautogui.click(1050,666)
        time.sleep(sleep_time)

        #naklikat utok v dialou
        pyautogui.click(1400,793)
        time.sleep(sleep_time)
        pyautogui.click(1400,700)
        time.sleep(sleep_time)
        pyautogui.click(1500,910)
        time.sleep(sleep_time)
        pyautogui.click(1111,730)
        time.sleep(sleep_time)
        pyautogui.click(1200,500)
        time.sleep(sleep_time)
        pyautogui.click(1090,750)
        time.sleep(sleep_time)












