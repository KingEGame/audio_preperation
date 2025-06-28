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

def print_header():
    """Красивый заголовок"""
    print("\n" + "🎵" + "="*58 + "🎵")
    print("    ИНТЕЛЛЕКТУАЛЬНАЯ ОБРАБОТКА АУДИО ФАЙЛОВ")
    print("    Оптимизировано для RTX 5080 + R5 5600X + 32GB RAM")
    print("🎵" + "="*58 + "🎵")

def validate_path_input(prompt, is_input=True):
    """Валидация и получение пути с проверками"""
    while True:
        print(f"\n{prompt}")
        if is_input:
            print("📁 Примеры входных путей:")
            print("   • audio.mp3")
            print("   • /path/to/audio.wav") 
            print("   • ./audio_folder")
            print("   • C:\\Users\\User\\Music\\audio.mp3")
        else:
            print("📂 Примеры выходных путей:")
            print("   • results")
            print("   • /path/to/results")
            print("   • C:\\Users\\User\\Desktop\\processed_audio")
        
        path = input("➤ Путь: ").strip().strip('"').strip("'")
        
        if not path:
            print("❌ Путь не может быть пустым!")
            continue
            
        path_obj = Path(path)
        
        if is_input:
            if path_obj.exists():
                if path_obj.is_file():
                    if path_obj.suffix.lower() in ['.mp3', '.wav']:
                        print(f"✅ Файл найден: {path_obj.name}")
                        return str(path_obj)
                    else:
                        print("❌ Файл должен быть .mp3 или .wav!")
                        continue
                elif path_obj.is_dir():
                    audio_files = list(path_obj.glob('*.mp3')) + list(path_obj.glob('*.wav'))
                    if audio_files:
                        print(f"✅ Папка найдена: {len(audio_files)} аудио файлов")
                        for i, f in enumerate(audio_files[:5], 1):
                            print(f"   {i}. {f.name}")
                        if len(audio_files) > 5:
                            print(f"   ... и еще {len(audio_files) - 5} файлов")
                        return str(path_obj)
                    else:
                        print("❌ В папке нет аудио файлов (.mp3 или .wav)!")
                        continue
            else:
                print("❌ Файл или папка не существует!")
                continue
        else:
            # Для выходной папки
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                print(f"✅ Выходная папка: {path_obj}")
                return str(path_obj)
            except Exception as e:
                print(f"❌ Не удается создать папку: {e}")
                continue

def get_processing_steps():
    """Интерактивный выбор этапов обработки"""
    steps_info = {
        'split': {
            'name': 'Разбивка на части', 
            'desc': 'Разделение длинных файлов на управляемые сегменты',
            'time': 'быстро',
            'recommended': True
        },
        'denoise': {
            'name': 'Шумоподавление', 
            'desc': 'Удаление фонового шума с помощью Demucs AI',
            'time': 'медленно',
            'recommended': True
        },
        'vad': {
            'name': 'Удаление тишины', 
            'desc': 'Удаление пауз и тишины с помощью Silero VAD',
            'time': 'быстро',
            'recommended': True
        },
        'diar': {
            'name': 'Диаризация спикеров', 
            'desc': 'Разделение речи по спикерам с помощью PyAnnote',
            'time': 'медленно',
            'recommended': True
        }
    }
    
    print("\n🔧 НАСТРОЙКА ЭТАПОВ ОБРАБОТКИ:")
    print("Выберите этапы, которые нужно выполнить:\n")
    
    selected_steps = []
    
    for step, info in steps_info.items():
        rec_mark = "⭐" if info['recommended'] else "  "
        time_mark = "🐌" if info['time'] == 'медленно' else "⚡"
        
        print(f"{rec_mark} {step.upper()}: {info['name']} {time_mark}")
        print(f"   📝 {info['desc']}")
        
        while True:
            choice = input(f"   ➤ Включить этап {step}? (y/n, по умолчанию y): ").strip().lower()
            if choice in ['', 'y', 'yes', 'да']:
                selected_steps.append(step)
                print(f"   ✅ Этап {step} включен\n")
                break
            elif choice in ['n', 'no', 'нет']:
                print(f"   ⏭️  Этап {step} пропущен\n")
                break
            else:
                print("   ❌ Введите y или n")
    
    return selected_steps

