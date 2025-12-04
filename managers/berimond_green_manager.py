from services.base_tab import BaseTab
import time

class BerimondGreenManager(BaseTab):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def RunBerimondGreenManager(self, color_type, green_array, red_array, attack_count, delay_attack, feather_horses):

        # =============================
        #  VÝBĚR SPRÁVNÉHO POLE PODLE BARVY
        # =============================
        if color_type == "red":
            targets = red_array
        elif color_type == "blue":
            targets = green_array
        else:  # all
            targets = green_array + red_array

        # =============================
        #  FILTRACE PRÁZDNÝCH SOUŘADNIC
        # =============================
        targets = [t for t in targets if not (t[0] == 0 and t[1] == 0)]

        if not targets:
            self.log_message(status="error", message="Nebyla nalezena žádná platná souřadnice!")
            return

        # index použitý pro cyklus dokola
        index = 0
        total_targets = len(targets)

        # =============================
        #  HLAVNÍ CYKLUS ÚTOKŮ
        # =============================
        for i in range(attack_count):

            x = targets[index][0]
            y = targets[index][1]

            # pauza před útokem
            time.sleep(delay_attack)

            # poslání útoku
            try:
                self.SendAttackFirstWaveAuto(
                    close_popups=True,
                    skip_samu_nomad_cd=False,
                    target_x=x,
                    target_y=y,
                    send_with_cords=True,
                    kingdom=None,
                    feather_horse=feather_horses,
                    note=f"{i+1}/{attack_count}",
                    attack_code=""
                )
            except Exception as e:
                self.log_message(status="error", message=f"Chyba při útoku: {e}")

            # posun na další souřadnici, dokola
            index = (index + 1) % total_targets
