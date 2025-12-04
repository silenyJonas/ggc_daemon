import time
from services.base_tab import BaseTab
import pyautogui


class BerimondContinentManager(BaseTab):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def BerimondOnContinent(self, max_attacks, horses, attacks_between_refill, troops_from_left, delay_between_attacks):
        for x in range(max_attacks):
            if x % attacks_between_refill == 0 and x != 0:
                #refill
                self.BerimondRefill(troops_from_left)

            time.sleep(delay_between_attacks)

            #click pravo dole
            time.sleep(0.1)
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.berimond_find_target_right_down.x"),
                self.config_reader.get_value("actions_click_patter.berimond_find_target_right_down.y")
            )

            time.sleep(self.config_reader.get_value("settings.offsets.default_click_delay"))
            self.SendAttackFirstWaveAuto(send_with_cords=False, feather_horse=horses)

            time.sleep(0.1)
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.berimond_no_troop_army_1.x"),
                self.config_reader.get_value("actions_click_patter.berimond_no_troop_army_1.y")
            )
            time.sleep(0.1)
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.berimond_no_troop_army_2.x"),
                self.config_reader.get_value("actions_click_patter.berimond_no_troop_army_2.y")
            )
            self.log_message(
                status="ok",
                message="Útok poslán | Note: " + str(x+1)+"/"+str(max_attacks),
            )
            #time.sleep(self.config_reader.get_value("settings.offsets.default_click_delay"))
    def BerimondRefill(self, troops_from_left):
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_1.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_2.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_2.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.troops_offsets.offset_troop_"+str(troops_from_left)+".x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.troops_offsets.offset_troop_"+str(troops_from_left)+".y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_3.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_3.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_4.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_4.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_5.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_5.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_6.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_6.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_7.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_7.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_8.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_8.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_9.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_9.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_10.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_10.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_11.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_11.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_12.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_12.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_13.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_13.y")
        )

        self.log_message(
            status="ok",
            message="Jednotky doplněny"
        )