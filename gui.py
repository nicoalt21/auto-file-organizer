import customtkinter as ctk
from watchdog.observers import Observer
import organizer
import os
import sys
import time
import platform
import subprocess
import threading
import json
from pathlib import Path

from plyer import notification
import pystray
from PIL import Image, ImageDraw

# --- CONTROLLO SISTEMA OPERATIVO ---
SISTEMA_OPERATIVO = platform.system()

if SISTEMA_OPERATIVO == 'Windows':
    import winreg

mio_observer = None
file_spostati = 0

# Trova i percorsi corretti (compatibile con PyInstaller)
if getattr(sys, 'frozen', False):
    cartella_script = Path(sys.executable).parent
else:
    cartella_script = Path(__file__).parent

percorso_config = cartella_script / "config.json"
percorso_settings = cartella_script / "settings.json"

# --- GESTIONE IMPOSTAZIONI ---
impostazioni_default = {
    "notifiche_attive": True,
    "tray_attiva": True,
    "ultima_cartella": str(organizer.trova_cartella_download())
}


def carica_impostazioni():
    if percorso_settings.exists():
        try:
            with open(percorso_settings, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Impostazioni corrotte, uso default: {e}")
    return impostazioni_default.copy()


impostazioni_attuali = carica_impostazioni()

cartella_selezionata = Path(impostazioni_attuali.get("ultima_cartella", str(organizer.trova_cartella_download())))
if not cartella_selezionata.exists():
    cartella_selezionata = organizer.trova_cartella_download()


def salva_impostazioni(*args):
    impostazioni = {
        "notifiche_attive": switch_notifiche_var.get(),
        "tray_attiva": switch_tray_var.get(),
        "ultima_cartella": str(cartella_selezionata)
    }
    try:
        with open(percorso_settings, "w") as f:
            json.dump(impostazioni, f, indent=4)
    except Exception as e:
        print(f"Errore salvataggio impostazioni: {e}")


# --- FUNZIONI DI WINDOWS ---
def controlla_stato_avvio():
    if SISTEMA_OPERATIVO != 'Windows':
        return False
    try:
        chiave = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ
        )
        winreg.QueryValueEx(chiave, "SmartFileOrganizer")
        winreg.CloseKey(chiave)
        return True
    except FileNotFoundError:
        return False


def imposta_avvio_windows():
    if SISTEMA_OPERATIVO != 'Windows':
        return
    attiva = switch_avvio_var.get()

    if getattr(sys, 'frozen', False):
        comando = f'"{sys.executable}"'
    else:
        comando = f'"{sys.executable}" "{os.path.abspath(__file__)}"'

    try:
        chiave = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        if attiva:
            winreg.SetValueEx(chiave, "SmartFileOrganizer", 0, winreg.REG_SZ, comando)
            aggiungi_log("Avvio con Windows: ATTIVATO")
        else:
            try:
                winreg.DeleteValue(chiave, "SmartFileOrganizer")
            except FileNotFoundError:
                pass
            aggiungi_log("Avvio con Windows: DISATTIVATO")
        winreg.CloseKey(chiave)
    except Exception as e:
        aggiungi_log(f"Errore registro: {e}")


# --- FUNZIONI SYSTEM TRAY ---
def crea_immagine_icona():
    image = Image.new('RGB', (64, 64), color=(43, 43, 43))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(0, 200, 0))
    return image


def mostra_finestra(icon, item):
    icon.stop()
    app.after(0, app.deiconify)


def esci_da_tray(icon, item):
    icon.stop()
    ferma_organizer()
    app.after(0, app.destroy)


def nascondi_nella_tray():
    app.withdraw()
    menu = pystray.Menu(
        pystray.MenuItem("Mostra Organizer", mostra_finestra),
        pystray.MenuItem("Esci", esci_da_tray)
    )
    icon = pystray.Icon("SmartOrganizer", crea_immagine_icona(), "Smart File Organizer", menu)
    threading.Thread(target=icon.run, daemon=True).start()


