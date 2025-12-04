import time
from services.base_tab import BaseTab
import pyautogui

class BulkBuyItemManager(BaseTab):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def BulkBuyItemStart(self, count):
        for x in range(count):
            self.FullBuy()
            self.log_message(
                status="ok",
                message="Prostředek zakoupen | Note: " + str(x) + "/" + str(count)
            )

    def FullBuy(self):
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.bulk_buy.click_1.x"),
            self.config_reader.get_value("actions_click_patter.bulk_buy.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.bulk_buy.click_2.x"),
            self.config_reader.get_value("actions_click_patter.bulk_buy.click_2.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.bulk_buy.click_3.x"),
            self.config_reader.get_value("actions_click_patter.bulk_buy.click_3.y")
        )