# 數據壓縮和虛擬化管理
import os
import gzip
import json
import pickle
import tarfile
from pathlib import Path
from typing import Dict, Any
import hashlib

class DataManager:
    def __init__(self, base_dir: str = "/root/comic_ai"):
        self.base_dir = Path(base_dir)
        self.compressed_dir = self.base_dir / "compressed_data"
        self.compressed_dir.mkdir(exist_ok=True)
        
    def compress_file(self, file_path: str, compression_level: int = 6) -> str:
        """壓縮單個文件"""
        file_path = Path(file_path)
        compressed_path = self.compressed_dir / f"{file_path.name}.gz"
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=compression_level) as f_out:
                f_out.writelines(f_in)
        
        return str(compressed_path)
    
    def decompress_file(self, compressed_path: str, output_path: str = None) -> str:
        """解壓縮文件"""
        compressed_path = Path(compressed_path)
        
        if output_path is None:
            output_path = self.base_dir / compressed_path.stem
        
        with gzip.open(compressed_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        return str(output_path)
    
    def create_archive(self, source_dir: str, archive_name: str = None) -> str:
        """創建壓縮存檔"""
        source_dir = Path(source_dir)
        
        if archive_name is None:
            archive_name = f"{source_dir.name}.tar.gz"
        
        archive_path = self.compressed_dir / archive_name
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(source_dir, arcname=source_dir.name)
        
        return str(archive_path)
    
    def batch_compress(self, file_patterns: list = ["*.csv", "*.json", "*.txt", "*.log"]) -> Dict[str, str]:
        """批量壓縮文件"""
        results = {}
        
        for pattern in file_patterns:
            for file_path in self.base_dir.rglob(pattern):
                if file_path.is_file():
                    compressed = self.compress_file(file_path)
                    results[str(file_path)] = compressed
        
        return results
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """獲取存儲統計信息"""
        total_size = 0
        compressed_size = 0
        
        for file_path in self.base_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        for file_path in self.compressed_dir.rglob("*"):
            if file_path.is_file():
                compressed_size += file_path.stat().st_size
        
        compression_ratio = (compressed_size / total_size * 100) if total_size > 0 else 0
        
        return {
            "original_size_mb": total_size / (1024 * 1024),
            "compressed_size_mb": compressed_size / (1024 * 1024),
            "compression_ratio_percent": compression_ratio,
            "space_saved_mb": (total_size - compressed_size) / (1024 * 1024)
        }

if __name__ == "__main__":
    dm = DataManager()
    
    # 批量壓縮數據
    print("🗜️ 開始壓縮數據...")
    results = dm.batch_compress()
    
    # 創建完整存檔
    print("📦 創建數據存檔...")
    archive = dm.create_archive("./data")
    
    # 顯示統計
    stats = dm.get_storage_stats()
    print(f"📊 壓縮統計:")
    print(f"   原始大小: {stats['original_size_mb']:.2f} MB")
    print(f"   壓縮後: {stats['compressed_size_mb']:.2f} MB")
    print(f"   節省空間: {stats['space_saved_mb']:.2f} MB")
    print(f"   壓縮率: {stats['compression_ratio_percent']:.1f}%")