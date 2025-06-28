"""
Конфигурация для системы обработки аудио
"""

import multiprocessing as mp
import psutil
import torch

# Глобальные настройки для оптимизации производительности
MAX_WORKERS = min(mp.cpu_count(), 6)  # Ограничено для стабильности
GPU_MEMORY_LIMIT = 0.95  # 95% GPU памяти для лучшей стабильности
BATCH_SIZE = 4  # Уменьшенный размер батча

def get_optimal_workers():
    """
    Определяет оптимальное количество рабочих процессов на основе системы
    """
    cpu_count = mp.cpu_count()
    memory_gb = psutil.virtual_memory().total / 1024**3
    
    # Консервативный подход для стабильности
    if cpu_count >= 12 and memory_gb >= 24:
        return min(6, cpu_count // 2)  # Используем половину ядер
    elif cpu_count >= 8 and memory_gb >= 16:
        return min(4, cpu_count // 2)
    else:
        return min(2, cpu_count // 2)

def setup_gpu_optimization():
    """
    Настраивает GPU для оптимальной производительности с улучшенным управлением памятью
    """
    if torch.cuda.is_available():
        # Устанавливаем оптимальные настройки для RTX 5080
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        
        # Настраиваем управление памятью
        torch.cuda.set_per_process_memory_fraction(GPU_MEMORY_LIMIT)
        
        # Включаем эффективное внимание если доступно
        if hasattr(torch.backends.cuda, 'enable_flash_sdp'):
            torch.backends.cuda.enable_flash_sdp(True)
        
        total_memory = torch.cuda.get_device_properties(0).total_memory
        max_memory = int(total_memory * GPU_MEMORY_LIMIT)
        
        print(f"GPU optimization: {total_memory / 1024**3:.1f}GB -> {max_memory / 1024**3:.1f}GB")
        return True
    return False