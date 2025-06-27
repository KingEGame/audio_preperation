#!/usr/bin/env python3
"""
Мониторинг производительности системы во время аудио-обработки
Оптимизировано для RTX 5080, R5 5600X, 32GB RAM
"""

import psutil
import time
import threading
import os
import json
from datetime import datetime
from pathlib import Path

try:
    import torch
    import GPUtil
except ImportError:
    print("Установите зависимости: pip install psutil GPUtil")
    exit(1)

class PerformanceMonitor:
    def __init__(self, log_file="performance_log.json"):
        self.log_file = log_file
        self.monitoring = False
        self.metrics = []
        self.start_time = None
        
    def start_monitoring(self):
        """Запускает мониторинг производительности"""
        self.monitoring = True
        self.start_time = time.time()
        self.metrics = []
        
        # Запускаем мониторинг в отдельном потоке
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("✓ Мониторинг производительности запущен")
        print("  - GPU: температура, память, загрузка")
        print("  - CPU: загрузка, температура")
        print("  - RAM: использование")
        print("  - Диск: I/O операции")
        
    def stop_monitoring(self):
        """Останавливает мониторинг и сохраняет результаты"""
        self.monitoring = False
        time.sleep(1)  # Даем время на завершение мониторинга
        
        # Сохраняем результаты
        self._save_results()
        
        print("✓ Мониторинг производительности остановлен")
        print(f"  Результаты сохранены в: {self.log_file}")
        
    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.monitoring:
            try:
                metric = self._collect_metrics()
                self.metrics.append(metric)
                time.sleep(5)  # Обновляем каждые 5 секунд
            except Exception as e:
                print(f"Ошибка мониторинга: {e}")
                time.sleep(10)
    
    def _collect_metrics(self):
        """Собирает метрики производительности"""
        timestamp = time.time()
        
        # CPU метрики
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        # RAM метрики
        memory = psutil.virtual_memory()
        
        # Диск метрики
        disk_io = psutil.disk_io_counters()
        
        # GPU метрики
        gpu_metrics = self._get_gpu_metrics()
        
        return {
            'timestamp': timestamp,
            'cpu': {
                'percent': cpu_percent,
                'freq_mhz': cpu_freq.current if cpu_freq else None,
                'count': cpu_count
            },
            'memory': {
                'total_gb': memory.total / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent': memory.percent
            },
            'disk': {
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0
            },
            'gpu': gpu_metrics
        }
    
    def _get_gpu_metrics(self):
        """Получает метрики GPU"""
        try:
            if torch.cuda.is_available():
                # PyTorch GPU метрики
                gpu_memory_allocated = torch.cuda.memory_allocated() / (1024**3)
                gpu_memory_reserved = torch.cuda.memory_reserved() / (1024**3)
                gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                
                # GPUtil для дополнительных метрик
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Первая GPU
                    return {
                        'name': gpu.name,
                        'temperature': gpu.temperature,
                        'load_percent': gpu.load * 100 if gpu.load else 0,
                        'memory_used_gb': gpu.memoryUsed,
                        'memory_total_gb': gpu.memoryTotal,
                        'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100,
                        'pytorch_allocated_gb': gpu_memory_allocated,
                        'pytorch_reserved_gb': gpu_memory_reserved,
                        'pytorch_total_gb': gpu_memory_total
                    }
                else:
                    return {
                        'name': 'Unknown GPU',
                        'pytorch_allocated_gb': gpu_memory_allocated,
                        'pytorch_reserved_gb': gpu_memory_reserved,
                        'pytorch_total_gb': gpu_memory_total
                    }
            else:
                return {'available': False}
        except Exception as e:
            return {'error': str(e)}
    
    def _save_results(self):
        """Сохраняет результаты мониторинга"""
        if not self.metrics:
            return
            
        results = {
            'system_info': self._get_system_info(),
            'monitoring_duration_seconds': time.time() - self.start_time,
            'metrics_count': len(self.metrics),
            'metrics': self.metrics,
            'summary': self._calculate_summary()
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def _get_system_info(self):
        """Получает информацию о системе"""
        return {
            'platform': os.name,
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'gpu_available': torch.cuda.is_available(),
            'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
            'gpu_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        }
    
    def _calculate_summary(self):
        """Вычисляет сводную статистику"""
        if not self.metrics:
            return {}
        
        # CPU статистика
        cpu_percents = [m['cpu']['percent'] for m in self.metrics if m['cpu']['percent'] is not None]
        
        # RAM статистика
        memory_percents = [m['memory']['percent'] for m in self.metrics]
        
        # GPU статистика
        gpu_temps = []
        gpu_loads = []
        gpu_memory_percents = []
        
        for m in self.metrics:
            if 'gpu' in m and m['gpu'] and 'temperature' in m['gpu']:
                gpu_temps.append(m['gpu']['temperature'])
            if 'gpu' in m and m['gpu'] and 'load_percent' in m['gpu']:
                gpu_loads.append(m['gpu']['load_percent'])
            if 'gpu' in m and m['gpu'] and 'memory_percent' in m['gpu']:
                gpu_memory_percents.append(m['gpu']['memory_percent'])
        
        return {
            'cpu': {
                'avg_percent': sum(cpu_percents) / len(cpu_percents) if cpu_percents else 0,
                'max_percent': max(cpu_percents) if cpu_percents else 0,
                'min_percent': min(cpu_percents) if cpu_percents else 0
            },
            'memory': {
                'avg_percent': sum(memory_percents) / len(memory_percents),
                'max_percent': max(memory_percents),
                'min_percent': min(memory_percents)
            },
            'gpu': {
                'avg_temperature': sum(gpu_temps) / len(gpu_temps) if gpu_temps else 0,
                'max_temperature': max(gpu_temps) if gpu_temps else 0,
                'avg_load': sum(gpu_loads) / len(gpu_loads) if gpu_loads else 0,
                'max_load': max(gpu_loads) if gpu_loads else 0,
                'avg_memory': sum(gpu_memory_percents) / len(gpu_memory_percents) if gpu_memory_percents else 0,
                'max_memory': max(gpu_memory_percents) if gpu_memory_percents else 0
            }
        }
    
    def print_realtime_stats(self):
        """Выводит текущую статистику в реальном времени"""
        if not self.metrics:
            print("Нет данных для отображения")
            return
        
        latest = self.metrics[-1]
        
        print("\n" + "="*60)
        print("ТЕКУЩАЯ СТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ")
        print("="*60)
        
        # CPU
        cpu = latest['cpu']
        print(f"CPU: {cpu['percent']:.1f}% | {cpu['freq_mhz']:.0f} MHz | {cpu['count']} ядер")
        
        # RAM
        memory = latest['memory']
        print(f"RAM: {memory['used_gb']:.1f}/{memory['total_gb']:.1f} GB ({memory['percent']:.1f}%)")
        
        # GPU
        gpu = latest.get('gpu', {})
        if gpu and 'temperature' in gpu:
            print(f"GPU: {gpu['temperature']:.1f}°C | {gpu['load_percent']:.1f}% | {gpu['memory_percent']:.1f}% памяти")
            if 'pytorch_allocated_gb' in gpu:
                print(f"PyTorch GPU: {gpu['pytorch_allocated_gb']:.2f}/{gpu['pytorch_total_gb']:.2f} GB")
        
        # Время работы
        if self.start_time:
            elapsed = time.time() - self.start_time
            print(f"Время мониторинга: {elapsed/60:.1f} минут")
        
        print("="*60)

def main():
    """Основная функция для запуска мониторинга"""
    print("МОНИТОРИНГ ПРОИЗВОДИТЕЛЬНОСТИ СИСТЕМЫ")
    print("Оптимизировано для RTX 5080 + R5 5600X + 32GB RAM")
    print()
    
    monitor = PerformanceMonitor()
    
    print("Выберите режим:")
    print("1. Запустить мониторинг и ждать завершения")
    print("2. Запустить мониторинг в фоне")
    print("3. Показать текущую статистику системы")
    
    choice = input("Выбор (1-3): ").strip()
    
    if choice == "1":
        print("\nЗапуск мониторинга...")
        monitor.start_monitoring()
        
        try:
            while True:
                time.sleep(30)  # Обновляем каждые 30 секунд
                monitor.print_realtime_stats()
        except KeyboardInterrupt:
            print("\nОстановка мониторинга...")
            monitor.stop_monitoring()
    
    elif choice == "2":
        print("\nЗапуск мониторинга в фоне...")
        monitor.start_monitoring()
        print("Мониторинг запущен в фоне.")
        print("Для остановки нажмите Ctrl+C или завершите процесс")
        
        try:
            while True:
                time.sleep(60)  # Проверяем каждую минуту
        except KeyboardInterrupt:
            print("\nОстановка мониторинга...")
            monitor.stop_monitoring()
    
    elif choice == "3":
        print("\nТекущая статистика системы:")
        monitor.start_monitoring()
        time.sleep(5)  # Собираем данные
        monitor.print_realtime_stats()
        monitor.stop_monitoring()
    
    else:
        print("Неверный выбор")

if __name__ == "__main__":
    main() 