def estimate_processing_time(files_count, total_duration_minutes, steps, parallel_workers):
    """Примерная оценка времени обработки"""
    time_per_minute = {
        'split': 0.05,     # 3 сек на минуту аудио
        'denoise': 0.8,    # 48 сек на минуту аудио  
        'vad': 0.1,        # 6 сек на минуту аудио
        'diar': 0.3        # 18 сек на минуту аудио
    }
    
    total_time = 0
    for step in steps:
        total_time += time_per_minute.get(step, 0) * total_duration_minutes
    
    # Учитываем параллелизацию
    if files_count > 1:
        total_time = total_time / min(parallel_workers, files_count)
    
    return total_time

def show_interactive_menu():
    """
    Улучшенное интерактивное меню для настройки параметров обработки
    """
    print_header()
    
    # === ШАГ 1: ВХОДНЫЕ ФАЙЛЫ ===
    print("\n📥 ШАГ 1: ВЫБОР ВХОДНЫХ ФАЙЛОВ")
    input_path = validate_path_input("Укажите путь к аудио файлу или папке с аудио файлами:", is_input=True)
    
    # === ШАГ 2: ВЫХОДНАЯ ПАПКА ===
    print("\n📤 ШАГ 2: ВЫБОР ПАПКИ ДЛЯ РЕЗУЛЬТАТОВ")
    output_path = validate_path_input("Укажите папку для сохранения обработанных файлов:", is_input=False)
    
    # === ШАГ 3: ЭТАПЫ ОБРАБОТКИ ===
    print("\n⚙️ ШАГ 3: НАСТРОЙКА ОБРАБОТКИ")
    steps = get_processing_steps()
    
    if not steps:
        print("❌ Не выбрано ни одного этапа обработки!")
        return None
    
    # === ШАГ 4: ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ===
    print("🔧 ШАГ 4: ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ")
    
    # Длительность чанка
    print("\n📏 Максимальная длительность одной части:")
    print("   • Рекомендуется: 600 сек (10 минут)")
    print("   • Для слабых ПК: 300 сек (5 минут)")
    print("   • Для мощных ПК: 900 сек (15 минут)")
    
    while True:
        duration_input = input("➤ Длительность чанка в секундах (по умолчанию 600): ").strip()
        if not duration_input:
            chunk_duration = 600
            break
        try:
            chunk_duration = int(duration_input)
            if 60 <= chunk_duration <= 1800:  # от 1 до 30 минут
                break
            else:
                print("❌ Длительность должна быть от 60 до 1800 секунд!")
        except ValueError:
            print("❌ Введите число!")
    
    # Минимальная длительность сегмента спикера
    print("\n👤 Минимальная длительность сегмента одного спикера:")
    print("   • Рекомендуется: 1.5 сек")
    print("   • Для коротких фраз: 1.0 сек")
    print("   • Для длинных фраз: 2.0 сек")
    
    while True:
        segment_input = input("➤ Минимальная длительность сегмента в секундах (по умолчанию 1.5): ").strip()
        if not segment_input:
            min_speaker_segment = 1.5
            break
        try:
            min_speaker_segment = float(segment_input)
            if 0.5 <= min_speaker_segment <= 10.0:
                break
            else:
                print("❌ Длительность должна быть от 0.5 до 10.0 секунд!")
        except ValueError:
            print("❌ Введите число!")
    
    # Метод разбивки (только если включен split)
    if 'split' in steps:
        print("\n✂️ Метод разбивки аудио:")
        print("   1. simple - простая разбивка по времени (быстро)")
        print("   2. word_boundary - разбивка по границам слов (медленно, но качественно)")
        
        while True:
            method_choice = input("➤ Выберите метод (1/2, по умолчанию 2): ").strip()
            if method_choice == '1':
                split_method = 'simple'
                break
            elif method_choice == '2' or not method_choice:
                split_method = 'word_boundary'
                break
            else:
                print("❌ Введите 1 или 2!")
    else:
        split_method = 'simple'
    
    # Система оптимизации
    print("\n🚀 ШАГ 5: СИСТЕМНАЯ ОПТИМИЗАЦИЯ")
    gpu_available = setup_gpu_optimization()
    optimal_workers = get_optimal_workers()
    
    print(f"🖥️  GPU: {'✅ Обнаружен и настроен' if gpu_available else '❌ Не обнаружен'}")
    print(f"⚡ Оптимальное количество процессов: {optimal_workers}")
    
    # Параллельная обработка
    print("\n🔄 Параллельная обработка файлов:")
    print("   • Да - быстрее для нескольких файлов")
    print("   • Нет - меньше нагрузка на систему")
    
    while True:
        parallel_choice = input("➤ Использовать параллельную обработку? (y/n, по умолчанию y): ").strip().lower()
        if parallel_choice in ['', 'y', 'yes', 'да']:
            parallel = True
            break
        elif parallel_choice in ['n', 'no', 'нет']:
            parallel = False
            optimal_workers = 1
            break
        else:
            print("❌ Введите y или n!")
    
    # === ШАГ 6: ФИНАЛЬНОЕ ПОДТВЕРЖДЕНИЕ ===
    print("\n" + "="*60)
    print("📋 ИТОГОВАЯ КОНФИГУРАЦИЯ:")
    print("="*60)
    print(f"📁 Входной путь: {input_path}")
    print(f"📂 Выходная папка: {output_path}")
    print(f"🔧 Этапы обработки: {' → '.join(steps)}")
    print(f"📏 Длительность чанка: {chunk_duration} сек")
    print(f"👤 Мин. сегмент спикера: {min_speaker_segment} сек")
    if 'split' in steps:
        print(f"✂️  Метод разбивки: {split_method}")
    print(f"🔄 Параллельная обработка: {'Да' if parallel else 'Нет'}")
    print(f"⚡ Процессов: {optimal_workers}")
    print(f"🖥️  GPU: {'Включен' if gpu_available else 'Отключен'}")
    
    # Примерная оценка времени
    try:
        input_path_obj = Path(input_path)
        if input_path_obj.is_file():
            files_count = 1
            # Примерная оценка - 1 час аудио
            estimated_duration = 60
        else:
            audio_files = list(input_path_obj.glob('*.mp3')) + list(input_path_obj.glob('*.wav'))
            files_count = len(audio_files)
            # Примерная оценка - 1 час на файл
            estimated_duration = files_count * 60
        
        estimated_time = estimate_processing_time(files_count, estimated_duration, steps, optimal_workers)
        
        if estimated_time < 60:
            time_str = f"{estimated_time:.1f} минут"
        else:
            time_str = f"{estimated_time/60:.1f} часов"
        
        print(f"⏱️  Примерное время: {time_str}")
    except:
        pass
    
    print("="*60)
    
    while True:
        confirm = input("\n✅ Начать обработку с этими настройками? (y/n/edit): ").strip().lower()
        if confirm in ['y', 'yes', 'да', '']:
            break
        elif confirm in ['n', 'no', 'нет']:
            print("❌ Обработка отменена.")
            return None
        elif confirm in ['edit', 'e', 'изменить']:
            print("🔄 Перезапуск настройки...")
            return show_interactive_menu()  # Рекурсивный вызов для повторной настройки
        else:
            print("❌ Введите y (да), n (нет) или edit (изменить)!")
    
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
        
        # Если пользователь отменил настройку
        if config is None:
            return
            
        # Применяем настройки из интерактивного меню
        args.input = config['input']
        args.output = config['output']
        args.chunk_duration = config['chunk_duration']
        args.min_speaker_segment = config['min_speaker_segment']
        args.split_method = config['split_method']
        args.steps = config['steps']
        args.parallel = config['parallel']
        args.use_gpu = config['use_gpu']
        optimal_workers = config['workers']
        
        # Уже подтверждено в интерактивном меню, можно продолжать
        print("\n🚀 Запуск обработки...")

    logger.info(f"Входные параметры: {vars(args)}")

    input_path = Path(args.input)
    output_dir = Path(args.output)
    chunk_duration = args.chunk_duration
    steps = args.steps
    split_method = args.split_method

    # Проверяем существование входного файла/папки
    if not input_path.exists():
        logger.error(f"Входной файл/папка не найдена: {input_path}")
        print(f"\n❌ ОШИБКА: Файл или папка '{input_path}' не существует!")
        print("🔍 Проверьте путь и попробуйте снова.")
        return

    files = []
    if input_path.is_file():
        files = [input_path]
        logger.info(f"Обработка одного файла: {input_path}")
        print(f"\n📄 Найден файл: {input_path.name}")
        print(f"   📂 Расположение: {input_path.parent}")
    elif input_path.is_dir():
        files = list(input_path.glob('*.mp3')) + list(input_path.glob('*.wav'))
        logger.info(f"Найдено {len(files)} файлов в папке: {input_path}")
        print(f"\n📁 Найдено {len(files)} аудио файлов в папке: {input_path.name}")
        if not files:
            print("❌ Не найдено аудио файлов (.mp3 или .wav) в папке")
            return
        for i, file in enumerate(files, 1):
            print(f"   {i:2d}. 🎵 {file.name}")
            if i >= 10:  # Показываем максимум 10 файлов
                print(f"   ... и еще {len(files) - 10} файлов")
                break
    else:
        logger.error(f"Файл или папка не найдена: {input_path}")
        return

    # Создаем выходную папку
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n💾 Результаты будут сохранены в: {output_dir}")

    # Начинаем отсчет времени
    start_time = time.time()
    
    if args.parallel and len(files) > 1:
        # Параллельная обработка частей для нескольких файлов
        print(f"\n🚀 Запуск параллельной обработки для {len(files)} файлов...")
        print(f"⚡ Использование {optimal_workers} параллельных процессов")
        logger.info("Использование параллельной обработки частей")
        
        results = parallel_audio_processing_optimized(
            files, output_dir, steps, chunk_duration,
            args.min_speaker_segment, split_method, args.use_gpu, logger
        )
        
        # Подсчитываем общее количество обработанных файлов
        total_processed = sum(len(r) if r else 0 for r in results)
        print(f"\n✅ Параллельная обработка завершена! Обработано файлов: {total_processed}")
        
    else:
        # Последовательная обработка для одного файла или отключенной параллелизации
        print(f"\n🔄 Запуск последовательной обработки...")
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
    print(f"\n🎉" + "="*58 + "🎉")
    print("    ✅ ОБРАБОТКА УСПЕШНО ЗАВЕРШЕНА!")
    print("🎉" + "="*58 + "🎉")
    
    # Форматируем время
    if total_time < 60:
        time_str = f"{total_time:.1f} секунд"
    elif total_time < 3600:
        time_str = f"{total_time/60:.1f} минут"
    else:
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        time_str = f"{hours}ч {minutes}м"
    
    print(f"⏱️  Общее время выполнения: {time_str}")
    print(f"💾 Результаты сохранены в: {output_dir}")
    
    # Показываем что создано
    if output_dir.exists():
        print(f"\n📊 Структура результатов:")
        
        # Показываем файлы спикеров если выполнялась диаризация
        if 'diar' in steps:
            speaker_files = list(output_dir.glob('speaker_*.wav'))
            if speaker_files:
                print(f"👥 Файлы спикеров: {len(speaker_files)} файлов")
                for i, speaker_file in enumerate(speaker_files, 1):
                    try:
                        duration_str = get_mp3_duration(str(speaker_file))
                        print(f"   {i:2d}. 🎤 {speaker_file.name} ({duration_str})")
                    except:
                        print(f"   {i:2d}. 🎤 {speaker_file.name}")
                    if i >= 10:  # Показываем максимум 10 файлов
                        print(f"   ... и еще {len(speaker_files) - 10} файлов")
                        break
        
        # Показываем другие результаты
        other_files = [f for f in output_dir.glob('*.wav') if not f.name.startswith('speaker_')]
        if other_files:
            print(f"📄 Другие файлы: {len(other_files)} файлов")
            for i, file in enumerate(other_files, 1):
                print(f"   {i:2d}. 🎵 {file.name}")
                if i >= 5:  # Показываем максимум 5 файлов
                    print(f"   ... и еще {len(other_files) - 5} файлов")
                    break
    
    print(f"\n📝 Лог обработки сохранен в: audio_processing.log")
    print(f"🗑️  Временные файлы автоматически удалены")
    
    # Показываем статистику производительности
    if args.parallel and len(files) > 1:
        print(f"\n📈 СТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ:")
        print(f"   📁 Обработано файлов: {len(files)}")
        print(f"   ⚡ Время на файл: {total_time/len(files):.1f} секунд")
        print(f"   🚀 Ускорение от параллелизации: ~{optimal_workers}x")
        print(f"   🖥️  GPU использован: {'Да' if gpu_available else 'Нет'}")
        print(f"   🧠 Логика: Оптимизированная параллельная обработка с управлением памятью")
    
    print(f"\n🎯 Обработка завершена успешно! Ваши файлы готовы к использованию.")

if __name__ == "__main__":
    main() 