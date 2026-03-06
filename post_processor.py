import numpy as np
import soundfile as sf
import scipy.signal as signal
from math import gcd

def process_audio(input_file, output_file, target_freq=7500, target_sr=16000):
    """
    Processes an audio file:
    1. Loads the audio.
    2. Converts to mono if needed.
    3. Finds the point where the target_freq starts.
    4. Trims the audio from that point.
    5. Resamples to target_sr and saves.
    """
    try:
        # Load audio
        data, sr = sf.read(input_file)
        
        # 1. To mono
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
            
        # 2. Find the tone
        # Design a narrow bandpass filter around target_freq
        nyq = 0.5 * sr
        low = max(0.01, (target_freq - 500) / nyq)
        high = min(0.99, (target_freq + 500) / nyq)
        
        # Check if bounds are valid
        start_idx = 0
        if low < high:
            b, a = signal.butter(5, [low, high], btype='band')
            filtered = signal.filtfilt(b, a, data)
            
            # Simple envelope detection with moving average over 10ms
            window_shape = int(sr * 0.01)
            if window_shape > 0:
                env = np.convolve(np.abs(filtered), np.ones(window_shape)/window_shape, mode='same')
                # Threshold to detect the tone (10% of the max expected envelope if it's prominent)
                max_amp = np.max(env)
                
                # If the max isn't significant it might just be noise
                if max_amp > 0.0001: 
                    threshold = max_amp * 0.1
                    # np.argmax returns the first index where condition is True
                    detected_idx = np.argmax(env > threshold)
                    if detected_idx > 0 or env[0] > threshold:
                        start_idx = detected_idx
                    
        if start_idx == 0 and not (env[0] > threshold if 'env' in locals() and 'threshold' in locals() else False):
            print(f"Warning: Tone of {target_freq} Hz not clearly found in {input_file}. Trimming skipped.")
             
        # 3. Trim
        trimmed = data[start_idx:]
        
        # 4. Resample to target_sr
        if sr != target_sr:
            # Finding optimal up/down factors
            g = gcd(target_sr, sr)
            up = target_sr // g
            down = sr // g
            resampled = signal.resample_poly(trimmed, up, down)
        else:
            resampled = trimmed
            
        # Save as PCM 16-bit
        sf.write(output_file, resampled, target_sr, subtype='PCM_16')
        return True, f"Successfully processed. Trimmed {start_idx} samples ({start_idx/sr:.2f}s). Original SR: {sr} -> {target_sr} Hz."
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    # Test script usage directly if needed
    import sys
    if len(sys.argv) > 2:
        ans, msg = process_audio(sys.argv[1], sys.argv[2])
        print(msg)
    else:
        print("Usage: python post_processor.py <input.wav> <output.wav>")
