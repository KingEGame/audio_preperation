"""
Менеджеры для управления GPU памятью и моделями
"""

import threading
import gc
import torch
import whisper
from demucs.pretrained import get_model

# Глобальный блокировщик доступа к GPU
GPU_LOCK = threading.Lock()

class GPUMemoryManager:
    """Продвинутое управление GPU памятью с автоматической очисткой"""
    
    def __init__(self, memory_limit=0.75):
        self.memory_limit = memory_limit
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.initial_memory = self._get_gpu_memory() if self.device.type == "cuda" else 0
        
    def _get_gpu_memory(self):
        """Получить текущее использование GPU памяти"""
        if self.device.type == "cuda":
            return torch.cuda.memory_allocated() / 1024**3  # GB
        return 0
    
    def _get_gpu_memory_total(self):
        """Получить общий объем GPU памяти"""
        if self.device.type == "cuda":
            return torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
        return 0
    
    def check_memory(self, required_gb=2.0):
        """Проверить, достаточно ли GPU памяти"""
        if self.device.type != "cuda":
            return True
            
        current_usage = self._get_gpu_memory()
        total_memory = self._get_gpu_memory_total()
        available = total_memory * self.memory_limit - current_usage
        
        return available >= required_gb
    
    def cleanup(self, force=False):
        """Очистить GPU память"""
        if self.device.type == "cuda":
            with GPU_LOCK:
                torch.cuda.empty_cache()
                gc.collect()
                
                if force:
                    # Принудительная очистка путем выделения и освобождения памяти
                    try:
                        temp_tensor = torch.zeros(1, device=self.device)
                        del temp_tensor
                        torch.cuda.empty_cache()
                    except:
                        pass
    
    def monitor_memory(self, logger=None):
        """Мониторинг и логирование использования GPU памяти"""
        if self.device.type == "cuda":
            current = self._get_gpu_memory()
            total = self._get_gpu_memory_total()
            if logger:
                logger.info(f"GPU Memory: {current:.2f}GB / {total:.2f}GB ({current/total*100:.1f}%)")
            return current, total
        return 0, 0

class ModelManager:
    """Централизованное управление моделями с кэшированием и GPU оптимизацией"""
    
    def __init__(self, gpu_manager):
        self.gpu_manager = gpu_manager
        self.models = {}
        self.device = gpu_manager.device
        
    def get_whisper_model(self, model_size="base"):
        """Получить Whisper модель с кэшированием"""
        model_key = f"whisper_{model_size}"
        
        if model_key not in self.models:
            self.gpu_manager.cleanup()
            self.models[model_key] = whisper.load_model(model_size)
            if self.device.type == "cuda":
                self.models[model_key] = self.models[model_key].to(self.device)
        
        return self.models[model_key]
    
    def get_demucs_model(self):
        """Получить Demucs модель с кэшированием"""
        model_key = "demucs_htdemucs"
        
        if model_key not in self.models:
            self.gpu_manager.cleanup()
            self.models[model_key] = get_model("htdemucs")
            if self.device.type == "cuda":
                self.models[model_key] = self.models[model_key].to(self.device)
        
        return self.models[model_key]
    
    def get_silero_vad_model(self):
        """Получить Silero VAD модель с кэшированием"""
        model_key = "silero_vad"
        
        if model_key not in self.models:
            try:
                import silero_vad
                self.models[model_key] = silero_vad.load_silero_vad()
                # Пытаемся использовать GPU, но с fallback на CPU
                try:
                    if self.device.type == "cuda":
                        self.models[model_key] = self.models[model_key].to(self.device)
                except Exception as e:
                    # Если не удалось переместить на GPU, используем CPU
                    self.models[model_key] = self.models[model_key].cpu()
            except ImportError:
                raise ImportError("silero-vad not installed")
        
        return self.models[model_key]
    
    def get_diarization_pipeline(self, token):
        """Получить PyAnnote диаризационный пайплайн с кэшированием"""
        model_key = "pyannote_diarization"
        
        if model_key not in self.models:
            self.gpu_manager.cleanup()
            from pyannote.audio import Pipeline
            self.models[model_key] = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=token
            )
            if self.device.type == "cuda":
                self.models[model_key] = self.models[model_key].to(self.device)
        
        return self.models[model_key]
    
    def cleanup_models(self):
        """Очистить все модели"""
        for model in self.models.values():
            if hasattr(model, 'cpu'):
                model.cpu()
            del model
        self.models.clear()
        self.gpu_manager.cleanup(force=True)