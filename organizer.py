import sys
import json
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def carica_regole():
    # Permette al file config.json di essere trovato anche quando creiamo l'EXE
    if getattr(sys, 'frozen', False):
        cartella_script = Path(sys.executable).parent
    else:
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

    def __init__(self, cartella_base, regole, log_callback=None):
        self.cartella_base = cartella_base
        self.regole = regole
        self.log_callback = log_callback

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

        # Logica Anti-Duplicati
        contatore = 1
        while destinazione_finale.exists():
            nuovo_nome = f"{percorso_file.stem}_{contatore}{percorso_file.suffix}"
            destinazione_finale = cartella_destinazione / nuovo_nome
            contatore += 1

        time.sleep(1)

        try:
            shutil.move(str(percorso_file), str(destinazione_finale))
            messaggio = f"Spostato: {destinazione_finale.name} -> {nome_cartella}"
            print(messaggio)

            # Se la GUI è connessa, invia il messaggio al log visivo
            if self.log_callback:
                self.log_callback(messaggio)

        except PermissionError:
            pass
        except Exception as e:
            errore = f"Errore imprevisto con {percorso_file.name}: {e}"
            print(errore)
            if self.log_callback:
                self.log_callback(errore)


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