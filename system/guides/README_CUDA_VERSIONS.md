# CUDA Version Requirements Guide

Этот каталог содержит различные файлы requirements для разных версий CUDA и конфигураций.

## Структура файлов

### Основные файлы:
- **`requirements.txt`** - Основные зависимости (без PyTorch)
- **`requirements_cu118.txt`** - Только PyTorch для CUDA 11.8
- **`requirements_cu121.txt`** - Только PyTorch для CUDA 12.1
- **`requirements_cu128.txt`** - Только PyTorch для CUDA 12.8
- **`requirements_cpu.txt`** - Только PyTorch для CPU

## Как выбрать правильную версию

### 1. Проверьте вашу версию CUDA
```bash
nvidia-smi
```
Или
```bash
nvcc --version
```

### 2. Установите зависимости

#### Автоматический выбор (рекомендуется):
```bash
system\instructions\install_dependencies_choice.bat
```

#### Ручная установка:

##### Шаг 1: Установите PyTorch для нужной версии CUDA
```bash
# Для CUDA 12.8
pip install -r system/requirements/requirements_cu128.txt

# Для CUDA 12.1
pip install -r system/requirements/requirements_cu121.txt

# Для CUDA 11.8
pip install -r system/requirements/requirements_cu118.txt

# Для CPU-only
pip install -r system/requirements/requirements_cpu.txt
```

##### Шаг 2: Установите основные зависимости
```bash
pip install -r system/requirements/requirements.txt
```

## Важные замечания

### Совместимость версий
- **CUDA 12.8**: Самая новая версия, для последних GPU (RTX 4000, RTX 5000 серии)
- **CUDA 12.1**: Стабильная версия для большинства современных систем
- **CUDA 11.8**: Хорошая стабильность, широкий диапазон совместимости
- **CPU-only**: Работает на любой системе, но медленнее

### Производительность
- **CUDA 12.8**: Максимальная производительность для новейших GPU
- **CUDA 12.1**: Отличная производительность для большинства систем
- **CUDA 11.8**: Хорошая производительность, широкая совместимость
- **CPU-only**: Медленнее в 10-50 раз, но не требует GPU

### Установка CUDA Toolkit
Перед установкой PyTorch убедитесь, что у вас установлен соответствующий CUDA Toolkit:

- **CUDA 12.8**: https://developer.nvidia.com/cuda-12-8-0-download-archive
- **CUDA 12.1**: https://developer.nvidia.com/cuda-12-1-0-download-archive
- **CUDA 11.8**: https://developer.nvidia.com/cuda-11-8-0-download-archive

## Устранение неполадок

### Ошибка "CUDA not available"
1. Проверьте, что CUDA Toolkit установлен
2. Проверьте версию CUDA: `nvidia-smi`
3. Убедитесь, что используете правильный файл requirements

### Ошибка "torch not found"
1. Убедитесь, что используете правильный `--extra-index-url`
2. Попробуйте установить PyTorch отдельно:
   ```bash
   pip install torch==2.1.2+cu128 torchaudio==2.1.2+cu128 torchvision==0.16.2+cu128 --extra-index-url https://download.pytorch.org/whl/cu128
   ```

### Медленная работа
- Если у вас GPU, убедитесь, что используете CUDA версию, а не CPU
- Проверьте, что PyTorch видит GPU: `python -c "import torch; print(torch.cuda.is_available())"`

## Рекомендации

- **Для новейших систем**: Используйте CUDA 12.8
- **Для современных систем**: Используйте CUDA 12.1
- **Для старых систем**: Используйте CUDA 11.8
- **Для систем без GPU**: Используйте CPU-only версию

## Автоматическая установка

Для автоматического выбора и установки зависимостей используйте:
```bash
system\instructions\install_dependencies_choice.bat
```

Этот скрипт поможет вам выбрать правильную версию CUDA и установит все необходимые зависимости.

## Логика работы

1. **`requirements.txt`** содержит все основные зависимости (numpy, scipy, whisper, demucs и т.д.)
2. **`requirements_cuXXX.txt`** содержат только PyTorch для конкретной версии CUDA
3. При установке сначала устанавливается PyTorch, затем основные зависимости
4. Это позволяет легко переключаться между версиями CUDA без переустановки всех зависимостей 