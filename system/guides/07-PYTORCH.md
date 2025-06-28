# 🔧 Установка PyTorch с CUDA - Audio Processing Pipeline

Руководство по установке и настройке PyTorch с поддержкой CUDA для ускорения обработки аудио.

## 🎯 Выбор версии CUDA

### Поддерживаемые версии:
- **CUDA 11.8** - Стабильная, широко поддерживаемая
- **CUDA 12.1** - Рекомендуемая для новых карт
- **CUDA 12.8** - Последняя версия (экспериментальная)
- **CPU Only** - Без GPU ускорения

## 🚀 Автоматическая установка

### Через setup.bat
```cmd
setup.bat
```
Выберите опцию **1** → **Install PyTorch** → Выберите версию CUDA

### Прямой запуск
```cmd
system\instructions\install_pytorch.bat
```

## 🔧 Ручная установка

### 1. Проверка текущей версии
```cmd
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
```

### 2. Удаление старой версии
```cmd
pip uninstall torch torchvision torchaudio -y
```

### 3. Установка новой версии

#### CUDA 11.8 (рекомендуется для стабильности)
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### CUDA 12.1 (рекомендуется для новых карт)
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### CUDA 12.8 (экспериментальная)
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

#### CPU Only (без GPU)
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## 🔍 Проверка установки

### Проверка PyTorch
```cmd
python -c "import torch; print('PyTorch version:', torch.__version__)"
```

### Проверка CUDA
```cmd
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

### Проверка GPU
```cmd
python -c "import torch; print('GPU count:', torch.cuda.device_count()); print('GPU name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')"
```

### Тест производительности
```cmd
python -c "
import torch
import time

if torch.cuda.is_available():
    device = torch.device('cuda')
    print('Testing GPU performance...')
    
    # Создаем тестовый тензор
    x = torch.randn(1000, 1000).to(device)
    y = torch.randn(1000, 1000).to(device)
    
    # Тестируем умножение матриц
    start_time = time.time()
    z = torch.mm(x, y)
    torch.cuda.synchronize()
    end_time = time.time()
    
    print(f'GPU matrix multiplication time: {end_time - start_time:.4f} seconds')
    print('GPU test completed successfully!')
else:
    print('CUDA not available, using CPU')
    device = torch.device('cpu')
    
    x = torch.randn(1000, 1000)
    y = torch.randn(1000, 1000)
    
    start_time = time.time()
    z = torch.mm(x, y)
    end_time = time.time()
    
    print(f'CPU matrix multiplication time: {end_time - start_time:.4f} seconds')
"
```

## ⚠️ Устранение неполадок

### Ошибка "CUDA not available"
```cmd
# Проверьте драйверы NVIDIA
nvidia-smi

# Переустановите PyTorch с правильной версией CUDA
system\instructions\install_pytorch.bat
```

### Ошибка "Version mismatch"
```cmd
# Полностью удалите PyTorch
pip uninstall torch torchvision torchaudio -y

# Очистите кэш
pip cache purge

# Установите заново
system\instructions\install_pytorch.bat
```

### Медленная работа GPU
```cmd
# Проверьте загрузку GPU
nvidia-smi

# Очистите память GPU
python -c "import torch; torch.cuda.empty_cache()"
```

## 📊 Совместимость версий

### NVIDIA GPU
| GPU Series | Рекомендуемая CUDA | PyTorch версия |
|------------|-------------------|----------------|
| RTX 40xx | CUDA 12.1 | 2.1+ |
| RTX 30xx | CUDA 11.8/12.1 | 2.0+ |
| RTX 20xx | CUDA 11.8 | 1.13+ |
| GTX 16xx | CUDA 11.8 | 1.13+ |
| GTX 10xx | CUDA 11.8 | 1.13+ |

### Системные требования
- **Windows 10/11** (64-bit)
- **NVIDIA GPU** с поддержкой CUDA
- **Драйверы NVIDIA** версии 450+
- **Python 3.8-3.11**

## 🔄 Обновление версии

### Автоматическое обновление
```cmd
system\instructions\install_pytorch.bat
```

### Ручное обновление
```cmd
# Удалить старую версию
pip uninstall torch torchvision torchaudio -y

