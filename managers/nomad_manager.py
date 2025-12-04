import time
from services.base_tab import BaseTab


class NomadManager(BaseTab):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def NomadOrSamuOnContinent(self, horses, delay_between_attacks, use_fill_all_waves, first_wave_from_bottom,
                               other_waves_from_bottom, auto_fill_waves, target_x, target_y, max_attacks):
        for x in range(max_attacks):

            time.sleep(int(delay_between_attacks))

            if other_waves_from_bottom == None:
                self.SendAttackFirstWaveAuto(
                    target_x=int(target_x),
                    target_y=int(target_y),
                    feather_horse=horses,
                    note="Útok poslán",
                    skip_samu_nomad_cd=True
                )
            else:
                self.SendAttackMultiWaveAuto(
                    target_x=int(target_x),
                    target_y=int(target_y),
                    feather_horse=horses,
                    first_wave_from_bottom=first_wave_from_bottom,
                    other_waves_from_bottom=other_waves_from_bottom,
                    auto_fill_waves=auto_fill_waves,
                    skip_samu_nomad_cd=True
                )
            self.log_message(
                status="ok",
                message="Útok poslán | Note: " + str(x) + "/" + str(max_attacks)
            )

