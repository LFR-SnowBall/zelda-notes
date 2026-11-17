# 🗡️ Zelda Notes — Purah Pad Companion OS

[![Release](https://img.shields.io/github/v/release/LFR-SnowBall/zelda-notes?color=00e5ff&style=for-the-badge)](https://github.com/LFR-SnowBall/zelda-notes/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Steam%20Deck-7928CA?style=for-the-badge)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-success?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)]()

**Real-time interactive multi-level map, live RAM telemetry beacon, and exploration companion for the PC native port of *The Legend of Zelda: Ocarina of Time* (`NX2navi` / `ocarina.exe`).**

Inspired by the Sheikah Purah Pad and high-fidelity cartographic atlases, running **100% locally, lightweight, and zero-install** without external package managers (`pip`) or invasive background drivers.

---

## ⚡ Quick Download & Start (Zero-Install)

No development tools, Python installations, or environment variables are required. Everything is self-contained.

[<img src="https://img.shields.io/badge/DOWNLOAD-ZeldaNotes--v1.0.0--windows.zip%20(12%20MB)-00e5ff?style=for-the-badge&logo=windows&logoColor=000000" alt="Download Standalone Zip" height="42">](https://github.com/LFR-SnowBall/zelda-notes/releases/download/v1.0.0/ZeldaNotes-v1.0.0-windows.zip)

### How to Run:
1. **Download & Extract:**
   - Grab the pre-built [**ZeldaNotes-v1.0.0-windows.zip**](https://github.com/LFR-SnowBall/zelda-notes/releases/download/v1.0.0/ZeldaNotes-v1.0.0-windows.zip) from [Releases](https://github.com/LFR-SnowBall/zelda-notes/releases).
   - Extract it to any folder of your choice.
2. **Launch:**
   - **On Windows (Recommended):** Double-click **`ZeldaNotes.exe`**.
     - Launches as an independent desktop app window (GPU-accelerated, borderless Sheikah frame, system tray integration, and zero black terminal windows).
     - *(Alternative)*: You can also double-click `start-zelda-notes.bat`.
   - **On Linux / Steam Deck:**
     ```bash
     python3 server.py
     ```
3. **Enjoy:**
   - **Main Purah Pad Dashboard:** [http://localhost:8080](http://localhost:8080)
   - **Popout Radar / Second Monitor:** [http://localhost:8080/popout](http://localhost:8080/popout)
   - **Mobile / Tablet (Same Wi-Fi):** Click the **`[ 📱 Mobile ]`** button in the header or scan the instant on-screen QR code from your smartphone.

---

## 🧭 Key Features & Exploration Design

### 👑 Age-Adaptive Anti-Spoiler Engine (Child Link vs Adult Link)
- **Live Era Context Detection:** Reads whether you are currently playing as Child Link or Adult Link from save telemetry (`caption.sav` / `progress.sav`).
- **Temporal Collectible Filtering:** If playing as Child Link, the map and checklist **ONLY display pins and secrets reachable as a child**, hiding endgame items that require adult equipment (such as Hookshot or Megaton Hammer) to prevent spoilers and wasted exploration.
- **Dynamic Era Floor Switching:** Automatically swaps regional layouts when switching eras (e.g., liquid Zora's Fountain vs frozen winter ice, Kakariko Village, and Castle Town).
- **Manual Era Override:** Toggle between `[ 🧒 Child Only ]`, `[ 🗡️ Adult Only ]`, or `[ 🌐 View Both ]` at any time with active in-game indicator badges.

### ⚡ 10 Hz Live RAM Telemetry Tracking (20 µs Latency)
- **Real-Time GPS Player Beacon:** Direct memory reading from `ocarina.exe` using native Win32 `ReadProcessMemory`.
- **Instant 3D Dungeon Detection:** Instantly detects when entering a dungeon or interior room by 3D actor coordinates without waiting for a save file write.
- **Continuous Elevation-Based Floor Snapping:** Dynamically switches between floor maps (`1F`, `2F`, `B1`, etc.) based on Link's vertical $Y$ altitude in memory.
- **Smooth Visual Sliding:** Link's directional Sheikah beacon glides fluidly across vector maps with CSS transforms at 60 FPS.

### 🗺️ High-Fidelity Multi-Level Vector Maps (SVG)
- **32 Hand-Curated Dungeon & Zone Blueprints:** Extracted and decompressed directly from the official game scene files (`.bcett.byml.zs`) with affine projection matrix calibration (`map_transforms.json`).
- **Fluid Infinite Zoom & Panning:** Smooth scaling from `0.6x` to `4.0x` (400%) using mouse wheel, on-screen controls, or touchscreen pinch gestures. Being pure SVG vectors, blueprints remain tack-sharp at any zoom level.
- **Multi-Monitor Popout Mode:** Open [http://localhost:8080/popout](http://localhost:8080/popout) on a second screen or tablet with bidirectional real-time synchronization.

### 📱 Smartphone & Tablet Second-Screen (Auto LAN IP + QR Code)
- Tap the **`[ 📱 Mobile ]`** button in the header to open a connection modal:
  - Generates an on-screen **QR code** for instant scanning with your phone's camera.
  - Displays your PC's local Wi-Fi IP address with one-click **Copy URL** buttons.
  - Supports both the full Purah Pad companion and the dedicated mini-radar popout view.

### 📦 100% Self-Contained Canonical Database
- **184 Official Collectibles Mapped:**
  - **100 Gold Skulltulas** (with era, night-time conditions, and required equipment tags).
  - **36 Pieces of Heart** (for all 9 additional Heart Containers).
  - **48 Great Fairies, Songs, and Key Upgrades.**
- **Interactive Checklists with Gossip Stone Hints:** Reveal subtle Sheikah riddle hints only when requested.
- **Automatic Save Detection:** Automatically discovers default save paths for `NX2navi` at:
  `%LOCALAPPDATA%\Programs\NX2navi\game\profile\save`
  *(Custom save folders can also be configured directly from the web UI via the `[ ⚙️ Save File ]` button).*

---

## 🛠️ Tech Stack & Architecture

- **Desktop Launcher:** Native C# Win32 executable (`ZeldaNotes.exe`, 12 KB) compiled with .NET Framework 4.8 `csc.exe`. Includes system tray icon, window management (`--app` Chromium frame), and embedded runtime bootstrapping.
- **Backend Server:** Python 3.11 lightweight HTTP daemon (`server.py`) using strictly standard libraries (`http.server`, `ctypes`, `socket`, `json`, `struct`). Zero `pip` packages required.
- **Frontend OS:** Pure modern JavaScript (ES6+), CSS Grid/Flexbox, Sheikah tech aesthetics, and standalone SVG vector map stages.

---

## 💻 Building from Source

If you prefer to compile or run from source:

```bash
# Clone the repository
git clone https://github.com/LFR-SnowBall/zelda-notes.git
cd zelda-notes

# Compile native launcher (Windows)
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:winexe /r:System.Windows.Forms.dll /r:System.Drawing.dll /r:System.IO.Compression.FileSystem.dll /out:ZeldaNotes.exe ZeldaNotes.cs

# Run server directly
python server.py
```

---

## 📜 Disclaimer & License

This project is an open-source fan-made exploration tool and is not affiliated with, endorsed by, or associated with Nintendo. *The Legend of Zelda* and all associated assets are trademarks and copyright of Nintendo.

Licensed under the **MIT License**.
