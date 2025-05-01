# Statistarr

A simple Python script to track **failed** and **successful** grabs per indexer. Currently works with **Sonarr** and **Radarr** only.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

### 🧐 Why?

Prowlarr doesn’t track failed grabs, and when you remove movies or shows from Radarr/Sonarr, their associated stats vanish too.  
Statistarr solves that by:

- Fetching your history via the API  
- Logging grab stats per indexer  
- Saving it to a persistent `JSON` file  

> [!Note]
> Stats may be inaccurate at first, not because the script starts fresh, but because Radarr and Sonarr delete history data for any shows or movies you’ve removed. Once something is gone, so is its history — meaning the script has nothing to track for it. Let the script run continuously from now on, and over time you'll build a more complete picture of how each indexer performs.

---

### ⚙️ How does it work?

Honestly? It’s a messy little script mostly written by ChatGPT.  
It:

1. Calls the `v3/history` API
2. Filters and processes events
3. Notes the latest event date
4. Saves stats in a `JSON` file  
5. Merges new stats with older ones (so historical data isn’t lost)

> **First-time run might take a while** depending on how big your history is.  
> It's not perfect—bugs may exist. Feel free to open an issue if something breaks.

---

### 🧰 Setup


**Requirements**
- Python 3 (tested on `3.13.3`)
- `pip`
- Install dependencies:

```
pip install requests quickchart.io pyinstaller plyer pystray apscheduler psutil
```

> [!Tip]
> Keep all script files in one separate directory for smoother execution.

Moving ahead:
1. Download all the files from `script` folder.
2. Rename `config.json.example` to `config.json`.
3. Fill in your API details inside `config.json`.
4. Build executables using `pyinstaller` or download pre-built executables (Windows only) from [Releases](https://github.com/lostb053/Statistarr/releases) page:

```bash
pyinstaller --onefile --noconsole fetcher.py
pyinstaller --onefile --noconsole tray.py
```
5. Get the executables from `dist` and place them back in parent folder. Clean up extra files from pyinstaller.
6. Run `tray.exe` (or whatever executable you end up with)
<br><br>

**Expected directory structure:**
```
Statistarr/
|- cchart.py
|- config.json
|- fetcher.exe
|- fetcher.py (optional, helpful for debugging code yourself)
|- icon.ico
|- statistarr.py
|- tray.exe
|- tray.py (optional, helpful for debugging code yourself)
|- backup/ (created later by app)
|- error.log (created later by app)
|- Stats *.json (created later by app)
|- untracked.log (created later by app)

```

> [!Tip]
> Add tray.exe to startup app.

---

## 🛠 Script Overview

- `statistarr.py` – Prints readable output to the terminal. Also creates or updates the `JSON` stats dump.
- `statistarr_silent.py` – Same functionality as above, but runs quietly in the background (when used as an app).
- `cchart.py` – Uses [QuickChart.io](https://quickchart.io/) to display your collected stats in a simple graph or chart.

> [!Important]
> PyInstaller executables may trigger false positives in antivirus tools or VirusTotal. This is a known issue and not unique to this project.

---

## 📸 Screenshots

### `statistarr.py` Terminal Output

_(Indexers have been blurred to protect the innocent 😭)_

![Screenshot](https://github.com/user-attachments/assets/20787e55-4e36-4f30-9b6e-9a2707eee41c)  
![Screenshot](https://github.com/user-attachments/assets/add7f0a2-8306-46a9-ab87-429042c48144)

> [!note]
> **Failure Rate = Failed Grabs ÷ (Successful Grabs + Failed Grabs)**

---

### `cchart.py` Graph Output

![Chart](https://github.com/user-attachments/assets/a7824839-d075-46d2-beeb-77f8687d7a37)

---

## 🙏 Credits

- **ChatGPT** – For assembling most of this script
- **[@typpo](https://github.com/typpo)** – For the excellent [quickchart-python](https://github.com/typpo/quickchart-python) library

---

## 🤷 The Code is Bad?

You're probably right.  
I’m just a biotech student fiddling around—this isn’t meant to be elegant or production-grade. But hey, if it helps you track bad indexers, mission accomplished.

Feel free to open issues, submit PRs, or fork and improve!
