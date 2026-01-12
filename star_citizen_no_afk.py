import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pydirectinput
import keyboard

class AFKToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Star Citizen Anti-AFK Tool")
        self.root.geometry("400x450")
        self.root.resizable(False, False)

        # State variables
        self.is_running = False
        self.stop_event = threading.Event()
        self.thread = None
        self.hotkey_hook = None

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

        # Input: Hotkey
        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.pack(fill=tk.X, pady=5)
        ttk.Label(hotkey_frame, text="Start/Stop Hotkey:").pack(anchor=tk.W)
        self.hotkey_var = tk.StringVar(value="f6")
        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var)
        self.hotkey_entry.pack(fill=tk.X, pady=(2, 0))
        
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
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.log_text = tk.Text(log_frame, height=6, width=40, font=("Consolas", 9), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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
        if self.is_running:
            self.stop_loop()
        else:
            self.start_loop()

    def start_loop(self):
        """Starts the background thread"""
        if self.is_running:
            return

        try:
            # Validate inputs
            keys = [k.strip() for k in self.keys_var.get().split(',') if k.strip()]
            interval = float(self.interval_var.get())
            if not keys:
                raise ValueError("No keys specified")
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
        
        self.log("Started anti-AFK sequence.")

        # Start Thread
        self.thread = threading.Thread(target=self.run_afk_logic, args=(keys, interval))
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
        
        self.log("Stopped.")

    def run_afk_logic(self, keys, interval):
        """The actual logic running in the background"""
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

if __name__ == "__main__":
    root = tk.Tk()
    app = AFKToolApp(root)
    # Ensure hotkeys are cleaned up on exit
    root.protocol("WM_DELETE_WINDOW", lambda: (keyboard.unhook_all(), root.destroy()))
    root.mainloop()