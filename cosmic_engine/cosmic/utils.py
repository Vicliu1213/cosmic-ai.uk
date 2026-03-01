import logging
from typing import Optional
from pathlib import Path
import json
from datetime import datetime

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """設置日誌系統"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 建立日誌格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # 配置根日誌記錄器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # 文件處理器（如果指定了日誌文件）
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """取得日誌記錄器"""
    return logging.getLogger(name)

def export_json_snapshot(data: dict, filepath: str):
    """匯出 JSON 快照"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json_snapshot(filepath: str) -> dict:
    """載入 JSON 快照"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_timestamp() -> str:
    """生成時間戳"""
    return datetime.now().isoformat()

def format_percentage(value: float, decimals: int = 2) -> str:
    """格式化百分比"""
    return f"{value * 100:.{decimals}f}%"

def calculate_statistics(values: list) -> dict:
    """計算統計信息"""
    if not values:
        return {'mean': 0, 'min': 0, 'max': 0, 'std': 0}
    
    import statistics
    
    mean = statistics.mean(values)
    min_val = min(values)
    max_val = max(values)
    
    try:
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
    except:
        std_dev = 0
    
    return {
        'mean': mean,
        'min': min_val,
        'max': max_val,
        'std': std_dev,
        'count': len(values)
    }
