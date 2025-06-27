#!/usr/bin/env python3
"""
Тестовый скрипт для проверки доступности GPU и PyTorch
"""

import torch
import sys

def test_gpu():
    print("=" * 50)
    print("ТЕСТ GPU И PYTORCH")
    print("=" * 50)
    
    # Проверка версии PyTorch
    print(f"PyTorch версия: {torch.__version__}")
    
    # Проверка доступности CUDA
    cuda_available = torch.cuda.is_available()
    print(f"CUDA доступна: {cuda_available}")
    
    if cuda_available:
        # Информация о GPU
        gpu_count = torch.cuda.device_count()
        print(f"Количество GPU: {gpu_count}")
        
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} ГБ)")
        
        # Текущий GPU
        current_device = torch.cuda.current_device()
        print(f"Текущий GPU: {current_device}")
        
        # Тест производительности
        print("\nТест производительности GPU...")
        try:
            # Создаем тестовый тензор на GPU
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            
            # Измеряем время умножения матриц
            import time
            start_time = time.time()
            for _ in range(100):
                z = torch.mm(x, y)
            torch.cuda.synchronize()  # Ждем завершения GPU операций
            end_time = time.time()
            
            print(f"Время 100 умножений матриц 1000x1000: {end_time - start_time:.3f} сек")
            print("GPU тест пройден успешно!")
            
        except Exception as e:
            print(f"Ошибка при тесте GPU: {e}")
            return False
    else:
        print("CUDA недоступна. Проверьте:")
        print("1. Установлены ли драйверы NVIDIA")
        print("2. Установлен ли PyTorch с поддержкой CUDA")
        print("3. Совместима ли версия CUDA")
        return False
    
    # Проверка других библиотек
    print("\nПроверка других библиотек...")
    
    try:
        import torchaudio
        print(f"✓ torchaudio: {torchaudio.__version__}")
    except ImportError:
        print("✗ torchaudio не установлен")
    
    try:
        import whisper
        print(f"✓ whisper: {whisper.__version__}")
    except ImportError:
        print("✗ whisper не установлен")
    
    try:
        from demucs.pretrained import get_model
        print("✓ demucs доступен")
    except ImportError:
        print("✗ demucs не установлен")
    
    try:
        from silero import vad
        print("✓ silero-vad доступен")
    except ImportError:
        print("✗ silero-vad не установлен")
    
    print("\n" + "=" * 50)
    if cuda_available:
        print("✅ GPU ГОТОВ К РАБОТЕ!")
        print("Аудио-процессинг будет использовать GPU ускорение.")
    else:
        print("⚠️  GPU НЕДОСТУПЕН")
        print("Аудио-процессинг будет работать на CPU (медленнее).")
    print("=" * 50)
    
    return cuda_available

if __name__ == "__main__":
    test_gpu() 