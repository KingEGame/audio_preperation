"""
Audio Processing Package
Модульная система для обработки аудио файлов
"""

from .managers import GPUMemoryManager, ModelManager
from .processors import (
    process_audio_file_optimized,
    process_multiple_files_parallel_optimized,
    process_file_multithreaded_optimized
)
from .stages import (
    clean_audio_with_demucs_optimized,
    diarize_with_pyannote_optimized
)
from .splitters import (
    split_audio_by_duration_optimized,
    split_audio_at_word_boundary_optimized,
    split_audio_smart_multithreaded_optimized
)
from .utils import (
    get_mp3_duration,
    setup_logging,
    copy_results_to_output_optimized,
    parallel_audio_processing_optimized
)
from .config import (
    get_optimal_workers, setup_gpu_optimization,
    MAX_WORKERS,
    GPU_MEMORY_LIMIT,
    BATCH_SIZE
)

__all__ = [
    'GPUMemoryManager', 'ModelManager',
    'process_audio_file_optimized', 'parallel_audio_processing_optimized',
    'process_multiple_files_parallel_optimized', 'process_file_multithreaded_optimized',
    'clean_audio_with_demucs_optimized', 'diarize_with_pyannote_optimized',
    'split_audio_by_duration_optimized', 'split_audio_at_word_boundary_optimized',
    'split_audio_smart_multithreaded_optimized',
    'get_mp3_duration', 'setup_logging', 'copy_results_to_output_optimized',
    'get_optimal_workers', 'setup_gpu_optimization', 'MAX_WORKERS', 'GPU_MEMORY_LIMIT', 'BATCH_SIZE'
]