import customtkinter as ctk
from watchdog.observers import Observer
import organizer
import os
import sys
import time
import winreg
from pathlib import Path

mio_observer = None
cartella_selezionata = organizer.trova_cartella_download()
file_spostati = 0

# Trova il percorso corretto sia da script che da .exe
if getattr(sys, 'frozen', False):
    cartella_script = Path(sys.executable).parent
else:
    cartella_script = Path(__file__).parent
percorso_config = cartella_script / "config.json"


# --- FUNZIONI DI WINDOWS (AVVIO AUTOMATICO) ---
def controlla_stato_avvio():
    try:
        chiave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                winreg.KEY_READ)
        winreg.QueryValueEx(chiave, "SmartFileOrganizer")
        winreg.CloseKey(chiave)
        return True
    except FileNotFoundError:
        return False


def imposta_avvio_windows():
    attiva = switch_avvio_var.get()
    percorso_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)

    try:
        chiave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                winreg.KEY_SET_VALUE)
        if attiva:
            winreg.SetValueEx(chiave, "SmartFileOrganizer", 0, winreg.REG_SZ, f'"{percorso_exe}"')
            aggiungi_log("Avvio con Windows: ATTIVATO")
        else:
            try:
                winreg.DeleteValue(chiave, "SmartFileOrganizer")
                aggiungi_log("Avvio con Windows: DISATTIVATO")
            except FileNotFoundError:
                pass
        winreg.CloseKey(chiave)
    except Exception as e:
        aggiungi_log(f"Errore registro di sistema: {e}")


# --- FUNZIONI GUI ---
def apri_impostazioni():
    # Crea una nuova finestra per editare il JSON
    finestra_regole = ctk.CTkToplevel(app)
    finestra_regole.title("Editor Regole JSON")
    finestra_regole.geometry("450x400")
    finestra_regole.attributes("-topmost", True)

    label_info = ctk.CTkLabel(finestra_regole, text="Modifica le estensioni qui sotto:", font=("Helvetica", 14))
    label_info.pack(pady=10)

    box_testo = ctk.CTkTextbox(finestra_regole, width=400, height=280, font=("Consolas", 12))
    box_testo.pack(pady=5)

    # Carica il testo dal file
    try:
        with open(percorso_config, "r") as file:
            box_testo.insert("0.0", file.read())
    except FileNotFoundError:
        box_testo.insert("0.0", "{\n}")

    def salva_regole():
        try:
            with open(percorso_config, "w") as file:
                file.write(box_testo.get("0.0", "end"))
            aggiungi_log("Regole salvate! Riavvia l'organizer per applicarle.")
            finestra_regole.destroy()
        except Exception as e:
            aggiungi_log(f"Errore salvataggio: {e}")

    btn_salva = ctk.CTkButton(finestra_regole, text="Salva", fg_color="green", hover_color="darkgreen",
                              command=salva_regole)
    btn_salva.pack(pady=10)


def scegli_cartella():
    global cartella_selezionata
    cartella = ctk.filedialog.askdirectory(title="Scegli la cartella")
    if cartella:
        cartella_selezionata = Path(cartella)
        lbl_cartella.configure(text=f"Cartella: {cartella_selezionata.name}")
        aggiungi_log(f"Nuova cartella: {cartella_selezionata.name}")


def evento_spostamento(messaggio):
    global file_spostati
    if "Spostato" in messaggio:
        file_spostati += 1
        lbl_contatore.configure(text=f"File spostati: {file_spostati}")
    orario = time.strftime('%H:%M:%S')
    aggiungi_log(f"[{orario}] {messaggio}")


