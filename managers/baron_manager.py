# managers/baron_manager.py
import time
from services.base_tab import BaseTab


class BaronManager(BaseTab):
    """Manager pro logiku útoku na Barony."""

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def SendBaronAttacks(
            self,
            start_index: int,
            end_index: int,
            selected_world: str,
            feather_horses: bool,
            tab_instance  # Přijímáme referenci na instanci BaronTab
    ):
        """
        Hlavní smyčka pro posílání útoků na Barony v daném rozsahu.

        Kontroluje stav is_running na předané instanci záložky.
        """
        self.log_message(
            status="info",
            message=f"Baron manager spuštěn pro svět '{selected_world}'. Rozsah: {start_index} - {end_index}."
        )

        config_path_prefix = f"entity_list.barons.{selected_world}"
        prefix = "target_"
        private_offset_time = self.config_reader.get_value("settings.offsets.default_time_delay_offset")

        # Hodnota pro malý, častý spánek
        CHECK_INTERVAL = 0.1

        # Kontrola, zda je instance platná a zda běží
        if not hasattr(tab_instance, 'is_running') or not tab_instance.is_running:
            self.log_message(status="error", message="Chyba: is_running není k dispozici nebo je false.")
            return

        while tab_instance.is_running:
            for x in range(start_index, end_index + 1):
                if not tab_instance.is_running:
                    self.log_message(status="info", message="Útok přerušen uživatelem.")
                    return  # Okamžité zastavení uprostřed smyčky

                # Dynamický výpočet počtu iterací spánku
                if private_offset_time is not None:
                    iterations = int(private_offset_time / CHECK_INTERVAL)
                else:
                    iterations = 0

                # Dlouhý spánek s častou kontrolou
                for _ in range(iterations):
                    if not tab_instance.is_running:
                        return
                    time.sleep(CHECK_INTERVAL)

                current_target_key = f"{config_path_prefix}.{prefix}{x}"
                target_x = self.config_reader.get_value(f"{current_target_key}.x")
                target_y = self.config_reader.get_value(f"{current_target_key}.y")

                # Ujistíme se, že hodnoty nejsou None před voláním
                if target_x is not None and target_y is not None:
                    note = f"Baron target: {x}"

                    # Volání akce z BaseTab
                    self.SendAttackFirstWaveAuto(
                        target_x=target_x,
                        target_y=target_y,
                        feather_horse=feather_horses,
                        note=note
                    )
                else:
                    self.log_message(
                        status="error",
                        message=f"Chyba: Nebyly nalezeny souřadnice pro cíl '{current_target_key}'."
                    )

            # Po dokončení celého cyklu nastavíme is_running na False
            tab_instance.is_running = False
            self.log_message(
                status="INFO",
                message="Posílání session baronů úspěšně dokončeno."
            )
            return