# 📂 Smart File Organizer (v1.1.0)
![Python](https://img.shields.io/badge/python-3.x-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)

An intelligent, event-driven Python utility that monitors your folders and automatically organizes incoming files into categorized subdirectories based on their extensions.

## Overview
This tool runs silently in the background and acts as a digital librarian. Unlike basic scripts that scan folders on a timer, this project uses OS-level event monitoring to trigger actions only when a new file is actually created, ensuring 0% idle CPU usage.

## Key Features
* **Event-Driven Architecture**: Powered by `watchdog` to intercept File System events instantly.
* **Zero-UI Background Execution**: Run it as a "daemon" process (`.pyw`) on Windows for invisible operation.
* **Smart Conflict Handling**: Includes a 1-second safety delay to ensure files are fully downloaded before moving.
* **Dynamic Configuration**: Manage your sorting rules via `config.json` without touching the code.
* **Cross-Platform**: Built using `pathlib` for full compatibility (Windows, macOS, Linux).
* **Auto-Renaming (Anti-Duplicates)**: If a downloaded file already exists, it intelligently renames it (e.g., `file_1.pdf`) to prevent data loss.

## Technical Stack
* Language: Python `3.x`
* Core Library: `watchdog` (Event monitoring)
* Architecture: Observer Pattern

---

## 📥 Installation & Setup

### Option 1: Quick Start (Recommended)
1. **Install Python**: Download it from [python.org](https://www.python.org/downloads/). 
   * **IMPORTANT**: During installation, check the box **"Add Python to PATH"**.
2. **Download the Project**: Go to the [Releases](https://github.com/nicoalt21/auto-file-organizer/releases) page and download the `.zip`. Extract it to a folder on your PC (e.g., Desktop).
3. **Install Dependencies**:
   * Open the extracted folder.
   * Click on the address bar at the top, type `cmd`, and press **Enter**.
   * In the black window that appears, paste the following command and press Enter:
     ```bash
     pip install -r requirements.txt
     ```
   * Once finished, you can close the window.
4. Follow the **"How to Use"** instructions below.

### Option 2: Clone for Developers
```bash
git clone [https://github.com/nicoalt21/auto-file-organizer.git](https://github.com/nicoalt21/auto-file-organizer.git)
cd auto-file-organizer
pip install -r requirements.txt
5. Follow the "How to Use" instructions below.

### Option 2: Clone for Developers

```bash
git clone https://github.com/nicoalt21/auto-file-organizer.git
cd auto-file-organizer
pip install -r requirements.txt
```
---

## ⚙️ How to Use

### 1. Configure Rules

Edit the config.json file to define your categories and extensions:

```json
{
  "Immagini": [".jpg", ".png", ".jpeg", ".gif", ".svg", ".webp"],
  "Documenti": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
  "Archivi": [".zip", ".rar", ".7z", ".tar", ".gz"],
  "Installatori": [".exe", ".msi", ".dmg", ".iso"],
  "Video": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
  "Musica": [".mp3", ".wav", ".flac", ".ogg", ".m4a"],
  "Codice": [".py", ".html", ".css", ".js", ".cpp", ".json"]
}
```
### 2. Run the Organizer

* **Visible Mode (Testing)**: Execute `python organizer.py` to see logs in the terminal.
* **Stealth Mode (Production)**: Rename `organizer.py` to `organizer.pyw` and double-click it.

### 3. Stop the Program

To stop the background process on Windows:
1. Open Task Manager (CTRL+SHIFT+ESC).
2. Find and Kill the `pythonw.exe` process associated with the script.

## Bonus: Autostart on Windows
To make the organizer run automatically every time you turn on your PC:
1. Press `Win + R`, type `shell:startup`, and hit Enter.
2. Create a shortcut of your `organizer.pyw` (or a `.bat` file) in that folder.
3. That's it! The script will now work silently in the background from boot.

---
*Developed as a portfolio project to demonstrate Python automation and system-level programming.*

---

## 🇮🇹 Istruzioni in Italiano (Guida Rapida)

Questo strumento serve a tenere pulita la cartella "Download" spostando automaticamente i file nelle cartelle giuste (Immagini, Documenti, ecc.) non appena vengono scaricati.

### 📥 Come installarlo (Passo dopo passo)

1. **Installa Python**: Scaricalo da [python.org](https://www.python.org/downloads/). 
   * **IMPORTANTE**: Durante l'installazione, spunta la casella **"Add Python to PATH"**.
2. **Scarica il progetto**: Vai nella sezione [Releases](https://github.com/nicoalt21/auto-file-organizer/releases) e scarica lo ZIP. Estrai il contenuto in una cartella sul tuo PC (es. sul Desktop).
3. **Installa i componenti**: 
   * Entra nella cartella estratta.
   * Clicca sulla barra degli indirizzi in alto (dove vedi il percorso della cartella), scrivi `cmd` e premi **Invio**.
   * Nella finestra nera che appare, incolla questo comando e premi Invio:
     ```bash
     pip install -r requirements.txt
     ```
   * Quando ha finito, puoi chiudere la finestra.

### 🚀 Come usarlo

* **Per testarlo**: Nella stessa cartella, scrivi `cmd` nella barra in alto e digita `python organizer.py`. Vedrai i messaggi ogni volta che un file viene spostato.
* **Per l'uso quotidiano**: Rinomina il file `organizer.py` in `organizer.pyw`. Facendo doppio clic su di esso, il programma partirà "invisibile" e lavorerà in sottofondo senza disturbarti.

### ⚙️ Personalizzazione
Puoi cambiare i nomi delle cartelle o aggiungere nuove estensioni modificando il file `config.json` con un semplice editor di testo (come il Blocco Note).

---
*Progetto realizzato per dimostrare competenze di automazione e programmazione di sistema.*