# Установить новую версию
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 📋 Проверочный список

После установки проверьте:

- [ ] PyTorch установлен: `python -c "import torch; print(torch.__version__)"`
- [ ] CUDA доступен: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] GPU определяется: `python -c "import torch; print(torch.cuda.get_device_name(0))"`
- [ ] Тест производительности проходит
- [ ] Другие библиотеки работают: `python -c "import demucs, whisper, torchaudio"`

## 🎯 Оптимизация для обработки аудио

### Настройки для Demucs
```python
# Оптимальные настройки для шумоподавления
import torch
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.deterministic = False
```

### Настройки для Whisper
```python
# Оптимальные настройки для транскрипции
import torch
torch.backends.cudnn.benchmark = True
```

### Настройки для PyAnnote
```python
# Оптимальные настройки для диаризации
import torch
torch.backends.cudnn.benchmark = True
```

## 🔧 Дополнительные настройки

### Управление памятью GPU
```python
# Очистка памяти GPU
import torch
torch.cuda.empty_cache()

# Мониторинг использования памяти
print(f"GPU Memory: {torch.cuda.memory_allocated()/1024**3:.2f}GB")
print(f"GPU Memory Cached: {torch.cuda.memory_reserved()/1024**3:.2f}GB")
```

### Оптимизация производительности
```python
# Включение оптимизаций
import torch
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.deterministic = False

# Установка количества потоков
torch.set_num_threads(4)
```

## 🚨 Частые проблемы

### Проблема: "CUDA out of memory"
**Решение:**
```python
# Очистите память GPU
import torch
torch.cuda.empty_cache()

# Уменьшите размер батча
batch_size = 1  # Вместо 4 или 8
```

### Проблема: "CUDA driver version is insufficient"
**Решение:**
```cmd
# Обновите драйверы NVIDIA
# Скачайте с https://www.nvidia.com/Download/index.aspx
```

### Проблема: "PyTorch version mismatch"
**Решение:**
```cmd
# Переустановите PyTorch
system\instructions\install_pytorch.bat
```

## 📊 Мониторинг производительности

### Проверка загрузки GPU
```cmd
# Мониторинг в реальном времени
nvidia-smi -l 1
```

### Проверка температуры GPU
```cmd
# Проверка температуры
nvidia-smi --query-gpu=temperature.gpu --format=csv
```

### Проверка использования памяти
```cmd
# Проверка памяти GPU
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

## 🔗 Интеграция с системой

### Автоматическая проверка GPU
```cmd
# Тест GPU через систему
setup.bat → опция 4 → опция 7 (Fix GPU detection)
```

### Оптимизированные зависимости
```cmd
# Установка оптимизированных версий
setup.bat → опция 4 → опция 11 (Install optimized dependencies)
```

### Проверка совместимости
```cmd
# Полная проверка системы
setup.bat → опция 2 (Test Everything)
```

## 📚 Следующие шаги

После установки PyTorch:

1. **[Оптимизация производительности](06-PERFORMANCE.md)** - Настройка GPU и CPU
2. **[Примеры использования](03-EXAMPLES.md)** - Попробуйте обработку с GPU
3. **[Руководство по использованию](04-USAGE.md)** - Изучите все параметры
4. **[Устранение неполадок](10-TROUBLESHOOTING.md)** - Решения проблем с GPU

## 🔗 Связанные руководства

- **[Установка и настройка](01-INSTALLATION.md)** - Полная установка системы
- **[Оптимизация производительности](06-PERFORMANCE.md)** - Настройки производительности
- **[Устранение неполадок](10-TROUBLESHOOTING.md)** - Решения проблем с GPU
- **[Диаризация говорящих](05-DIARIZATION.md)** - Использование GPU в диаризации 