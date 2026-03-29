# Smart File Organizer (v2.0.0)

## English

A Python-based desktop application that automatically monitors a selected folder and organizes incoming files into specific subfolders based on their extensions.

### Key Features
* Graphical User Interface (GUI): Clean and modern dark mode interface to control the script without using the terminal.
* Custom Folder Selection: Choose any folder on your computer to monitor (Downloads, Desktop, etc.).
* Smart Conflict Handling: If a downloaded file already exists, the program intelligently renames it (e.g., `file_1.pdf`) to prevent data loss.
* Live Terminal & Stats: Real-time visual feedback of moved files and a session counter directly in the app.
* Integrated Rule Editor: Modify the sorting rules (JSON format) through a dedicated window inside the application.
* Run on Startup (Windows Only): Toggle option to automatically start the organizer in the background when Windows boots.

### How to Use
1. Windows Users: Download the `SmartOrganizer_v2.0.0_Windows.zip` from the Releases page. Extract it, keep the `.exe` and the `config.json` in the same folder, and run the executable.
2. Mac/Linux Users: Run the source code directly using `python gui.py` (Requires Python and the dependencies listed in `requirements.txt`).

---

## Italiano

Un'applicazione desktop basata su Python che monitora automaticamente una cartella selezionata e organizza i file in entrata in sottocartelle specifiche in base alla loro estensione.

### Funzionalità Principali
* Interfaccia Grafica (GUI): Interfaccia moderna in dark mode per controllare il programma senza usare il terminale.
* Selezione Cartella Personalizzata: Scegli qualsiasi cartella sul tuo computer da monitorare (Download, Desktop, ecc.).
* Gestione Intelligente Duplicati: Se un file appena scaricato esiste già, il programma lo rinomina in automatico (es. `file_1.pdf`) per evitare sovrascritture.
* Terminale Live e Statistiche: Feedback visivo in tempo reale dei file spostati e contatore della sessione direttamente nell'app.
* Editor di Regole Integrato: Modifica le regole di smistamento (formato JSON) tramite una finestra dedicata all'interno dell'applicazione.
* Avvio Automatico (Solo Windows): Opzione per avviare automaticamente l'organizer in background all'accensione del PC.

### Come Usarlo
1. Utenti Windows: Scarica il file `SmartOrganizer_v2.0.0_Windows.zip` dalla pagina Releases. Estrailo, mantieni il file `.exe` e `config.json` nella stessa cartella e avvia l'eseguibile.
2. Utenti Mac/Linux: Avvia direttamente il codice sorgente usando `python gui.py` (Richiede Python e le dipendenze elencate in `requirements.txt`).
