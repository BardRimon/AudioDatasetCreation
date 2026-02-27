import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import time
import os
import threading
import re
import sounddevice as sd
from audio_engine import AudioEngine

class DatasetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Dataset Creator")
        self.root.geometry("800x600")
        
        self.audio_engine = AudioEngine()
        self.recording = False
        self.start_time = 0
        self.tone_played_time = None
        self.timestamps = []
        self.current_filename = ""
        
        # UI Setup
        self._setup_ui()
        
    def _setup_ui(self):
        # Top frame for text loading
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(top_frame, text="Load Text File", command=self.load_text).pack(side=tk.LEFT)
        self.status_label = tk.Label(top_frame, text="Ready", fg="blue", font=("Arial", 12, "bold"))
        self.status_label.pack(side=tk.RIGHT)
        
        # Meta info frame
        meta_frame = tk.Frame(self.root)
        meta_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(meta_frame, text="Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_name = tk.Entry(meta_frame, width=15)
        self.entry_name.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(meta_frame, text="ID:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_id = tk.Entry(meta_frame, width=15)
        self.entry_id.pack(side=tk.LEFT, padx=(0, 15))
        
        # Middle frame for text display
        mid_frame = tk.Frame(self.root)
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.text_widget = scrolledtext.ScrolledText(mid_frame, wrap=tk.WORD, font=("Arial", 14))
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.text_widget.insert(tk.END, "Please load a text file or type your text here to read during recording...")
        
        # Bottom frame for controls
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 1: Recording controls
        row1 = tk.Frame(bottom_frame)
        row1.pack(fill=tk.X, pady=5)
        
        self.btn_start = tk.Button(row1, text="Start Recording [R]", command=self.start_recording, bg="lightgreen", font=("Arial", 12))
        self.btn_start.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.btn_stop = tk.Button(row1, text="Stop Recording [Enter]", command=self.stop_recording, bg="salmon", font=("Arial", 12), state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Row 2: In-recording actions
        row2 = tk.Frame(bottom_frame)
        row2.pack(fill=tk.X, pady=5)
        
        self.btn_tone = tk.Button(row2, text="Play HF Tone [S]", command=self.play_tone, bg="lightblue", font=("Arial", 12))
        self.btn_tone.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.btn_mark = tk.Button(row2, text="Mark Timestamp [Space]", command=self.mark_timestamp, bg="yellow", font=("Arial", 12), state=tk.DISABLED)
        self.btn_mark.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Keyboard Bindings
        self._setup_bindings()
        
    def _setup_bindings(self):
        def make_handler(btn, func):
            def handler(event):
                # Отключаем горячие клавиши, если фокус на текстовом поле
                if self.root.focus_get() == self.text_widget:
                    return
                # Проверяем, активна ли кнопка
                if str(btn['state']) == 'normal':
                    func()
            return handler
            
        self.root.bind('<r>', make_handler(self.btn_start, self.start_recording))
        self.root.bind('<R>', make_handler(self.btn_start, self.start_recording))
        self.root.bind('<s>', make_handler(self.btn_tone, self.play_tone))
        self.root.bind('<S>', make_handler(self.btn_tone, self.play_tone))
        self.root.bind('<space>', make_handler(self.btn_mark, self.mark_timestamp))
        self.root.bind('<Return>', make_handler(self.btn_stop, self.stop_recording))
        
    def load_text(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{e}")
            
    def start_recording(self):
        if self.recording:
            return
            
        try:
            device_info = sd.query_devices(sd.default.device[0])
            mic_name = device_info.get('name', 'UnknownMic')
        except:
            mic_name = "UnknownMic"
            
        # Clean mic name for filename
        mic_name = re.sub(r'[\\/*?:"<>|]', "", mic_name)
        mic_name = mic_name.replace(" ", "_")
        
        name_val = self.entry_name.get().strip() or "Name"
        id_val = self.entry_id.get().strip() or "ID"
        
        date_str = time.strftime("%Y-%m-%d")
        
        filename = f"case_{date_str}_MIC_{mic_name}_{name_val}_Health_{id_val}.wav"
        self.current_filename = os.path.join("recordings", filename)
        
        try:
            self.audio_engine.start_recording(self.current_filename)
        except Exception as e:
            messagebox.showerror("Error", f"Could not start recording: {e}")
            return
            
        self.recording = True
        self.tone_played_time = None
        self.timestamps = []
        
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_mark.config(state=tk.NORMAL)
        self.status_label.config(text="RECORDING", fg="red")
        
    def stop_recording(self):
        if not self.recording:
            return
            
        self.audio_engine.stop_recording()
        self.recording = False
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_mark.config(state=tk.DISABLED)
        self.status_label.config(text="Ready", fg="blue")
        self.root.update()
        
        # Save timestamps
        json_filename = self.current_filename.replace(".wav", ".json")
        try:
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump({"timestamps_sec": self.timestamps}, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save timestamps:\n{e}")
        
    def play_tone(self):
        self.audio_engine.play_hf_tone()
        if self.tone_played_time is None:
            self.tone_played_time = time.time()
        self._flash_status("Playing Tone")
        
    def mark_timestamp(self):
        if self.recording:
            if self.tone_played_time is None:
                messagebox.showwarning("Внимание", "Сначала проиграйте ВЧ-тон (Button 1), чтобы начать отсчет времени!")
                return
            elapsed = time.time() - self.tone_played_time
            self.timestamps.append(elapsed)
            self._flash_status(f"Marked: {elapsed:.2f}s")
            
    def _flash_status(self, text):
        old_text = self.status_label.cget("text")
        old_fg = self.status_label.cget("fg")
        self.status_label.config(text=text, fg="purple")
        self.root.after(1000, lambda: self.status_label.config(text=old_text, fg=old_fg) if not self.recording else self.status_label.config(text="RECORDING", fg="red"))

if __name__ == "__main__":
    if not os.path.exists("recordings"):
        os.makedirs("recordings")
    root = tk.Tk()
    app = DatasetApp(root)
    root.mainloop()
