# Star Citizen Anti-AFK Tool

**Repository:** [https://github.com/chiccamew/star-citizen-no-afk](https://github.com/chiccamew/star-citizen-no-afk)

A lightweight, external Python GUI application designed to prevent being kicked for inactivity (AFK) in *Star Citizen*. It uses specialized input simulation to interface correctly with DirectX-based games.

## 🛡️ How it Works & Safety

Many standard macro recorders or Python scripts (like those using `pyautogui`) fail in games like *Star Citizen* because the game utilizes DirectX (DirectInput) for controls. Standard software interrupts are often ignored by the game engine.

**This tool is different because:**

1. **DirectX Input:** It uses `pydirectinput` to simulate hardware-level scan codes. This mimics a physical keyboard press at the driver level, ensuring the game registers the movement.
2. **External Only:** This tool **does not** read game memory, inject code, or hook into the `StarCitizen.exe` process. It operates strictly as an external input source.
3. **Human-like Behavior:** The script includes customizable intervals and small delays between key presses to simulate human timing rather than instantaneous machine inputs.

> **Disclaimer:** While this tool is designed to be safe by acting only as an external keyboard, always use automation tools at your own risk regarding the game's Terms of Service.

## 🚀 Prerequisites

* **Operating System:** Windows 10 or 11 (Required for DirectX input libraries).
* **Python:** Version 3.8 or higher. [Download Python](https://www.python.org/downloads/).

## 💻 Running Locally (Development)

Follow these instructions to run the Python script directly on your machine using a virtual environment (venv) to keep your system clean.

### 1. Clone the Repository

Open your terminal (Command Prompt or PowerShell) and run:

```bash
git clone https://github.com/chiccamew/star-citizen-no-afk.git
cd star-citizen-no-afk

```

### 2. Create a Virtual Environment

This creates an isolated folder (`venv`) to hold the project dependencies.

```bash
python -m venv venv

```

### 3. Activate the Environment

* **Command Prompt (cmd):**
```bash
venv\Scripts\activate.bat

```


* **PowerShell:**
```powershell
venv\Scripts\Activate.ps1

```



*(You will see `(venv)` appear at the start of your command line).*

### 4. Install Dependencies

Install the required libraries (`pydirectinput`, `keyboard`, and `pyinstaller` for building).

```bash
pip install pydirectinput keyboard pyinstaller

```

### 5. Run the Application

You must run the script as **Administrator** because the `keyboard` library requires elevated privileges to listen for global hotkeys (like F6) and send inputs to games running in Admin mode.

```bash
python star_citizen_no_afk.py

```

---

## 📦 Building the Executable (.exe)

To share this tool with friends or run it without Python installed, you can build a standalone Windows executable using the included `.spec` file.

### 1. Prepare the Build

Ensure your virtual environment is active and dependencies are installed (see steps above).

### 2. Verify the Spec File

Ensure the file `StarCitizenNoAFK.spec` points to the correct script name. If your script is named `star_citizen_no_afk.py`, open the `.spec` file and ensure the `Analysis` block looks like this:

```python
a = Analysis(
    ['star_citizen_no_afk.py'], # Make sure this matches your python filename
    ...
)

```

### 3. Run PyInstaller

Execute the following command to build the EXE based on the configuration in the spec file:

```bash
pyinstaller StarCitizenNoAFK.spec

```

### 4. Locate the App

Once the build completes, your standalone application will be located in the `dist` folder:

* `dist\StarCitizenAFK.exe`

You can now move this `.exe` anywhere on your computer (or a friend's computer) and run it. **Note:** You must run the `.exe` as Administrator for the hotkeys to work inside Star Citizen.

---

## 🎮 How to Use

1. **Launch the App** (as Administrator).
2. **Configure Keys:** Enter the sequence of keys you want to simulate (e.g., `w, s, space`).
3. **Set Interval:** Choose how many seconds the tool waits before repeating the sequence.
4. **Set Hotkey:** Choose a key to toggle the tool on/off (Default: `F6`). click "Update Hotkey Listener".
5. **Focus the Game:** Tab back into Star Citizen.
6. **Activate:** Press your hotkey (`F6`). The status will change to **RUNNING**, and your character will perform the movements to stay active.