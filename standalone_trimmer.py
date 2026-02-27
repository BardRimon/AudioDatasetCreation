import sys
import os
import glob
from post_processor import process_audio

def process_path(path):
    # Если это папка, ищем все wav файлы внутри (в том числе во вложенных папках)
    if os.path.isdir(path):
        # Ищем wav файлы рекурсивно и не рекурсивно
        files = glob.glob(os.path.join(path, "**", "*.wav"), recursive=True)
        files = [f for f in files if not f.endswith("_processed.wav")]
        if not files:
            print(f"В папке '{path}' не найдено .wav файлов для обработки.")
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
    output_file = input_file.replace(".wav", "_processed.wav")
    if output_file == input_file:
        output_file = input_file + "_processed.wav"
        
    print(f"Обработка: {os.path.basename(input_file)}...", end=" ")
    success, msg = process_audio(input_file, output_file)
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
        target_path = input("Введите путь к аудиофайлу (.wav) или папке с аудиофайлами: ").strip()
        # Удаляем кавычки, если пользователь вставил путь с ними
        target_path = target_path.strip('"\'')
        if target_path:
            process_path(target_path)
        else:
            print("Путь не указан. Завершение работы.")
