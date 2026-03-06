import sys
import os
import glob
import tempfile
import subprocess
from post_processor import process_audio

def convert_to_mono_original_sr_wav(input_path, output_path):
    # Try pydub first
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(input_path, format="wav")
        # We only set channels to 1. We keep original frame rate to not lose high frequencies
        audio = audio.set_channels(1)
        audio.export(output_path, format="wav")
        return True
    except Exception as e_pydub:
        # Fallback to ffmpeg
        try:
            subprocess.run(["ffmpeg", "-y", "-i", input_path, "-acodec", "pcm_s16le", "-ac", "1", output_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e_ffmpeg:
            print(f"\nОшибка конвертации файла {os.path.basename(input_path)}:")
            print(f"  -> Неизвестная ошибка Pydub: {e_pydub}")
            return False


def process_path(path):
    # Если это папка, ищем все wav файлы внутри
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, "**", "*.wav"), recursive=True)
        files = [f for f in files if not f.endswith("_processed.wav")]
        if not files:
            print(f"В папке '{path}' не найдено файлов .wav для обработки.")
            return
        
        print(f"Найдено {len(files)} файлов. Начинаю пакетную обработку...")
        for file in files:
            trim_single_file(file)
            
    # Если это конкретный файл
    elif os.path.isfile(path) and path.lower().endswith('.wav'):
        trim_single_file(path)
    else:
        print(f"Ошибка: Путь '{path}' не является ни папкой, ни .wav файлом.")

def trim_single_file(input_file):
    base_ext = os.path.splitext(input_file)[1].lower()
    output_file = input_file.replace(base_ext, "_processed.wav", 1)
    if output_file == input_file:
        output_file = input_file + "_processed.wav"
        
    print(f"Обработка: {os.path.basename(input_file)}...", end=" ")
    
    # Сначала конвертируем во временный Mono WAV (без смены герцовки), независимо от исходного формата
    fd, source_wav = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    
    if not convert_to_mono_original_sr_wav(input_file, source_wav):
        if os.path.exists(source_wav):
            os.remove(source_wav)
        print("Ошибка конвертации файла в Mono WAV!")
        return

    success, msg = process_audio(source_wav, output_file)
    
    # Удаляем временный wav-файл
    if os.path.exists(source_wav):
        os.remove(source_wav)
        
    if success:
        print("Готово!")
        print(f"  -> {msg}")
    else:
        print("Ошибка!")
        print(f"  -> {msg}")

if __name__ == "__main__":
    print("=== Standalone Audio Trimmer ===")
    print("Этот скрипт отсекает от начала аудиодорожки кусок до высокочастотного сигнала (7.5 кГц).")
    print("Он также конвертирует файл в формат Mono, 16000 Hz.")
    print("-" * 50)
    
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
        process_path(target_path)
    else:
        target_path = input("Введите путь к аудиофайлу (.wav) или папке с аудиофайлами: ").strip()
        # Удаляем кавычки, если пользователь вставил путь с ними
        target_path = target_path.strip('"\'')
        if target_path:
            process_path(target_path)
        else:
            print("Путь не указан. Завершение работы.")
