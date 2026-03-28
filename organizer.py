import json
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def carica_regole():
    cartella_script = Path(__file__).parent
    percorso_file = cartella_script / "config.json"

    try:
        with open(percorso_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Errore: File config.json non trovato.")
        return None


def trova_cartella_download():
    cartella = Path.home() / "Downloads"
    if not cartella.exists():
        cartella = Path.home() / "Download"
    return cartella


class GestoreDownload(FileSystemEventHandler):

    def __init__(self, cartella_base, regole):
        self.cartella_base = cartella_base
        self.regole = regole

    def on_modified(self, event):
        if event.is_directory:
            return

        percorso_file = Path(event.src_path)
        estensione = percorso_file.suffix.lower()

        if estensione in ['.crdownload', '.tmp', '.part'] or not estensione:
            return

        for nome_cartella, estensioni_valide in self.regole.items():
            if estensione in estensioni_valide:
                self.sposta_file(percorso_file, nome_cartella)
                break

    def sposta_file(self, percorso_file, nome_cartella):
        cartella_destinazione = self.cartella_base / nome_cartella
        cartella_destinazione.mkdir(exist_ok=True)

        destinazione_finale = cartella_destinazione / percorso_file.name

        time.sleep(1)

        try:
            if not destinazione_finale.exists():
                shutil.move(str(percorso_file), str(destinazione_finale))
                print(f"Spostato: {percorso_file.name} -> {nome_cartella}")
        except PermissionError:
            pass
        except Exception as e:
            print(f"Errore imprevisto con {percorso_file.name}: {e}")


if __name__ == "__main__":
    regole = carica_regole()
    cartella_download = trova_cartella_download()

    if regole and cartella_download.exists():
        print(f"Organizer avviato. Sto monitorando: {cartella_download}")
        print("Premi CTRL+C nel terminale per fermare il programma.\n")

        gestore_eventi = GestoreDownload(cartella_download, regole)
        observer = Observer()
        observer.schedule(gestore_eventi, str(cartella_download), recursive=False)

        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\nProgramma terminato.")

        observer.join()