import sounddevice as sd
import numpy as np
import time
from audio_engine import AudioEngine
from post_processor import process_audio
import os

def test_microphone_compatibility(test_freq=10000):
    print(f"=== Проверка совместимости микрофона (Тест частоты {test_freq} Гц) ===")
    print("Суть теста: Убедиться, что ваш микрофон способен записать звук такой высоты.")
    print("Некоторые дешевые или Bluetooth микрофоны имеют низкую частоту дискретизации и физически не могут услышать этот звук.")
    print("-" * 50)
    
    engine = AudioEngine()
    test_file = "test_data/mic_test_recording.wav"
    os.makedirs("test_data", exist_ok=True)
    
    print("1. Начинаю фоновую запись...")
    engine.start_recording(test_file)
    time.sleep(1)
    
    print("2. Проигрываю тестовый сигнал...")
    engine.play_hf_tone(frequency=test_freq, duration=1.0)
    
    # Ждем пока звук проиграется и запишется
    time.sleep(2)
    
    print("3. Останавливаю запись и анализирую...")
    engine.stop_recording()
    
    # Пытаемся найти тон в записанном файле
    dummy_out = "test_data/mic_test_processed.wav"
    success, msg = process_audio(test_file, dummy_out, target_freq=test_freq)
    
    if success and "Trimmed 0 samples" not in msg:
        print("\n✅ УСПЕХ! Ваш микрофон отлично улавливает этот высокочастотный сигнал.")
        print(f"Детали: {msg}")
    else:
        print("\n❌ ОШИБКА! Микрофон НЕ СМОГ уловить сигнал.")
        print("Причины:")
        print("1. Звук колонок слишком тихий, микрофон его не услышал.")
        print("2. Это Bluetooth микрофон с частотой дискретизации 8-16 кГц, который физически обрезает высокие частоты.")
        print("Решение: В файлах audio_engine.py и post_processor.py попробуйте снизить частоту (frequency) до 7500 или 5000.")

if __name__ == "__main__":
    test_microphone_compatibility()