# --- EDITOR REGOLE A "BADGE" ---
def apri_impostazioni():
    finestra_regole = ctk.CTkToplevel(app)
    finestra_regole.title("Gestione Regole")
    finestra_regole.geometry("700x500")
    finestra_regole.attributes("-topmost", True)

    label_info = ctk.CTkLabel(
        finestra_regole,
        text="Organizza le tue cartelle e le estensioni:",
        font=("Helvetica", 14, "bold")
    )
    label_info.pack(pady=(10, 5))

    frame_scroll = ctk.CTkScrollableFrame(finestra_regole, width=650, height=350)
    frame_scroll.pack(pady=5, padx=10, fill="both", expand=True)

    righe_regole = []

    def aggiungi_riga_ui(nome_cartella="", estensioni_list=None):
        if estensioni_list is None:
            estensioni_list = []

        riga = ctk.CTkFrame(frame_scroll, fg_color="#2b2b2b", corner_radius=10)
        riga.pack(fill="x", pady=8, padx=5, ipadx=5, ipady=5)

        frame_top = ctk.CTkFrame(riga, fg_color="transparent")
        frame_top.pack(fill="x", pady=(0, 5))

        entry_nome = ctk.CTkEntry(
            frame_top, width=200,
            placeholder_text="Nome Cartella (es. Immagini)",
            font=("Helvetica", 14, "bold")
        )
        entry_nome.insert(0, nome_cartella)
        entry_nome.pack(side="left")

        # Dati riga registrati prima del callback di eliminazione
        dati_riga = {"nome": entry_nome, "estensioni_list": [], "frame": riga}
        righe_regole.append(dati_riga)

        def elimina_riga():
            riga.destroy()
            # FIX: rimuove anche i dati dalla lista per evitare righe zombie
            if dati_riga in righe_regole:
                righe_regole.remove(dati_riga)

        btn_elimina_riga = ctk.CTkButton(
            frame_top, text="Elimina Cartella", width=100,
            fg_color="#8b0000", hover_color="#5a0000",
            command=elimina_riga
        )
        btn_elimina_riga.pack(side="right")

        frame_bot = ctk.CTkFrame(riga, fg_color="transparent")
        frame_bot.pack(fill="x")

        frame_badges = ctk.CTkFrame(frame_bot, fg_color="transparent")
        frame_badges.pack(side="left", fill="x", expand=True)

        def aggiungi_badge(ext_str):
            ext_str = ext_str.strip().lower()
            if not ext_str:
                return
            if not ext_str.startswith('.'):
                ext_str = '.' + ext_str
            if ext_str in dati_riga["estensioni_list"]:
                return

            dati_riga["estensioni_list"].append(ext_str)

            badge = ctk.CTkFrame(frame_badges, fg_color="#1f538d", corner_radius=15)
            badge.pack(side="left", padx=3, pady=2)

            lbl = ctk.CTkLabel(badge, text=ext_str, font=("Helvetica", 12))
            lbl.pack(side="left", padx=(8, 2))

            def rimuovi_badge():
                badge.destroy()
                if ext_str in dati_riga["estensioni_list"]:
                    dati_riga["estensioni_list"].remove(ext_str)

            btn_x = ctk.CTkButton(
                badge, text="x", width=20, height=20,
                fg_color="transparent", hover_color="red",
                text_color="white", command=rimuovi_badge
            )
            btn_x.pack(side="left", padx=(0, 5))

        for ext in estensioni_list:
            aggiungi_badge(ext)

        entry_new_ext = ctk.CTkEntry(frame_bot, width=80, placeholder_text=".pdf")
        entry_new_ext.pack(side="left", padx=5)

        def on_add(*args):
            aggiungi_badge(entry_new_ext.get())
            entry_new_ext.delete(0, 'end')

        entry_new_ext.bind("<Return>", on_add)

        btn_add_ext = ctk.CTkButton(frame_bot, text="+ Aggiungi", width=80, command=on_add)
        btn_add_ext.pack(side="left")

    try:
        with open(percorso_config, "r") as file:
            regole_attuali = json.load(file)
            for cartella, estensioni in regole_attuali.items():
                aggiungi_riga_ui(cartella, estensioni)
    except FileNotFoundError:
        aggiungi_riga_ui()
    except json.JSONDecodeError as e:
        aggiungi_log(f"Errore lettura config.json: {e}")

    btn_aggiungi_riga = ctk.CTkButton(
        finestra_regole, text="+ Aggiungi Nuova Cartella",
        fg_color="#444444", hover_color="#222222",
        command=aggiungi_riga_ui
    )
    btn_aggiungi_riga.pack(pady=5)

    def salva_tutto():
        nuove_regole = {}
        for dati in righe_regole:
            nome = dati["nome"].get().strip()
            ext_list = dati["estensioni_list"]
            if nome and ext_list:
                nuove_regole[nome] = ext_list

        try:
            with open(percorso_config, "w") as file:
                json.dump(nuove_regole, file, indent=4)
            aggiungi_log("Regole salvate! Clicca su 'Riavvia' per applicarle.")
            finestra_regole.destroy()
        except Exception as e:
            aggiungi_log(f"Errore salvataggio: {e}")

    btn_salva = ctk.CTkButton(
        finestra_regole, text="Salva Impostazioni",
        fg_color="green", hover_color="darkgreen",
        command=salva_tutto
    )
    btn_salva.pack(pady=10)


