# gge_clicker/fortress_data_storage/db_writer.py
import os
from datetime import datetime

class DbWriter:
    def __init__(self):
        self.base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "fortress_data_storage"
        )
        self.json_name = ""
        self.db_path = ""

    def UpdateBaseDb_save(self, name):
        """Vymaže db.txt a naplní ho podle vybraného světa nebo kombinace."""
        db_txt_path = os.path.join(self.base_dir, "db.txt")

        # krok 1 – vymazání db.txt
        with open(db_txt_path, "w", encoding="utf-8") as db_file:
            db_file.write("")

        # pomocná funkce pro přidání obsahu jednoho souboru
        def append_from(src_filename):
            src_path = os.path.join(self.base_dir, src_filename)
            if not os.path.exists(src_path):
                print(f"[DbWriter] Soubor {src_filename} nebyl nalezen.")
                return
            with open(src_path, "r", encoding="utf-8") as src, open(db_txt_path, "a", encoding="utf-8") as dest:
                for line in src:
                    dest.write(line)
                dest.write("\n")

        # krok 2 – podle režimu připojit odpovídající soubory
        if name == "zim":
            append_from("winter_db.txt")
        elif name == "pis":
            append_from("sand_db.txt")
        elif name == "ohn":
            append_from("fire_db.txt")
        elif name == "zim_pis":
            append_from("winter_db.txt")
            append_from("sand_db.txt")
        elif name == "zim_ohn":
            append_from("winter_db.txt")
            append_from("fire_db.txt")
        elif name == "pis_ohn":
            append_from("sand_db.txt")
            append_from("fire_db.txt")
        elif name == "all":
            append_from("winter_db.txt")
            append_from("sand_db.txt")
            append_from("fire_db.txt")
        else:
            print(f"[DbWriter] Neznámý parametr: {name}")

    def UpdateBaseDb(self, name):
        """Vymaže db.txt a naplní ho podle vybraného světa nebo kombinace."""
        db_txt_path = os.path.join(self.base_dir, "db.txt")

        # krok 1 – vymazání db.txt
        with open(db_txt_path, "w", encoding="utf-8") as db_file:
            db_file.write("")

        # pomocná funkce pro přidání obsahu jednoho souboru
        def append_from(src_filename):
            src_path = os.path.join(self.base_dir, src_filename)
            if not os.path.exists(src_path):
                print(f"[DbWriter] Soubor {src_filename} nebyl nalezen.")
                return

            with open(src_path, "r", encoding="utf-8") as src:
                lines = [line.strip() for line in src if line.strip()]  # odstraní prázdné řádky

            # pokud jsou v souboru platné řádky, přidej je do db.txt
            if lines:
                with open(db_txt_path, "a", encoding="utf-8") as dest:
                    for line in lines:
                        dest.write(line.rstrip() + "\n")  # zajistí 1 řádek na záznam

        # krok 2 – podle režimu připojit odpovídající soubory
        if name == "zim":
            append_from("winter_db.txt")
        elif name == "pis":
            append_from("sand_db.txt")
        elif name == "ohn":
            append_from("fire_db.txt")
        elif name == "zim_pis":
            append_from("winter_db.txt")
            append_from("sand_db.txt")
        elif name == "zim_ohn":
            append_from("winter_db.txt")
            append_from("fire_db.txt")
        elif name == "pis_ohn":
            append_from("sand_db.txt")
            append_from("fire_db.txt")
        elif name == "all":
            append_from("winter_db.txt")
            append_from("sand_db.txt")
            append_from("fire_db.txt")
        else:
            print(f"[DbWriter] Neznámý parametr: {name}")



    def WriteToDb(self, data: str, json_name: str):
        """Připíše řetězec na konec db souboru podle světa."""
        self.db_path = os.path.join(self.base_dir, json_name + "_db.txt")
        try:
            with open(self.db_path, "a", encoding="utf-8") as f:
                f.write(data.strip() + "\n")
        except Exception as e:
            print(f"[DbWriter] Chyba při zápisu do DB: {e}")

    def getSortedDb(self, json_name: str):
        """Vrátí budoucí záznamy z db.txt seřazené podle času."""
        self.db_path = os.path.join(self.base_dir, json_name + ".txt")
        sorted_list = []

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"[DbWriter] Soubor {self.db_path} nenalezen.")
            return []

        now = datetime.now()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                _, _, time_part = line.split(";")
                record_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
                if record_time > now:
                    sorted_list.append((record_time, line))
            except Exception as e:
                print(f"[DbWriter] Chybný záznam: {line}")
                continue

        sorted_list.sort(key=lambda x: x[0])
        return [x[1] for x in sorted_list]
