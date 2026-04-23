# CLAUDE.md - Star Citizen Anti-AFK AutoClicker

## Project Overview

A lightweight Windows GUI tool that prevents Star Citizen from kicking idle characters by simulating periodic keyboard input. Built with Python/Tkinter, it runs a configurable key sequence on a timer in a background thread. Uses `pydirectinput` for DirectX-level hardware scan codes — required because Star Citizen ignores standard Windows API input simulation.

## Tech Stack

- **Python 3.8+** — single source file (`star_citizen_no_afk.py`)
- **tkinter** — built-in GUI framework
- **pydirectinput** — DirectX hardware-level input simulation
- **keyboard** — global hotkey detection
- **PyInstaller** — builds standalone Windows `.exe`
- **Platform:** Windows only; requires Administrator privileges

## How to Run

**Development:**
```bash
python -m venv venv
venv\Scripts\activate
pip install pydirectinput keyboard pyinstaller
# Run as Administrator:
python star_citizen_no_afk.py
```

**Build executable:**
```bash
pyinstaller StarCitizenNoAFK.spec
# Output: dist\StarCitizenAFK.exe
```

> **Known issue:** `StarCitizenNoAFK.spec` references `star_citizen_afk.py` — update it to `star_citizen_no_afk.py` before rebuilding.

## Key Constraints

- Must run as Administrator (global hotkeys and DirectX input require elevated privileges)
- Use `pydirectinput` for all key simulation — never `pyautogui` or `win32api` (Star Citizen ignores non-DirectX input)
- Keep the app single-file (`star_citizen_no_afk.py`) — no splitting into modules
- All GUI updates from background threads must go through thread-safe mechanisms (tkinter is not thread-safe)
- Windows-only — no cross-platform abstractions needed

## Behavioral Guidelines

**1. Think Before Coding**

Surface assumptions early. This codebase has subtle constraints (DirectX input, thread safety, Admin mode) that aren't obvious. Ask before choosing an input library, changing threading behavior, or modifying the hotkey system. Don't silently substitute alternatives.

**2. Simplicity First**

Implement only what's requested. The tool is intentionally minimal — one file, one class, one purpose. Avoid adding config persistence, plugin systems, profiles, or other speculative features. If a change can be done in fewer lines without losing clarity, prefer the shorter version.

**3. Surgical Changes**

Touch only what the task requires. The GUI layout, threading model, and input simulation are tightly coupled — changing one area can break another. Match existing style (method naming, tkinter widget patterns, thread management). Don't refactor unrelated code while fixing a bug.

**4. Goal-Driven Execution**

Define verifiable success before changing anything. For a UI change: what should the user see? For a behavior change: what key sequence/timing should result? For a build: does the `.exe` run without Python installed? Make the success condition concrete before writing code.
