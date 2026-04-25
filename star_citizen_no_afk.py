import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import ctypes
import pydirectinput
import keyboard

class AFKToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Star Citizen Anti-AFK Tool")
        self.root.geometry("420x890")
        self.root.resizable(False, True)

        # State variables
        self.is_running = False
        self.stop_event = threading.Event()
        self.thread = None
        self.hotkey_hook = None

        # String typer state
        self.strings_running = False
        self.strings_stop_event = threading.Event()
        self.strings_thread = None

        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))

        # --- UI Layout ---

        # Main Container
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="AFK Preventer", font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Input: Keys
        keys_frame = ttk.Frame(main_frame)
        keys_frame.pack(fill=tk.X, pady=5)
        ttk.Label(keys_frame, text="Key Sequence (comma sep):").pack(anchor=tk.W)
        self.keys_var = tk.StringVar(value="w, w, w, w, w, s, s, s, s, s, s, space")
        self.keys_entry = ttk.Entry(keys_frame, textvariable=self.keys_var)
        self.keys_entry.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(keys_frame, text="Example: w, a, s, d, space", font=("Segoe UI", 8), foreground="gray").pack(anchor=tk.W)

        # Input: Interval
        interval_frame = ttk.Frame(main_frame)
        interval_frame.pack(fill=tk.X, pady=5)
        ttk.Label(interval_frame, text="Interval (seconds):").pack(anchor=tk.W)
        self.interval_var = tk.DoubleVar(value=2.0) # Default 2 seconds
        self.interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var)
        self.interval_entry.pack(fill=tk.X, pady=(2, 0))

        # Input: Start Delay
        start_delay_frame = ttk.Frame(main_frame)
        start_delay_frame.pack(fill=tk.X, pady=5)
        ttk.Label(start_delay_frame, text="Start delay (seconds):").pack(anchor=tk.W)
        self.start_delay_var = tk.StringVar(value="3")
        self.start_delay_entry = ttk.Entry(start_delay_frame, textvariable=self.start_delay_var)
        self.start_delay_entry.pack(fill=tk.X, pady=(2, 0))

        # Input: Hotkey
        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.pack(fill=tk.X, pady=5)
        ttk.Label(hotkey_frame, text="Start/Stop Hotkey:").pack(anchor=tk.W)
        self.hotkey_var = tk.StringVar(value="f6")
        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var)
        self.hotkey_entry.pack(fill=tk.X, pady=(2, 0))
        
        # Hotkey target radio buttons
        self.hotkey_target_var = tk.StringVar(value="afk")
        radio_row = ttk.Frame(hotkey_frame)
        radio_row.pack(fill=tk.X, pady=(4, 0))
        ttk.Radiobutton(radio_row, text="AFK Preventer", variable=self.hotkey_target_var, value="afk").pack(side=tk.LEFT)
        ttk.Radiobutton(radio_row, text="String Typer", variable=self.hotkey_target_var, value="strings").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(radio_row, text="Both", variable=self.hotkey_target_var, value="both").pack(side=tk.LEFT, padx=(10, 0))

        # Apply Hotkey Button
        self.apply_btn = ttk.Button(hotkey_frame, text="Update Hotkey Listener", command=self.update_hotkey)
        self.apply_btn.pack(fill=tk.X, pady=(5, 0))

        # Status Indicator
        self.status_label = tk.Label(main_frame, text="STATUS: IDLE", font=("Segoe UI", 12, "bold"), fg="#d9534f", bg="#f0f0f0", pady=10)
        self.status_label.pack(fill=tk.X, pady=20)

        # Manual Controls
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        self.start_btn = ttk.Button(btn_frame, text="Start (Manual)", command=self.start_loop)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.stop_btn = ttk.Button(btn_frame, text="Stop (Manual)", command=self.stop_loop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        # Logs
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log")
        log_frame.pack(fill=tk.X, pady=(10, 0))
        self.log_text = tk.Text(log_frame, height=2, width=40, font=("Consolas", 9), state=tk.DISABLED)
        self.log_text.pack(fill=tk.X, padx=5, pady=5)

        # --- String Typer Section ---
        str_frame = ttk.LabelFrame(main_frame, text="String Typer")
        str_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Label(str_frame, text='Format: string | delay_ms    Use "[enter]" to press Enter', font=("Segoe UI", 8), foreground="gray").pack(anchor=tk.W, padx=5, pady=(4, 0))

        self.strings_text = tk.Text(str_frame, height=5, width=45, font=("Consolas", 9))
        self.strings_text.pack(fill=tk.X, padx=5, pady=(2, 5))
        self.strings_text.insert(tk.END, "/work | 500\n[enter] | 3000\n/deposit | 500\n[enter] | 3000\n/collect-income | 500\n[enter] | 0")

        self.strings_auto_enter_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(str_frame, text="Auto-press Enter after each string", variable=self.strings_auto_enter_var).pack(anchor=tk.W, padx=5)

        str_interval_row = ttk.Frame(str_frame)
        str_interval_row.pack(fill=tk.X, padx=5, pady=4)
        ttk.Label(str_interval_row, text="Interval (minutes):").pack(side=tk.LEFT)
        self.strings_interval_var = tk.StringVar(value="16")
        self.strings_interval_entry = ttk.Entry(str_interval_row, textvariable=self.strings_interval_var, width=8)
        self.strings_interval_entry.pack(side=tk.LEFT, padx=(5, 0))

        str_delay_row = ttk.Frame(str_frame)
        str_delay_row.pack(fill=tk.X, padx=5, pady=(0, 4))
        ttk.Label(str_delay_row, text="Start delay (seconds):").pack(side=tk.LEFT)
        self.strings_start_delay_var = tk.StringVar(value="5")
        self.strings_start_delay_entry = ttk.Entry(str_delay_row, textvariable=self.strings_start_delay_var, width=8)
        self.strings_start_delay_entry.pack(side=tk.LEFT, padx=(5, 0))

        self.strings_status_label = tk.Label(str_frame, text="IDLE", font=("Segoe UI", 10, "bold"), fg="#d9534f", bg="#f0f0f0")
        self.strings_status_label.pack(pady=2)

        str_btn_frame = ttk.Frame(str_frame)
        str_btn_frame.pack(fill=tk.X, padx=5, pady=(0, 6))
        self.strings_start_btn = ttk.Button(str_btn_frame, text="Start", command=self.start_string_loop)
        self.strings_start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.strings_stop_btn = ttk.Button(str_btn_frame, text="Stop", command=self.stop_string_loop, state=tk.DISABLED)
        self.strings_stop_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        # Initialize hotkey
        self.update_hotkey()

    def log(self, message):
        """Thread-safe logging to the text box"""
        def _log():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"> {message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _log)

    def update_hotkey(self):
        """Updates the global hotkey listener"""
        hk = self.hotkey_var.get().strip()
        
        try:
            # Remove old hotkey if it exists
            if self.hotkey_hook:
                try:
                    keyboard.remove_hotkey(self.hotkey_hook)
                except:
                    pass
            
            # Add new hotkey
            self.hotkey_hook = keyboard.add_hotkey(hk, self.toggle_running)
            self.log(f"Hotkey set to: {hk}")
        except Exception as e:
            messagebox.showerror("Hotkey Error", f"Invalid hotkey: {e}")

    def toggle_running(self):
        """Toggles the state called by hotkey"""
        target = self.hotkey_target_var.get()
        if target == "afk":
            self.stop_loop() if self.is_running else self.start_loop()
        elif target == "strings":
            self.stop_string_loop() if self.strings_running else self.start_string_loop()
        else:  # both
            if self.is_running or self.strings_running:
                self.stop_loop()
                self.stop_string_loop()
            else:
                self.start_loop()
                self.start_string_loop()

    def start_loop(self):
        """Starts the background thread"""
        if self.is_running:
            return

        try:
            # Validate inputs
            keys = [k.strip() for k in self.keys_var.get().split(',') if k.strip()]
            interval = float(self.interval_var.get())
            start_delay = float(self.start_delay_var.get())
            if not keys:
                raise ValueError("No keys specified")
            if start_delay < 0:
                raise ValueError("Start delay cannot be negative")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        self.is_running = True
        self.stop_event.clear()

        # UI Updates
        self.status_label.config(text="STATUS: RUNNING", fg="#5cb85c")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.keys_entry.config(state=tk.DISABLED)
        self.interval_entry.config(state=tk.DISABLED)
        self.start_delay_entry.config(state=tk.DISABLED)

        self.log("Started anti-AFK sequence.")

        # Start Thread
        self.thread = threading.Thread(target=self.run_afk_logic, args=(keys, interval, start_delay))
        self.thread.daemon = True
        self.thread.start()

    def stop_loop(self):
        """Stops the background thread"""
        if not self.is_running:
            return

        self.is_running = False
        self.stop_event.set()

        # UI Updates
        self.root.after(0, lambda: self.status_label.config(text="STATUS: IDLE", fg="#d9534f"))
        self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.keys_entry.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.interval_entry.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.start_delay_entry.config(state=tk.NORMAL))

        self.log("Stopped.")

    def run_afk_logic(self, keys, interval, start_delay):
        """The actual logic running in the background"""
        elapsed = 0
        while elapsed < start_delay and not self.stop_event.is_set():
            time.sleep(0.1)
            elapsed += 0.1
        while not self.stop_event.is_set():
            for key in keys:
                if self.stop_event.is_set():
                    break
                
                self.log(f"Pressing: {key}")
                # pydirectinput is crucial for games like Star Citizen
                pydirectinput.press(key)
                
                # Small delay between keys in a sequence so the game registers them
                time.sleep(0.5)

            # Wait for the interval, checking for stop signal frequently
            elapsed = 0
            while elapsed < interval and not self.stop_event.is_set():
                time.sleep(0.1)
                elapsed += 0.1

    def start_string_loop(self):
        if self.strings_running:
            return

        raw_lines = self.strings_text.get("1.0", tk.END).splitlines()
        entries = []
        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                text_part, delay_part = line.split("|", 1)
                text_part = text_part.strip()
                try:
                    delay_ms = int(delay_part.strip())
                except ValueError:
                    delay_ms = 0
            else:
                text_part = line
                delay_ms = 0
            entries.append((text_part, delay_ms))

        if not entries:
            messagebox.showerror("Input Error", "No strings specified.")
            return

        try:
            interval_min = float(self.strings_interval_var.get())
            if interval_min <= 0:
                raise ValueError("Interval must be a positive number.")
            strings_start_delay = float(self.strings_start_delay_var.get())
            if strings_start_delay < 0:
                raise ValueError("Start delay cannot be negative.")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        self.strings_running = True
        self.strings_stop_event.clear()
        self.strings_text.config(state=tk.DISABLED)
        self.strings_interval_entry.config(state=tk.DISABLED)
        self.strings_start_delay_entry.config(state=tk.DISABLED)
        self.strings_start_btn.config(state=tk.DISABLED)
        self.strings_stop_btn.config(state=tk.NORMAL)
        self.strings_status_label.config(text="RUNNING", fg="#5cb85c")
        ctypes.windll.kernel32.SetThreadExecutionState(
            0x80000000 | 0x00000001 | 0x00000002  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )

        auto_enter = self.strings_auto_enter_var.get()
        self.strings_thread = threading.Thread(
            target=self.run_string_logic, args=(entries, interval_min, auto_enter, strings_start_delay)
        )
        self.strings_thread.daemon = True
        self.strings_thread.start()

    def stop_string_loop(self):
        if not self.strings_running:
            return
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)  # ES_CONTINUOUS — clears the request
        self.strings_running = False
        self.strings_stop_event.set()
        self.root.after(0, lambda: self.strings_text.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.strings_interval_entry.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.strings_start_delay_entry.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.strings_start_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.strings_stop_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.strings_status_label.config(text="IDLE", fg="#d9534f"))
        self.log("String typer stopped.")

    def run_string_logic(self, entries, interval_min, auto_enter, start_delay):
        elapsed = 0
        while elapsed < start_delay and not self.strings_stop_event.is_set():
            time.sleep(0.1)
            elapsed += 0.1
        self.log("String typer started.")
        while not self.strings_stop_event.is_set():
            for text, delay_ms in entries:
                if self.strings_stop_event.is_set():
                    break
                if text == "[enter]":
                    pydirectinput.press("enter")
                    self.log("Pressed: Enter")
                else:
                    pydirectinput.typewrite(text, interval=0.05)
                    self.log(f"Typed: {text}")
                    if auto_enter:
                        pydirectinput.press("enter")
                elapsed = 0
                target = delay_ms / 1000.0
                while elapsed < target and not self.strings_stop_event.is_set():
                    time.sleep(0.1)
                    elapsed += 0.1

            total_seconds = interval_min * 60
            elapsed = 0
            while elapsed < total_seconds and not self.strings_stop_event.is_set():
                time.sleep(0.1)
                elapsed += 0.1

if __name__ == "__main__":
    root = tk.Tk()
    app = AFKToolApp(root)
    # Ensure hotkeys are cleaned up on exit
    root.protocol("WM_DELETE_WINDOW", lambda: (keyboard.unhook_all(), root.destroy()))
    root.mainloop()