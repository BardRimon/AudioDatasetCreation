import sounddevice as sd
import numpy as np
import soundfile as sf
import queue
import threading
import sys
import os

class AudioEngine:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.q = queue.Queue()
        self.recording = False
        self.stream = None
        self.file = None
        self.write_thread = None

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def start_recording(self, filename):
        if self.recording:
            return
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        # Use mode 'w' to overwrite if it exists
        self.file = sf.SoundFile(filename, mode='w', samplerate=self.sample_rate, channels=self.channels)
        self.q = queue.Queue()
        self.recording = True
        
        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self.callback)
        self.stream.start()
        
        # Thread to write data to file to prevent io blocking audio callback
        self.write_thread = threading.Thread(target=self._file_writer)
        self.write_thread.start()

    def _file_writer(self):
        while self.recording or not self.q.empty():
            try:
                data = self.q.get(timeout=0.1)
                self.file.write(data)
            except queue.Empty:
                pass

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        if self.write_thread:
            self.write_thread.join()
            self.write_thread = None
        if self.file:
            self.file.close()
            self.file = None

    def play_hf_tone(self, frequency=7500, duration=0.5):
        """Generates and plays a high-frequency sine wave asynchronously."""
        # Using 44100 for playback specifically
        playback_sr = 44100
        t = np.linspace(0, duration, int(playback_sr * duration), False)
        # Generate sine wave
        tone = np.sin(frequency * t * 2 * np.pi)
        
        # Apply slight fade in/out to prevent speakers from popping or clicking
        fade_len = int(playback_sr * 0.01)
        if fade_len > 0 and len(tone) > fade_len * 2:
            fade_in = np.linspace(0, 1, fade_len)
            fade_out = np.linspace(1, 0, fade_len)
            tone[:fade_len] *= fade_in
            tone[-fade_len:] *= fade_out
        
        # Play asynchronously
        sd.play(tone, samplerate=playback_sr)
