@echo off
setlocal

:: Переходим в папку со скриптом
cd /d "%~dp0"

chcp 65001 > nul
set PYTHONIOENCODING=utf-8
echo =======================================================
echo          Audio Dataset Trimmer (Пакетная обработка)
echo =======================================================

:: Проверяем, был ли передан файл или папка через Drag-and-Drop
if "%~1"=="" (
    echo.
    echo Вы можете просто ПЕРЕТАЩИТЬ папку ^(например, all_rec^) прямо на этот файл run_trimmer.bat!
    echo.
    set /p "TARGET_PATH=Или введите/вставьте путь к папке с аудиофайлами прямо сейчас: "
) else (
    :: Берем путь из аргумента ^(Drag-and-Drop^)
    set "TARGET_PATH=%~1"
)

:: Убираем лишние кавычки, если пользователь их случайно вставил
set "TARGET_PATH=%TARGET_PATH:"=%"

if "%TARGET_PATH%"=="" (
    echo Ошибка: Путь не указан.
    pause
    exit /b
)

echo.
echo Запуск обработки для: "%TARGET_PATH%"
echo Пожалуйста, подождите...
echo.

.\venv\Scripts\python.exe standalone_trimmer.py "%TARGET_PATH%"

echo.
echo Обработка завершена!
pause