# --- ALTRE FUNZIONI GUI ---
def scegli_cartella():
    global cartella_selezionata
    cartella = ctk.filedialog.askdirectory(title="Scegli la cartella", initialdir=cartella_selezionata)
    if cartella:
        cartella_selezionata = Path(cartella)
        lbl_cartella.configure(text=f"Cartella: {cartella_selezionata.name}")
        salva_impostazioni()
        aggiungi_log(f"Nuova cartella: {cartella_selezionata.name}")


def apri_cartella_selezionata():
    percorso = str(cartella_selezionata)
    try:
        if SISTEMA_OPERATIVO == 'Windows':
            os.startfile(percorso)
        elif SISTEMA_OPERATIVO == 'Darwin':
            subprocess.call(('open', percorso))
        else:
            subprocess.call(('xdg-open', percorso))
    except Exception as e:
        aggiungi_log(f"Errore: {e}")


def evento_spostamento(messaggio):
    """
    Callback chiamato dal thread watchdog.
    FIX: usa app.after() per aggiornare la GUI in modo thread-safe.
    """
    app.after(0, lambda: _aggiorna_gui_spostamento(messaggio))


def _aggiorna_gui_spostamento(messaggio):
    """Aggiornamento GUI eseguito nel main thread."""
    global file_spostati
    if "Spostato" in messaggio:
        file_spostati += 1
        lbl_contatore.configure(text=f"File spostati: {file_spostati}")

        if switch_notifiche_var.get():
            try:
                notification.notify(
                    title="File Organizzato",
                    message=messaggio,
                    app_name="Smart Organizer",
                    timeout=3
                )
            except Exception:
                pass

    orario = time.strftime('%H:%M:%S')
    aggiungi_log(f"[{orario}] {messaggio}")


def avvia_organizer():
    global mio_observer
    if mio_observer is not None and mio_observer.is_alive():
        return

    regole = organizer.carica_regole()
    if regole and cartella_selezionata.exists():
        gestore = organizer.GestoreDownload(cartella_selezionata, regole, log_callback=evento_spostamento)
        mio_observer = Observer()
        mio_observer.schedule(gestore, str(cartella_selezionata), recursive=False)
        mio_observer.start()

        stato_label.configure(text="Stato: In esecuzione", text_color="green")
        btn_avvia.configure(state="disabled")
        btn_ferma.configure(state="normal")
        btn_riavvia.configure(state="normal")
        aggiungi_log(f"[{time.strftime('%H:%M:%S')}] Organizer avviato.")
    else:
        aggiungi_log("Errore: Impossibile caricare regole o cartella non trovata.")


def ferma_organizer():
    global mio_observer
    if mio_observer is not None and mio_observer.is_alive():
        mio_observer.stop()
        mio_observer.join()
        mio_observer = None

        stato_label.configure(text="Stato: Fermo", text_color="gray")
        btn_avvia.configure(state="normal")
        btn_ferma.configure(state="disabled")
        btn_riavvia.configure(state="disabled")
        aggiungi_log(f"[{time.strftime('%H:%M:%S')}] Organizer fermato.")


def riavvia_organizer():
    if mio_observer is not None and mio_observer.is_alive():
        aggiungi_log("Riavvio motore in corso...")
        ferma_organizer()
        app.after(1000, avvia_organizer)
    else:
        avvia_organizer()


def aggiungi_log(messaggio):
    box_log.configure(state="normal")
    box_log.insert("end", messaggio + "\n")
    box_log.see("end")
    box_log.configure(state="disabled")


def alla_chiusura():
    if switch_tray_var.get() and SISTEMA_OPERATIVO != 'Darwin':
        nascondi_nella_tray()
    else:
        ferma_organizer()
        app.destroy()


# --- COSTRUZIONE INTERFACCIA GRAFICA ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Smart File Organizer")
app.geometry("520x680")