def avvia_organizer():
    global mio_observer
    if mio_observer is not None and mio_observer.is_alive(): return

    regole = organizer.carica_regole()
    if regole and cartella_selezionata.exists():
        gestore = organizer.GestoreDownload(cartella_selezionata, regole, log_callback=evento_spostamento)
        mio_observer = Observer()
        mio_observer.schedule(gestore, str(cartella_selezionata), recursive=False)
        mio_observer.start()

        stato_label.configure(text="Stato: In esecuzione", text_color="green")
        btn_avvia.configure(state="disabled")
        btn_ferma.configure(state="normal")
        btn_scegli.configure(state="disabled")
        aggiungi_log(f"[{time.strftime('%H:%M:%S')}] Organizer avviato.")
    else:
        aggiungi_log("Errore: Impossibile caricare regole o cartella.")


def ferma_organizer():
    global mio_observer
    if mio_observer is not None and mio_observer.is_alive():
        mio_observer.stop()
        mio_observer.join()
        mio_observer = None

        stato_label.configure(text="Stato: Fermo", text_color="gray")
        btn_avvia.configure(state="normal")
        btn_ferma.configure(state="disabled")
        btn_scegli.configure(state="normal")
        aggiungi_log(f"[{time.strftime('%H:%M:%S')}] Organizer fermato.")


def aggiungi_log(messaggio):
    box_log.configure(state="normal")
    box_log.insert("end", messaggio + "\n")
    box_log.see("end")
    box_log.configure(state="disabled")


# --- INTERFACCIA GRAFICA ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Smart File Organizer")
app.geometry("500x600")

titolo = ctk.CTkLabel(app, text="Smart File Organizer", font=("Helvetica", 20, "bold"))
titolo.pack(pady=(15, 5))

stato_label = ctk.CTkLabel(app, text="Stato: Fermo", font=("Helvetica", 14), text_color="gray")
stato_label.pack(pady=(0, 5))

lbl_cartella = ctk.CTkLabel(app, text=f"Cartella: {cartella_selezionata.name}", font=("Helvetica", 12))
lbl_cartella.pack(pady=(0, 10))

# Interruttore Avvio con Windows
switch_avvio_var = ctk.BooleanVar(value=controlla_stato_avvio())
switch_avvio = ctk.CTkSwitch(app, text="Avvia con Windows", command=imposta_avvio_windows, variable=switch_avvio_var)
switch_avvio.pack(pady=5)

frame_bottoni = ctk.CTkFrame(app, fg_color="transparent")
frame_bottoni.pack(pady=5)

btn_scegli = ctk.CTkButton(frame_bottoni, text="Scegli Cartella", width=140, command=scegli_cartella)
btn_scegli.grid(row=0, column=0, padx=5)

btn_impostazioni = ctk.CTkButton(frame_bottoni, text="Modifica Regole", width=140, fg_color="#555555",
                                 hover_color="#333333", command=apri_impostazioni)
btn_impostazioni.grid(row=0, column=1, padx=5)

frame_controlli = ctk.CTkFrame(app, fg_color="transparent")
frame_controlli.pack(pady=10)

btn_avvia = ctk.CTkButton(frame_controlli, text="Avvia", width=140, fg_color="green", hover_color="darkgreen",
                          command=avvia_organizer)
btn_avvia.grid(row=0, column=0, padx=5)

btn_ferma = ctk.CTkButton(frame_controlli, text="Ferma", width=140, fg_color="red", hover_color="darkred",
                          state="disabled", command=ferma_organizer)
btn_ferma.grid(row=0, column=1, padx=5)

lbl_contatore = ctk.CTkLabel(app, text="File spostati: 0", font=("Helvetica", 12, "bold"), text_color="#aaaaaa")
lbl_contatore.pack(pady=(10, 5))

box_log = ctk.CTkTextbox(app, width=450, height=150, fg_color="#1e1e1e", text_color="#00ff00", font=("Consolas", 12))
box_log.pack(pady=5)
box_log.insert("0.0", "--- LOG DI SISTEMA ---\n")
box_log.configure(state="disabled")


def alla_chiusura():
    ferma_organizer()
    app.destroy()


app.protocol("WM_DELETE_WINDOW", alla_chiusura)
app.mainloop()