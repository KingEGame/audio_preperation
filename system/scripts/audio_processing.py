#!/usr/bin/env python3
"""
Главный скрипт для обработки аудио
Оптимизированный пайплайн обработки аудио: разбивка, шумоподавление, удаление тишины, диаризация
Оптимизирован для RTX 5080, 32GB RAM, R5 5600X
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path

# Добавляем путь к модулям аудио
sys.path.append(str(Path(__file__).parent))

# Импорт модульной системы аудио обработки
try:
    from audio import (
        setup_logging, get_mp3_duration, setup_gpu_optimization, get_optimal_workers,
        parallel_audio_processing_optimized, process_audio_file_optimized,
        GPUMemoryManager, ModelManager, GPU_MEMORY_LIMIT
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed and audio modules are available")
    sys.exit(1)

def show_interactive_menu():
    """
    Интерактивное меню для настройки параметров обработки
    """
    print("\n" + "="*60)
    print("AUDIO PROCESSING PIPELINE (OPTIMIZED)")
    print("="*60)
    
    # Получаем входной файл/папку
    print("\nВведите путь к аудио файлу или папке с аудио файлами:")
    print("Примеры:")
    print("  - audio.mp3")
    print("  - C:\\path\\to\\audio.mp3")
    print("  - audio_folder")
    print("  - C:\\path\\to\\audio_folder")
    input_path = input("Входной файл/папка: ").strip().strip('"')
    
    # Получаем выходную папку
    print("\nВведите папку для сохранения результатов:")
    print("Примеры:")
    print("  - results")
    print("  - C:\\path\\to\\results")
    output_path = input("Выходная папка: ").strip().strip('"')
    
    # Настройки по умолчанию
    chunk_duration = 600
    min_speaker_segment = 1.5
    split_method = 'word_boundary'
    steps = ['split', 'denoise', 'vad', 'diar']
    parallel = True
    gpu_available = setup_gpu_optimization()
    optimal_workers = get_optimal_workers()
    
    # Показываем текущие настройки
    print(f"\nТекущие настройки:")
    print(f"  - Длительность чанка: {chunk_duration} сек")
    print(f"  - Минимальная длительность сегмента спикера: {min_speaker_segment} сек")
    print(f"  - Метод разбивки: {split_method}")
    print(f"  - Этапы: {', '.join(steps)}")
    print(f"  - Параллельная обработка частей: {'Включена' if parallel else 'Отключена'}")
    print(f"  - Количество процессов: {optimal_workers}")
    print(f"  - GPU: {'Включен' if gpu_available else 'Отключен'}")
    
    change_settings = input("\nИзменить настройки? (y/n, по умолчанию n): ").strip().lower()
    if change_settings in ['y', 'yes', 'да']:
        # Длительность чанка
        new_duration = input(f"Длительность чанка в секундах (по умолчанию {chunk_duration}): ").strip()
        if new_duration and new_duration.isdigit():
            chunk_duration = int(new_duration)
        
        # Минимальная длительность сегмента спикера
        new_min_segment = input(f"Минимальная длительность сегмента спикера в секундах (по умолчанию {min_speaker_segment}): ").strip()
        if new_min_segment and new_min_segment.replace('.', '').isdigit():
            min_speaker_segment = float(new_min_segment)
        
        # Метод разбивки
        print("\nМетод разбивки:")
        print("  simple - простая разбивка по времени")
        print("  word_boundary - разбивка по границам слов (рекомендуется)")
        new_method = input(f"Метод (по умолчанию {split_method}): ").strip()
        if new_method in ['simple', 'word_boundary']:
            split_method = new_method
        
        # Этапы обработки
        print("\nЭтапы обработки:")
        print("  split - разбивка на чанки")
        print("  denoise - удаление шумов (Demucs)")
        print("  vad - удаление тишины (Silero VAD)")
        print("  diar - диаризация спикеров (PyAnnote)")
        new_steps = input(f"Этапы через пробел (по умолчанию {' '.join(steps)}): ").strip()
        if new_steps:
            steps = new_steps.split()
        
        # Параллельная обработка частей
        parallel_choice = input("Использовать параллельную обработку частей? (y/n, по умолчанию y): ").strip().lower()
        parallel = parallel_choice not in ['n', 'no', 'нет']
        
        # Количество процессов
        new_workers = input(f"Количество процессов для частей (по умолчанию {optimal_workers}): ").strip()
        if new_workers and new_workers.isdigit():
            optimal_workers = min(int(new_workers), optimal_workers)
    
    return {
        'input': input_path,
        'output': output_path,
        'chunk_duration': chunk_duration,
        'min_speaker_segment': min_speaker_segment,
        'split_method': split_method,
        'steps': steps,
        'parallel': parallel,
        'use_gpu': gpu_available,
        'workers': optimal_workers
    }

def main():
    parser = argparse.ArgumentParser(description="Оптимизированный пайплайн обработки аудио: разбивка, шумоподавление, удаление тишины, диаризация с разделением спикеров.")
    parser.add_argument('--input', '-i', help='Путь к аудио файлу (mp3/wav) или папке с файлами')
    parser.add_argument('--output', '-o', help='Папка для сохранения результатов')
    parser.add_argument('--chunk_duration', type=int, default=600, help='Максимальная длительность чанка (секунды), по умолчанию 600 (10 минут)')
    parser.add_argument('--min_speaker_segment', type=float, default=1.5, help='Минимальная длительность сегмента спикера (секунды), по умолчанию 1.5')
    parser.add_argument('--steps', nargs='+', default=['split','denoise','vad', 'diar'],
                        help='Этапы обработки: split, denoise, vad, diar')
    parser.add_argument('--split_method', type=str, default='word_boundary', choices=['simple', 'word_boundary'],
                        help='Метод разбивки: simple или word_boundary')
    parser.add_argument('--use_gpu', action='store_true', help='Использовать GPU для VAD (по умолчанию CPU для стабильности)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробное логирование')
    parser.add_argument('--interactive', action='store_true', help='Интерактивный режим с запросом параметров')
    parser.add_argument('--parallel', action='store_true', default=True, help='Использовать параллельную обработку (включена по умолчанию)')
    parser.add_argument('--workers', type=int, help='Количество рабочих процессов (определяется автоматически)')
    args = parser.parse_args()

    # Настройка логирования
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("=== Запуск оптимизированного пайплайна обработки аудио ===")
    
    # Настройка оптимизации для RTX 5080
    print("\n" + "="*60)
    print("ОПТИМИЗАЦИЯ ДЛЯ RTX 5080 + R5 5600X + 32GB RAM")
    print("="*60)
    
    # Настройка GPU
    gpu_available = setup_gpu_optimization()
    if gpu_available:
        print("✓ Оптимизация GPU применена")
        args.use_gpu = True  # Автоматически включаем GPU
    else:
        print("⚠ GPU недоступен, используется CPU")
    
    # Определяем оптимальное количество процессов
    optimal_workers = get_optimal_workers()
    if args.workers:
        optimal_workers = min(args.workers, optimal_workers)
    
    print(f"✓ Оптимальное количество процессов: {optimal_workers}")
    print(f"✓ Параллельная обработка частей: {'Включена' if args.parallel else 'Отключена'}")
    
    # Интерактивный режим или получение параметров
    if args.interactive or not args.input or not args.output:
        config = show_interactive_menu()
        args.input = config['input']
        args.output = config['output']
        args.chunk_duration = config['chunk_duration']
        args.min_speaker_segment = config['min_speaker_segment']
        args.split_method = config['split_method']
        args.steps = config['steps']
        args.parallel = config['parallel']
        args.use_gpu = config['use_gpu']
        optimal_workers = config['workers']
        
        print(f"\nНачинаем обработку с параметрами:")
        print(f"  Вход: {args.input}")
        print(f"  Выход: {args.output}")
        print(f"  Длительность чанка: {args.chunk_duration} сек")
        print(f"  Минимальная длительность сегмента спикера: {args.min_speaker_segment} сек")
        print(f"  Метод разбивки: {args.split_method}")
        print(f"  Этапы: {', '.join(args.steps)}")
        print(f"  Параллельная обработка частей: {'Да' if args.parallel else 'Нет'}")
        print(f"  Количество процессов: {optimal_workers}")
        print(f"  GPU: {'Да' if gpu_available else 'Нет'}")
        
        confirm = input("\nПродолжить? (y/n, по умолчанию y): ").strip().lower()
        if confirm in ['n', 'no', 'нет']:
            print("Обработка отменена.")
            return

    logger.info(f"Входные параметры: {vars(args)}")

    input_path = Path(args.input)
    output_dir = Path(args.output)
    chunk_duration = args.chunk_duration
    steps = args.steps
    split_method = args.split_method

    # Проверяем существование входного файла/папки
    if not input_path.exists():
        logger.error(f"Входной файл/папка не найдена: {input_path}")
        print(f"\nОШИБКА: Файл или папка '{input_path}' не существует!")
        print("Проверьте путь и попробуйте снова.")
        return

    files = []
    if input_path.is_file():
        files = [input_path]
        logger.info(f"Обработка одного файла: {input_path}")
        print(f"\nНайден файл: {input_path}")
    elif input_path.is_dir():
        files = list(input_path.glob('*.mp3')) + list(input_path.glob('*.wav'))
        logger.info(f"Найдено {len(files)} файлов в папке: {input_path}")
        print(f"\nНайдено {len(files)} аудио файлов в папке: {input_path}")
        if not files:
            print("Не найдено аудио файлов (.mp3 или .wav) в папке")
            return
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file.name}")
    else:
        logger.error(f"Файл или папка не найдена: {input_path}")
        return

    # Создаем выходную папку
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nРезультаты будут сохранены в: {output_dir}")

    # Начинаем отсчет времени
    start_time = time.time()
    
    if args.parallel and len(files) > 1:
        # Параллельная обработка частей для нескольких файлов
        print(f"\nЗапуск параллельной обработки частей для {len(files)} файлов...")
        logger.info("Использование параллельной обработки частей")
        
        results = parallel_audio_processing_optimized(
            files, output_dir, steps, chunk_duration,
            args.min_speaker_segment, split_method, args.use_gpu, logger
        )
        
        # Подсчитываем общее количество обработанных файлов
        total_processed = sum(len(r) if r else 0 for r in results)
        print(f"\nПараллельная обработка частей завершена! Обработано файлов: {total_processed}")
        
    else:
        # Последовательная обработка для одного файла или отключенной параллелизации
        print(f"\nЗапуск последовательной обработки...")
        logger.info("Использование последовательной обработки")
        
        # Создаем временную папку для промежуточных файлов
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            logger.info(f"Создана временная папка: {temp_path}")
            
            # Инициализируем менеджеры для последовательной обработки
            gpu_manager = GPUMemoryManager(GPU_MEMORY_LIMIT)
            model_manager = ModelManager(gpu_manager)
            
            # Загружаем модель Whisper только для разбивки по границам слов
            whisper_model = None
            if 'split' in steps and split_method == 'word_boundary':
                logger.info("Загрузка модели Whisper для анализа границ слов...")
                print("Загрузка модели Whisper для анализа границ слов...")
                whisper_model = model_manager.get_whisper_model("base")

            # Обрабатываем файлы с прогресс-баром
            print(f"\nНачинаем обработку {len(files)} файлов...")
            from tqdm import tqdm
            
            all_processed_files = []  # Список всех обработанных файлов
            
            with tqdm(total=len(files), desc="Обработка файлов", unit="файл") as pbar_files:
                for audio in files:
                    logger.info(f"\n=== Обработка файла: {audio} ===")
                    print(f"\n{'='*50}")
                    print(f"Обработка: {audio.name}")
                    print(f"{'='*50}")
                    
                    # Обрабатываем файл
                    result = process_audio_file_optimized(
                        audio, output_dir, steps, chunk_duration,
                        args.min_speaker_segment, split_method, args.use_gpu, logger
                    )
                    
                    if result:
                        all_processed_files.extend(result)
                    
                    pbar_files.update(1)
            
            # Финальная очистка
            model_manager.cleanup_models()
            gpu_manager.cleanup(force=True)
    
    # Вычисляем время выполнения
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info("=== Обработка завершена ===")
    print(f"\n{'='*60}")
    print("ОБРАБОТКА ЗАВЕРШЕНА!")
    print(f"{'='*60}")
    print(f"Общее время выполнения: {total_time/60:.1f} минут")
    print(f"Результаты сохранены в: {output_dir}")
    print("\nСтруктура результатов:")
    
    # Показываем что создано
    if output_dir.exists():
        # Показываем файлы спикеров если выполнялась диаризация
        if 'diar' in steps:
            speaker_files = list(output_dir.glob('speaker_*.wav'))
            if speaker_files:
                print(f"  speaker_*.wav ({len(speaker_files)} файлов)")
                for speaker_file in speaker_files:
                    try:
                        duration_str = get_mp3_duration(str(speaker_file))
                        print(f"    - {speaker_file.name}: {duration_str}")
                    except:
                        print(f"    - {speaker_file.name}")
    
    print(f"\nЛог обработки сохранен в: audio_processing.log")
    print(f"Временные файлы автоматически удалены")
    
    # Показываем статистику производительности
    if args.parallel and len(files) > 1:
        print(f"\nСТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ:")
        print(f"  - Обработано файлов: {len(files)}")
        print(f"  - Время на файл: {total_time/len(files):.1f} секунд")
        print(f"  - Ускорение от параллелизации: ~{optimal_workers}x")
        print(f"  - GPU использован: {'Да' if gpu_available else 'Нет'}")
        print(f"  - Логика: Оптимизированная параллельная обработка с управлением памятью")

if __name__ == "__main__":
    main() 