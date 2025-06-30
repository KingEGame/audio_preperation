# AllTalk - Решение конфликтов зависимостей

## Проблема

При установке и запуске AllTalk возникают конфликты зависимостей между различными версиями пакетов, особенно:
- `transformers` и `faster-whisper` (конфликт версий `tokenizers`)
- `gradio` и `spacy` (конфликт версий `typer`)
- `pydantic` версии 1.x vs 2.x
- Проблемы с CUDA и cuDNN для новых GPU (RTX 5080)
- Проблемы с PyTorch 2.6+ и weights_only режимом

## Пошаговое решение

### 1. Установка совместимых версий transformers и faster-whisper

```bash
# Устанавливаем transformers 4.42.4
pip install transformers==4.42.4

# Устанавливаем совместимую версию tokenizers для faster-whisper
pip install tokenizers==0.14

# Устанавливаем faster-whisper 1.1 (совместимую версию)
pip install faster-whisper==1.1

# Возвращаем transformers 4.42.4
pip install transformers==4.42.4
```

### 2. Установка PyTorch для CUDA 12.9 (RTX 5080)

```bash
# Удаляем старый PyTorch
pip uninstall torch torchvision torchaudio -y

# Устанавливаем nightly сборку для CUDA 12.9
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu129
```

### 3. Решение проблемы weights_only в PyTorch 2.6+

Создайте файл `sitecustomize.py` в папке виртуальной среды:
```python
# D:\StoneSegmentation\alltalk2\alltalk_environment\env\Lib\site-packages\sitecustomize.py

import torch
from torch.serialization import add_safe_globals
import os, importlib.util, pathlib

# Разрешаем классы XTTS для загрузки чекпоинтов
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig
from TTS.config.shared_configs import BaseDatasetConfig

add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig])

# Добавляем путь к cuDNN DLL
spec = importlib.util.find_spec("nvidia")
if spec is not None:
    cudnn_lib = pathlib.Path(spec.origin).with_name("cudnn").joinpath("lib")
    if cudnn_lib.exists():
        os.add_dll_directory(str(cudnn_lib))
```

### 4. Установка cuDNN 8.9 для CUDA 12.9

**ВАЖНО**: PyTorch 2.9 для Windows требует cuDNN 8.x, а не 9.x!

```bash
# Удаляем cuDNN 9.x (если установлен)
pip uninstall -y nvidia-cudnn-cu12 nvidia-cublas-cu12 nvidia-cuda-nvrtc-cu12

# Устанавливаем cuDNN 8.9 для CUDA 12
pip install --force-reinstall --no-cache-dir "nvidia-cudnn-cu12==8.9.*"
```

### 5. Решение конфликтов Gradio и spaCy

#### Вариант A: Совместимые версии (рекомендуется)

```bash
# Удаляем конфликтующие версии
pip uninstall -y gradio gradio-client typer click spacy weasel

# Устанавливаем совместимый набор
pip install "click>=8.1.7" "typer>=0.12" "gradio==5.35.0"

# Возвращаем spaCy без зависимостей
pip install --no-deps "spacy==3.7.4" "weasel==0.3.4"
```

#### Вариант B: Откат к Gradio 3.50.2 (для finetune.py)

```bash
# Удаляем новые версии
pip uninstall -y gradio gradio-client typer click

# Устанавливаем совместимые версии
pip install "gradio==3.50.2" "click>=8.1.7" "typer>=0.12"

# Откатываем Pydantic для совместимости
pip uninstall -y pydantic pydantic-core
pip install "pydantic<2.0" "pydantic-core<2.0"
```

### 6. Создание рабочего .bat файла

Создайте `start_finetune.bat`:

```batch
@echo off
cd /D "D:\StoneSegmentation\alltalk2"

call "D:\StoneSegmentation\alltalk_environment\conda\condabin\conda.bat" activate "D:\StoneSegmentation\alltalk_environment\env"

python finetune.py
pause
```

## Типичные ошибки и решения

### ❌ CUDA error: no kernel image is available for execution on the device

**Причина:** PyTorch не содержит ядер для вашей архитектуры GPU (SM 8.9 для RTX 5080)

**Решение:**
```bash
# Установить nightly PyTorch с поддержкой CUDA 12.9
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu129
```

### ❌ Could not locate cudnn_ops_infer64_8.dll

**Причина:** Отсутствуют cuDNN DLL файлы или установлена неправильная версия

**Решение:**
```bash
# Удаляем cuDNN 9.x и устанавливаем cuDNN 8.9
pip uninstall -y nvidia-cudnn-cu12
pip install --force-reinstall --no-cache-dir "nvidia-cudnn-cu12==8.9.*"
```

### ❌ cuDNN version: 91002 (вместо 8905)

**Причина:** Установлена версия cuDNN 9.x вместо 8.x

**Решение:** Удалить cuDNN 9.x и установить cuDNN 8.9.x

### ❌ UnpicklingError: Weights only load failed

**Причина:** PyTorch 2.6+ блокирует загрузку pickle объектов

**Решение:** Создать `sitecustomize.py` с allow-list (см. шаг 3)

### ❌ ValidationError: length Input should be a valid integer

**Причина:** Pydantic 2.x vs Gradio 3.50.2 конфликт

**Решение:**
```bash
pip uninstall -y pydantic pydantic-core
pip install "pydantic<2.0" "pydantic-core<2.0"
```

### ❌ TypeError: event_trigger() got an unexpected keyword argument 'every'

**Причина:** Gradio 5.x не поддерживает аргумент `every` в `demo.load()`

**Решение:** Откатиться к Gradio 3.50.2 (см. шаг 5, вариант B)

## Проверка установки

```bash
# Проверка версий
python - <<'PY'
import click, typer, gradio, spacy, flask, torch
print("click   :", click.__version__)
print("typer   :", typer.__version__)
print("gradio  :", gradio.__version__)
print("flask   :", flask.__version__)
print("spacy   :", spacy.__version__)
print("torch   :", torch.__version__)
if torch.cuda.is_available():
    print("GPU     :", torch.cuda.get_device_name(0))
    print("cuDNN   :", torch.backends.cudnn.version())
PY
```

## Рекомендуемые версии

| Пакет | Версия | Примечание |
|-------|--------|------------|
| transformers | 4.42.4 | Стабильная версия для XTTS |
| tokenizers | 0.19.1 | Совместима с transformers 4.42.4 |
| faster-whisper | 1.1.0 | Совместима с tokenizers 0.19.1 |
| gradio | 3.50.2 | Для finetune.py |
| pydantic | <2.0 | Для совместимости с Gradio 3.50.2 |
| typer | >=0.12 | Для Gradio 3.50.2 |
| click | >=8.1.7 | Для Flask 3.0 |
| nvidia-cudnn-cu12 | 8.9.* | cuDNN 8.x для PyTorch 2.9 Windows |

## Альтернативные решения

### Запуск на CPU (если GPU не критичен)

```bash
# Временно отключить GPU
set CUDA_VISIBLE_DEVICES=
python finetune.py
```

### Создание отдельного окружения

```bash
# Создать отдельное окружение для AllTalk
python -m venv alltalk_env
alltalk_env\Scripts\activate
# Установить только необходимые пакеты
```

## Если появится новый трейсбек

Пришлите его полностью, посмотрим дальше. Обычно проблемы решаются пошагово, следуя логике зависимостей.

После всех изменений:
1. AllTalk должен запускаться без ошибок
2. XTTS должен загружаться в CUDA
3. finetune.py должен работать без ValidationError
4. Whisper должен обрабатывать аудио без ошибок cuDNN
5. cuDNN version должен быть 8905 (не 91002)