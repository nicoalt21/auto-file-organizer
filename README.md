# 🗂️ Smart File Organizer (v3.0.0)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> Un'applicazione desktop cross-platform che monitora una cartella e smista automaticamente i file in sottocartelle, basandosi su regole configurabili per estensione.

---

## Funzionalità

- **Monitoraggio Event-Driven** — Nessun polling: reagisce istantaneamente agli eventi del filesystem tramite `watchdog`.
- **GUI dark-mode moderna** — Interfaccia reattiva costruita con `CustomTkinter`.
- **Editor Regole a Badge** — Aggiungi o rimuovi estensioni con un'interfaccia visiva, senza toccare JSON a mano.
- **Gestione Anti-Duplicati** — Rinomina automaticamente i file con lo stesso nome (es. `documento_1.pdf`).
- **Notifiche Desktop Native** — Avvisi OS-level ad ogni file organizzato tramite `plyer`.
- **System Tray** — Chiudi la finestra e l'app continua a lavorare in background (Windows e Linux).
- **Avvio con Windows** — Integrazione diretta con il Registro (`HKEY_CURRENT_USER`) per l'autorun.
- **Impostazioni Persistenti** — Cartella, preferenze e stato degli switch salvati in `settings.json`.
- **Modalità CLI** — `organizer.py` è eseguibile standalone da terminale, senza GUI.

---

##  Struttura del Progetto
```
auto-file-organizer/
├── gui.py           # Entry point dell'applicazione con interfaccia grafica
├── organizer.py     # Logica di monitoraggio e spostamento file (usabile anche standalone)
├── config.json      # Regole di organizzazione (cartelle → estensioni)
├── settings.json    # Preferenze utente (generato automaticamente, escluso da git)
├── requirements.txt # Dipendenze Python
└── .gitignore       # Esclude settings.json e percorsi locali
```

---

## Come Funziona

### Architettura
```
gui.py  ──────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                              │
│  CTk UI Loop (main thread)                                                                   │
│  ├── Switch: Notifiche / Tray / Avvio Windows                                                │
│  ├── Badge Editor  ──► legge/scrive config.json                                              │
│  └── Bottoni Avvia/Ferma/Riavvia  ──► controlla Observer                                    │
│                                                                                              │
│  watchdog.Observer (thread secondario)                                                        │
│  └── GestoreDownload (FileSystemEventHandler)  ──► on_modified()                             │
│       ├── Filtra estensioni temporanee (.crdownload, .tmp, .part)                             │
│       ├── Cerca cartella di destinazione in config.json                                       │
│       └── sposta_file()  ──► anti-duplicati + shutil.move()                                  │
│                                                                                               │
│  pystray.Icon (thread daemon)  ─── attivo solo quando la finestra è nascosta                  │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Flusso di uno spostamento

1. `watchdog` intercetta un evento `on_modified` sulla cartella monitorata.
2. Vengono filtrati i file temporanei (`.crdownload`, `.tmp`, `.part`) e quelli senza estensione.
3. L'estensione del file viene cercata nelle regole caricate da `config.json`.
4. Se trovata, viene creata la sottocartella di destinazione (se non esiste).
5. Loop anti-duplicati: se il file esiste già, aggiunge `_1`, `_2`, ecc.
6. `shutil.move()` sposta il file; un `time.sleep(1)` garantisce che il file sia stato scritto completamente.
7. Il log visivo e le notifiche desktop vengono aggiornati tramite `log_callback`.

---

## Formato di `config.json`
```json
{
    "Immagini": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
    "Documenti": [".pdf", ".docx", ".xlsx", ".pptx", ".txt"],
    "Video":     [".mp4", ".mkv", ".avi", ".mov"],
    "Audio":     [".mp3", ".wav", ".flac", ".aac"],
    "Archivi":   [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programmi": [".exe", ".msi", ".dmg", ".deb"]
}
```

Puoi modificarlo direttamente o usare l'**Editor Regole a Badge** nell'interfaccia grafica.

---

## Compatibilità OS

| Feature                  | Windows | macOS | Linux |
|--------------------------|:-------:|:-----:|:-----:|
| Monitoraggio file        | ✅      | ✅    | ✅    |
| GUI dark-mode            | ✅      | ✅    | ✅    |
| Notifiche desktop        | ✅      | ✅    | ✅    |
| System Tray              | ✅      | ❌ *  | ✅ ** |
| Avvio automatico         | ✅      | ❌    | ❌    |

> \* Disabilitata su macOS: le interazioni UI da thread secondari causano crash.  
> \*\* Dipende dal Desktop Environment (GNOME, KDE, ecc.).

---

## Installazione (Sorgente)

**Prerequisiti:** Python 3.8+
```bash
# 1. Clona il repository
git clone https://github.com/nicoalt21/auto-file-organizer.git
cd auto-file-organizer

# 2. Installa le dipendenze
pip install -r requirements.txt

# 3. Avvia l'applicazione
python gui.py

# Oppure, modalità solo CLI (nessuna GUI)
python organizer.py
```

### Dipendenze (`requirements.txt`)

| Libreria        | Utilizzo                                      |
|-----------------|-----------------------------------------------|
| `customtkinter` | Interfaccia grafica dark-mode                 |
| `watchdog`      | Monitoraggio eventi filesystem                |
| `plyer`         | Notifiche desktop native cross-platform       |
| `pystray`       | Icona e menu nella System Tray                |
| `Pillow`        | Generazione dell'icona tray a runtime         |

---

## Release Ufficiali (Windows)

Per chi non vuole eseguire il sorgente, sono disponibili eseguibili pre-compilati nella sezione **[Releases](https://github.com/nicoalt21/auto-file-organizer/releases)**.

1. Scarica `SmartOrganizer.exe` dalla pagina Releases.
2. Eseguilo direttamente — nessuna installazione richiesta.
3. Assicurati che `config.json` sia nella stessa cartella dell'eseguibile.

> **Nota:** Il percorso di `config.json` e `settings.json` viene risolto relativamente all'eseguibile tramite `sys.executable` quando l'app è compilata con PyInstaller (`getattr(sys, 'frozen', False)`).

---

## Privacy

`settings.json` contiene percorsi assoluti locali ed è escluso dal repository tramite `.gitignore`. Nessun dato viene inviato a servizi esterni.