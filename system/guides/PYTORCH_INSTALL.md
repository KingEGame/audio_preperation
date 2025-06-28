# 🔧 Установка PyTorch с CUDA

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

## 🔗 Связанные руководства

- **[Основное руководство](MAIN_GUIDE.md)** - Полная установка системы
- **[Оптимизированная версия](OPTIMIZED_GUIDE.md)** - Настройки производительности
- **[Быстрое исправление](TROUBLESHOOTING.md)** - Решения проблем с GPU
- **[Параллельная обработка](PARALLEL_PROCESSING.md)** - Использование GPU в обработке 