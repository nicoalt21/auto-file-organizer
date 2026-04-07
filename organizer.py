import sys
import json
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

__all__ = ["carica_regole", "trova_cartella_download", "GestoreDownload"]


def carica_regole():
    """Carica le regole di organizzazione da config.json."""
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
    except json.JSONDecodeError as e:
        print(f"Errore: config.json non è un JSON valido: {e}")
        return None


def trova_cartella_download():
    """Trova la cartella Download dell'utente in modo cross-platform."""
    # Prova prima la variabile d'ambiente XDG su Linux
    xdg = Path.home() / ".config" / "user-dirs.dirs"
    if xdg.exists():
        try:
            with open(xdg, "r") as f:
                for line in f:
                    if line.startswith("XDG_DOWNLOAD_DIR"):
                        path_str = line.split("=")[1].strip().strip('"').replace("$HOME", str(Path.home()))
                        candidate = Path(path_str)
                        if candidate.exists():
                            return candidate
        except Exception:
            pass

    # Fallback standard
    for nome in ("Downloads", "Download", "Scaricati", "Téléchargements"):
        cartella = Path.home() / nome
        if cartella.exists():
            return cartella

    # Ultimo fallback: home directory
    return Path.home()


def _attendi_file_stabile(percorso: Path, attesa: float = 0.5, tentativi: int = 10) -> bool:
    """
    Aspetta che la dimensione del file smetta di crescere prima di spostarlo.
    Restituisce True se il file è stabile, False se non esiste più.
    """
    size_precedente = -1
    for _ in range(tentativi):
        try:
            size_attuale = percorso.stat().st_size
        except FileNotFoundError:
            return False
        if size_attuale == size_precedente:
            return True
        size_precedente = size_attuale
        time.sleep(attesa)
    return True  # Procedi comunque dopo i tentativi massimi


class GestoreDownload(FileSystemEventHandler):
    # Estensioni temporanee da ignorare
    ESTENSIONI_TEMPORANEE = {'.crdownload', '.tmp', '.part', '.download', '.!ut'}

    def __init__(self, cartella_base, regole, log_callback=None):
        self.cartella_base = Path(cartella_base)
        self.regole = regole
        self.log_callback = log_callback

    def on_modified(self, event):
        if event.is_directory:
            return

        percorso_file = Path(event.src_path)
        estensione = percorso_file.suffix.lower()

        # Ignora file temporanei e file senza estensione
        if estensione in self.ESTENSIONI_TEMPORANEE or not estensione:
            return

        # Cerca la cartella di destinazione nelle regole
        for nome_cartella, estensioni_valide in self.regole.items():
            if estensione in estensioni_valide:
                self.sposta_file(percorso_file, nome_cartella)
                break

    def sposta_file(self, percorso_file: Path, nome_cartella: str):
        # Aspetta che il file sia completamente scritto su disco
        if not _attendi_file_stabile(percorso_file):
            return  # File scomparso durante l'attesa

        cartella_destinazione = self.cartella_base / nome_cartella
        cartella_destinazione.mkdir(exist_ok=True)

        destinazione_finale = cartella_destinazione / percorso_file.name

        # Logica anti-duplicati
        contatore = 1
        while destinazione_finale.exists():
            nuovo_nome = f"{percorso_file.stem}_{contatore}{percorso_file.suffix}"
            destinazione_finale = cartella_destinazione / nuovo_nome
            contatore += 1

        try:
            shutil.move(str(percorso_file), str(destinazione_finale))
            messaggio = f"Spostato: {destinazione_finale.name} -> {nome_cartella}"
            print(messaggio)
            if self.log_callback:
                self.log_callback(messaggio)
        except FileNotFoundError:
            # Il file è stato già spostato da un evento precedente (race condition)
            pass
        except PermissionError:
            # Il file è ancora in uso
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
        print("Premi CTRL+C per fermare.\n")

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
    else:
        print("Impossibile avviare: cartella Download non trovata o config.json mancante.")