titolo = ctk.CTkLabel(app, text="Smart File Organizer", font=("Helvetica", 20, "bold"))
titolo.pack(pady=(15, 5))

stato_label = ctk.CTkLabel(app, text="Stato: Fermo", font=("Helvetica", 14), text_color="gray")
stato_label.pack(pady=(0, 5))

lbl_cartella = ctk.CTkLabel(app, text=f"Cartella: {cartella_selezionata.name}", font=("Helvetica", 12))
lbl_cartella.pack(pady=(0, 5))

btn_apri_cartella = ctk.CTkButton(
    app, text="Apri Cartella", width=120, height=24,
    fg_color="#444444", hover_color="#222222",
    command=apri_cartella_selezionata
)
btn_apri_cartella.pack(pady=(0, 15))

# --- ZONA INTERRUTTORI OPZIONI ---
frame_opzioni = ctk.CTkFrame(app, fg_color="transparent")
frame_opzioni.pack(pady=5)

switch_notifiche_var = ctk.BooleanVar(value=impostazioni_attuali.get("notifiche_attive", True))
switch_notifiche = ctk.CTkSwitch(
    frame_opzioni, text="Notifiche Desktop",
    variable=switch_notifiche_var, command=salva_impostazioni
)
switch_notifiche.grid(row=0, column=0, padx=15, pady=5)

switch_tray_var = ctk.BooleanVar(value=impostazioni_attuali.get("tray_attiva", True))
switch_tray = ctk.CTkSwitch(
    frame_opzioni, text="Minimizza in Tray",
    variable=switch_tray_var, command=salva_impostazioni
)
switch_tray.grid(row=0, column=1, padx=15, pady=5)

# Disattiva la tray su macOS
if SISTEMA_OPERATIVO == 'Darwin':
    switch_tray_var.set(False)
    switch_tray.configure(state="disabled", text="Tray (Non supp. su Mac)")

if SISTEMA_OPERATIVO == 'Windows':
    switch_avvio_var = ctk.BooleanVar(value=controlla_stato_avvio())
    switch_avvio = ctk.CTkSwitch(
        frame_opzioni, text="Avvia con Windows",
        command=imposta_avvio_windows, variable=switch_avvio_var
    )
    switch_avvio.grid(row=1, column=0, columnspan=2, pady=10)

# --- ZONA BOTTONI PRINCIPALI ---
frame_bottoni = ctk.CTkFrame(app, fg_color="transparent")
frame_bottoni.pack(pady=5)

btn_scegli = ctk.CTkButton(frame_bottoni, text="Scegli Cartella", width=140, command=scegli_cartella)
btn_scegli.grid(row=0, column=0, padx=5)

btn_impostazioni = ctk.CTkButton(
    frame_bottoni, text="Modifica Regole", width=140,
    fg_color="#555555", hover_color="#333333",
    command=apri_impostazioni
)
btn_impostazioni.grid(row=0, column=1, padx=5)

frame_controlli = ctk.CTkFrame(app, fg_color="transparent")
frame_controlli.pack(pady=10)

btn_avvia = ctk.CTkButton(
    frame_controlli, text="Avvia", width=100,
    fg_color="green", hover_color="darkgreen",
    command=avvia_organizer
)
btn_avvia.grid(row=0, column=0, padx=5)

btn_ferma = ctk.CTkButton(
    frame_controlli, text="Ferma", width=100,
    fg_color="red", hover_color="darkred",
    state="disabled", command=ferma_organizer
)
btn_ferma.grid(row=0, column=1, padx=5)

btn_riavvia = ctk.CTkButton(
    frame_controlli, text="Riavvia", width=100,
    fg_color="#b8860b", hover_color="#8b6508",
    state="disabled", command=riavvia_organizer
)
btn_riavvia.grid(row=0, column=2, padx=5)

lbl_contatore = ctk.CTkLabel(app, text="File spostati: 0", font=("Helvetica", 12, "bold"), text_color="#aaaaaa")
lbl_contatore.pack(pady=(5, 5))

box_log = ctk.CTkTextbox(app, width=460, height=130, fg_color="#1e1e1e", text_color="#00ff00",
                         font=("Consolas", 12))
box_log.pack(pady=5)
box_log.insert("0.0", "--- LOG DI SISTEMA ---\n")
box_log.configure(state="disabled")

app.protocol("WM_DELETE_WINDOW", alla_chiusura)
app.mainloop()