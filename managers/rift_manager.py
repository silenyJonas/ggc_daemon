import time
from services.base_tab import BaseTab
import pyautogui


class RiftManager(BaseTab):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def Run(self, max_attacks, feather_horses, x, y, tab_instance):
        """
        Spustí smyčku útoků na fixní souřadnice.

        :param max_attacks: Počet opakování (zadáno uživatelem)
        :param feather_horses: Boolean (Pírka vs Gold koně)
        :param x: Fixní souřadnice X
        :param y: Fixní souřadnice Y
        :param tab_instance: Instance záložky pro kontrolu běhu a logování
        """

        #find cords
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
        pyautogui.typewrite(str(x))
        pyautogui.press("Tab")
        pyautogui.typewrite(str(y))
        pyautogui.press("Enter")

        for i in range(max_attacks):
            # Kontrola, zda uživatel proces nezastavil v GUI
            if not tab_instance.is_running:
                self.log_message(status="info", message="Proces byl uživatelem přerušen.")
                break

            # Logování aktuálního postupu
            self.log_message(status="info", message=f"Útok {i + 1} z {max_attacks}...")

            try:
                # Volání vaší existující metody pro odeslání útoku
                # Souřadnice x a y jsou stále stejné (fixní)
                self.SendAttackFirstWaveAuto(
                    close_popups=False,
                    skip_samu_nomad_cd=False,
                    target_x=x,
                    target_y=y,
                    send_with_cords=False,
                    kingdom=None,
                    feather_horse=feather_horses,
                    note=f"Rift {i + 1}/{max_attacks}",
                    attack_code=""
                )
            except Exception as e:
                self.log_message(status="error", message=f"Chyba při odesílání útoku {i + 1}: {e}")
                # Pokud dojde k chybě, proces se zastaví, nebo můžete přidat 'continue'
                break

            # Krátká pauza mezi útoky (volitelné, lze upravit nebo vytáhnout z configu)
            time.sleep(1)

        self.log_message(status="info", message="Všechny útoky byly dokončeny.")