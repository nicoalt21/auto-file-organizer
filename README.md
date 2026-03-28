# 📂 Smart File Organizer (v1.0.0)
An intelligent, event-driven Python utility that monitors your folders and automatically organizes incoming files into categorized subdirectories based on their extensions.
## Overview
Tired of a cluttered "Downloads" folder? This tool runs silently in the background and acts as a digital librarian. Unlike basic scripts that scan folders on a timer, this project uses OS-level event monitoring to trigger actions only when a new file is actually created, ensuring 0% idle CPU usage.
## Key Features
* **Event-Driven Architecture**: Powered by `watchdog` to intercept File System events instantly.
* **Zero-UI Background Execution**: Run it as a "daemon" process (`.pyw`) on Windows for invisible operation.
* **Smart Conflict Handling**: Includes a 1-second safety delay to ensure files are fully downloaded before moving.
* **Dynamic Configuration**: Manage your sorting rules via `config.json` without touching the code.
* **Cross-Platform**: Built using `pathlib` for full compatibility (Windows, macOS, Linux).

## 🛠️ Technical Stack

* Language: Python `3.x`
* Core Library: `watchdog` (Event monitoring)
* Architecture: Observer Pattern

## 📥 Installation & Setup

### Option 1: Quick Start (Recommended)

1. Go to the [Releases](https://github.com/nicoalt21/auto-file-organizer/releases) page.
2. Download the latest source code (`.zip` or `.tar.gz`).
3. Extract the files and follow the instructions below.

### 🛠️ Option 2: Clone for Developers

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
  "Images": [".jpg", ".png", ".jpeg"],
  "Documents": [".pdf", ".docx", ".txt"],
  "Archives": [".zip", ".rar"],
  "Programs": [".exe", ".msi"]
}
```
### 2. Run the Organizer

* **Visible Mode (Testing)**: Execute `python organizer.py` to see logs in the terminal.
* **Stealth Mode (Production)**: Rename `organizer.py` to `organizer.pyw` and double-click it.

### 3. Stop the Program

To stop the background process on Windows:
1. Open Task Manager (CTRL+SHIFT+ESC).
2. Find and Kill the `pythonw.exe` process associated with the script.

---
*Developed as a portfolio project to demonstrate Python automation and system-level programming.*
