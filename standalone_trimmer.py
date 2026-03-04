import sys
import os
import glob
import tempfile
import subprocess
from post_processor import process_audio

def convert_m4a_to_wav(m4a_path, wav_path):
    # Try pydub first
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(m4a_path, format="m4a")
        audio.export(wav_path, format="wav")
        return True
    except ImportError:
        # Fallback to ffmpeg
        try:
            subprocess.run(["ffmpeg", "-y", "-i", m4a_path, "-acodec", "pcm_s16le", wav_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Ошибка конвертации m4a: Установите pydub (pip install pydub) или ffmpeg. Ошибка: {e}")
            return False


def process_path(path):
    # Если это папка, ищем все wav и m4a файлы внутри
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, "**", "*.wav"), recursive=True)
        files.extend(glob.glob(os.path.join(path, "**", "*.m4a"), recursive=True))
        files = [f for f in files if not f.endswith("_processed.wav")]
        if not files:
            print(f"В папке '{path}' не найдено файлов .wav или .m4a для обработки.")
            return
        
        print(f"Найдено {len(files)} файлов. Начинаю пакетную обработку...")
        for file in files:
            trim_single_file(file)
            
    # Если это конкретный файл
    elif os.path.isfile(path) and (path.lower().endswith('.wav') or path.lower().endswith('.m4a')):
        trim_single_file(path)
    else:
        print(f"Ошибка: Путь '{path}' не является ни папкой, ни .wav/.m4a файлом.")

def trim_single_file(input_file):
    base_ext = os.path.splitext(input_file)[1].lower()
    output_file = input_file.replace(base_ext, "_processed.wav", 1)
    if output_file == input_file:
        output_file = input_file + "_processed.wav"
        
    print(f"Обработка: {os.path.basename(input_file)}...", end=" ")
    
    source_wav = input_file
    m4a_temp = False
    
    if base_ext == ".m4a":
        fd, source_wav = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        if not convert_m4a_to_wav(input_file, source_wav):
            if os.path.exists(source_wav):
                os.remove(source_wav)
            print("Ошибка конвертации m4a!")
            return
        m4a_temp = True

    success, msg = process_audio(source_wav, output_file)
    
    # Удаляем временный wav-файл, если он был создан
    if m4a_temp and os.path.exists(source_wav):
        os.remove(source_wav)
        
    if success:
        print("Готово!")
        print(f"  -> {msg}")
    else:
        print("Ошибка!")
        print(f"  -> {msg}")

if __name__ == "__main__":
    print("=== Standalone Audio Trimmer ===")
    print("Этот скрипт отсекает от начала аудиодорожки кусок до высокочастотного сигнала (10 кГц).")
    print("Он также конвертирует файл в формат Mono, 16000 Hz.")
    print("-" * 50)
    
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
        process_path(target_path)
    else:
        target_path = input("Введите путь к аудиофайлу (.wav/.m4a) или папке с аудиофайлами: ").strip()
        # Удаляем кавычки, если пользователь вставил путь с ними
        target_path = target_path.strip('"\'')
        if target_path:
            process_path(target_path)
        else:
            print("Путь не указан. Завершение работы.")
