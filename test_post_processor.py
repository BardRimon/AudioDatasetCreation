import numpy as np
import soundfile as sf
import os
from post_processor import process_audio

def run_test():
    sr = 44100
    duration = 3.0
    t = np.linspace(0, duration, int(sr * duration), False)
    
    # Generate background noise (speech like) 
    audio = np.random.normal(0, 0.1, size=len(t))
    
    # Add a 15kHz tone starting at t=1.0s
    tone_start_idx = int(sr * 1.0)
    tone_len = int(sr * 0.5)
    t_tone = np.linspace(0, 0.5, tone_len, False)
    tone = 0.5 * np.sin(15000 * 2 * np.pi * t_tone)
    
    audio[tone_start_idx:tone_start_idx+tone_len] += tone
    
    # Save dummy file
    os.makedirs("test_data", exist_ok=True)
    in_file = "test_data/dummy_in.wav"
    out_file = "test_data/dummy_out.wav"
    sf.write(in_file, audio, sr)
    
    print("Testing post_processor...")
    success, msg = process_audio(in_file, out_file)
    print(msg)
    
    if success:
        out_data, out_sr = sf.read(out_file)
        print(f"Output shape: {out_data.shape}, sr: {out_sr}")
        # Expected duration: originally 3s, trimmed from 1.0s, so ~2s left. 
        # Output SR 16000, length ~ 32000.
        if 31000 < len(out_data) < 33000 and out_sr == 16000:
            print("TEST PASSED!")
        else:
            print("TEST FAILED: length or SR mismatch.")
    
if __name__ == "__main__":
    run_test()
