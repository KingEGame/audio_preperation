# Translation Guide: Cyrillic to Latin

## Overview

All Cyrillic text in the project has been translated to Latin to ensure compatibility across different systems and locales.

## Translated Files

### Python Scripts
- `system/scripts/audio_processing.py` - Main audio processing pipeline
- `system/scripts/setup_diarization.py` - PyAnnote setup script
- `system/scripts/test_diarization_token.py` - Token testing script
- `system/scripts/fix_diarization_access.py` - Access fix script
- `system/scripts/config.py` - Configuration module

### Key Changes

#### Comments and Docstrings
```python
# Before (Cyrillic)
"""
Аудио-процессинг пайплайн с поддержкой GPU
"""

# After (Latin)
"""
Audio processing pipeline with GPU support
"""
```

#### User Messages
```python
# Before
print("Обработка завершена!")

# After
print("Processing completed!")
```

#### Error Messages
```python
# Before
logger.error("Ошибка при диаризации")

# After
logger.error("Error during diarization")
```

#### Function Names and Variables
- All function names remain in English
- Variable names remain in English
- Only user-facing text was translated

## Benefits

1. **Universal Compatibility** - Works on all systems regardless of locale
2. **No Encoding Issues** - Eliminates potential character encoding problems
3. **Professional Appearance** - Consistent English interface
4. **Easier Maintenance** - Standard ASCII characters only

## Translation Rules

### Preserved Elements
- Function names: `process_audio()`, `setup_diarization()`
- Variable names: `audio_file`, `output_dir`
- Technical terms: `GPU`, `CUDA`, `PyTorch`
- File paths and URLs

### Translated Elements
- User messages and prompts
- Error messages and warnings
- Comments and documentation
- Help text and instructions

### Examples

#### User Interface
```python
# Before
print("Введите путь к аудиофайлу:")
print("Примеры: audio.mp3, C:\\path\\to\\file.mp3")

# After
print("Enter path to audio file:")
print("Examples: audio.mp3, C:\\path\\to\\file.mp3")
```

#### Error Handling
```python
# Before
logger.error("Файл не найден")
logger.info("Проверьте правильность пути")

# After
logger.error("File not found")
logger.info("Check path correctness")
```

#### Progress Messages
```python
# Before
print("Начинаем обработку файлов...")
print("Этап 1: Нарезка аудио")

# After
print("Starting file processing...")
print("Stage 1: Audio splitting")
```

## Testing

After translation, all scripts should:
1. Display English messages correctly
2. Handle user input properly
3. Generate English log files
4. Work on systems with different locales

## Future Considerations

- Keep all new code in English
- Use consistent terminology across all files
- Maintain professional documentation standards
- Consider internationalization if needed in future 