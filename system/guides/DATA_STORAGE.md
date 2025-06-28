# Структура хранения данных

## Обзор

В проекте используются следующие файлы для хранения конфигурационных данных:

## Файлы конфигурации

### 1. hf_token.txt
**Местоположение:** `[PROJECT_ROOT]/hf_token.txt`

**Назначение:** Хранит токен HuggingFace для доступа к моделям PyAnnote

**Содержимое:** Одна строка с токеном

**Как создается:**
- `system/instructions/setup_diarization.bat` - через batch скрипт
- `system/scripts/setup_diarization.py` - через Python скрипт

**Как используется:**
- `system/scripts/audio_processing.py` - для диаризации
- `system/scripts/test_diarization_token.py` - для тестирования
- `system/scripts/fix_diarization_access.py` - для исправления доступа

### 2. Access.txt (планируется)
**Местоположение:** `[PROJECT_ROOT]/Access.txt`

**Назначение:** Может использоваться для дополнительных настроек доступа

**Статус:** Пока не используется

## Структура папок

```
audio_preperation/
├── hf_token.txt              # Токен HuggingFace
├── Access.txt                # Дополнительные настройки (планируется)
├── system/
│   ├── scripts/
│   │   ├── config.py         # Централизованная конфигурация
│   │   ├── audio_processing.py
│   │   ├── setup_diarization.py
│   │   ├── test_diarization_token.py
│   │   └── fix_diarization_access.py
│   └── instructions/
│       └── setup_diarization.bat
└── results/                  # Папка для результатов (создается автоматически)
```

## Централизованная конфигурация

Файл `system/scripts/config.py` содержит централизованное управление путями:

```python
# Корневая папка проекта
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Файлы конфигурации
HF_TOKEN_FILE = PROJECT_ROOT / "hf_token.txt"
ACCESS_FILE = PROJECT_ROOT / "Access.txt"

# Функции для работы с токеном
def get_token(): ...
def save_token(token): ...
def token_exists(): ...
```

## Безопасность

### Рекомендации:
1. **Не коммитить токены в Git** - добавьте в `.gitignore`:
   ```
   hf_token.txt
   Access.txt
   ```

2. **Использовать переменные окружения** для продакшена

3. **Регулярно обновлять токены** HuggingFace

## Использование в коде

### Получение токена:
```python
from system.scripts.config import get_token, token_exists

if token_exists():
    token = get_token()
    # Использовать токен
else:
    # Обработать отсутствие токена
```

### Сохранение токена:
```python
from system.scripts.config import save_token

save_token("your_huggingface_token_here")
```

## Устранение неполадок

### Проблема: "Файл hf_token.txt не найден"
**Решение:**
1. Запустите `setup_diarization.bat`
2. Или запустите `system/scripts/setup_diarization.py`
3. Следуйте инструкциям для получения токена HuggingFace

### Проблема: "Токен невалиден"
**Решение:**
1. Проверьте токен на https://huggingface.co/settings/tokens
2. Создайте новый токен с правами 'Read'
3. Обновите файл `hf_token.txt`

### Проблема: "Доступ к модели запрещен"
**Решение:**
1. Примите условия использования на странице модели
2. Подождите 2-3 минуты после принятия условий
3. Запустите `system/scripts/test_diarization_token.py` для проверки 