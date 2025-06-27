#!/usr/bin/env python3
"""
Скрипт для конкатенации MP3 файлов через ffmpeg
Объединяет файлы в порядке их именования и сохраняет результат
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from tqdm import tqdm

def setup_logging(log_level=logging.INFO):
    """
    Настраивает логирование с временными метками и форматированием.
    :param log_level: Уровень логирования.
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('concatenate_mp3.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def get_mp3_duration(file_path):
    """
    Получает длительность MP3 файла с помощью ffprobe.
    :param file_path: Путь к MP3 файлу.
    :return: Строка с длительностью в формате HH:MM:SS.
    """
    try:
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ], capture_output=True, text=True, check=True)
        
        duration_seconds = float(result.stdout.strip())
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except subprocess.CalledProcessError:
        print(f"Ошибка при получении длительности файла: {file_path}")
        return "00:00:00"

def concatenate_mp3_files(input_dir, output_file, file_pattern="*.mp3", sort_by_name=True, logger=None):
    """
    Конкатенирует MP3 файлы из указанной папки в один файл.
    
    :param input_dir: Папка с MP3 файлами
    :param output_file: Путь к выходному файлу
    :param file_pattern: Паттерн для поиска файлов (по умолчанию *.mp3)
    :param sort_by_name: Сортировать ли файлы по имени
    :param logger: Логгер для записи сообщений
    :return: True если успешно, False в случае ошибки
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    input_path = Path(input_dir)
    output_path = Path(output_file)
    
    # Проверяем существование входной папки
    if not input_path.exists():
        logger.error(f"Входная папка не найдена: {input_path}")
        return False
    
    if not input_path.is_dir():
        logger.error(f"Указанный путь не является папкой: {input_path}")
        return False
    
    # Находим все MP3 файлы
    mp3_files = list(input_path.glob(file_pattern))
    
    if not mp3_files:
        logger.error(f"MP3 файлы не найдены в папке: {input_path}")
        return False
    
    # Сортируем файлы по имени если нужно
    if sort_by_name:
        mp3_files.sort(key=lambda x: x.name)
    
    logger.info(f"Найдено {len(mp3_files)} MP3 файлов")
    print(f"Найдено {len(mp3_files)} MP3 файлов:")
    
    # Показываем список файлов с их длительностью
    total_duration_seconds = 0
    for i, file_path in enumerate(mp3_files, 1):
        duration_str = get_mp3_duration(str(file_path))
        print(f"  {i:2d}. {file_path.name} ({duration_str})")
        
        # Подсчитываем общую длительность
        time_parts = duration_str.split(":")
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])
        total_duration_seconds += hours * 3600 + minutes * 60 + seconds
    
    # Конвертируем общую длительность обратно в формат HH:MM:SS
    total_hours = int(total_duration_seconds // 3600)
    total_minutes = int((total_duration_seconds % 3600) // 60)
    total_seconds = int(total_duration_seconds % 60)
    total_duration_str = f"{total_hours:02d}:{total_minutes:02d}:{total_seconds:02d}"
    
    print(f"\nОбщая длительность: {total_duration_str}")
    logger.info(f"Общая длительность: {total_duration_str}")
    
    # Создаем папку для выходного файла если нужно
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Создаем временный файл со списком файлов для ffmpeg
    temp_list_file = output_path.parent / "temp_file_list.txt"
    
    try:
        with open(temp_list_file, 'w', encoding='utf-8') as f:
            for file_path in mp3_files:
                # Используем абсолютные пути для надежности
                f.write(f"file '{file_path.absolute()}'\n")
        
        logger.info("Создан временный файл со списком файлов")
        
        # Выполняем конкатенацию через ffmpeg
        print(f"\nНачинаем конкатенацию файлов...")
        logger.info(f"Начинаем конкатенацию в файл: {output_path}")
        
        command = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", str(temp_list_file),
            "-c", "copy", str(output_path),
            "-y"  # Перезаписать если существует
        ]
        
        # Запускаем ffmpeg с прогресс-баром
        with tqdm(total=1, desc="Конкатенация", unit="операция") as pbar:
            result = subprocess.run(command, capture_output=True, text=True)
            pbar.update(1)
        
        if result.returncode == 0 and output_path.exists():
            # Проверяем размер и длительность созданного файла
            file_size = output_path.stat().st_size / (1024 * 1024)  # в МБ
            final_duration = get_mp3_duration(str(output_path))
            
            print(f"\n✅ Конкатенация завершена успешно!")
            print(f"📁 Выходной файл: {output_path}")
            print(f"📊 Размер: {file_size:.2f} МБ")
            print(f"⏱️  Длительность: {final_duration}")
            
            logger.info(f"Конкатенация завершена успешно: {output_path}")
            logger.info(f"Размер: {file_size:.2f} МБ, Длительность: {final_duration}")
            
            return True
        else:
            print(f"\n❌ Ошибка при конкатенации!")
            print(f"stderr: {result.stderr}")
            logger.error(f"Ошибка при конкатенации: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        logger.error(f"Неожиданная ошибка при конкатенации: {e}")
        return False
    finally:
        # Удаляем временный файл
        if temp_list_file.exists():
            temp_list_file.unlink()
            logger.info("Временный файл удален")

def main():
    parser = argparse.ArgumentParser(description="Конкатенация MP3 файлов через ffmpeg")
    parser.add_argument('--input', '-i', required=True, help='Папка с MP3 файлами')
    parser.add_argument('--output', '-o', required=True, help='Путь к выходному MP3 файлу')
    parser.add_argument('--pattern', '-p', default='*.mp3', help='Паттерн для поиска файлов (по умолчанию *.mp3)')
    parser.add_argument('--no-sort', action='store_true', help='Не сортировать файлы по имени')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробное логирование')
    parser.add_argument('--interactive', action='store_true', help='Интерактивный режим')
    args = parser.parse_args()

    # Настройка логирования
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("=== Запуск конкатенации MP3 файлов ===")

    # Интерактивный режим
    if args.interactive:
        print("\n" + "="*60)
        print("КОНКАТЕНАЦИЯ MP3 ФАЙЛОВ")
        print("="*60)
        
        # Получаем входную папку
        if not args.input:
            print("\nВведите путь к папке с MP3 файлами:")
            print("Примеры:")
            print("  - audio_files")
            print("  - C:\\path\\to\\audio_files")
            args.input = input("Входная папка: ").strip().strip('"')
        
        # Получаем выходной файл
        if not args.output:
            print("\nВведите путь к выходному MP3 файлу:")
            print("Примеры:")
            print("  - combined.mp3")
            print("  - C:\\path\\to\\combined.mp3")
            args.output = input("Выходной файл: ").strip().strip('"')
        
        # Дополнительные настройки
        print(f"\nТекущие настройки:")
        print(f"  - Паттерн файлов: {args.pattern}")
        print(f"  - Сортировка по имени: {'Нет' if args.no_sort else 'Да'}")
        
        change_settings = input("\nИзменить настройки? (y/n, по умолчанию n): ").strip().lower()
        if change_settings in ['y', 'yes', 'да']:
            # Паттерн файлов
            new_pattern = input(f"Паттерн файлов (по умолчанию {args.pattern}): ").strip()
            if new_pattern:
                args.pattern = new_pattern
            
            # Сортировка
            sort_choice = input("Сортировать файлы по имени? (y/n, по умолчанию y): ").strip().lower()
            args.no_sort = sort_choice in ['n', 'no', 'нет']
        
        print(f"\nЗапуск конкатенации с параметрами:")
        print(f"  Входная папка: {args.input}")
        print(f"  Выходной файл: {args.output}")
        print(f"  Паттерн файлов: {args.pattern}")
        print(f"  Сортировка по имени: {'Нет' if args.no_sort else 'Да'}")
        
        confirm = input("\nПродолжить? (y/n, по умолчанию y): ").strip().lower()
        if confirm in ['n', 'no', 'нет']:
            print("Конкатенация отменена.")
            return

    logger.info(f"Входные параметры: {vars(args)}")

    # Выполняем конкатенацию
    success = concatenate_mp3_files(
        input_dir=args.input,
        output_file=args.output,
        file_pattern=args.pattern,
        sort_by_name=not args.no_sort,
        logger=logger
    )
    
    if success:
        logger.info("=== Конкатенация завершена успешно ===")
        print(f"\n{'='*60}")
        print("КОНКАТЕНАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print(f"{'='*60}")
        print(f"Результат сохранен в: {args.output}")
        print(f"Лог сохранен в: concatenate_mp3.log")
    else:
        logger.error("=== Конкатенация завершена с ошибкой ===")
        print(f"\n{'='*60}")
        print("КОНКАТЕНАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ!")
        print(f"{'='*60}")
        print("Проверьте лог файл: concatenate_mp3.log")

if __name__ == "__main__":
    main() 